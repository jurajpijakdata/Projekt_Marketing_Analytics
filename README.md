# 📊 Customer Marketing & Retention Analytics - System Simulation Framework

An end-to-end data engineering and business intelligence framework designed to simulate high-volume customer behavior patterns within a B2C application layer. This system utilizes a dedicated synthetic generator to inject specific behavioral anomalies and churn vectors, proving that the Python data cleansing layer, PostgreSQL/SQLite warehouse tables, and Power BI dashboards can accurately capture, reconstruct, and surface target business signals.

## 🚀 Interactive Performance Demo
Below is a live interaction capture of the simulated production dashboard, demonstrating dynamic filtering across pre-calculated retention risk zones and metrics.

![Dashboard Interaction Demo](dashboard_demo.gif)

---

## 🏗️ Architecture Design: Enterprise Dual-Mode & Automated Test Automation
To maximize repository reliability and data product safety across enterprise ecosystems, the framework implements a strict multi-layered engineering and validation layout:
1. **Automated Unit Testing (`pytest`):** Core transformation algorithms are fully decoupled into pure isolated functions, verified against edge-case numeric parameters, string formatting anomalies, and mathematical grouping patterns to eliminate accounting drifting.
2. **Declarative Schema Validation (`pandera`):** The data ingestion pipeline is armed with a semantic quality schema matrix. It actively checks row matrices for missing indicators (`Null`), duplicates, out-of-bound variables, and structural variations before writing records to target infrastructure tables.
3. **Failover Connection Routing:** The framework evaluates endpoints dynamically. If remote production systems are unreachable, workloads route automatically to an isolated local file instance (`local_portfolio.db`) ensuring runtime continuity.

---

## 🔗 Algorithmic Data Generation & Disclosure
* **Pipeline Mechanism:** All analytical data is programmatically provisioned using the native script `marketing_data_gen.py` and saved inside the `data_raw` storage layer. 
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
- **Data Engineering:** Python (Pandas) sanitizing textual anomalies, removing grouping symbols, and executing type validation schemas via `pandera.pandas`.
- **Testing Suite:** `pytest` executing parametrized table-driven unit tests to simulate and intercept data edge cases.
- **Database Storage Cluster:** PostgreSQL (with automated failover configuration to a local standalone SQLite engine).
- **BI Reporting Layer:** Power BI Desktop tailored with strict algorithmic validation tests and precise DAX performance metrics.

---

## 📁 Repository Directory Structure

```text
Projekt_Marketing_Analytics/
│
├── data_raw/
│   ├── customer_churn_dataset.csv         # Full Production Raw Records
│   └── customer_churn_dataset_sample.csv  # Custom QA Sample Framework
│
├── marketing_ingestion.py                 # ETL Processing, Ingestion & Pandera In-line Validation
├── marketing_bi_layer.py                  # BI Layer Transformation Engine
├── marketing_data_gen.py                  # Synthetic Data Generation Script
├── test_marketing.py                      # Automated Pytest Suite & Test Simulator
├── requirements.txt                       # Locked Software Dependency Scheme
└── README.md                              # Enterprise Systems Documentation
```

---

## 🚀 Quick Start (Clone & Run Standard)

### 1. Deploy the Independent Software Stack
Install the standardized software dependencies inside your execution terminal:
```powershell
pip install -r requirements.txt
```

### 2. Run Automated Code Testing
Execute the validation suite with the built-in crash-test vectors to verify compliance:
```powershell
pytest test_marketing.py -v
```

### 3. Generate the Simulated Dataset Payload
Execute the synthetic behavioral data distribution script to write raw matrices into the `data_raw` directory:
```powershell
python marketing_data_gen.py
```

### 4. Verify Ingestion & Analytical Reporting Layers
Launch the automated cleaning, ingestion, and BI analytics modeling scripts sequentially:
```powershell
python marketing_ingestion.py
python marketing_bi_layer.py
```

---
*Engineered under the UpDataLogic Simulation Framework for verifiable, transparent, and reproducible system testing models.*
