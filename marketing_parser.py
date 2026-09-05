import pandas as pd
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

def clean_numeric_spend(value: Any) -> Optional[float]:
    """
    Safely normalizes and validates spend vectors without silent zero conversion.

    This function proactively strips local financial currency systems variations,
    handles international comma-to-dot groupings, and enforces strict numeric conversion.
    Malformed, incomplete, or negative parameters are mapped directly to strict None 
    to trigger transparent tracking flags downstream.

    Args:
        value (Any): The raw spend or revenue attribute incoming from marketing platforms.

    Returns:
        Optional[float]: A sanitized float representation for database validation schemas, 
                         or None if critical textual data quality drift is isolated.
    """
    if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
        return None
    
    clean_str: str = str(value).strip()
    
    # Self-healing cross-platform format normalization matrix
    if ',' in clean_str and '.' in clean_str:
        clean_str = clean_str.replace(',', '')
    elif ',' in clean_str and '.' not in clean_str:
        clean_str = clean_str.replace(',', '.')
        
    try:
        parsed_val: float = float(Decimal(clean_str).quantize(Decimal("0.01")))
        if parsed_val < 0:
            return None  # Rejects negative revenue/spend anomalies into isolation trackers
        return parsed_val
    except (InvalidOperation, ValueError):
        return None
