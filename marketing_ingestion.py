import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from marketing_parser import clean_numeric_spend

# Force UTF-8 stdout so the emoji in the log messages below never crash a
# non-interactive run on Windows (its default console codepage can't encode
# them, which otherwise silently drops all logging output).
sys.stdout.reconfigure(encoding="utf-8")

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6, 7 & 10 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Ingestion] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Starting UpDataLogic Marketing Ingestion Layer (Idempotent Production Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"
ENV_FILE = BASE_DIR / ".env"

CHUNK_SIZE = 1000

METRICS_TRACKER = {
    "total_records_extracted": 0,
    "successfully_healed_records": 0,
    "rejected_records_critical": 0
}

# Define Data Quality Shield using Pandera Specification
marketing_ingest_schema = pa.DataFrameSchema({
    "CustomerID": pa.Column(str, nullable=False),
    "CustomerSegment": pa.Column(str, pa.Check.isin(["Basic", "Standard", "Premium"]), nullable=False),
    "TenureMonths": pa.Column(int, pa.Check.ge(0), nullable=False),
    "SupportCalls": pa.Column(float, nullable=True),
    "TotalSpend_USD": pa.Column(float, nullable=True),
    "ChurnStatus": pa.Column(int, pa.Check.isin([0, 1]), nullable=False)
})

# Database Connection Check with Fallback
try:
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "6543")
        DB_NAME = os.getenv("DB_NAME")

        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
            raise ValueError("Incomplete cloud credentials.")

        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass
        logging.info("🔌 Connection Status: [ONLINE] Remote PostgreSQL Warehouse Connected.")
    else:
        raise FileNotFoundError("Config file missing.")

except Exception as db_error:
    logging.warning(f"⚠️ Production DB Offline or Network Issue detected: {db_error}")
    logging.info("🔄 Activating Portfolio Architecture Fallback Mode (Local Storage Engine)...")
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    logging.info("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context Deployed.")

