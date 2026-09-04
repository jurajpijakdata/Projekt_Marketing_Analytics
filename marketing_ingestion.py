import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Marketing Database Ingestion Pipeline...")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_raw"
FULL_DATA = DATA_DIR / "customer_churn_dataset.csv"
SAMPLE_DATA = DATA_DIR / "customer_churn_dataset_sample.csv"

# Load environmental variables if file exists
if (BASE_DIR / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env")

# 1. Establish Database Connection (With Active Operational Fallback Logic)
try:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "6543")
    DB_NAME = os.getenv("DB_NAME")
    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Missing database credentials in .env file.")
        
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    
    # Quick connectivity test to force resolution verification
    with engine.connect() as conn:
        pass
    print("🔌 Connection Status: [ONLINE] Connected to Remote Production PostgreSQL.")

except Exception as db_error:
    print(f"⚠️ Production DB Offline or Network Issue detected: {db_error}")
    print("🔄 Activating Portfolio Architecture Fallback Mode (Local Storage Engine)...")
    
    # SQLite local engine backup strategy to guarantee flawless showcase execution
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    print("🔌 Connection Status: [LOCAL ENGINE] Routing traffic to local physical storage architecture.")

# 2. Select Available Local Source File (Prioritizing Full Data over Sample Data)
if FULL_DATA.exists():
    target_source = FULL_DATA
    print(f"📥 Selected Target Source: Full Dataset [{FULL_DATA.name}]")
elif SAMPLE_DATA.exists():
    target_source = SAMPLE_DATA
    print(f"📥 Selected Target Source: Custom Sample Dataset [{SAMPLE_DATA.name}]")
else:
    print(f"❌ CRITICAL STORAGE ERROR: No source records found in folder target: {DATA_DIR}")
    sys.exit(1)

# 3. ETL Data Processing and Ingestion Execution Stage
try:
    print(f"⏳ Extracting raw marketing records from storage target...")
    df = pd.read_csv(target_source, low_memory=False)
    
    print("⏳ Executing structured data normalization and type validation pipeline...")
    # Strict fallback handling for text noise or malformed row parameters
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce')
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce')
    
    # Tagging records for quality assurance profiling inside the target storage
    df['data_quality_status'] = df[['SupportCalls', 'TotalSpend_USD']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    print(f"📤 Stream loading {len(df):,} records into operational target ['public.marketing_churn_raw']...")
    df.to_sql('marketing_churn_raw', engine, if_exists='replace', index=False)
    
    print("\n=== 🎉 DATA INGESTION STAGE COMPLETION: SUCCESS ===")

except Exception as pipeline_error:
    print(f"\n❌ PIPELINE CRITICAL RUNTIME ERROR: {pipeline_error}", file=sys.stderr)
    sys.exit(1)
