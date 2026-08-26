import pandas as pd
from sqlalchemy import create_engine, text

# Local production database connection string
db_url = 'postgresql+psycopg2://YOUR_DATABASE_USER:YOUR_DATABASE_PASSWORD@YOUR_DATABASE_HOST:5432/YOUR_DATABASE_NAME'
engine = create_engine(db_url)

# === 🧠 BUSINESS INTELLIGENCE LAYER: ENGINEERING PERMANENT SQL VIEW ===
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

    
    -- 1. ADVANCED LOGIC: Segmenting customers by behavioral churn risk tiers
    CASE 
        WHEN "ChurnStatus" = 1 THEN 'Lost Customer (Already Left)'
        WHEN "SupportCalls" >= 5 AND "CustomerSegment" = 'Basic' THEN 'Critical Risk Zone'
        WHEN "SupportCalls" >= 4 THEN 'High Attention Needed'
        ELSE 'Safe & Loyal Customer'
    END AS retention_risk_tier,
    
    -- 2. EFFICIENCY METRIC: Calculating average dollar spend per single active month
    CASE 
        WHEN "TenureMonths" > 0 THEN ROUND(CAST("TotalSpend_USD" / "TenureMonths" AS numeric), 2)
        ELSE 0
    END AS monthly_spend_efficiency

FROM public.marketing_churn_raw;
"""

try:
    with engine.connect() as conn:
        print("1. Executing production SQL Architecture layer on PostgreSQL server...")
        # Executing the query to build a permanent automated view for Power BI
        conn.execute(text(create_view_query))
        conn.commit()
        print("🎉 SUCCESS: Permanent SQL View 'v_marketing_retention_analytics' engineered successfully.")
        
        print("\n2. Fetching verification sample directly from the new production SQL View:")
        # Pulling a verification dataset to prove the pipeline is operational
        sample_df = pd.read_sql_query('SELECT customer_id, retention_risk_tier, monthly_spend_efficiency FROM public.v_marketing_retention_analytics LIMIT 10;', conn)

        print(sample_df.to_string(index=False))

except Exception as e:
    print(f"\n[CRITICAL PIPELINE ERROR]: {e}")
