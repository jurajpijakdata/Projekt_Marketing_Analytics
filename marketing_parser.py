import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def clean_numeric_spend(value: Any) -> Optional[float]:
    """
    Safely normalizes and validates spend vectors without silent zero conversion.

    Handles both US-style numbers ("2,500.75", comma as thousands separator, dot
    as decimal) and a plain European decimal comma ("1234,56" -> 1234.56). When a
    comma appears with no dot, it's ambiguous between the two: a single comma
    followed by exactly two digits is treated as a decimal separator (matching
    how cents are always written); anything else -- multiple commas, or three
    digits after the comma -- is treated as a thousands separator and stripped.
    Without this distinction, a plain thousands-formatted whole number like
    "1,234" would silently become 1.234 instead of 1234. Malformed, incomplete,
    or negative parameters are mapped directly to strict None to trigger
    transparent tracking flags downstream.

    Args:
        value (Any): The raw spend or revenue attribute incoming from marketing platforms.

    Returns:
        Optional[float]: A sanitized float representation for database validation schemas,
                         or None if critical textual data quality drift is isolated.
    """
    if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
        return None

    clean_str: str = str(value).strip()

    if ',' in clean_str and '.' in clean_str:
        clean_str = clean_str.replace(',', '')
    elif ',' in clean_str:
        parts = clean_str.split(',')
        if len(parts) == 2 and len(parts[1]) == 2:
            clean_str = clean_str.replace(',', '.')
        else:
            clean_str = clean_str.replace(',', '')

    try:
        parsed_val: float = float(Decimal(clean_str).quantize(Decimal("0.01")))
        if parsed_val < 0:
            return None  # Rejects negative revenue/spend anomalies into isolation trackers
        return parsed_val
    except (InvalidOperation, ValueError):
        return None


def retention_risk_profiler(churn_status: Any, support_calls: Optional[float]) -> str:
    """
    Categorizes a customer profile into a retention risk tier.

    Args:
        churn_status (Any): 1 if the customer already churned, 0 otherwise.
        support_calls (Optional[float]): Number of support calls, or None/NaN if
            that field was quarantined during ingestion (unparseable/missing).

    Returns:
        str: A retention risk tier label. A customer with unknown support-call
             data is flagged explicitly rather than silently folded into the
             low-risk bucket.
    """
    if churn_status == 1:
        return 'Lost Customer (Already Left)'
    if support_calls is None or pd.isna(support_calls):
        return 'Unknown Risk (Incomplete Data)'
    if support_calls >= 4:
        return 'Critical High Attention Zone'
    return 'Loyal Segment / Low Risk'
