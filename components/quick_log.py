from __future__ import annotations

from datetime import date

import streamlit as st

import database


@st.dialog("Log workout")
def workout_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_workout_date")
    split = st.selectbox(
        "Split",
        ["Upper A", "Lower A", "Upper B", "Lower B", "Full Body", "Conditioning", "Custom"],
        key="ql_split",
    )
    exercise = st.text_input("Exercise", placeholder="Leg press", key="ql_exercise")
    c1, c2, c3 = st.columns(3)
    sets = c1.number_input("Sets", 1, 20, 3, key="ql_sets")
    reps = c2.number_input("Total reps", 1, 300, 30, key="ql_reps")
    weight = c3.number_input("Top weight kg", 0.0, 500.0, 20.0, step=2.5, key="ql_weight")
    rpe = st.slider("Session effort", 1, 10, 7, key="ql_rpe")

    if st.button("Save workout", type="primary", width="stretch"):
        if not exercise.strip():
            st.warning("Add an exercise name first.")
            return
        database.add_workout(log_date, split, exercise.strip(), sets, reps, weight, rpe, "Medium", 0)
        st.toast("Workout saved.")
        st.rerun()


@st.dialog("Log meal")
def meal_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_food_date")
    meal = st.radio("Meal", ["Breakfast", "Lunch", "Snack", "Dinner"], horizontal=True, key="ql_meal")
    name = st.text_input("Food", placeholder="Chicken rice bowl", key="ql_food")
    c1, c2 = st.columns(2)
    calories = c1.number_input("Calories", 0, 5000, 450, step=25, key="ql_calories")
    protein = c2.number_input("Protein g", 0, 400, 30, key="ql_protein")
    c3, c4, c5 = st.columns(3)
    carbs = c3.number_input("Carbs g", 0, 600, 45, key="ql_carbs")
    fats = c4.number_input("Fats g", 0, 300, 12, key="ql_fats")
    fiber = c5.number_input("Fiber g", 0, 100, 4, key="ql_fiber")

    if st.button("Save meal", type="primary", width="stretch"):
        if not name.strip() or calories <= 0:
            st.warning("Food name and calories are required.")
            return
        database.add_food_log(log_date, name.strip(), calories, protein, carbs, fats, fiber, meal)
        st.toast("Meal saved.")
        st.rerun()


@st.dialog("Log weight")
def weight_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_weight_date")
    weight = st.number_input("Weight kg", 0.0, 300.0, 80.0, step=0.1, format="%.1f", key="ql_weight_kg")
    waist = st.number_input("Waist inches optional", 0.0, 100.0, 0.0, step=0.1, key="ql_waist")

    if st.button("Save weight", type="primary", width="stretch"):
        if weight <= 0:
            st.warning("Enter a weight above zero.")
            return
        database.add_measurement(log_date, weight, waist or None)
        st.toast("Weight saved.")
        st.rerun()


@st.dialog("Log activity")
def steps_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_steps_date")
    steps = st.number_input("Steps", 0, 100000, 8000, step=500, key="ql_steps")
    distance = round(steps * 0.00076, 2)
    active_minutes = round(steps / 100, 0)
    st.caption(f"Estimated distance: {distance} km | active minutes: {int(active_minutes)}")

    if st.button("Save activity", type="primary", width="stretch"):
        database.add_steps(log_date.isoformat(), steps, distance, active_minutes)
        st.toast("Activity saved.")
        st.rerun()


@st.dialog("Daily check-in")
def checkin_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_checkin_date")
    c1, c2, c3 = st.columns(3)
    mood = c1.slider("Mood", 1, 5, 3, key="ql_mood")
    energy = c2.slider("Energy", 1, 5, 3, key="ql_energy")
    sleep = c3.number_input("Sleep hours", 0.0, 16.0, 7.0, step=0.25, key="ql_sleep")
    note = st.text_area("Note", placeholder="How did today feel?", key="ql_note")

    if st.button("Save check-in", type="primary", width="stretch"):
        database.add_checkin(log_date.isoformat(), mood, energy, sleep, note.strip())
        st.toast("Check-in saved.")
        st.rerun()


def render_quick_actions():
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("Workout", type="primary", width="stretch"):
        workout_dialog()
    if c2.button("Meal", width="stretch"):
        meal_dialog()
    if c3.button("Weight", width="stretch"):
        weight_dialog()
    if c4.button("Activity", width="stretch"):
        steps_dialog()
    if c5.button("Check-in", width="stretch"):
        checkin_dialog()
