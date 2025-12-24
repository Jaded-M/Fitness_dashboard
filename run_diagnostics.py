"""run_diagnostics.py
Simple diagnostics for your CSV files with beginner-friendly comments.
Run: python run_diagnostics.py
This prints columns, sample rows, and rows that failed date/number parsing.
"""

import pandas as pd
from pathlib import Path


def check_file(path, date_candidates, number_candidates):
    """Load CSV at `path` and check date/number parsing for given candidate column names.

    - date_candidates: list of possible date column names to try (e.g. ['Date','date']).
    - number_candidates: list of possible numeric column names to try (e.g. ['Steps','steps']).
    """
    p = Path(path)
    print('\n' + '='*60)
    print(f'Checking file: {p.name}')
    if not p.exists():
        print('File not found:', p)
        return

    df = pd.read_csv(p)
    print('\nColumns detected:', list(df.columns))
    print('\nFirst 5 rows:')
    print(df.head(5))

    # pick the first matching column name from the candidates list
    date_col = next((c for c in date_candidates if c in df.columns), None)
    num_col = next((c for c in number_candidates if c in df.columns), None)

    print('\nUsing date column:', date_col)
    print('Using numeric column:', num_col)

    if date_col:
        # Try parsing dates — use dayfirst=True because many files use DD-MM-YYYY
        parsed = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
        # Show how many failed to parse
        failed = parsed.isna().sum()
        print(f"Date parse: {len(parsed)-failed} parsed, {failed} failed (NaT)")
        if failed:
            print('\nSample problematic date strings:')
            print(df.loc[parsed.isna(), date_col].head(10))

    if num_col:
        # Clean common separators (commas) and convert to numeric
        cleaned = df[num_col].astype(str).str.replace(',', '', regex=False)
        numeric = pd.to_numeric(cleaned, errors='coerce')
        failed_num = numeric.isna().sum()
        print(f"\nNumeric parse: {len(numeric)-failed_num} parsed, {failed_num} failed (NaN)")
        if failed_num:
            print('\nSample problematic numeric strings:')
            print(df.loc[numeric.isna(), num_col].head(10))


def main():
    # Check the steps file (common columns: Date, date, Steps, steps)
    check_file('steps.csv', date_candidates=['Date','date','day'], number_candidates=['Steps','steps','step'])

    # Check workouts file (common columns: Date, Duration, Calories)
    check_file('workouts.csv', date_candidates=['Date','date'], number_candidates=['Duration','Calories','duration','calories'])

    print('\nDiagnostics complete. If you see problematic rows above, paste them here and I will tell you exact fixes.')


if __name__ == '__main__':
    main()
