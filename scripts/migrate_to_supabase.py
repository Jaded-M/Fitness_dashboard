import sqlite3
import pandas as pd
import sys
import os

# Add parent dir to path to import supabase_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase_client

DB_NAME = "fitness.db"
TABLES = [
    "workouts",
    "steps",
    "food_logs",
    "water_logs",
    "measurements",
    "checkins",
]


def normalize_records(table_name, df):
    records = df.where(pd.notna(df), None).to_dict(orient="records")

    if table_name == "workouts":
        import json
        for row in records:
            if isinstance(row.get("set_data"), str):
                try:
                    row["set_data"] = json.loads(row["set_data"])
                except Exception:
                    row["set_data"] = None

    return records


def remote_row_count(table_name):
    response = supabase_client.table(table_name).select("id", count="exact").limit(1).execute()
    return int(response.count or 0)

def migrate_table(table_name):
    print(f"Migrating {table_name}...")
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    
    if df.empty:
        print(f"No data in {table_name}.")
        return

    records = normalize_records(table_name, df)

    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            response = supabase_client.table(table_name).upsert(batch).execute()
            print(f"Upserted {len(batch)} rows into {table_name}")
        except Exception as e:
            print(f"Error upserting into {table_name}: {e}")

    remote_count = remote_row_count(table_name)
    print(f"{table_name}: local={len(df)} remote={remote_count}")
    if remote_count < len(df):
        print(f"Warning: remote row count for {table_name} is lower than local source.")


def run_migration():
    for table_name in TABLES:
        migrate_table(table_name)
    print("Migration complete!")

if __name__ == "__main__":
    run_migration()
