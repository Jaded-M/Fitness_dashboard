from __future__ import annotations

import streamlit as st

from components.design_system import apply_platform_theme, page_header
from components.overview import (
    render_checkins,
    render_intelligence_strip,
    render_insights,
    render_kpis,
    render_nutrition_chart,
    render_steps_chart,
    render_training_table,
    render_weight_chart,
)
from components.quick_log import render_quick_actions
from services.health_data import load_snapshot


st.set_page_config(
    page_title="Personal Health Intelligence",
    page_icon="PHI",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_platform_theme()


def sidebar_settings():
    st.sidebar.title("PHI")
    st.sidebar.caption("Personal Health Intelligence Platform")
    st.sidebar.divider()
    calorie_goal = st.sidebar.number_input("Daily calorie goal", 1000, 6000, 2300, step=50)
    step_goal = st.sidebar.number_input("Daily step goal", 1000, 30000, 8000, step=500)
    window = st.sidebar.selectbox("Analysis window", [30, 60, 90, 180], index=2)
    st.sidebar.divider()
    st.sidebar.caption("Phase 1 rebuild: premium shell, fast logging, and unified overview.")
    return calorie_goal, step_goal, window


calorie_goal, step_goal, window = sidebar_settings()
snapshot = load_snapshot(days=window)

page_header(
    "Your Health Command Center",
    "A cleaner, faster dashboard for body weight, nutrition, training, activity, and daily context.",
)

render_quick_actions()
st.markdown("")
render_intelligence_strip(snapshot, calorie_goal, step_goal)
st.markdown("")
render_kpis(snapshot, calorie_goal, step_goal)

overview, body, nutrition, training, activity, checkins = st.tabs(
    ["Overview", "Body", "Nutrition", "Training", "Activity", "Check-ins"]
)

with overview:
    i1, i2, i3 = st.columns(3)
    with i1:
        render_insights(snapshot, calorie_goal, step_goal)
    with i2:
        render_nutrition_chart(snapshot, calorie_goal, key="overview_nutrition_chart")
    with i3:
        render_steps_chart(snapshot, step_goal, key="overview_steps_chart")

with body:
    st.subheader("Body composition signal")
    render_weight_chart(snapshot, key="body_weight_chart")

with nutrition:
    st.subheader("Nutrition signal")
    render_nutrition_chart(snapshot, calorie_goal, key="nutrition_detail_chart")

with training:
    st.subheader("Training progression")
    render_training_table(snapshot, key="training_detail_table")

with activity:
    st.subheader("Activity signal")
    render_steps_chart(snapshot, step_goal, key="activity_detail_chart")

with checkins:
    st.subheader("Daily context")
    render_checkins(snapshot, key="checkins_detail_table")
