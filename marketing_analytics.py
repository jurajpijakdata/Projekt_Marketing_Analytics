import sys
import pandas as pd
from pathlib import Path

print("🚀 Starting UpDataLogic Marketing Analytics & Cleanse Engine...")

# =====================================================================
# DYNAMIC PATH RESOLUTION (UpDataLogic Rule 2)
# =====================================================================
# Automatically detect the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"

# =====================================================================
# DATA PIPELINE EXECUTION
# =====================================================================
try:
    # Fail fast if the required data resource is missing from the environment
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource missing at targeted path: {DATA_FILE}")
        
    print(f"📥 Loading raw dataset: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"✅ Success: Dataset loaded. Total operational rows: {df.shape[0]:,}")
    
    print("\n⏳ Executing strict data cleansing pipeline...")
    # Fix 1: Normalize SupportCalls. Coerce string corruptions ('UNKNOWN') to NaN, fill with 0, cast to integer
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce').fillna(0).astype(int)
    
    # Fix 2: Normalize TotalSpend_USD. Coerce textual missing tags ('NaN') to float, fill with 0.0
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce').fillna(0.0)
    
    print("=== 🎉 DATA CLEANSING COMPLETED SUCCESSFULLY ===")
    
    # Advanced Customer Intelligence: Quantify churn risk distribution across marketing vectors
    print("\n=== 📊 GLOBAL INSIGHT: CHURN RATE BY CUSTOMER SEGMENT ===")
    # ChurnStatus binary flag (1/0) mean calculation yields exact operational percentage
    churn_analysis = df.groupby('CustomerSegment')['ChurnStatus'].mean() * 100
    
    # Formatting output for clean engineering delivery
    for segment, rate in churn_analysis.items():
        print(f"• {segment:<10}: {rate:.2f} %")
        
    print("\n🏆 ANALYTICS RUN COMPLETED SUCCESSFULLY.")

except Exception as e:
    # HARD FAILURE SIGNALING (UpDataLogic Rule 3)
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)

