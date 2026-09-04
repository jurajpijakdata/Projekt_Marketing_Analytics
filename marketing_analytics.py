import os
import sys
import pandas as pd
from pathlib import Path
from decimal import Decimal, InvalidOperation

print("🚀 Starting UpDataLogic Marketing Analytics & Cleanse Engine...")

# =====================================================================
# DYNAMIC PATH RESOLUTION (Cross-Platform Execution Compatibility)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data_raw" / "customer_churn_dataset.csv"

# =====================================================================
# DATA PIPELINE EXECUTION
# =====================================================================
try:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Critical data resource missing at targeted path: {DATA_FILE}")
        
    print(f"📥 Loading raw dataset: {DATA_FILE.name}...")
    df = pd.read_csv(DATA_FILE, low_memory=False)
    print(f"✅ Success: Dataset loaded. Total operational rows: {df.shape[0]:,}")
    
    print("\n⏳ Executing strict data cleansing pipeline...")
    
    # Robust Integer Parser for Support Calls (Keeps corruptions as None to save calculation accuracy)
    def parse_support_calls(value):
        if pd.isna(value) or str(value).strip() in ('', 'UNKNOWN'):
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return None

        # High-precision Monetary Parser for Customer Spend to eliminate binary float drifting
    def parse_monetary_spend(value):
        if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
            return None
        
        clean_str = str(value).strip().replace('$', '').replace('€', '').strip()
        
        # Handling financial grouping 
        if ',' in clean_str and '.' in clean_str:
            clean_str = clean_str.replace(',', '')
        elif ',' in clean_str and '.' not in clean_str:
            clean_str = clean_str.replace(',', '.')
            
        try:
            return Decimal(clean_str)
        except InvalidOperation:
            return None


    # Apply non-destructive parsing matrices across data metrics
    df['SupportCalls_Clean'] = df['SupportCalls'].apply(parse_support_calls)
    df['TotalSpend_USD_Clean'] = df['TotalSpend_USD'].apply(parse_monetary_spend)
    
    # Decouple tracking flags into separate sibling column to preserve pure numeric states
    df['data_quality_status'] = df[['SupportCalls_Clean', 'TotalSpend_USD_Clean']].isnull().any(axis=1).map({True: 'UNKNOWN', False: 'CLEAN'})
    
    print("=== 🎉 DATA CLEANSING COMPLETED SUCCESSFULLY ===")
    
    # Advanced Customer Intelligence: Quantify churn risk distribution across marketing vectors
    print("\n=== 📊 GLOBAL INSIGHT: CHURN RATE BY CUSTOMER SEGMENT ===")
    churn_analysis = df.groupby('CustomerSegment')['ChurnStatus'].mean() * 100
    
    for segment, rate in churn_analysis.items():
        print(f"• {segment:<10}: {rate:.2f} %")
        
    print("\n🏆 ANALYTICS RUN COMPLETED SUCCESSFULLY.")

except Exception as e:
    print(f"\n❌ PIPELINE CRITICAL FAILURE: {e}", file=sys.stderr)
    sys.exit(1)
