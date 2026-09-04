import pytest
import pandas as pd
from decimal import Decimal
# Importujeme funkciu z našej novej čistej knižnice
from marketing_parser import clean_numeric_spend

def retention_risk_profiler(churn_status, support_calls):
    """Categorizes profiles based on deterministic churn vector rules."""
    if churn_status == 1: 
        return 'Lost Customer (Already Left)'
    elif support_calls >= 4: 
        return 'Critical High Attention Zone'
    return 'Loyal Segment / Low Risk'


# =====================================================================
# PYTEST UNIT TESTS (Table-Driven / Parametrized)
# =====================================================================

@pytest.mark.parametrize("input_val, expected_output", [
    ("150.50", 150.50),
    ("2,500.75", 2500.75),
    ("  45.00  ", 45.00),
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
