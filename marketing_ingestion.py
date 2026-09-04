import os
import sys
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from decimal import Decimal, InvalidOperation
from sqlalchemy import create_engine
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Marketing Database Ingestion Pipeline (Self-Healing & Validated)...")

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"
ENV_FILE = BASE_DIR / ".env"

# 1. Define Strict Data Quality Shield using Pandera
marketing_ingest_schema = pa.DataFrameSchema({
    "CustomerID": pa.Column(str, nullable=False, unique=True),
    "CustomerSegment": pa.Column(str, pa.Check.isin(["Basic", "Standard", "Premium"]), nullable=False),
    "TenureMonths": pa.Column(int, pa.Check.ge(0), nullable=False),
    "SupportCalls": pa.Column(float, nullable=True),
    "TotalSpend_USD": pa.Column(float, nullable=True),
    "ChurnStatus": pa.Column(int, pa.Check.isin([0, 1]), nullable=False)
})

# 2. Establish Database Connection (With Active Operational Fallback Logic)
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
        print("🔌 Connection Status: [ONLINE] Remote PostgreSQL Warehouse Connected.")
    else:
        raise FileNotFoundError("Local config .env file missing.")

except Exception as db_error:
    print(f"⚠️ Production DB Offline or Network Issue detected: {db_error}")
    print("🔄 Activating Portfolio Architecture Fallback Mode (Local Storage Engine)...")
    
    # SQLite local engine backup strategy to guarantee flawless showcase execution
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    print("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context Deployed.")

# =====================================================================
# ETL INGESTION STAGE
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    print(f"📥 1. Extracting raw records from: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, dtype={"CustomerID": str}, low_memory=False)
    
    print("⏳ 2. Executing self-healing data type normalization pipeline...")
    
    def self_heal_support_calls(value):
        if pd.isna(value) or str(value).strip() in ('', 'UNKNOWN'):
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

    def self_heal_marketing_spend(value):
        if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
            return None
        
        clean_str = str(value).strip()
        if ',' in clean_str and '.' in clean_str:
            clean_str = clean_str.replace(',', '')
        elif ',' in clean_str and '.' not in clean_str:
            clean_str = clean_str.replace(',', '.')
            
        clean_str = clean_str.replace('$', '').replace('€', '').strip()
        try:
            return float(Decimal(clean_str).quantize(Decimal("0.01")))
        except InvalidOperation:
            return None

    df['SupportCalls'] = df['SupportCalls'].apply(self_heal_support_calls)
    df['TotalSpend_USD'] = df['TotalSpend_USD'].apply(self_heal_marketing_spend)
    
    print("🛡️ 3. Running declarative data quality checks via Pandera schema evaluation...")
    validated_df = marketing_ingest_schema.validate(df)
    
    validated_df['data_quality_status'] = validated_df[['TotalSpend_USD', 'SupportCalls']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    print(f"📤 4. Stream loading {len(validated_df):,} validated records into database layer...")
    validated_df.to_sql('marketing_churn_raw', engine, if_exists='replace', index=False)
    
    print("\n=== 🎉 PIPELINE SUCCESS: ALL DATA PROVISIONED SUCCESSFULLY ===")

except pa.errors.SchemaError as schema_fault:
    print(f"\n❌ DATA QUALITY BREACH DETECTED BY PANDERA:\n{schema_fault}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
