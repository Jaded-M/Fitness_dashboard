import pandas as pd
import sqlite3
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "Physical_attribute.xlsx"
DB_PATH = BASE_DIR / "nutrition.db"

def migrate():
    if not EXCEL_PATH.exists():
        print("No Excel file found. Skipping migration.")
        return

    print(f"Reading {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Ensure table exists
    from database import init_db
    init_db()

    # Clear existing data just in case of multiple runs
    c.execute("DELETE FROM measurements")
    
    # Insert rows
    count = 0
    for _, row in df.iterrows():
        # Handle nan values gracefully
        weight = row.get("Weight")
        if pd.isna(weight): continue
        
        date_str = str(row["Date"])[:10]  # Get YYYY-MM-DD
        waist = row.get("Waist") if not pd.isna(row.get("Waist")) else None
        hips = row.get("Hips") if not pd.isna(row.get("Hips")) else None
        thigh = row.get("Thigh") if not pd.isna(row.get("Thigh")) else None
        chest = row.get("Chest") if not pd.isna(row.get("Chest")) else None
        arms = row.get("Arms") if not pd.isna(row.get("Arms")) else None
        
        c.execute('''
            INSERT INTO measurements (date, weight, waist, hips, thigh, chest, arms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, weight, waist, hips, thigh, chest, arms))
        count += 1
        
    conn.commit()
    conn.close()
    
    print(f"Successfully migrated {count} measurements to SQLite!")
    print("You can now safely delete the Excel file.")

if __name__ == "__main__":
    migrate()
