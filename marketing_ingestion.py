import os
import sys
import logging
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from decimal import Decimal, InvalidOperation
from sqlalchemy import create_engine
from dotenv import load_dotenv

# =====================================================================
# 1. ENTERPRISE LOGGING CONFIGURATION (Module 6 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Ingestion] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Clean routing to pipeline orchestrators
    ]
)

logging.info("🚀 Initializing UpDataLogic Marketing Ingestion Layer (Production Observability Mode)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"
ENV_FILE = BASE_DIR / ".env"

# Metrics Trackers for first-class alerting outputs
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

# Database Connection Context with Active Fallback
try:
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT", "6543")
        DB_NAME = os.getenv("DB_NAME")
        
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
            raise ValueError("Incomplete cloud warehouse credentials.")
            
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            pass
        logging.info("🔌 Connection Status: [ONLINE] Remote PostgreSQL Connected.")
    else:
        raise FileNotFoundError("Environment secure .env descriptor target missing.")

except Exception as db_error:
    logging.warning(f"⚠️ Production Data Core Offline or Network Issue: {db_error}")
    logging.info("🔄 Activating Portfolio Architecture Fallback Mode (Local Standalone Engine)...")
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    logging.info("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context Deployed.")

# =====================================================================
# ETL PIPELINE & DEFENSIVE ERROR HANDLING
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    logging.info(f"📥 1. EXTRACTION: Reading raw database log payload from: {DATA_FILE.name}")
    df = pd.read_csv(DATA_FILE, dtype={"CustomerID": str}, low_memory=False)
    
    METRICS_TRACKER["total_records_extracted"] = len(df)
    logging.info(f"✅ EXTRACTION SUCCESS: Pulled {METRICS_TRACKER['total_records_extracted']:,} transactional records into memory.")
    
    logging.info("⏳ 2. TRANSFORMATION: Executing pure self-healing data normalizers...")
    
    def self_heal_support_calls(value, row_idx):
        if pd.isna(value) or str(value).strip() in ('', 'UNKNOWN'):
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError) as e:
            # First-class error visibility: flag it, don't guess a silent zero
            logging.warning(f"🔧 Low-Level Type Slip on Row {row_idx} [SupportCalls='{value}']. Coercing to NULL. Reason: {e}")
            return None

    def self_heal_marketing_spend(value, row_idx):
        if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
            return None
        
        clean_str = str(value).strip()
        if ',' in clean_str and '.' in clean_str:
            clean_str = clean_str.replace(',', '')
        elif ',' in clean_str and '.' not in clean_str:
            clean_str = clean_str.replace(',', '.')
            
        clean_str = clean_str.replace('$', '').replace('€', '').strip()
        try:
            parsed_decimal = Decimal(clean_str).quantize(Decimal("0.01"))
            # Fail-fast constraint validation
            if parsed_decimal < 0:
                raise ValueError(f"Negative spend anomaly detected: {parsed_decimal}")
            return float(parsed_decimal)
        except (InvalidOperation, ValueError) as err:
            # We track the rejection actively as a first-class operational output
            logging.error(f"🚨 Data Quality Breach on Row {row_idx} [TotalSpend_USD='{value}']. Reason: {err}")
            return None

    # Execute transformations with index injection for robust troubleshooting logs
    df['SupportCalls'] = [self_heal_support_calls(val, idx) for idx, val in enumerate(df['SupportCalls'])]
    df['TotalSpend_USD'] = [self_heal_marketing_spend(val, idx) for idx, val in enumerate(df['TotalSpend_USD'])]
    
    # Calculate operational telemetry states
    df['data_quality_status'] = df[['TotalSpend_USD', 'SupportCalls']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    METRICS_TRACKER["rejected_records_critical"] = int(df['TotalSpend_USD'].isna().sum())
    METRICS_TRACKER["successfully_healed_records"] = METRICS_TRACKER["total_records_extracted"] - METRICS_TRACKER["rejected_records_critical"]

    logging.info("🛡️ 3. VALIDATION: Running declarative structural data quality tests via Pandera...")
    validated_df = marketing_ingest_schema.validate(df)
    
    # Alerting Threshold Execution Layer (Fail-fast engine rule)
    rejection_rate = (METRICS_TRACKER["rejected_records_critical"] / METRICS_TRACKER["total_records_extracted"]) * 100
    logging.info(f"📊 DATA QUALITY METRICS: Clean/Healed: {METRICS_TRACKER['successfully_healed_records']:,} | Quarantined/NULL: {METRICS_TRACKER['rejected_records_critical']:,} ({rejection_rate:.2f}%)")
    
    # Alert constraint threshold if critical errors compromise more than 5.0% of the payload
    if rejection_rate > 5.0:
        raise ValueError(f"Pipeline processing halted. Rejection threshold breached: {rejection_rate:.2f}% (Limit: 5.0%)")

    logging.info(f"📤 4. LOADING: Streaming verified fact matrices into warehouse target tables...")
    validated_df.to_sql('marketing_churn_raw', engine, if_exists='replace', index=False)
    
    logging.info("🏆 PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]. Financial telemetry secured successfully.\n")
    sys.exit(0) # Guarantee clean scheduler tracking exit code parameters

except pa.errors.SchemaError as schema_fault:
    logging.critical(f"❌ PIPELINE STOPPED VIA PANDERA STRUCTURAL SHIELD: {schema_fault}")
    sys.exit(1) # Enforce strict exit 1 error flag parameters for orchestrators
except Exception as fatal_error:
    logging.critical(f"❌ PIPELINE RUN CRITICAL FAILURE: {fatal_error}")
    sys.exit(1)
