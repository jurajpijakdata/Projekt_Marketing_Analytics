import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from decimal import Decimal, InvalidOperation
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Importujeme znovupoužiteľnú funkciu z parsera
from marketing_parser import clean_numeric_spend

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Ingestion] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Initializing UpDataLogic Marketing Ingestion Layer (Production Observability Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"
ENV_FILE = BASE_DIR / ".env"

METRICS_TRACKER = {
    "total_records_extracted": 0,
    "successfully_healed_records": 0,
    "rejected_records_critical": 0
}

# Define Data Quality Schema
marketing_ingest_schema = pa.DataFrameSchema({
    "CustomerID": pa.Column(str, nullable=False, unique=True),
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
# ETL INGESTION STAGE
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

    # Transformácie prebiehajú cez zosúladené funkcie
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

    logging.info(f"📤 4. Loading: Streaming {len(validated_df):,} validated records into target engine...")
    validated_df.to_sql('marketing_churn_raw', engine, if_exists='replace', index=False)
    
    logging.info("🏆 PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]. Financial telemetry secured successfully.\n")
    sys.exit(0)

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA SHIELD: {schema_fault}")
    sys.exit(1)
except Exception as e:
    logging.critical(f"❌ PIPELINE RUN CRITICAL FAILURE: {e}")
    sys.exit(1)
