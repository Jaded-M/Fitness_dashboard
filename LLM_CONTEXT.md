# Fitness Tracker Project Context

## Overview
This is a Streamlit-based Fitness & Nutrition Dashboard. It allows users to:
1.  **Track Workouts**: Log sets, reps, weight.
2.  **RPG Gamification**: Users gain XP and levels based on lifted volume.
3.  **Nutrition**: Log food, Macros, Water, and "Cheat Meals".
4.  **Analysis**: Visualize data with automated Charts (processed in `charts.py`).

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: Python (Pandas + SQLite)
- **Visualization**: Plotly Express + Altair
- **Database**: Local `gym.db` and `nutrition.db`

---

## File: `Fitness.py` (Main App)
```python
import streamlit as st
import pandas as pd
import os
import time
import json
from pathlib import Path
import random
from datetime import datetime, timedelta

# Local Modules
import database
import styles 
import charts 

# External Libs 
import altair as alt 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Initialize Data Management
database.init_db()
database.init_nutrition_db()

# ============================================
# EXERCISE LIBRARY (Splits)
# ============================================
EXERCISE_LIBRARY = {
    "Day A (Power & Push)": [
        "Leg Press", "Dumbbell Bench Press", "Lat Pulldown", "Machine Row",
        "Machine Shoulder Press", "Tricep Rope Pushdowns", "Bicep Hammer Curls"
    ],
    "Day B (Glutes, Pull, Core)": [
        "Romanian Deadlift (DB)", "Goblet Squat", "Seated Row",
        "Incline Dumbbell/Chest Machine", "Face Pulls", "Cable Crunch", "Calf Raises"
    ],
    "Day C (Balanced Strength)": [
        "Leg Press / Hack Squat", "Dumbbell Shoulder Press", "Single-Arm Row",
        "Pec Deck / Cable Fly", "Biceps Curls (Left Focus)", "Tricep Overhead DB", "Lateral Raises"
    ],
    "Cardio / Other": [
        "Walking (Target 7-10k)", "Mobility Work", "Light Cardio"
    ]
}

# ============================================
# PAGE SETUP
# ============================================
st.set_page_config(page_title="Fitness Dashboard", layout="wide", page_icon="💪")
st.markdown(styles.load_css(), unsafe_allow_html=True)

# ============================================
# DATA LOADING FUNCTIONS
# ============================================
def load_google_fit_steps(start_date, end_date):
    if not os.path.exists('fitness_credentials.json'): return None
    try:
        # Auth logic simplified for brevity (same as before)
        SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token: creds = pickle.load(token)
        if not creds or not creds.valid:
             if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
             else:
                 flow = InstalledAppFlow.from_client_secrets_file('fitness_credentials.json', SCOPES)
                 creds = flow.run_local_server(port=0)
             with open('token.pickle', 'wb') as token: pickle.dump(creds, token)
        
        service = build('fitness', 'v1', credentials=creds)
        start_time = datetime.combine(start_date, datetime.min.time())
        end_time_dt = datetime.combine(end_date, datetime.max.time())
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time_dt.timestamp() * 1000)
        dataset = f"{start_ms}000000-{end_ms}000000"
        data_source = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        
        response = service.users().dataSources().datasets().get(userId='me', dataSourceId=data_source, datasetId=dataset).execute()
        steps_data = []
        if 'point' in response:
            for point in response['point']:
                ts = int(point['startTimeNanos']) / 1e9
                date = datetime.fromtimestamp(ts)
                steps = point['value'][0]['intVal']
                steps_data.append({'date': date.date(), 'steps': steps})
        if steps_data:
            df = pd.DataFrame(steps_data)
            df = df.groupby('date', as_index=False)['steps'].sum()
            df['date'] = pd.to_datetime(df['date'])
            return df.sort_values('date')
        return None
    except Exception: return None

def load_excel_file(filename):
    try: return pd.read_excel(filename)
    except Exception as e: st.sidebar.error(f"❌ Excel error: {e}"); return None

# ============================================
# SIDEBAR
# ============================================
st.sidebar.title("⚙️ Helper")
if os.path.exists("chill_guy.jpg"):
    st.sidebar.image("chill_guy.jpg", width="stretch")

# Data Source Selection
data_source = st.sidebar.radio("📊 Source:", ["Local Database (New)", "Google Sheets", "Upload Excel"])
uploaded_file = None
if data_source == "Upload Excel":
    uploaded_file = st.sidebar.file_uploader("📁 Choose file", type=['xlsx', 'xls'])

# Steps Selection
load_steps = st.sidebar.checkbox("👟 Load Google Fit Steps", value=True)
start_date, end_date = datetime.now() - timedelta(days=30), datetime.now()
if load_steps:
    date_range = st.sidebar.date_input("Date Range", [start_date, end_date])
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range

st.sidebar.markdown("---")
st.sidebar.success("v2.0 Refactored 🚀")

# ============================================
# LOAD DATA
# ============================================
workout_df = None
if data_source == "Local Database (New)":
    workout_df = database.get_all_workouts()
    if not workout_df.empty:
        workout_df["Date"] = pd.to_datetime(workout_df["date"])
        workout_df = workout_df.rename(columns={"split": "Split", "exercise": "Workout", "weight": "Weight", "duration": "Duration"})
        # Fix missing columns
        for col in ["Duration", "Calories", "Weight", "sets", "reps"]:
             if col not in workout_df.columns: workout_df[col] = 0
        workout_df["Duration"] = pd.to_numeric(workout_df["Duration"], errors='coerce').fillna(0)
        workout_df["Weight"] = pd.to_numeric(workout_df["Weight"], errors='coerce').fillna(0)

elif data_source == "Google Sheets": 
    with st.spinner("Loading Sheets..."): workout_df = pd.DataFrame() # Placeholder
elif data_source == "Upload Excel" and uploaded_file:
    workout_df = load_excel_file(uploaded_file)

steps_df = None
if load_steps:
    with st.spinner("Loading Steps..."):
        steps_df = load_google_fit_steps(start_date, end_date)

# Clean Data
workout_ready = False
if workout_df is not None and not workout_df.empty:
    # Basic cleaning
    workout_df = workout_df.loc[:, ~workout_df.columns.duplicated()]
    if "Date" in workout_df.columns:
        workout_df["Date"] = pd.to_datetime(workout_df["Date"], errors='coerce')
        workout_df = workout_df.dropna(subset=["Date"])
        workout_ready = True

# ============================================
# SIDEBAR TOOLS (Timer, Stats, Gym Bro)
# ============================================
with st.sidebar.container():
    st.markdown("### 🤖 Ask Gym Bro AI")
    bro_q = st.text_input("Ask a question:", placeholder="Does creatine work?")
    if bro_q:
        bro_answers = [
            "Trust the process, bro.", "It's all about the pump.", "Eat big to get big.", 
            "Did you drink your protein shake?", "Squat deeper.", "Sleep is for gains.",
            "Light weight baby!", "Yeah buddy!", "Just lift it.", "Ask me after your set."
        ]
        st.sidebar.info(f"🤖 **Bro Says**: {random.choice(bro_answers)}")

    st.markdown("---")
    st.markdown("### ⏱️ Rest Timer")
    c1, c2, c3 = st.columns(3)
    dur = 0
    if c1.button("1:00"): dur = 60
    if c2.button("1:30"): dur = 90
    if c3.button("2:00"): dur = 120
    
    if dur > 0:
        place = st.empty()
        with place.container():
            bar = st.progress(0)
            status = st.empty()
            for i in range(dur):
                bar.progress((i+1)/dur)
                status.info(f"Resting... {dur-i}s")
                time.sleep(1)
            status.success("GO! 🔔")
            st.balloons()
            place.empty()

    if workout_ready:
        st.sidebar.subheader("🔥 Streak")
        # Simple streak calc
        dates = sorted(workout_df["Date"].dt.date.unique())
        streak = 0
        if dates:
            last = dates[-1]
            if last >= (datetime.now().date() - timedelta(days=1)):
                streak = 1
                for i in range(len(dates)-2, -1, -1):
                    if dates[i+1] - dates[i] == timedelta(days=1): streak += 1
                    else: break
        
        st.sidebar.metric("Current Streak", f"{streak} Days")

# ============================================
# MAIN DASHBOARD
# ============================================
st.title("💪 FITNESS DASHBOARD v2.0")

# 1. Log Session Time
with st.expander("⏱️ Log Session Duration", expanded=False):
    d_date = st.date_input("Date", datetime.now(), key="d_d")
    d_min = st.number_input("Mins", 1, 300, 45, step=5)
    if st.button("Save Time"):
        database.add_workout(d_date, "Session Info", "Session Duration", 0,0,0,0,"N/A", d_min)
        st.success("Saved!"); time.sleep(1); st.rerun()

# 2. Log Workout
with st.expander("📝 Log Workout Sets", expanded=False):
    l_date = st.date_input("Date", datetime.now())
    split = st.selectbox("Split", list(EXERCISE_LIBRARY.keys()))
    
    # Smart Exercise List
    std_ex = EXERCISE_LIBRARY[split]
    hist_ex = database.get_unique_exercises()
    final_opts = std_ex + [x for x in hist_ex if x not in std_ex] + ["+ Add New..."]
    
    ex_name = st.selectbox("Exercise", final_opts)
    if ex_name == "+ Add New...": ex_name = st.text_input("New Name")
    
    # Data Editor
    if "editor_key" not in st.session_state: st.session_state.editor_key = 0
    
    sets_data = st.data_editor(
        [{"Weight": 20.0, "Reps": 10, "RPE": 8}] * 3,
        num_rows="dynamic",
        key=f"edit_{st.session_state.editor_key}"
    )
    
    if st.button("Save Sets", type="primary"):
        if ex_name:
            valid_sets = [s for s in sets_data if s["Reps"] > 0]
            if valid_sets:
                # Calc stats
                count = len(valid_sets)
                max_w = max(s["Weight"] for s in valid_sets)
                tot_r = sum(s["Reps"] for s in valid_sets)
                
                # Check PR
                is_pr = False
                if workout_ready:
                    past = workout_df[workout_df["Workout"] == ex_name]
                    if not past.empty and max_w > past["Weight"].max(): is_pr = True
                
                database.add_workout(l_date, split, ex_name, count, tot_r, max_w, 0, "Medium", 0, json.dumps(valid_sets))
                msg = f"Saved {count} sets of {ex_name}!"
                if is_pr: msg += " 🏆 NEW PR!"
                st.success(msg)
                if is_pr: st.balloons()
                st.session_state.editor_key += 1; time.sleep(1); st.rerun()
            else:
                st.error("Add valid sets!")

st.markdown("---")

# ============================================
# RPG & GAMIFICATION 🎮
# ============================================
if workout_ready:
    st.subheader("⚔️ Lifter RPG Stats")
    
    # Calc XP (Volume)
    vol = (workout_df["reps"] * workout_df["Weight"]).sum()
    level = int(vol / 5000) + 1 # Easier leveling
    xp_prog = (vol % 5000) / 5000
    
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown(f"# 🛡️ Lvl {level}")
    with c2:
        st.caption(f"XP: {int(vol):,} / {level*5000:,}")
        st.progress(xp_prog)
    
    # Badges
    badges = []
    if len(workout_df) > 10: badges.append("🥉 Novice")
    if vol > 100000: badges.append("🚜 Bulldozer")
    if streak > 7: badges.append("🔥 On Fire")
    
    if badges: st.success("Badges Unlocked: " + "  ".join(badges))
    else: st.info("Keep lifting to unlock badges!")

st.markdown("---")

# ============================================
# METRICS & CHARTS (Modular)
# ============================================
# Metrics
m1, m2, m3 = st.columns(3)
if workout_ready:
    m1.metric("Total Workouts", len(workout_df))
    m2.metric("Avg Duration", f"{int(workout_df['Duration'].mean())} min")
    m3.metric("Max Weight Lifted", f"{workout_df['Weight'].max()} kg")

st.markdown("---")

# Render Charts using new Module
charts.render_training_balance(workout_df)
st.markdown("---")
charts.render_progression_chart(workout_df)
st.markdown("---")
charts.render_duration_chart(workout_df)
st.markdown("---")
charts.render_steps_chart(steps_df)
st.markdown("---")
charts.render_heatmap(workout_df, steps_df)

# ============================================
# FEATURE: QUOTES & DAILY CHALLENGE
# ============================================
st.markdown("---")

# Load Quotes
quotes_path = Path(__file__).resolve().parent / "quotes.txt"
try:
    quotes_list = [q.strip() for q in quotes_path.read_text(encoding="utf-8").splitlines() if q.strip()]
except:
    quotes_list = ["Light weight baby!"]

if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(quotes_list)

# Quote Card with Custom Style
st.markdown(f"""
<div style="background-color: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #00d2ff; margin-bottom: 20px;">
    <h4 style="margin:0; color: #00d2ff;">💡 Wisdom of the Reps</h4>
    <p style="font-style: italic; font-size: 18px; margin-top: 10px;">"{st.session_state.daily_quote}"</p>
</div>
""", unsafe_allow_html=True)

# Daily Quest
quests = ["Do 20 Pushups Now", "Hold a Plank for 1 min", "Drink a full glass of water", "Stretch your hamstrings", "Do 10 Squats", "Take a deep breath"]
if "quest" not in st.session_state: st.session_state.quest = random.choice(quests)

c1, c2 = st.columns([3, 1])
with c1:
    st.info(f"⚔️ **Daily Side-Quest**: {st.session_state.quest}!")
with c2:
    if st.button("Complete Quest"):
        st.balloons()
        st.success("XP Gained! (Imaginary)")
        st.session_state.quest = random.choice(quests) # New quest
        time.sleep(1)
        st.rerun()
```

