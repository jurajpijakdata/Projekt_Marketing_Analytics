import os
import random
import pandas as pd

output_dir = 'data_raw'
file_name = os.path.join(output_dir, 'customer_churn_dataset.csv')
os.makedirs(output_dir, exist_ok=True)

print("⚡ Generating 12,500 customer behavior records...")
random.seed(2026)

segments = ['Premium', 'Standard', 'Basic']
channels = ['Facebook Ads', 'Google Search', 'Organic', 'Email Marketing']

data = []
for i in range(1, 12501):
    cust_id = f"CUST_{i:05d}"
    segment = random.choice(segments)
    channel = random.choice(channels)
    tenure = random.randint(1, 48)  # months active
    support_calls = random.randint(0, 7)
    
    # Logic: More support calls + basic segment = higher churn risk
    if support_calls > 4 and segment == 'Basic':
        total_spend = round(random.uniform(50, 400), 2)
        churn = 1 if random.random() < 0.82 else 0  # 82% risk
    else:
        total_spend = round(random.uniform(150, 4500), 2)
        churn = 1 if random.random() < 0.08 else 0  # 8% risk

    # Injecting corrupt data (Null values and text bugs) for our cleaning pipeline
    if random.random() < 0.015:
        total_spend = "NaN"  # Missing values simulation
    if random.random() < 0.01:
        support_calls = "UNKNOWN"  # Text corruption inside numbers
        
    data.append([cust_id, segment, channel, tenure, support_calls, total_spend, churn])

df = pd.DataFrame(data, columns=['CustomerID', 'CustomerSegment', 'AcquisitionChannel', 'TenureMonths', 'SupportCalls', 'TotalSpend_USD', 'ChurnStatus'])
df.to_csv(file_name, index=False)
print(f"🎉 Success! Surové marketingové dáta uložené v: {file_name}")
