import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Marketing Database Ingestion Pipeline...")

# Load hidden database credentials from the local .env file
load_dotenv()

# =====================================================================
# DYNAMIC PATH RESOLUTION & CONFIGURATION
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "6543")
DB_NAME = os.getenv("DB_NAME")

# Fail fast if connection environment variables are missing
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    print("\n❌ CRITICAL CONFIG FAILURE: Missing database environment variables in .env", file=sys.stderr)
    print("Please replicate .env.example into a local .env file with valid credentials.", file=sys.stderr)
    sys.exit(1)

# Constructing the secure PostgreSQL connection URI string
connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)

# =====================================================================
# ETL INGESTION STAGE
# =====================================================================
try:
    # Fail fast if the source dataset is not accessible
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Extraction halted. Source dataset missing at: {DATA_FILE}")

    print(f"📥 1. Extracting records from local storage: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    
    print("⏳ 2. Executing pre-load data type normalization pipeline...")
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce').fillna(0).astype(int)
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce').fillna(0.0)
    
    print(f"📤 3. Stream loading {len(df):,} records into database target ['public.marketing_churn_raw']...")
    # chunksize configuration optimizes memory consumption during bulk writes
    df.to_sql('marketing_churn_raw', engine, schema='public', if_exists='replace', index=False, chunksize=5000)
    
    print("\n=== 🎉 PIPELINE SUCCESS: ALL MARKETING DATA PROVISIONED TO POSTGRESQL ===")

except Exception as e:
    # HARD FAILURE SIGNALING (UpDataLogic Rule 3)
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
