import pandas as pd

def clean_symptom(symptom: str) -> str | None:
    """
    Cleans a symptom string by stripping whitespace, 
    replacing underscores with spaces, and lowercasing.
    Returns None if the input is empty or NaN.
    """
    if pd.isna(symptom):
        return None
    cleaned = str(symptom).strip().replace('_', ' ').lower()
    return cleaned if cleaned else None
