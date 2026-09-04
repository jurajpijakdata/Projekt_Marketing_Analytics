import pandas as pd
from decimal import Decimal, InvalidOperation

def clean_numeric_spend(value):
    """Safely normalizes and validates spend vectors without silent zero conversion."""
    if pd.isna(value) or str(value).strip() in ('', 'NaN', 'UNKNOWN'):
        return None
    
    clean_str = str(value).strip()
    
    # Samoopravné finančné formátovanie
    if ',' in clean_str and '.' in clean_str:
        clean_str = clean_str.replace(',', '')
    elif ',' in clean_str and '.' not in clean_str:
        clean_str = clean_str.replace(',', '.')
        
    try:
        parsed_val = float(Decimal(clean_str).quantize(Decimal("0.01")))
        if parsed_val < 0:
            raise ValueError(f"Negative revenue/spend detected: {parsed_val}")
        return parsed_val
    except (InvalidOperation, ValueError):
        return None
