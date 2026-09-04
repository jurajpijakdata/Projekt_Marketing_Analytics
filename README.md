# 📊 Customer Marketing & Retention Analytics - System Simulation Framework

An end-to-end data engineering and business intelligence framework designed to simulate high-volume customer behavior patterns within a B2C application layer. This system utilizes a dedicated synthetic generator to inject specific behavioral anomalies and churn vectors, proving that the Python data cleansing layer, PostgreSQL/SQLite warehouse tables, and Power BI dashboards can accurately capture, reconstruct, and surface target business signals.

## 🚀 Interactive Performance Demo
Below is a live interaction capture of the simulated production dashboard, demonstrating dynamic filtering across pre-calculated retention risk zones and metrics.

![Dashboard Interaction Demo](dashboard_demo.gif)

---

## 🏗️ Architecture Design: Enterprise Dual-Mode & Failover Protection
To maximize showcase reliability across both cloud-connected and local offline evaluation environments, the framework implements a strict **Dual-Mode Data Pipeline**:
1. **Production Mode:** Automatically checks for your secure `.env` file to map incoming analytical feeds directly to a remote **PostgreSQL** cluster.
2. **Local Fallback Engine:** If network constraints, cloud downtime, or missing environment files are encountered, the pipeline gracefully intercepts the connection fault (`OperationalError`). It instantly routes workloads to an isolated local **SQLite** relational file instance (`local_portfolio.db`), ensuring flawless local execution and presentation.

---

## 🔗 Algorithmic Data Generation & Disclosure
* **Pipeline Mechanism:** All analytical data is programmatically provisioned using the native script `marketing_data_generator.py` and saved inside the `data_raw` storage layer. 
* **Injected Anomalies:** To test the robustness of the ingestion pipelines, the engine injects explicit string corruptions (`'UNKNOWN'`) into numerical vectors and missing markers (`'NaN'`) into financial attributes.
* **Deterministic Churn Signal:** The script seeds randomness to guarantee a fixed benchmark layout across test environments:
  * **Global Churn Target:** Enforced at exactly **16.94%** (representing 2,118 lost profiles out of a 12,500 customer matrix).
  * **Injected Basic Segment Risk:** An intentional high-churn loop simulates a **35.57%** customer attrition rate triggered specifically when `SupportCalls >= 5` inside the `Basic` customer tier.
* **Reviewer Sample Standard:** A pre-packaged, lightweight pool named **`customer_churn_dataset_sample.csv` (100 rows)** is available in the `data_raw` folder to verify cross-platform pipeline execution on public repositories without storage overhead.

---

## 🏗️ Data Engineering & Analytical SQL Architecture
The relational semantic intelligence layer is engineered directly within the database engine as an automated, calculated relational analytical framework. It serves as a strict test design model — proving that raw ingestion streams are transformed back into deterministic percentages without straining frontend memory layers:

```sql
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
    END AS customer_status,
    
    -- Advanced behavioral categorization
    CASE 
        WHEN "ChurnStatus" = 1 THEN 'Lost Customer (Already Left)'
        WHEN "SupportCalls" >= 5 AND "CustomerSegment" = 'Basic' THEN 'Critical Risk Zone'
        WHEN "SupportCalls" >= 4 THEN 'High Attention Needed'
        ELSE 'Safe & Loyal Customer'
    END AS retention_risk_tier,
    
    -- Spend Efficiency (Average dollar metric per active month)
    CASE 
        WHEN "TenureMonths" > 0 THEN ROUND(CAST("TotalSpend_USD" / "TenureMonths" AS numeric), 2)
        ELSE 0.0
    END AS monthly_spend_efficiency
FROM public.marketing_churn_raw;
```

---

## 🛠️ Tech Stack & Operational Configuration
- **Simulation Layer:** Python standard libs executing reproducible pseudorandom array distribution mapping.
- **Data Engineering:** Python (Pandas) sanitizing textual anomalies and casting objects to stable data models.
- **Database Storage Cluster:** PostgreSQL (with automated failover configuration to a local standalone SQLite engine).
- **BI Reporting Layer:** Power BI Desktop tailored with strict algorithmic validation tests and precise DAX performance metrics.

---

## 🚀 Quick Start (Clone & Run Standard)

### 1. Deploy the Independent Software Stack
Install the standardized software dependencies inside your execution terminal:
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment Secrets (Optional for Cloud Production)
To connect to a live database, replicate the structural template `.env.example` into a local file named `.env` and input your private database targets (fully restricted via `.gitignore`). *If omitted, the scripts will run smoothly using the automated local file storage backup engine.*
```text
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=your_supabase_host_string
DB_PORT=6543
DB_NAME=postgres
```

### 3. Generate the Simulated Dataset Payload
Execute the synthetic behavioral data distribution script to write raw matrices into the `data_raw` directory:
```powershell
python marketing_data_generator.py
```

### 4. Verify Ingestion & Analytical Reporting Layers
Launch the automated cleaning, ingestion, and BI analytics modeling scripts sequentially:
```powershell
python marketing_ingestion.py
python marketing_bi_layer.py
```

---
*Engineered under the UpDataLogic Simulation Framework for verifiable, transparent, and reproducible system testing models.*
