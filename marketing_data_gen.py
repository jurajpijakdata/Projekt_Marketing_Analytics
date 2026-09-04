import os
import sys
import random
import logging
import pandas as pd
from pathlib import Path

# =====================================================================
# ENTERPRISE LOGGING CONFIGURATION (Module 6 Standard)
# =====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [UpDataLogic Generator] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("🚀 Starting UpDataLogic Marketing Data Generation Engine...")

# =====================================================================
# DYNAMIC PATH RESOLUTION
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data_raw"
OUTPUT_FILE = OUTPUT_DIR / "customer_churn_dataset.csv"

# Enforce directory creation using pathlib
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================================
# SYNTHETIC DATA GENERATION SIMULATION
# =====================================================================
try:
    logging.info("⏳ Generating 12,500 customer behavior records with injected anomalies...")
    
    # Seeding randomness to guarantee reproducible results across environments
    random.seed(2026)

    segments = ['Premium', 'Standard', 'Basic']
    channels = ['Facebook Ads', 'Google Search', 'Organic', 'Email Marketing']

    data = []
    for i in range(1, 12501):
        cust_id = f"CUST_{i:05d}"
        segment = random.choice(segments)
        channel = random.choice(channels)
        tenure = random.randint(1, 48)  # Active contract longevity in months
        support_calls = random.randint(0, 7)
        
        # Risk logic calibration: Basic segment + heavy support interaction spikes churn probability
        if support_calls > 4 and segment == 'Basic':
            total_spend = round(random.uniform(50, 400), 2)
            churn = 1 if random.random() < 0.82 else 0  # 82% churn probability
        else:
            total_spend = round(random.uniform(150, 4500), 2)
            churn = 1 if random.random() < 0.08 else 0  # Baseline 8% churn probability

        # Explicit injection of missing entries and structural textual data corruption
        if random.random() < 0.015:
            total_spend = "NaN"  # Missing values emulation
        if random.random() < 0.01:
            support_calls = "UNKNOWN"  # String noise inside numerical schemas
            
        data.append([cust_id, segment, channel, tenure, support_calls, total_spend, churn])

    # Construct the data framing model
    columns = ['CustomerID', 'CustomerSegment', 'AcquisitionChannel', 'TenureMonths', 'SupportCalls', 'TotalSpend_USD', 'ChurnStatus']
    df = pd.DataFrame(data, columns=columns)
    
    # Exporting the raw payload
    df.to_csv(OUTPUT_FILE, index=False)
    logging.info(f"=== 🎉 SUCCESS: Raw marketing records stored at: {OUTPUT_FILE.name} ===")
    logging.info(f"Total Rows Generated: {len(df):,}")
    sys.exit(0)

except Exception as e:
    logging.critical(f"❌ GENERATION CRITICAL FAILURE: {e}")
    sys.exit(1)
