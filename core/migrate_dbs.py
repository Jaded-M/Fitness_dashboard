import sqlite3
import pandas as pd
import os

def migrate():
    print("Starting database migration to fitness.db...")
    
    # Target DB
    target_db = "fitness.db"
    
    # Source DBs
    gym_db = "gym.db"
    nutrition_db = "nutrition.db"
    
    # Create target connection
    conn_target = sqlite3.connect(target_db)
    
    # 1. Migrate GYM tables
    if os.path.exists(gym_db):
        print(f"Migrating from {gym_db}...")
        conn_gym = sqlite3.connect(gym_db)
        
        # Get all tables from gym.db
        cursor = conn_gym.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name != "sqlite_sequence":
                print(f"  -> Copying table '{table_name}'")
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn_gym)
                df.to_sql(table_name, conn_target, if_exists="replace", index=False)
                print(f"     Copied {len(df)} rows.")
                
        conn_gym.close()
    else:
        print(f"{gym_db} not found, skipping.")
        
    # 2. Migrate NUTRITION tables
    if os.path.exists(nutrition_db):
        print(f"Migrating from {nutrition_db}...")
        conn_nut = sqlite3.connect(nutrition_db)
        
        # Get all tables from nutrition.db
        cursor = conn_nut.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if table_name != "sqlite_sequence":
                print(f"  -> Copying table '{table_name}'")
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn_nut)
                df.to_sql(table_name, conn_target, if_exists="replace", index=False)
                print(f"     Copied {len(df)} rows.")
                
        conn_nut.close()
    else:
        print(f"{nutrition_db} not found, skipping.")

    conn_target.commit()
    conn_target.close()
    print("Migration complete! You can now safely delete gym.db and nutrition.db.")

if __name__ == "__main__":
    migrate()
