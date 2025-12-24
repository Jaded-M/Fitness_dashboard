"""utils.py
Small helper functions for safe parsing of dates and numbers.
Designed for beginners: short functions and clear comments.
"""
import pandas as pd
from typing import List, Optional


def safe_to_datetime(series: pd.Series, dayfirst: bool = True, formats: Optional[List[str]] = None) -> pd.Series:
    """Try to convert a Series to datetimes safely.

    - formats: optional list of strftime formats to try first, e.g. ['%d-%m-%Y']
    - dayfirst: passed to pandas.to_datetime for ambiguous dates
    Returns a Series of dtype datetime64[ns] with NaT for failures.
    """
    # If user gave explicit formats, try them for the rows that fail.
    if formats:
        # Start with an all-NaT series to fill progressively
        parsed = pd.Series(pd.NaT, index=series.index)
        remaining = series.copy()
        for fmt in formats:
            try:
                part = pd.to_datetime(remaining, format=fmt, errors='coerce')
            except Exception:
                part = pd.to_datetime(remaining, errors='coerce', dayfirst=dayfirst)
            # take parsed where available
            mask = parsed.isna() & part.notna()
            parsed.loc[mask] = part.loc[mask]
            # drop parsed values from remaining
            remaining = remaining[parsed.isna()]
            if remaining.empty:
                break
        # For any still-unparsed rows, try a last generic parse
        if parsed.isna().any():
            fallback = pd.to_datetime(series.loc[parsed.isna()], errors='coerce', dayfirst=dayfirst)
            parsed.loc[parsed.isna()] = fallback
        return parsed

    # No explicit formats: use pandas' flexible parser
    return pd.to_datetime(series, errors='coerce', dayfirst=dayfirst)


def safe_to_numeric(series: pd.Series) -> pd.Series:
    """Convert a Series to numbers safely.

    - Removes common thousands separators like commas
    - Converts percent strings to floats (e.g. '12%' -> 12.0)
    - Returns numeric Series with NaN for failures
    """
    s = series.astype(str).str.strip()
    # Remove commas used as thousands separators: '1,234' -> '1234'
    s = s.str.replace(',', '', regex=False)
    # Handle percent values '12%' -> '12'
    percent_mask = s.str.endswith('%')
    if percent_mask.any():
        s.loc[percent_mask] = s.loc[percent_mask].str.rstrip('%')
    # Finally convert to numeric, coercing errors to NaN
    return pd.to_numeric(s, errors='coerce')