---

## File: `database.py`
```python
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

    conn.commit()
    conn.close()

def add_workout(date, split, exercise, sets, reps, weight, rpe=None, fatigue=None, duration=0, set_data=None):
    """Add a new workout log to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO workouts (date, split, exercise, sets, reps, weight, rpe, fatigue, duration, set_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, split, exercise, sets, reps, weight, rpe, fatigue, duration, set_data))
    
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

def get_unique_exercises():
    """Fetch all unique exercise names ordered by usage count."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # Get exercises sorted by how often they are used (most popular first)
        c.execute('''
            SELECT exercise, COUNT(*) as count 
            FROM workouts 
            GROUP BY exercise 
            ORDER BY count DESC
        ''')
        return [row[0] for row in c.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()

# ========================================================
# NUTRITION DATABASE
# ========================================================
NUTRITION_DB_NAME = "nutrition.db"

def init_nutrition_db():
    """Initialize the nutrition database."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    c = conn.cursor()
    
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
            meal_type TEXT DEFAULT 'Snack'
        )
    ''')
    
    # Migration: Add meal_type if missing
    c.execute("PRAGMA table_info(food_logs)")
    cols = [info[1] for info in c.fetchall()]
    if 'meal_type' not in cols:
        try: c.execute("ALTER TABLE food_logs ADD COLUMN meal_type TEXT DEFAULT 'Snack'")
        except: pass
        
    # Create water_logs table (Simple date-based counter seems easier, but let's log entries for history)
    c.execute('''
        CREATE TABLE IF NOT EXISTS water_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            cups INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

def add_food_log(date, food_item, calories, protein=0, carbs=0, fats=0, meal_type="Snack"):
    """Add a food log entry."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO food_logs (date, food_item, calories, protein, carbs, fats, meal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, food_item, calories, protein, carbs, fats, meal_type))
    
    conn.commit()
    conn.close()

def get_food_logs():
    """Fetch all food logs."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM food_logs ORDER BY date DESC", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def log_water(date, cups=1):
    """Log water intake."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO water_logs (date, cups) VALUES (?, ?)", (date, cups))
    conn.commit()
    conn.close()

def get_water_history():
    """Get all water logs."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    try:
        return pd.read_sql_query("SELECT * FROM water_logs", conn)
    except:
        return pd.DataFrame()
    finally:
        conn.close()

def delete_food_log(log_id):
    """Delete a specific food log by ID."""
    conn = sqlite3.connect(NUTRITION_DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM food_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()
```

