import streamlit as st
from components.design_system import apply_platform_theme
from components.pr_tracker import render_pr_board, render_overload_status, render_1rm_chart
import database

st.set_page_config(
    page_title="PR Tracker & Overload",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_platform_theme()

st.markdown(
    """
    <div class="phi-page-head">
        <div>
            <div class="phi-eyebrow">Performance</div>
            <h1 style="margin:0; padding:0;">PRs & Overload</h1>
            <div class="phi-subtitle">Track your all-time heaviest lifts and monitor your session-to-session progressive overload.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    render_pr_board()

with col2:
    render_overload_status()
    
    st.markdown(
        """
        <div class="phi-section">
            <div class="phi-section-title">1RM Progression Explorer</div>
            <div class="phi-section-caption">Select an exercise to view your estimated 1 Rep Max over time.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Get all exercises that have been logged
    workouts = database.get_all_workouts()
    if not workouts.empty:
        exercises = sorted(workouts[workouts["exercise"] != "Session Duration"]["exercise"].unique())
        if exercises:
            selected_ex = st.selectbox("Select Exercise", exercises, label_visibility="collapsed")
            if selected_ex:
                render_1rm_chart(selected_ex)

