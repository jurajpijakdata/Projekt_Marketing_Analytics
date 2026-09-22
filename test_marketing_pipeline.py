"""
Integration tests that actually run the pipeline scripts end to end, the way
a real user would, rather than just unit-testing their internal functions.

Both scripts are run as subprocesses inside a clean temporary directory that
contains nothing but a copy of the source files -- no .env file, so both
scripts must fall back to a fresh local SQLite database on their own, exactly
like a first-time clone would.

marketing_ingestion.py always reads data_raw/customer_churn_dataset.csv by
name. The 100-row customer_churn_dataset_sample.csv wasn't referenced by any
script before this -- it's used here as the fixture data (staged in place of
the full 12,500-row file) so the integration suite runs in a fraction of a
second instead of processing the full dataset on every test run.
"""
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent
SOURCE_FILES = ["marketing_parser.py", "marketing_ingestion.py", "marketing_bi_layer.py"]
SAMPLE_DATA_FILE = REPO_ROOT / "data_raw" / "customer_churn_dataset_sample.csv"


@pytest.fixture
def clean_project_dir(tmp_path):
    for filename in SOURCE_FILES:
        shutil.copy(REPO_ROOT / filename, tmp_path / filename)
    data_raw = tmp_path / "data_raw"
    data_raw.mkdir()
    # Staged under the exact filename marketing_ingestion.py reads.
    shutil.copy(SAMPLE_DATA_FILE, data_raw / "customer_churn_dataset.csv")
    return tmp_path


def _run_script(script_name, cwd):
    return subprocess.run(
        [sys.executable, script_name],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


def test_marketing_ingestion_runs_clean_on_fresh_clone_with_no_env(clean_project_dir):
    result = _run_script("marketing_ingestion.py", clean_project_dir)
    assert result.returncode == 0, f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    assert "LOCAL ENGINE" in result.stdout
    assert "PIPELINE RUN COMPLETION: STATUS 0 [SUCCESS]" in result.stdout

    db_path = clean_project_dir / "local_portfolio.db"
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    try:
        total_rows = conn.execute("SELECT COUNT(*) FROM marketing_churn_raw").fetchone()[0]
        assert total_rows == 100
    finally:
        conn.close()


def test_marketing_ingestion_is_idempotent(clean_project_dir):
    first = _run_script("marketing_ingestion.py", clean_project_dir)
    assert first.returncode == 0, first.stderr
    second = _run_script("marketing_ingestion.py", clean_project_dir)
    assert second.returncode == 0, second.stderr

    db_path = clean_project_dir / "local_portfolio.db"
    conn = sqlite3.connect(db_path)
    try:
        total_rows = conn.execute("SELECT COUNT(*) FROM marketing_churn_raw").fetchone()[0]
        assert total_rows == 100, "running the pipeline twice should not duplicate rows"
    finally:
        conn.close()


def test_marketing_bi_layer_runs_after_ingestion(clean_project_dir):
    ingestion_result = _run_script("marketing_ingestion.py", clean_project_dir)
    assert ingestion_result.returncode == 0, ingestion_result.stderr

    bi_result = _run_script("marketing_bi_layer.py", clean_project_dir)
    assert bi_result.returncode == 0, f"stdout:\n{bi_result.stdout}\n\nstderr:\n{bi_result.stderr}"
    assert "MARKETING BI LAYER PROCESSING CYCLE COMPLETED SUCCESSFULLY" in bi_result.stdout

    db_path = clean_project_dir / "local_portfolio.db"
    conn = sqlite3.connect(db_path)
    try:
        total_rows = conn.execute("SELECT COUNT(*) FROM v_marketing_retention_analytics").fetchone()[0]
        assert total_rows == 100

        tiers = {
            row[0]
            for row in conn.execute("SELECT DISTINCT retention_risk_tier FROM v_marketing_retention_analytics").fetchall()
        }
        # Every tier label the classifier can produce should be a valid, known
        # value -- this also guards against the BI layer silently going back
        # to a local, untested copy of the risk logic instead of the shared one.
        assert tiers <= {
            'Lost Customer (Already Left)',
            'Critical High Attention Zone',
            'Loyal Segment / Low Risk',
            'Unknown Risk (Incomplete Data)',
        }
    finally:
        conn.close()