---

## File: `pages/1_🍎_Nutrition.py`
```python
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import sys
import os
import time

# Add parent directory to path so we can import styles and database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import styles
import database

# Page Setup
st.set_page_config(page_title="Nutrition Tracker", page_icon="🍎", layout="wide")
st.markdown(styles.load_css(), unsafe_allow_html=True)

# Header
st.title("🍎 Nutrition Tracker")

# Initialize DB
database.init_nutrition_db()

# Session State for Goals
if "cal_goal" not in st.session_state: st.session_state.cal_goal = 2500
if "water_goal" not in st.session_state: st.session_state.water_goal = 8

# Layout
col_log, col_dash = st.columns([1, 2])

# ================================
# RIGHT COL: LOGGING
# ================================
with col_log:
    # 1. Water Tracker (Top Priority)
    st.markdown("### 💧 Hydration")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Get water today
        w_df = database.get_water_history()
        today_cups = 0
        if not w_df.empty:
            w_df["date"] = pd.to_datetime(w_df["date"]).dt.date
            today_cups = w_df[w_df["date"] == datetime.date.today()]["cups"].sum()
            
        st.metric("Cups Today", f"{today_cups} / {st.session_state.water_goal}")
        
        # Add Water
        wc1, wc2, wc3 = st.columns(3)
        if wc1.button("💧 +1 Cup"):
            database.log_water(datetime.date.today(), 1)
            st.rerun()
        if wc2.button("🥤 +2 Cups"):
            database.log_water(datetime.date.today(), 2)
            st.rerun()
        if wc3.button("Reset"):
            # Not implemented in DB yet, but could be specific DELETE
            st.toast("Stay hydrated!")
        
        # Hydration Progress
        progress = min(today_cups / st.session_state.water_goal, 1.0)
        st.progress(progress)
        if today_cups >= st.session_state.water_goal: st.success("Hydration Goal Met! 🌊")
        
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # 2. Food Log Form
    st.markdown("### 🍽️ Log Meal")
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        log_date = st.date_input("Date", datetime.date.today())
        meal_type = st.select_slider("Meal", options=["Breakfast", "Lunch", "Snack", "Dinner"], value="Snack")
        food_name = st.text_input("Food Item", placeholder="e.g., Oatmeal & Berries")
        
        c1, c2 = st.columns(2)
        with c1: calories = st.number_input("Calories", 0, 5000, 0, step=10)
        with c2: protein = st.number_input("Protein (g)", 0, 500, 0)
            
        c3, c4 = st.columns(2)
        with c3: carbs = st.number_input("Carbs (g)", 0, 500, 0)
        with c4: fats = st.number_input("Fats (g)", 0, 500, 0)
            
        if st.button("Add Entry", type="primary", use_container_width=True):
            if food_name and calories > 0:
                database.add_food_log(log_date, food_name, calories, protein, carbs, fats, meal_type)
                st.success(f"Added to **{meal_type}**!")
            else:
                st.warning("Needs Name & Calories")

        # CHEAT MEAL (EDITABLE)
        with st.expander("🚨 Cheat Meal (Config)"):
            c_name = st.text_input("What did you eat?", "Pizza/Burger")
            c_cal = st.number_input("Calories", 100, 5000, 1000, step=50)
            if st.button("Log Cheat Meal", type="primary"):
                database.add_food_log(log_date, c_name, c_cal, 0, 0, 0, "Dinner")
                st.toast(f"Logged {c_name}! Tomorrow is a new day.", icon="🍕")
                time.sleep(1)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Healthy Recipe Tip
    import random
    recipes = [
        "**Greek Yogurt Bowl**: 1 cup yogurt + 1 scoop protein + berries.",
        "**Chicken Stir Fry**: 200g Chicken + Broccoli + Soy Sauce.",
        "**Oats & Whey**: 50g Oats + 1 scoop Whey + Peanut Butter.",
        "**Tuna Salad**: 1 can Tuna + Light Mayo + Corn.",
        "**Egg White Omelet**: 1 cup Egg Whites + Spinach + Feta."
    ]
    st.info(f"🥗 **Recipe Idea**: {random.choice(recipes)}")

    st.markdown("---")
        
    # Goal Settings
    with st.expander("⚙️ Settings"):
        st.session_state.cal_goal = st.number_input("Daily Calorie Goal", 1000, 5000, st.session_state.cal_goal)
        st.session_state.water_goal = st.number_input("Daily Cups Goal", 1, 20, st.session_state.water_goal)


# ================================
# LEFT COL: DASHBOARD
# ================================
with col_dash:
    st.markdown("### 📊 Daily Overview")
    
    # Load Data
    df = database.get_food_logs()
    
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        today = pd.Timestamp.now().normalize()
        today_df = df[df["date"] == today]
        
        # Aggregates
        t_cals = today_df["calories"].sum()
        t_prot = today_df["protein"].sum()
        t_carb = today_df["carbs"].sum()
        t_fat = today_df["fats"].sum()
        
        # 1. Main Stats Logic
        # Calorie Circle or Bar? Let's do a Progress Bar with numbers
        rem_cals = st.session_state.cal_goal - t_cals
        st.metric("Calories Consumed", f"{t_cals} / {st.session_state.cal_goal}", f"{rem_cals} remaining", delta_color="normal")
        st.progress(min(t_cals / st.session_state.cal_goal, 1.0))
        
        # Macros
        m1, m2, m3 = st.columns(3)
        m1.metric("🥩 Protein", f"{t_prot}g")
        m2.metric("🍞 Carbs", f"{t_carb}g")
        m3.metric("🥑 Fats", f"{t_fat}g")
        
        st.markdown("---")
        
        # 2. Charts Tabs
        tab1, tab2, tab3 = st.tabs(["📅 Weekly Trends", "🍽️ Meal Split", "📃 History"])
        
        with tab1:
            # 7 Day History
            last_7 = df[df["date"] >= (today - datetime.timedelta(days=7))]
            daily = last_7.groupby("date")["calories"].sum().reset_index()
            
            fig = px.bar(
                daily, x="date", y="calories", 
                title="Last 7 Days (Calories)",
                color_discrete_sequence=["#2bd9fe"]
            )
            # Add goal line
            fig.add_hline(y=st.session_state.cal_goal, line_dash="dash", line_color="orange", annotation_text="Goal")
            
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            # Meal Type Breakdown (Donut)
            if not today_df.empty:
                meal_split = today_df.groupby("meal_type")["calories"].sum().reset_index()
                fig2 = px.pie(
                    meal_split, values="calories", names="meal_type", 
                    hole=0.4, title="Calories by Meal",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Log food today to see breakdown!")
                
        with tab3:
            # Manage Logs (Delete)
            st.markdown("##### 🗑️ Manage Recent Logs")
            
            # Show recent logs with ID
            history_df = df.head(20).copy()
            st.dataframe(history_df[["id", "date", "food_item", "calories", "meal_type"]], use_container_width=True, hide_index=True)
            
            # Delete Form
            delete_ids = st.multiselect("Select Logs to Delete", options=history_df["id"], format_func=lambda x: f"ID {x}: {history_df[history_df['id']==x]['food_item'].values[0]}")
            
            if delete_ids:
                if st.button(f"Delete {len(delete_ids)} Entries", type="primary"):
                    for d_id in delete_ids:
                        database.delete_food_log(d_id)
                    st.success("Deleted!")
                    time.sleep(1)
                    st.rerun()

    else:
        st.info("👋 Welcome! Log your first meal on the left to activate the dashboard.")
```

