import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "gym.db"

def init_db():
    """Initialize the database with the workouts table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            split TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL,
            rpe REAL,
            fatigue TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_workout(date, split, exercise, sets, reps, weight, rpe=None, fatigue=None):
    """Add a new workout log to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO workouts (date, split, exercise, sets, reps, weight, rpe, fatigue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, split, exercise, sets, reps, weight, rpe, fatigue))
    
    conn.commit()
    conn.close()

def get_all_workouts():
    """Fetch all workout logs as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    
    try:
        df = pd.read_sql_query("SELECT * FROM workouts ORDER BY date DESC", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()
