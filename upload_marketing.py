import pandas as pd
from sqlalchemy import create_engine

# 1. Definícia ciest a pripojenia
file_path = 'data_raw/customer_churn_dataset.csv'
db_url = 'postgresql+psycopg2://postgres:postgres01@localhost:5432/postgres'

try:
    print("1. Loading raw marketing data into production pipeline...")
    df = pd.read_csv(file_path, low_memory=False)
    
    print("2. Executing automated Pandas cleansing routines...")
    # Fix the data types exactly as we discovered in JupyterLab
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce').fillna(0).astype(int)
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce').fillna(0.0)
    
    print("3. Establishing secure database bridge to PostgreSQL...")
    engine = create_engine(db_url)
    
    print("4. Streaming data into 'marketing_churn_raw' table...")
    # Safe chunking configuration for corporate optimization
    df.to_sql('marketing_churn_raw', engine, schema='public', if_exists='replace', index=False, chunksize=5000)
    
    print("\n=== 🎉 SUCCESS! PRODUCTION MARKETING DATA LOADED TO POSTGRESQL ===")

except Exception as e:
    print(f"\n[Database Pipeline Error]: {e}")