---

## File: `styles.py`
```python
def load_css():
    """Returns the custom CSS for the Midnight Theme."""
    return """
    <style>
        /* Midnight Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            color: white;
        }
        
        /* Headers - Modern Gradient Text */
        h1 {
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            background: linear-gradient(120deg, #ff00cc, #333399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            padding-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        h2, h3, h4 {
            color: #e0e0e0 !important;
            font-family: 'Roboto', sans-serif;
            font-weight: 300;
        }
        
        /* Glassmorphism Cards for Metrics */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            background-color: rgba(255, 255, 255, 0.15);
        }
        
        [data-testid="stMetricValue"] {
            font-size: 32px !important;
            font-weight: 700 !important;
            color: #00d2ff !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 14px !important;
            color: #b0bec5 !important;
            letter-spacing: 1px;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.2);
        }
        
        /* Custom Buttons - Neon Glow */
        .stButton > button {
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 30px;
            font-weight: bold;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.5);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.8);
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.05);
            color: white !important;
            border-radius: 10px;
        }
    </style>
    """
```

---

## File: `charts.py`
```python
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import matplotlib.pyplot as plt
import datetime

def render_training_balance(workout_df):
    """Renders a simple, fun Donut chart for Split distribution."""
    st.subheader("🥧 Training Balance")
    
    if workout_df is None or workout_df.empty:
        st.info("Log some workouts to see your split balance!")
        return

    split_counts = workout_df["Split"].value_counts().reset_index()
    split_counts.columns = ["Split", "Count"]

    # Simple, Fun Donut Chart
    fig = px.pie(
        split_counts, 
        values="Count", 
        names="Split", 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel  # Fun pastel colors
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        showlegend=True,
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    # Fun fact
    top_split = split_counts.iloc[0]["Split"]
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Looks like you love **{top_split}** days! Keep it balanced! ⚖️")


def render_progression_chart(workout_df):
    """Renders usage and strength progression charts."""
    st.subheader("📈 Exercise Progression")
    
    if workout_df is None or workout_df.empty:
        st.info("Log workouts to unlock progression stats!")
        return

    # Filter out Session Duration
    all_exercises = workout_df["Workout"].unique()
    valid_exercises = [ex for ex in all_exercises if str(ex) != "Session Duration"]
    unique_exercises = sorted(valid_exercises)
    
    exercise_choice = st.selectbox("Select Exercise to Analyze:", unique_exercises)
    
    if exercise_choice:
        ex_df = workout_df[workout_df["Workout"] == exercise_choice].copy()
        ex_df = ex_df.sort_values("Date")
        
        if not ex_df.empty:
            # Stats Cards
            col1, col2 = st.columns(2)
            with col1:
                max_w = ex_df["Weight"].max()
                st.metric("🏆 Personal Best", f"{max_w} kg")
            with col2:
                # Approximate max reps
                max_r = ex_df["reps"].max() if "reps" in ex_df.columns else 0
                st.metric("🔥 Max Reps", max_r)
            
            # Chart 1: Strength (Weight)
            st.markdown("##### 💪 Strength Gains (Max Weight)")
            daily_max = ex_df.groupby("Date")[["Weight"]].max().reset_index()
            
            chart_cost = alt.Chart(daily_max).mark_line(point=True, color="#00d2ff").encode(
                x='Date:T',
                y=alt.Y('Weight:Q', title='Weight (kg)'),
                tooltip=['Date', 'Weight']
            ).interactive()
            
            st.altair_chart(chart_cost, use_container_width=True)
            
            # Chart 2: Volume (Fun Addition)
            st.markdown("##### 🏋️ Total Volume (The Grind)")
            ex_df["Volume"] = ex_df["reps"] * ex_df["Weight"]
            daily_vol = ex_df.groupby("Date")[["Volume"]].sum().reset_index()
            
            chart_vol = alt.Chart(daily_vol).mark_area(
                line={'color':'#ff00cc'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#ff00cc', offset=0),
                           alt.GradientStop(color='rgba(255, 0, 204, 0.1)', offset=1)],
                    x1=1, x2=1, y1=1, y2=0
                )
            ).encode(
                x='Date:T',
                y=alt.Y('Volume:Q', title='Volume (kg)'),
                tooltip=['Date', 'Volume']
            ).interactive()
            
            st.altair_chart(chart_vol, use_container_width=True)
            
        else:
            st.info(f"No data for {exercise_choice} yet.")


def render_duration_chart(workout_df):
    """Renders workout duration over time."""
    st.subheader("⏱️ Time in the Gym")
    
    if workout_df is None or workout_df.empty:
        st.info("No duration data.")
        return
        
    if "Date" not in workout_df.columns or "Duration" not in workout_df.columns:
        return

    # Simple toggle
    view_mode = st.radio("View:", ["Actual Logged Time", "Calculated Est."], horizontal=True, label_visibility="collapsed")
    
    daily = pd.DataFrame()
    
    if view_mode == "Actual Logged Time":
        daily = workout_df[workout_df["Workout"] == "Session Duration"].groupby("Date")["Duration"].max().reset_index()
    else:
        # Sum of estimated duration of exercises (excluding session logs)
        sub = workout_df[workout_df["Workout"] != "Session Duration"]
        daily = sub.groupby("Date")["Duration"].sum().reset_index()
        
    if not daily.empty:
        chart = alt.Chart(daily).mark_bar(color="#8B4FEC", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x='Date:T',
            y='Duration:Q',
            tooltip=['Date', 'Duration']
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.caption("No data for this view selection.")


def render_steps_chart(steps_df):
    """Renders steps history."""
    st.subheader("👟 Step Tracker")
    
    if steps_df is None or steps_df.empty:
        st.info("Connect Google Fit to see steps!")
        return
        
    # Color logic
    steps_df['Status'] = steps_df['steps'].apply(
        lambda s: '🔥 Crushed It!' if s >= 10000 else '✅ Good' if s >= 7000 else '💤 Lazy Day'
    )
    
    chart = alt.Chart(steps_df).mark_bar().encode(
        x='date:T',
        y='steps:Q',
        color=alt.Color('Status:N', scale=alt.Scale(
            domain=['🔥 Crushed It!', '✅ Good', '💤 Lazy Day'],
            range=['#00ff00', '#ffff00', '#ff0000']
        )),
        tooltip=['date', 'steps', 'Status']
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
    
    avg = int(steps_df["steps"].mean())
    st.caption(f"You average **{avg:,}** steps a day.")


def render_heatmap(workout_df, steps_df):
    """Renders the fancy activity strip heatmap."""
    st.subheader("🔥 Consistency Heatmap")
    
    if workout_df is None: return

    # Gather dates
    dates = workout_df["Date"].tolist()
    if steps_df is not None and not steps_df.empty:
        dates.extend(steps_df["date"].tolist())
        
    if not dates:
        st.info("No activity yet.")
        return
        
    start = min(dates)
    end = datetime.datetime.now()
    all_dates = pd.date_range(start, end)
    
    # Calculate scores
    scores = []
    for d in all_dates:
        s = 0
        # Wokout points
        day_sets = workout_df[workout_df["Date"] == d]["sets"].sum()
        s += day_sets * 2 
        
        # Step points
        if steps_df is not None:
            day_step_row = steps_df[steps_df["date"] == d.date()] # steps_df date is usually just date
            # Fix date comparison if needed (pd timestamp vs date)
            # Actually steps_df setup in Fitness.py sets 'date' as datetime64 usually or object
            # Let's simple check:
            if not day_step_row.empty:
                steps = day_step_row.iloc[0]["steps"]
                if steps > 10000: s += 5
                elif steps > 5000: s += 2
        
        scores.append(s)
        
    # Plot
    # We'll use a simple GitHub style line logic or just render the heatmap image
    # For simplicity/speed in this refactor, let's use a simple Github-like grid using Altair heatmap?
    # Or stick into the matplotlib one but cleaner.
    
    # Let's try an Altair Heatmap (Year/Month/Day) - actually simple bar strip is easier for now to replace the complex matplotlib
    # Simpler: Bar chart of "Activity Score"
    
    activity_df = pd.DataFrame({"Date": all_dates, "Score": scores})
    
    chart = alt.Chart(activity_df[-90:]).mark_rect().encode( # Last 90 days
        x='Date:T',
        y=alt.value(20), # fixed height
        color=alt.Color('Score:Q', scale=alt.Scale(scheme='greens'), legend=None),
        tooltip=['Date', 'Score']
    ).properties(height=50) # Thin strip
    
    st.altair_chart(chart, use_container_width=True)
    st.caption("Darker Green = More Gains 💪")
```
