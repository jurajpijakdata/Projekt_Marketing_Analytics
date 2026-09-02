import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

print("🚀 Starting UpDataLogic Marketing BI Layer Architecture...")

# Load hidden database credentials from the local .env file
load_dotenv()

# =====================================================================
# 1. DATABASE CONNECTION CONFIGURATION
# =====================================================================
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
# 2. BUSINESS INTELLIGENCE LAYER: ENGINEERING PERMANENT SQL VIEW
# =====================================================================
create_view_query = """
CREATE OR REPLACE VIEW public.v_marketing_retention_analytics AS
SELECT 
    "CustomerID" AS customer_id,
    "CustomerSegment" AS customer_segment,
    "AcquisitionChannel" AS acquisition_channel,
    "TenureMonths" AS tenure_months,
    "SupportCalls" AS support_calls,
    "TotalSpend_USD" AS total_spend,
    
    CASE 
        WHEN "ChurnStatus" = 1 THEN 'Churned'
        ELSE 'Active'
    END AS customer_loyalty_status,

    -- ADVANCED LOGIC: Segmenting customers by behavioral churn risk tiers
    CASE 
        WHEN "ChurnStatus" = 1 THEN 'Lost Customer (Already Left)'
        WHEN "SupportCalls" >= 5 AND "CustomerSegment" = 'Basic' THEN 'Critical Risk Zone'
        WHEN "SupportCalls" >= 4 THEN 'High Attention Needed'
        ELSE 'Safe & Loyal Customer'
    END AS retention_risk_tier,
    
    -- EFFICIENCY METRIC: Calculating average dollar spend per single active month
    CASE 
        WHEN "TenureMonths" > 0 THEN 
            ROUND(CAST("TotalSpend_USD" / "TenureMonths" AS numeric), 2)
        ELSE 0.0
    END AS monthly_spend_efficiency

FROM public.marketing_churn_raw;
"""

# =====================================================================
# 3. EXECUTION STAGE
# =====================================================================
try:
    with engine.connect() as conn:
        print("📥 Engineering permanent automated SQL View for BI reporting layer...")
        conn.execute(text(create_view_query))
        conn.commit()
        print("🎉 SUCCESS: Production SQL View 'v_marketing_retention_analytics' deployed successfully.")
        
        print("\n🔍 Fetching verification sample directly from the new production database layer:")
        # Pulling a verification dataset to prove the pipeline is operational
        sample_df = pd.read_sql_query('SELECT customer_id, retention_risk_tier, monthly_spend_efficiency FROM public.v_marketing_retention_analytics LIMIT 10;', conn)
        print("\n" + "="*70)
        print(sample_df.to_string(index=False))
        print("="*70)
        print("\n🏆 BI PIPELINE RUN COMPLETED SUCCESSFULLY.")

except Exception as e:
    # HARD FAILURE SIGNALING (UpDataLogic Rule 3)
    print(f"\n❌ BI LAYER CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
