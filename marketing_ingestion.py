import os
import sys
import pandas as pd
import pandera.pandas as pa
from pathlib import Path
from sqlalchemy import create_engine

print("🚀 Starting UpDataLogic Marketing Database Ingestion Pipeline...")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data_raw"
FULL_DATA = DATA_DIR / "customer_churn_dataset.csv"
SAMPLE_DATA = DATA_DIR / "customer_churn_dataset_sample.csv"

# 1. Define Strict Data Quality Shield using Pandera
data_schema_shield = pa.DataFrameSchema({
    "CustomerID": pa.Column(str, nullable=False, unique=True), # Check for duplicates and Nulls
    "CustomerSegment": pa.Column(str, pa.Check.isin(["Basic", "Standard", "Premium"]), nullable=False),
    "TenureMonths": pa.Column(int, pa.Check.ge(0), nullable=False), # Non-negative age constraint
    "SupportCalls": pa.Column(float, nullable=True),
    "TotalSpend_USD": pa.Column(float, nullable=True),
    "ChurnStatus": pa.Column(int, pa.Check.isin([0, 1]), nullable=False)
})

# 2. Database Connection Check
try:
    if (BASE_DIR / ".env").exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=BASE_DIR / ".env")
    
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "6543")
    DB_NAME = os.getenv("DB_NAME")
    
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
        raise ValueError("Missing database credentials.")
        
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        pass
    print("🔌 Connection Status: [ONLINE] Remote PostgreSQL Warehouse Connected.")
except Exception:
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    print("🔌 Connection Status: [LOCAL ENGINE] Active Fallback SQLite Context.")

# 3. Source Selection
if FULL_DATA.exists():
    target_source = FULL_DATA
elif SAMPLE_DATA.exists():
    target_source = SAMPLE_DATA
else:
    print(f"❌ CRITICAL STORAGE ERROR: No records found at {DATA_DIR}")
    sys.exit(1)

# 4. Ingestion & Validation Execution
try:
    print(f"📥 Extracting records from: {target_source.name}...")
    df = pd.read_csv(target_source, low_memory=False)
    
    print("⏳ Sanitizing and converting raw text data formats...")
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce')
    
    # SENIORSKÁ OPRAVA: Odstránenie tisíckových čiarok z textu pred číselnou konverziou
    df['TotalSpend_USD'] = df['TotalSpend_USD'].astype(str).str.replace(',', '', regex=False)
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce')
    
    print("🛡️ Running declarative data quality checks via Pandera schema evaluation...")
    # Validate the data matrix. If it fails, pandera stops execution before database pollution
    validated_df = data_schema_shield.validate(df)
    
    print(f"📤 Stream loading {len(validated_df):,} validated records into target tables...")
    validated_df.to_sql('marketing_churn_raw', engine, if_exists='replace', index=False)
    print("🎉 DATA INGESTION STAGE COMPLETION: SUCCESS")

except pa.errors.SchemaError as schema_fault:
    print(f"\n❌ DATA QUALITY BREACH DETECTED BY PANDERA:\n{schema_fault}", file=sys.stderr)
    sys.exit(1)
except Exception as pipeline_error:
    print(f"\n❌ PIPELINE CRITICAL RUNTIME ERROR: {pipeline_error}", file=sys.stderr)
    sys.exit(1)
