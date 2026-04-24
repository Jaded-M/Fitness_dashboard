import streamlit as st
import pandas as pd
import datetime
import random
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
import styles
from ui import nutrition_charts as charts
from ui import nutrition_forms as forms
from config import STREAK_TOLERANCE_KCAL, MACRO_SPLIT_PROTEIN, MACRO_SPLIT_CARBS, MACRO_SPLIT_FATS
from utils import get_day_stats

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nutrition", page_icon="🍎", layout="wide")

st.markdown(styles.load_css(), unsafe_allow_html=True)

# --- Initialize Session State ---
if "cal_goal" not in st.session_state:
    st.session_state.cal_goal = 2300
if "water_goal" not in st.session_state:
    st.session_state.water_goal = 10

# --- Load Data ---
today_date = datetime.date.today()
food_df = database.get_food_logs()
water_df_raw = database.get_water_history()
physical_df = database.get_measurements()

# Process Water Data
today_water = 0
if not water_df_raw.empty:
    water_df_raw["date"] = pd.to_datetime(water_df_raw["date"]).dt.normalize()
    today_ts = pd.Timestamp(today_date).normalize()
    today_water = water_df_raw[water_df_raw["date"] == today_ts]["cups"].sum()

# Process Measurement Data
latest_weight = 0
if not physical_df.empty:
    physical_df["Date"] = pd.to_datetime(physical_df["Date"]).dt.normalize()
    latest_weight = physical_df.iloc[-1]["Weight"]

# Process Day Stats
t_cal, t_prot, t_carb, t_fat, t_fib = 0, 0, 0, 0, 0
if not food_df.empty:
    food_df["date"] = pd.to_datetime(food_df["date"])
    t_cal, t_prot, t_carb, t_fat, t_fib = get_day_stats(food_df, today_date)

# ============================================================
# PAGE HEADER + TOP METRICS
# ============================================================
col_title, col_action = st.columns([0.8, 0.2])
with col_title:
    st.title("Nutrition")

# --- Synergy Logic: Load Gym Data for Nutrition Intel ---
workout_raw = database.get_all_workouts()
w_count = 0
max_lift = 0
if not workout_raw.empty:
    w_df = pd.DataFrame(workout_raw)
    w_count = w_df["date"].nunique()
    if 'weight' in w_df.columns:
        max_lift = pd.to_numeric(w_df["weight"], errors='coerce').max()

