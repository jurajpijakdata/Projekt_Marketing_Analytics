import pytest
import pandas as pd
from decimal import Decimal
# Import the actual production functions, not local copies -- so these tests
# actually protect the code that runs in marketing_ingestion.py and
# marketing_bi_layer.py, instead of a clone that can silently drift from it.
from marketing_parser import clean_numeric_spend, retention_risk_profiler


# =====================================================================
# PYTEST UNIT TESTS (Table-Driven / Parametrized)
# =====================================================================

@pytest.mark.parametrize("input_val, expected_output", [
    ("150.50", 150.50),
    ("2,500.75", 2500.75),
    ("  45.00  ", 45.00),
    ("1,234", 1234.0),
    ("1234,56", 1234.56),
    ("1,234,567", 1234567.0),
    ("-50.00", None),
    ("", None),
    ("UNKNOWN", None),
])
def test_clean_numeric_spend_valid_cases(input_val, expected_output):
    """Verifies standard clean string parsing and missing marker extraction."""
    assert clean_numeric_spend(input_val) == expected_output


def test_retention_risk_profiler_logic():
    """Verifies rule-based loyalty segment tier distribution mappings."""
    assert retention_risk_profiler(1, 6) == 'Lost Customer (Already Left)'
    assert retention_risk_profiler(0, 4) == 'Critical High Attention Zone'
    assert retention_risk_profiler(0, 2) == 'Loyal Segment / Low Risk'
    assert retention_risk_profiler(0, None) == 'Unknown Risk (Incomplete Data)'
    assert retention_risk_profiler(0, float('nan')) == 'Unknown Risk (Incomplete Data)'
