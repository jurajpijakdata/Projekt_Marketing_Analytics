# 📊 Customer Marketing & Retention Analytics - System Simulation Framework

An end-to-end data engineering and business intelligence framework designed to simulate high-volume customer behavior patterns within a B2C application layer. This system utilizes a dedicated synthetic generator to inject specific behavioral anomalies and churn vectors, proving that the Python data cleansing layer, PostgreSQL/SQLite warehouse tables, and Power BI dashboards can accurately capture, reconstruct, and surface target business signals.

## 🚀 Interactive Performance Demo
Below is a live interaction capture of the simulated production dashboard, demonstrating dynamic filtering across pre-calculated retention risk zones and metrics.

![Dashboard Interaction Demo](dashboard_demo.gif)

---

## 🏗️ Architecture Design: Enterprise Observability & Self-Healing Layout
To meet the rigorous data quality, error boundaries, and monitoring standards required in production-grade data platforms, the framework deploys a strict multi-layered engineering and monitoring architecture:

1. **Enterprise Logging Framework (`logging`):** Replaced legacy, unmonitored standard stdout text prints with a formal Python logging machine. Events, warning tracks, and subsystem errors are systematically piped across precise structural states (`INFO`, `WARNING`, `CRITICAL`) to allow direct parsing by cloud orchestrators.
2. **First-Class Rejection Metrics & Quarantine:** Malformed textual data corruptions are dynamically intercepted. Instead of masks using silent zero conversions that distort accounting aggregates downstream, failed parameters are cleanly cast to explicit `NULL` types and tracked as a primary first-class data quality metric.
3. **Automated Alerting Thresholds (Fail-Fast):** Incorporates an active runtime processing boundary constraint. If the data ingestion pipeline encounters a critical row rejection rate greater than **5.0%** of the batch payload volume, the entire framework halts execution immediately and throws a hard termination state (`sys.exit(1)`) to trigger modern orchestrator alerts.
4. **Self-Healing Pre-Load Layer:** Coerces incoming data structure alignments (e.g., dynamically removing alphanumeric grouping separators or currency text elements) prior to schema evaluation, eliminating unexpected type-mismatch crashes.
5. **Decoupled Unit Testing (`pytest`):** Core transformation math and data cleaning algorithms are fully decoupled into an independent logic module (`marketing_parser.py`) to eliminate environmental connection dependencies, allowing rapid parameterized testing execution.
6. **Declarative Schema Validation (`pandera`):** Screens the fully aligned, cleaned, and healed dataframe for missing attributes, duplicate entity constraints, and boundary keys before writing records downstream.

---

## 🔗 Algorithmic Data Generation & Disclosure
* **Pipeline Mechanism:** All analytical data is programmatically provisioned using the native script `marketing_data_gen.py` and saved inside the `data_raw` storage layer. 
* **Injected Anomalies:** To test the robustness of the ingestion pipelines, the engine injects explicit string corruptions (`'UNKNOWN'`) into numerical vectors and missing markers (`'NaN'`) into financial attributes.
* **Deterministic Churn Signal:** The script seeds randomness to guarantee a fixed benchmark layout across test environments:
  * **Global Churn Target:** Enforced at exactly **16.94%** (representing 2,118 lost profiles out of a 12,500 customer matrix).
  * **Injected Basic Segment Risk:** An intentional high-churn loop simulates a **35.57%** customer attrition rate triggered specifically when `SupportCalls >= 5` inside the `Basic` customer tier.

---

## 🛠️ Tech Stack & Pipeline Configurations
- **Data Engineering:** Python (Pandas) utilizing strict standalone self-healing data normalizers, robust `logging` stream handlers, and structural schema validation wrappers via `pandera.pandas`. High-precision monetary metrics utilize `decimal.Decimal` logic to prevent floating-point drifting.
- **Testing Suite:** `pytest` executing parametrized table-driven unit tests to simulate and intercept data edge cases.
- **Database Storage Cluster:** PostgreSQL (with automated fallback connection routing to a local standalone SQLite file database).
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
├── marketing_parser.py                    # Pure Decoupled Parsing & Business Logic (100% Testable)
├── marketing_ingestion.py                 # ETL Pipeline with Integrated Self-Healing, Logging & Pandera
├── marketing_bi_layer.py                  # BI Semantic Transformation Layer with Production Logging Handlers
├── marketing_data_gen.py                  # Synthetic Data Generation Script with Structural Enterprise Logs
├── test_marketing.py                      # Parametrized Pytest Suite Suite & Automated Crash Simulator
├── requirements.txt                       # Locked Software Dependency Layout Scheme
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