with st.container(border=True):
    st.markdown(f"""
    <div style="padding: 4px;">
        <h3 style="margin-top:0; color:#888888;">Training Intelligence</h3>
        <p style="font-size:14px; font-weight:500; margin:0;">
            Completed Sessions: <strong>{w_count}</strong> &nbsp;|&nbsp; Current Max Lift: <strong>{max_lift:.1f} kg</strong><br/>
            <span style="color:#888;">{"Fully fueled for training!" if t_prot >= (st.session_state.cal_goal * 0.3 / 4 * 0.8) else "Tip: Increase protein intake for your next heavy session."}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# STREAK CALCULATION
cal_streak = 0
if not food_df.empty:
    daily_cals = food_df.groupby(food_df["date"].dt.date)["calories"].sum()
    check_date = today_date - datetime.timedelta(days=1)
    max_allowed = st.session_state.cal_goal + STREAK_TOLERANCE_KCAL
    while check_date in daily_cals.index:
        if 0 < daily_cals[check_date] <= max_allowed:
            cal_streak += 1
            check_date -= datetime.timedelta(days=1)
        else:
            break
    if 0 < t_cal <= max_allowed:
        cal_streak += 1

seven_day_avg = 0
if not food_df.empty:
    last_7_days = today_date - datetime.timedelta(days=7)
    recent_food = food_df[food_df["date"].dt.date > last_7_days]
    if not recent_food.empty:
        seven_day_avg = int(recent_food.groupby(recent_food["date"].dt.date)["calories"].sum().mean())

target_protein = int((st.session_state.cal_goal * MACRO_SPLIT_PROTEIN) / 4) 
target_carbs   = int((st.session_state.cal_goal * MACRO_SPLIT_CARBS) / 4)   
target_fats    = int((st.session_state.cal_goal * MACRO_SPLIT_FATS) / 9)    

# Metric Rows
with st.container(border=True):
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric("Calories", f"{t_cal}", f"{(st.session_state.cal_goal - t_cal):+} remaining", delta_color="inverse")
    r1c2.metric("Protein",  f"{t_prot}g", f"{(target_protein - t_prot):+} remaining", delta_color="inverse")
    r1c3.metric("Carbs",    f"{t_carb}g", f"{(target_carbs - t_carb):+} remaining", delta_color="inverse")
    r1c4.metric("Fats",      f"{t_fat}g", f"{(target_fats - t_fat):+} remaining", delta_color="inverse")

with st.container(border=True):
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    r2c1.metric("7-Day Avg",      f"{seven_day_avg} kcal")
    r2c2.metric("Goal Streak",    f"{cal_streak} Days")
    r2c3.metric("Water",          f"{today_water} / {st.session_state.water_goal} cup")
    r2c4.metric("Weight",         f"{latest_weight:.1f} kg" if latest_weight else "—")

st.markdown("<br>", unsafe_allow_html=True)
cal_pct_val = min(t_cal / st.session_state.cal_goal, 1.0) * 100 if st.session_state.cal_goal > 0 else 0
with st.container(border=True):
    st.markdown(f"""
    <div style="padding: 4px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 500; color: #888888; font-size:14px; text-transform:uppercase;">Calorie Tracker</span>
            <span style="color: #FFFFFF; font-weight: 600;">{t_cal:,} / {st.session_state.cal_goal:,} kcal</span>
        </div>
        <div class="custom-progress-track">
            <div class="custom-progress-fill {'over' if t_cal > st.session_state.cal_goal else ''}" 
                 style="width: {cal_pct_val}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# MAIN LAYOUT — ACTION BUTTONS
# ============================================================
action1, action2, action3, action4 = st.columns(4)
with action1:
    if st.button("Log Meal", use_container_width=True, type="primary"):
        forms.render_food_log_form(today_date)
with action2:
    if st.button("Log Measurements", use_container_width=True):
        forms.render_measurements_form(today_date)
with action3:
    st.button("+1 Cup Water", use_container_width=True, on_click=database.log_water, args=(today_date, 1))
with action4:
    with st.popover("Goals & Settings", use_container_width=True):
        st.session_state.cal_goal   = st.number_input("Daily Calorie Goal", 1000, 5000, st.session_state.cal_goal)
        st.session_state.water_goal = st.number_input("Daily Water Goal", 1, 20, st.session_state.water_goal)
        recipes = [
            "**Greek Yogurt Bowl**: yogurt + protein + berries ≈ 350 kcal",
            "**Paneer Tikka Salad**: paneer + greens + mint chutney ≈ 400 kcal",
            "**Tuna Salad**: 1 can tuna + light mayo + corn ≈ 300 kcal",
        ]
        st.info(f"🥗 **Recipe Idea**: {random.choice(recipes)}")

st.markdown("---")

# ============================================================
# DASHBOARD TABS
# ============================================================
timeframe = st.radio("Timeframe", ["7 Days", "14 Days", "30 Days", "90 Days", "All Time"], index=1, horizontal=True)
tf_days = {"7 Days": 7, "14 Days": 14, "30 Days": 30, "90 Days": 90, "All Time": 9999}[timeframe]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Weekly Trends", "Day Breakdown", "Body Progress",
    "Macro History", "Biological Engine", "Manage Logs"
])

with tab1: charts.render_weekly_trends(food_df, tf_days, st.session_state.cal_goal)
with tab2: charts.render_day_breakdown(food_df, st.session_state.cal_goal, MACRO_SPLIT_PROTEIN, MACRO_SPLIT_CARBS, MACRO_SPLIT_FATS)
with tab3: charts.render_body_progress(physical_df, tf_days)
with tab4: charts.render_macro_history(food_df, water_df_raw, tf_days, st.session_state.water_goal)
with tab5: charts.render_bca_engine(latest_weight)

with tab6:
    st.markdown("##### Delete Food Log Entries")
    if not food_df.empty:
        recent_disp = food_df.head(30)
        del_ids = st.multiselect("Select IDs to delete:", recent_disp["id"].tolist())
        if del_ids and st.button("Delete Entries", type="primary"):
            for d_id in del_ids:
                database.delete_food_log(d_id)
            st.success("Deleted!")
            st.rerun()
