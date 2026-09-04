import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

print("🚀 Starting UpDataLogic Marketing BI Layer Architecture Analytics...")

BASE_DIR = Path(__file__).resolve().parent

# 1. Establish Database Context Alignment to keep data layer identical
try:
    if not (BASE_DIR / ".env").exists():
        raise FileNotFoundError("Local config missing.")
        
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    
    connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '6543')}/{os.getenv('DB_NAME')}"
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        pass
    print("🔌 BI Layer Context: [ONLINE] Direct Live Production Pipeline Connection.")

except Exception:
    connection_string = f"sqlite:///{BASE_DIR / 'local_portfolio.db'}"
    engine = create_engine(connection_string)
    print("🔌 BI Layer Context: [LOCAL ENGINE] Direct Local File Storage Data Alignment.")

# 2. Process Business Intelligence Model Strategy
try:
    print("📥 Loading operational table data directly into high-performance dataframe memory...")
    raw_df = pd.read_sql_query("SELECT * FROM marketing_churn_raw", engine)
    
    print("📊 Engineering analytical metrics layer and advanced risk tier structures...")
    bi_df = pd.DataFrame()
    bi_df['customer_id'] = raw_df['CustomerID']
    bi_df['customer_segment'] = raw_df['CustomerSegment']
    bi_df['acquisition_channel'] = raw_df['AcquisitionChannel']
    bi_df['tenure_months'] = raw_df['TenureMonths']
    bi_df['total_spend'] = raw_df['TotalSpend_USD']
    
    # Advanced logic segmentation showing analytical capability to clients
    def retention_risk_profiler(row):
        if row['ChurnStatus'] == 1: 
            return 'Lost Customer (Already Left)'
        elif row['SupportCalls'] >= 4: 
            return 'Critical High Attention Zone'
        return 'Loyal Segment / Low Risk'
        
    bi_df['retention_risk_tier'] = raw_df.apply(retention_risk_profiler, axis=1)
    
    # Export permanent BI Layer Target Output
    bi_df.to_sql('v_marketing_retention_analytics', engine, if_exists='replace', index=False)
    print("🎉 SUCCESS: Analytical Data View 'v_marketing_retention_analytics' compiled successfully.")
    
    print("\n🔍 Verification Preview Output (First 5 processed production records):")
    print("=" * 80)
    print(bi_df.head(5).to_string(index=False))
    print("=" * 80)
    print("\n🏆 MARKETING BI LAYER PROCESSING CYCLE COMPLETED.")

except Exception as bi_error:
    print(f"❌ BI GENERATION CRITICAL ERROR: {bi_error}", file=sys.stderr)
    sys.exit(1)