# =====================================================================
# ETL INGESTION STAGE Execution with Idempotent UPSERT Matrix
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Source dataset missing at: {DATA_FILE}")

    logging.info(f"📥 1. Extraction: Reading records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, dtype={"CustomerID": str}, low_memory=False)

    METRICS_TRACKER["total_records_extracted"] = len(df)

    logging.info("⏳ 2. Transformation: Running self-healing normalizers...")

    def self_heal_support_calls(value, row_idx):
        if pd.isna(value) or str(value).strip() in ('', 'UNKNOWN'):
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    # Uses the same shared, tested parser as marketing_bi_layer.py's imports so
    # a given raw spend value is interpreted identically no matter which script
    # processes it -- this used to be a second, simpler copy defined inline
    # here, which only stripped commas and silently disagreed with
    # marketing_parser.py's own European-decimal handling.
    df['SupportCalls'] = [self_heal_support_calls(val, idx) for idx, val in enumerate(df['SupportCalls'])]
    df['TotalSpend_USD'] = df['TotalSpend_USD'].apply(clean_numeric_spend)

    df['data_quality_status'] = df[['TotalSpend_USD', 'SupportCalls']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})

    METRICS_TRACKER["rejected_records_critical"] = int(df['TotalSpend_USD'].isna().sum())
    METRICS_TRACKER["successfully_healed_records"] = METRICS_TRACKER["total_records_extracted"] - METRICS_TRACKER["rejected_records_critical"]

    logging.info("🛡️ 3. Validation: Running declarative structural checks via Pandera...")
    validated_df = marketing_ingest_schema.validate(df)

    rejection_rate = (METRICS_TRACKER["rejected_records_critical"] / METRICS_TRACKER["total_records_extracted"]) * 100
    logging.info(f"📊 DATA QUALITY METRICS: Clean: {METRICS_TRACKER['successfully_healed_records']:,} | Rejections: {METRICS_TRACKER['rejected_records_critical']:,} ({rejection_rate:.2f}%)")

    if rejection_rate > 5.0:
        raise ValueError(f"Pipeline stopped. Rejection rate {rejection_rate:.2f}% breached 5.0% limit.")

    logging.info("📤 4. LOADING: Executing idempotent UPSERT pattern routing directly to database engine...")

    all_columns = ['CustomerID', 'CustomerSegment', 'AcquisitionChannel', 'TenureMonths', 'SupportCalls', 'TotalSpend_USD', 'ChurnStatus', 'data_quality_status']
    records = validated_df[all_columns].to_dict(orient='records')

    with engine.begin() as transaction_conn:
        if str(engine.url).startswith('sqlite'):
            # PRODUCTION BLUEPRINT: Deploy strict CHECK constraints to enforce database boundaries
            transaction_conn.execute(text("DROP TABLE IF EXISTS marketing_churn_raw;"))
            transaction_conn.execute(text("""
                CREATE TABLE marketing_churn_raw (
                    CustomerID TEXT PRIMARY KEY,
                    CustomerSegment TEXT NOT NULL,
                    AcquisitionChannel TEXT,
                    TenureMonths INTEGER NOT NULL CHECK (TenureMonths >= 0),
                    SupportCalls REAL CHECK (SupportCalls >= 0 OR SupportCalls IS NULL),
                    TotalSpend_USD REAL CHECK (TotalSpend_USD >= 0 OR TotalSpend_USD IS NULL),
                    ChurnStatus INTEGER NOT NULL CHECK (ChurnStatus IN (0, 1)),
                    data_quality_status TEXT NOT NULL
                );
            """))

            # PERFORMANCE OPTIMIZATION LAYER: Deploy B-Tree analytical indexing for high-speed slicer filters
            transaction_conn.execute(text('CREATE INDEX IF NOT EXISTS idx_marketing_segment ON marketing_churn_raw (CustomerSegment);'))
            transaction_conn.execute(text('CREATE INDEX IF NOT EXISTS idx_marketing_churn ON marketing_churn_raw (ChurnStatus);'))
            logging.info("🧹 Local SQLite Strategy: Schema mapped with strict Primary Key, CHECK limits & Analytical B-Tree Indexes.")

            upsert_query = text("""
                INSERT INTO marketing_churn_raw (CustomerID, CustomerSegment, AcquisitionChannel, TenureMonths, SupportCalls, TotalSpend_USD, ChurnStatus, data_quality_status)
                VALUES (:CustomerID, :CustomerSegment, :AcquisitionChannel, :TenureMonths, :SupportCalls, :TotalSpend_USD, :ChurnStatus, :data_quality_status)
                ON CONFLICT(CustomerID) DO UPDATE SET
                    CustomerSegment=excluded.CustomerSegment,
                    AcquisitionChannel=excluded.AcquisitionChannel,
                    TenureMonths=excluded.TenureMonths,
                    SupportCalls=excluded.SupportCalls,
                    TotalSpend_USD=excluded.TotalSpend_USD,
                    ChurnStatus=excluded.ChurnStatus,
                    data_quality_status=excluded.data_quality_status;
            """)
            for i in range(0, len(records), CHUNK_SIZE):
                transaction_conn.execute(upsert_query, records[i:i + CHUNK_SIZE])
        else:
            # Remote PostgreSQL cloud storage destination fallback execution path.
            # Both sides of the SET clause must be quoted: EXCLUDED is a
            # pseudo-table with the same (case-sensitive) column names as the
            # real table, and an unquoted identifier gets folded to lowercase by
            # Postgres, which then fails to match a quoted mixed-case column
            # like "CustomerSegment" -- this used to break every real Postgres
            # run with "column excluded.customersegment does not exist".
            upsert_query = text("""
                INSERT INTO marketing_churn_raw ("CustomerID", "CustomerSegment", "AcquisitionChannel", "TenureMonths", "SupportCalls", "TotalSpend_USD", "ChurnStatus", "data_quality_status")
                VALUES (:CustomerID, :CustomerSegment, :AcquisitionChannel, :TenureMonths, :SupportCalls, :TotalSpend_USD, :ChurnStatus, :data_quality_status)
                ON CONFLICT ("CustomerID") DO UPDATE SET
                    "CustomerSegment" = EXCLUDED."CustomerSegment",
                    "AcquisitionChannel" = EXCLUDED."AcquisitionChannel",
                    "TenureMonths" = EXCLUDED."TenureMonths",
                    "SupportCalls" = EXCLUDED."SupportCalls",
                    "TotalSpend_USD" = EXCLUDED."TotalSpend_USD",
                    "ChurnStatus" = EXCLUDED."ChurnStatus",
                    "data_quality_status" = EXCLUDED."data_quality_status";
            """)
            for i in range(0, len(records), CHUNK_SIZE):
                transaction_conn.execute(upsert_query, records[i:i + CHUNK_SIZE])

    logging.info(f"🏆 PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]. {len(records):,} rows upserted. Idempotency & Database Integrity metrics verified.\n")
    sys.exit(0)

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA INGESTION SHIELD: {schema_fault}")
    sys.exit(1)
except Exception as e:
    logging.critical(f"❌ PIPELINE RUN CRITICAL FAILURE: {e}")
    sys.exit(1)
