import pytest
import pandas as pd
from decimal import Decimal, InvalidOperation

# =====================================================================
# 1. PURE TRANSFORM FUNCTIONS (Extracted for Testability)
# =====================================================================
def clean_numeric_spend(value):
    """Safely normalizes and validates spend vectors without silent zero conversion."""
    if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
        return None
    
    # Prísna normalizácia: Najprv vyčistíme biele znaky
    clean_str = str(value).strip()
    
    # Ak reťazec obsahuje tisíckovú čiarku aj desatinnú bodku (napr. 2,500.75)
    if ',' in clean_str and '.' in clean_str:
        clean_str = clean_str.replace(',', '') # Úplne vymažeme tisíckovú čiarku
    elif ',' in clean_str and '.' not in clean_str:
        # Ak obsahuje iba čiarku (európsky formát napr. 150,50), premeníme ju na bodku
        clean_str = clean_str.replace(',', '.')
        
    try:
        parsed_val = float(Decimal(clean_str).quantize(Decimal("0.01")))
        if parsed_val < 0:
            raise ValueError(f"Negative revenue/spend detected: {parsed_val}")
        return parsed_val
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Data quality breach during numeric parsing: {e}")


def retention_risk_profiler(churn_status, support_calls):
    """Categorizes profiles based on deterministic churn vector rules."""
    if churn_status == 1: 
        return 'Lost Customer (Already Left)'
    elif support_calls >= 4: 
        return 'Critical High Attention Zone'
    return 'Loyal Segment / Low Risk'


# =====================================================================
# 2. PYTEST UNIT TESTS (Table-Driven / Parametrized)
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


def test_clean_numeric_spend_catches_negative_bug():
    """Verifies that the minus-sign bug from Module 4 forces an explicit failure."""
    with pytest.raises(ValueError, match="Negative revenue/spend detected"):
        clean_numeric_spend("-25.00")


def test_retention_risk_profiler_logic():
    """Verifies rule-based loyalty segment tier distribution mappings."""
    assert retention_risk_profiler(1, 6) == 'Lost Customer (Already Left)'
    assert retention_risk_profiler(0, 4) == 'Critical High Attention Zone'
    assert retention_risk_profiler(0, 2) == 'Loyal Segment / Low Risk'
