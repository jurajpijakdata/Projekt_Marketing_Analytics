import pandas as pd

# Path to our freshly generated dataset
file_path = 'data_raw/customer_churn_dataset.csv'

try:
    print("1. Loading raw marketing dataset into Pandas...")
    df = pd.read_csv(file_path, low_memory=False)
    
    print(f"Dataset successfully loaded. Total rows: {df.shape[0]:,}")
    
    print("\n2. Executing strict data cleansing pipeline...")
    # Fix 1: Convert SupportCalls to numeric. Force 'UNKNOWN' text bugs to become NaN, then fill with 0
    df['SupportCalls'] = pd.to_numeric(df['SupportCalls'], errors='coerce').fillna(0).astype(int)
    
    # Fix 2: Convert TotalSpend_USD to numeric. Force 'NaN' string bugs to become actual 0
    df['TotalSpend_USD'] = pd.to_numeric(df['TotalSpend_USD'], errors='coerce').fillna(0.0)
    
    print("=== 🎉 DATA CLEANSING COMPLETED SUCCESSFULLY ===")
    
    # Advanced Data Science Metric: Let's calculate Customer Churn Rate by Segment
    print("\n=== 📊 GLOBAL INSIGHT: CHURN RATE BY CUSTOMER SEGMENT ===")
    # ChurnStatus is 1 (left) or 0 (stayed), so the mean gives us the exact percentage
    churn_analysis = df.groupby('CustomerSegment')['ChurnStatus'].mean() * 100
    print(churn_analysis.round(2).to_string() + " %")

except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please check your folders.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
