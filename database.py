import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
import streamlit as st

DB_NAME = "fitness.db"

@contextmanager
def _db(db_path=None):
    """Context manager: opens connection, commits on success, always closes."""
    conn = sqlite3.connect(db_path or DB_NAME)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

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
            fatigue TEXT,
            duration INTEGER DEFAULT 0
        )
    ''')
    
    # Migration: Check for 'duration' and 'set_data' columns
    c.execute("PRAGMA table_info(workouts)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'duration' not in columns:
        try:
            c.execute("ALTER TABLE workouts ADD COLUMN duration INTEGER DEFAULT 0")
        except Exception:
            pass
            
    if 'set_data' not in columns:
        try:
            c.execute("ALTER TABLE workouts ADD COLUMN set_data TEXT")
        except Exception:
            pass

    # Create steps table
    c.execute('''
        CREATE TABLE IF NOT EXISTS steps (
            date TEXT PRIMARY KEY,
            steps INTEGER NOT NULL,
            distance REAL,
            active_minutes INTEGER
        )
    ''')

    # Migration: Ensure 'steps' table has a primary key on 'date'
    c.execute("PRAGMA table_info(steps)")
    steps_cols = c.fetchall()
    if steps_cols:
        # Check if the 'date' column (index 1) has pk flag (index 5)
        date_pk = any(col[1] == 'date' and col[5] > 0 for col in steps_cols)
        if not date_pk:
            try:
                c.execute("ALTER TABLE steps RENAME TO steps_old")
                c.execute('''
                    CREATE TABLE steps (
                        date TEXT PRIMARY KEY,
                        steps INTEGER NOT NULL,
                        distance REAL,
                        active_minutes INTEGER
                    )
                ''')
                # Copy data, handle potential duplicates just in case
                c.execute('''
                    INSERT INTO steps (date, steps, distance, active_minutes)
                    SELECT date, MAX(steps), MAX(distance), MAX(active_minutes)
                    FROM steps_old
                    GROUP BY date
                ''')
                c.execute("DROP TABLE steps_old")
            except Exception:
                pass

    # Create food_logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            food_item TEXT NOT NULL,
            calories INTEGER DEFAULT 0,
            protein INTEGER DEFAULT 0,
            carbs INTEGER DEFAULT 0,
            fats INTEGER DEFAULT 0,
            fiber INTEGER DEFAULT 0,
            meal_type TEXT DEFAULT 'Snack'
        )
    ''')
    
    # Migration: Add meal_type if missing
    c.execute("PRAGMA table_info(food_logs)")
    cols = [info[1] for info in c.fetchall()]
    if 'meal_type' not in cols:
        try: c.execute("ALTER TABLE food_logs ADD COLUMN meal_type TEXT DEFAULT 'Snack'")
        except: pass
        
    if 'fiber' not in cols:
        try: c.execute("ALTER TABLE food_logs ADD COLUMN fiber INTEGER DEFAULT 0")
        except: pass
        
    # Create water_logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS water_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            cups INTEGER DEFAULT 1
        )
    ''')
    
    # Create draft_food_logs table for the Meal Builder
    c.execute('''
        CREATE TABLE IF NOT EXISTS draft_food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_item TEXT NOT NULL,
            calories INTEGER DEFAULT 0,
            protein INTEGER DEFAULT 0,
            carbs INTEGER DEFAULT 0,
            fats INTEGER DEFAULT 0,
            fiber INTEGER DEFAULT 0
        )
    ''')
    
    # Create measurements table to replace Excel
    c.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            weight REAL,
            waist REAL,
            hips REAL,
            thigh REAL,
            chest REAL,
            arms REAL
        )
    ''')

    # Daily notes/check-ins for context around the numbers.
    c.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            mood INTEGER DEFAULT 3,
            energy INTEGER DEFAULT 3,
            sleep_hours REAL,
            note TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_workout(date, split, exercise, sets, reps, weight, rpe, fatigue, duration=0, set_data=None):
    """Add a new workout log to the database."""
    with _db() as conn:
        conn.execute('''
            INSERT INTO workouts (date, split, exercise, sets, reps, weight, rpe, fatigue, duration, set_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, split, exercise, sets, reps, weight, rpe, fatigue, duration, set_data))
    
    # Invalidate caches so the UI reflects the new workout immediately
    get_all_workouts.clear()
    get_unique_exercises.clear()
    get_best_lifts.clear()
    get_exercise_history.clear()

@st.cache_data(ttl=300)
def get_all_workouts():
    """
    Fetch all workout logs as a Pandas DataFrame.
    
    Why ORDER BY date DESC? 
    It ensures the most recent workouts are loaded first, which makes
    building the history table and streak calculators in Python much faster.
    """
    with _db() as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM workouts ORDER BY date DESC", conn)
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading workouts: {e}")
            return pd.DataFrame()

@st.cache_data(ttl=300)
def get_unique_exercises():
    """Fetch all unique exercise names ordered by usage count."""
    with _db() as conn:
        try:
            c = conn.cursor()
            c.execute('''
                SELECT exercise, COUNT(*) as count 
                FROM workouts 
                GROUP BY exercise 
                ORDER BY count DESC
            ''')
            return [row[0] for row in c.fetchall()]
        except sqlite3.Error as e:
            st.error(f"Database error loading unique exercises: {e}")
            return []

def delete_workout_by_id(workout_id):
    """Delete a specific workout log by ID."""
    with _db() as conn:
        conn.execute("DELETE FROM workouts WHERE id=?", (workout_id,))
    
    # Invalidate caches
    get_all_workouts.clear()
    get_unique_exercises.clear()
    get_best_lifts.clear()
    get_exercise_history.clear()

@st.cache_data(ttl=300)
def get_best_lifts():
    """Get the personal best (max weight) for each exercise."""
    with _db() as conn:
        try:
            df = pd.read_sql_query("""
                SELECT exercise, MAX(weight) as best_weight, MAX(reps) as best_reps, COUNT(*) as sessions
                FROM workouts
                WHERE exercise != 'Session Duration'
                GROUP BY exercise
                ORDER BY best_weight DESC
            """, conn)
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading best lifts: {e}")
            return pd.DataFrame()


@st.cache_data(ttl=300)
def get_exercise_history(exercise_name, limit=5):
    """Returns the last N sessions for a specific exercise."""
    with _db() as conn:
        try:
            df = pd.read_sql_query(
                """
                SELECT date, sets, reps, weight, rpe, set_data
                FROM workouts
                WHERE exercise = ?
                  AND exercise != 'Session Duration'
                ORDER BY date DESC
                LIMIT ?
                """,
                conn,
                params=(exercise_name, limit)
            )
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading exercise history: {e}")
            return pd.DataFrame()


def get_weekly_volume_by_split(weeks=4):
    """Calculates total volume per split per week. weeks param is an int — safe."""
    days = weeks * 7  # pre-calculate so we pass a plain int, not an expression
    with _db() as conn:
        try:
            df = pd.read_sql_query(
                """
                SELECT
                    strftime('%Y-W%W', date) as week,
                    split,
                    SUM(weight * reps) as total_volume,
                    COUNT(DISTINCT date) as session_count
                FROM workouts
                WHERE exercise != 'Session Duration'
                  AND date >= date('now', ? || ' days')
                GROUP BY week, split
                ORDER BY week DESC
                """,
                conn,
                params=(f"-{days}",)
            )
            return df
        except Exception:
            return pd.DataFrame()


# ========================================================
# STEPS DATABASE FUNCTIONS
# ========================================================

def add_steps(date, steps, distance=0, active_minutes=0):
    """Add or update steps for a specific date."""
    with _db() as conn:
        conn.execute('''
            INSERT INTO steps (date, steps, distance, active_minutes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                steps=excluded.steps,
                distance=excluded.distance,
                active_minutes=excluded.active_minutes
        ''', (date, steps, distance, active_minutes))

@st.cache_data(ttl=300)
def get_steps_data(start_date=None, end_date=None):
    """Fetch steps data, optionally filtered by date range."""
    with _db() as conn:
        try:
            query = "SELECT * FROM steps"
            params = []
            if start_date and end_date:
                query += " WHERE date BETWEEN ? AND ?"
                params = [str(start_date), str(end_date)]
            elif start_date:
                query += " WHERE date >= ?"
                params = [str(start_date)]
            
            query += " ORDER BY date ASC"
            df = pd.read_sql_query(query, conn, params=params)
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading steps: {e}")
            return pd.DataFrame()

def delete_steps_by_date(date):
    """Delete steps for a specific date."""
    with _db() as conn:
        conn.execute("DELETE FROM steps WHERE date=?", (date,))
    get_steps_data.clear()

# ========================================================
# NUTRITION DATABASE
# ========================================================

def add_food_log(date, food_item, calories, protein=0, carbs=0, fats=0, fiber=0, meal_type="Snack"):
    """Add a food log entry."""
    with _db() as conn:
        conn.execute('''
            INSERT INTO food_logs (date, food_item, calories, protein, carbs, fats, fiber, meal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, food_item, calories, protein, carbs, fats, fiber, meal_type))
    get_food_logs.clear()

def add_draft_food(food_item, calories, protein=0, carbs=0, fats=0, fiber=0):
    """Add a temporary food item to the Meal Builder cart."""
    with _db() as conn:
        conn.execute('''
            INSERT INTO draft_food_logs (food_item, calories, protein, carbs, fats, fiber)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (food_item, calories, protein, carbs, fats, fiber))
    get_draft_foods.clear()

@st.cache_data(ttl=300)
def get_draft_foods():
    """Fetch all temporary food items currently in the Meal Builder cart."""
    with _db() as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM draft_food_logs", conn)
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading draft foods: {e}")
            return pd.DataFrame()

def clear_draft_foods():
    """Clear the entire Meal Builder cart."""
    with _db() as conn:
        conn.execute("DELETE FROM draft_food_logs")
    get_draft_foods.clear()

@st.cache_data(ttl=300)
def get_food_logs():
    """Fetch all food logs."""
    with _db() as conn:
        try:
            df = pd.read_sql_query("SELECT * FROM food_logs ORDER BY date DESC", conn)
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading food logs: {e}")
            return pd.DataFrame()

def log_water(date, cups=1):
    """Log water intake."""
    with _db() as conn:
        conn.execute("INSERT INTO water_logs (date, cups) VALUES (?, ?)", (date, cups))
    get_water_history.clear()

@st.cache_data(ttl=300)
def get_water_history():
    """Get all water logs."""
    with _db() as conn:
        try:
            return pd.read_sql_query("SELECT * FROM water_logs", conn)
        except sqlite3.Error as e:
            st.error(f"Database error loading water logs: {e}")
            return pd.DataFrame()

def delete_food_log(log_id):
    """Delete a specific food log by ID."""
    with _db() as conn:
        conn.execute("DELETE FROM food_logs WHERE id=?", (log_id,))
    get_food_logs.clear()

# ── MEASUREMENTS (Phase 4 SQLite Migration) ──
def add_measurement(date, weight, waist=None, hips=None, thigh=None, chest=None, arms=None):
    """Save body measurements to SQLite (Replaces Excel)."""
    with _db() as conn:
        conn.execute('''
            INSERT INTO measurements (date, weight, waist, hips, thigh, chest, arms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date, weight, waist, hips, thigh, chest, arms))
    get_measurements.clear()

@st.cache_data(ttl=300)
def get_measurements():
    """Retrieve all body measurements as a DataFrame."""
    with _db() as conn:
        try:
            df = pd.read_sql("SELECT * FROM measurements", conn)
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                # Rename columns to match old capitalized format to maintain compatibility with charts
                df = df.rename(columns={
                    "date": "Date", "weight": "Weight", "waist": "Waist",
                    "hips": "Hips", "thigh": "Thigh", "chest": "Chest", "arms": "Arms"
                })
            return df
        except sqlite3.Error as e:
            st.error(f"Database error loading measurements: {e}")
            return pd.DataFrame()


# ========================================================
# DAILY CHECK-INS
# ========================================================

def add_checkin(date, mood=3, energy=3, sleep_hours=None, note=""):
    """Save a daily subjective check-in."""
    with _db() as conn:
        conn.execute(
            '''
            INSERT INTO checkins (date, mood, energy, sleep_hours, note)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (date, mood, energy, sleep_hours, note),
        )
    get_checkins.clear()


@st.cache_data(ttl=300)
def get_checkins():
    """Fetch daily check-ins ordered newest first."""
    with _db() as conn:
        try:
            return pd.read_sql_query("SELECT * FROM checkins ORDER BY date DESC", conn)
        except sqlite3.Error as e:
            st.error(f"Database error loading check-ins: {e}")
            return pd.DataFrame()

