from __future__ import annotations

import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import database
from components.design_system import apply_platform_theme, page_header
from components.widgets import calculate_logging_streak
from components.overview import (
    render_activity_sync_panel,
    render_recovery_matrix,
    render_secondary_layer,
    render_steps_chart,
    render_training_table,
    render_weight_chart,
    render_workout_progression,
)
from components.quick_log import render_quick_actions
from core.spotify import render_spotify_widget
from services.google_fit import sync_google_fit_data
from services.health_data import kpi_summary, load_snapshot


st.set_page_config(
    page_title="Personal Health Intelligence",
    page_icon="PHI",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_platform_theme()
render_spotify_widget()

st.markdown(
    """
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#008fb3">
    """,
    unsafe_allow_html=True
)


def _save_exercise_library(library: dict) -> None:
    """Write the updated exercise library back to JSON."""
    import json
    with open("exercise_library.json", "w", encoding="utf-8") as file:
        json.dump(library, file, indent=4)


def _progress_bar(label: str, value: int, goal: int, caption: str = "") -> None:
    pct = min(max(value / max(goal, 1), 0), 1)
    tone = " warn" if value > goal * 1.08 and "calorie" in label.lower() else ""
    st.sidebar.markdown(
        f"""
        <div class="phi-sidebar-card compact">
            <div class="phi-sidebar-row" style="margin-top:0">
                <div class="phi-label">{label}</div>
                <div class="phi-sidebar-status">{int(pct * 100)}%</div>
            </div>
            <div class="phi-sidebar-kpi">{value:,}<small>/ {goal:,}</small></div>
            <div class="phi-sidebar-progress{tone}"><span style="width:{int(pct * 100)}%"></span></div>
            <div class="phi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _today_water() -> int:
    water_df = database.get_water_history()
    if water_df.empty or "date" not in water_df.columns:
        return 0
    water = water_df.copy()
    water["date"] = pd.to_datetime(water["date"], errors="coerce").dt.date
    return int(water.loc[water["date"] == datetime.date.today(), "cups"].sum())


def _auto_sync_steps():
    """Auto-sync Google Fit data on app load (runs once per session)."""
    if "auto_synced" not in st.session_state:
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.Timedelta(days=7)
        sync_google_fit_data(start_date, end_date)
        st.session_state["auto_synced"] = True


def _page_path(pattern: str) -> str:
    match = next(Path("pages").glob(pattern), None)
    return match.as_posix() if match else pattern


def render_landing_sidebar() -> None:
    """Main-page navigation without experimental pages."""
    st.sidebar.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
            .phi-main-nav-title {
                color: var(--blue);
                font-size: 0.65rem;
                font-weight: 800;
                letter-spacing: 0.14em;
                margin: 0.9rem 0 0.4rem;
                text-transform: uppercase;
            }
        </style>
        <div class="phi-sidebar-brand">
            <div class="phi-sidebar-logo">PHI</div>
            <div>
                <div class="phi-sidebar-title">Personal Health Intelligence</div>
                <div class="phi-sidebar-subtitle">Training, nutrition, and recovery</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="phi-main-nav-title">Navigation</div>', unsafe_allow_html=True)
    nav_items = [
        ("Fitness.py", "Command Center", "Today and training intelligence"),
        (_page_path("1_Nutrition.py"), "Nutrition", "Calories, macros, hydration"),
        (_page_path("2_Muscle_Atlas.py"), "Muscle Atlas", "Mapping and recovery"),
        (_page_path("4_PR_Tracker.py"), "PR Tracker", "Records and overload"),
    ]
    for path, label, caption in nav_items:
        active_class = " active" if path == "Fitness.py" else ""
        st.sidebar.markdown(
            f'<div class="phi-nav-hint{active_class}"><span>{caption}</span></div>',
            unsafe_allow_html=True,
        )
        st.sidebar.page_link(path, label=label)


def sidebar_settings(snapshot=None):
    render_landing_sidebar()

    st.sidebar.markdown('<div class="phi-sidebar-section">Goals</div>', unsafe_allow_html=True)
    with st.sidebar.expander("Configure goals & window", expanded=False):
        calorie_goal = st.number_input("Daily calorie goal", 1000, 6000, 2300, step=50)
        step_goal = st.number_input("Daily step goal", 1000, 30000, 8000, step=500)
        target_weight = st.number_input("Target weight (kg)", 40.0, 150.0, 72.1, step=0.1)
        window = st.selectbox("Analysis window", [30, 60, 90, 180], index=2)

    st.sidebar.markdown('<div class="phi-sidebar-section">Library</div>', unsafe_allow_html=True)
    with st.sidebar.expander("Manage Exercise Library", expanded=False):
        import json
        with open("exercise_library.json", "r", encoding="utf-8") as f:
            exercise_library = json.load(f)

        all_splits = list(exercise_library.keys())
        st.markdown('<div class="phi-form-label">Add exercise</div>', unsafe_allow_html=True)
        new_exercise = st.text_input("Exercise name", placeholder="e.g. Incline Press", key="lib_new_ex")
        new_split = st.selectbox("To split", all_splits, key="lib_new_split")
        if st.button("Add", key="lib_add_btn", type="primary"):
            clean_name = new_exercise.strip()
            if clean_name:
                library = {key: list(dict.fromkeys(value)) for key, value in exercise_library.items()}
                if clean_name not in library[new_split]:
                    library[new_split].append(clean_name)
                    _save_exercise_library(library)
                    st.toast(f'"{clean_name}" added to {new_split}.')
                    st.rerun()
                else:
                    st.warning("Already in that split.")
            else:
                st.warning("Enter an exercise name.")

        st.markdown('<div class="phi-form-label">Remove exercise</div>', unsafe_allow_html=True)
        delete_split = st.selectbox("From split", all_splits, key="lib_del_split")
        split_exercises = list(dict.fromkeys(exercise_library.get(delete_split, [])))
        if split_exercises:
            delete_exercise = st.selectbox("Exercise to remove", split_exercises, key="lib_del_ex")
            if st.button("Remove", key="lib_del_btn"):
                library = {key: list(dict.fromkeys(value)) for key, value in exercise_library.items()}
                library[delete_split] = [exercise for exercise in library[delete_split] if exercise != delete_exercise]
                _save_exercise_library(library)
                st.toast(f'"{delete_exercise}" removed.')
                st.rerun()
        else:
            st.caption("No exercises in this split yet.")

    try:
        return calorie_goal, step_goal, target_weight, window
    except UnboundLocalError:
        return (
            st.session_state.get("calorie_goal", 2300),
            st.session_state.get("step_goal", 8000),
            st.session_state.get("target_weight", 72.1),
            st.session_state.get("window", 90),
        )


def render_sidebar_command(snapshot, summary, calorie_goal: int, step_goal: int) -> None:
    readiness = summary["readiness_report"]
    score = int(readiness.get("score", 0))
    tone = "good" if score >= 68 else "warn" if score >= 45 else "risk"

    st.sidebar.markdown('<div class="phi-sidebar-section">Today</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f"""
        <div class="phi-sidebar-card">
            <div class="phi-sidebar-row" style="margin-top:0">
                <div>
                    <div class="phi-label">Readiness</div>
                    <div class="phi-sidebar-kpi">{score}%</div>
                </div>
                <div class="phi-sidebar-status {tone}">{readiness.get('label', 'Status')}</div>
            </div>
            <div class="phi-caption">{readiness.get('key_action', readiness.get('recommended_split', 'Log today to calibrate.'))}</div>
            <div class="phi-sidebar-mini-grid">
                <div class="phi-sidebar-mini">
                    <div class="phi-label">Training</div>
                    <div class="phi-sidebar-kpi">{readiness.get('training_load_score', 0)}<small>%</small></div>
                </div>
                <div class="phi-sidebar-mini">
                    <div class="phi-label">Recovery</div>
                    <div class="phi-sidebar-kpi">{readiness.get('recovery_score', 0)}<small>%</small></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _progress_bar("Calories", summary["today_calories"], calorie_goal, "Food logged today")
    _progress_bar("Steps", summary["today_steps"], step_goal, "Activity progress today")

    water_goal = int(st.session_state.get("water_goal", 10))
    water_cups = _today_water()
    _progress_bar("Hydration", water_cups, water_goal, "Water intake today")
    h1, h2 = st.sidebar.columns(2)
    if h1.button("+1 cup", key="sidebar_water_one", use_container_width=True):
        database.log_water(datetime.date.today(), 1)
        st.rerun()
    if h2.button("+2 cups", key="sidebar_water_two", use_container_width=True):
        database.log_water(datetime.date.today(), 2)
        st.rerun()

    with st.sidebar.expander("Daily check-in", expanded=False):
        mood = st.slider("Mood", 1, 5, 3, key="sidebar_mood")
        energy = st.slider("Energy", 1, 5, 3, key="sidebar_energy")
        sleep = st.number_input("Sleep hours", 0.0, 14.0, 7.0, 0.25, key="sidebar_sleep")
        note = st.text_area("Note", placeholder="Optional context", key="sidebar_note")
        if st.button("Save check-in", key="sidebar_checkin_save", type="primary", use_container_width=True):
            database.add_checkin(datetime.date.today(), mood, energy, sleep, note.strip())
            st.toast("Check-in saved.")
            st.rerun()

def _workout_logged_today(snapshot) -> bool:
    if snapshot.workouts.empty or "Date" not in snapshot.workouts.columns:
        return False
    real = snapshot.workouts
    if "Workout" in real.columns:
        real = real[real["Workout"] != "Session Duration"]
    return bool((real["Date"].dt.date == datetime.date.today()).any())


def render_hero(summary: dict, readiness: dict, streak: int, snapshot=None, water_df=None) -> None:
    readiness_tone = "good" if readiness["score"] >= 68 else "warn" if readiness["score"] >= 45 else "risk"
    today_label = datetime.datetime.now().strftime("%A, %d %B")

    last_session = ""
    if snapshot is not None and snapshot.workouts is not None and not snapshot.workouts.empty:
        df = snapshot.workouts.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        last_row = df.loc[df["Date"].idxmax()]
        name = last_row["Workout"]
        days = (datetime.date.today() - last_row["Date"].date()).days
        when = "Today" if days == 0 else "Yesterday" if days == 1 else f"{days} days ago"
        last_session = f"{name} · {when}"

    st.markdown(
        f"""
        <section class="phi-home-hero">
            <div class="phi-home-hero-copy">
                <div>
                    <div class="phi-home-kicker">{today_label}</div>
                    <h2><span class="phi-typewriter"></span><span class="phi-cursor">█</span></h2>
                </div>
                <p>{readiness.get('key_action', 'Log today to keep training, nutrition, and recovery calibrated.')}</p>
            </div>
            <div class="phi-hero-grid">
                <div class="phi-hero-card calories">
                    <div class="phi-label">Calories logged</div>
                    <div class="phi-hero-value">{summary['today_calories']:,}</div>
                    <div class="phi-caption">{summary['today_protein']}g protein today</div>
                </div>
                <div class="phi-hero-card steps">
                    <div class="phi-label">Steps</div>
                    <div class="phi-hero-value">{summary['today_steps']:,}</div>
                    <div class="phi-caption">Activity progress today</div>
                </div>
                <div class="phi-hero-card streak">
                    <div class="phi-label">Logging streak</div>
                    <div class="phi-hero-value">{streak}</div>
                    <div class="phi-caption">Consecutive days</div>
                </div>
            </div>
            <div class="phi-hero-grid-bottom">
                <div class="phi-hero-card last-session">
                    <div class="phi-label">Last session</div>
                    <div class="phi-hero-value">{last_session}</div>
                    <div class="phi-caption">Most recent workout</div>
                </div>
                <div class="phi-hero-card {readiness_tone}">
                    <div class="phi-label">Readiness</div>
                    <div class="phi-hero-value">{readiness['score']}%</div>
                    <div class="phi-caption">{readiness.get('label', 'Status')}</div>
                </div>
            </div>
        </section>
        <style>
            .phi-home-hero {{
                position: relative;
                overflow: hidden;
                margin: 0.25rem 0 1.2rem;
                padding: 1.35rem;
                border: 1px solid var(--line);
                border-radius: var(--radius-lg);
                background: var(--panel);
            }}
            .phi-home-hero-copy {{
                display: flex;
                align-items: end;
                justify-content: space-between;
                gap: 1rem;
                margin-bottom: 1rem;
            }}
            .phi-home-kicker {{
                color: var(--muted);
                font-size: 0.72rem;
                font-weight: 700;
                letter-spacing: 0.10em;
                text-transform: uppercase;
            }}
            .phi-home-hero h2 {{
                margin: 0.2rem 0 0;
                color: var(--green);
                font-family: var(--font-display);
                font-size: clamp(1.6rem, 3.5vw, 2.8rem);
                font-weight: 800;
                line-height: 1.05;
            }}
            .phi-home-hero p {{
                max-width: 400px;
                margin: 0;
                color: var(--muted);
                font-size: 0.85rem;
                line-height: 1.5;
            }}
            .phi-hero-grid {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.75rem;
            }}
            .phi-hero-card {{
                padding: 1.1rem 1.25rem;
                border: 1px solid rgba(0, 204, 136, 0.10);
                border-radius: var(--radius);
                background: var(--panel-2);
            }}
            .phi-hero-grid-bottom {{
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.75rem;
                margin-top: 0.75rem;
            }}
            .phi-hero-card.calories {{ border-left: 3px solid var(--orange); }}
            .phi-hero-card.steps {{ border-left: 3px solid var(--green); }}
            .phi-hero-card.good {{ border-left: 3px solid var(--green); }}
            .phi-hero-card.warn {{ border-left: 3px solid var(--amber); }}
            .phi-hero-card.risk {{ border-left: 3px solid var(--rose); }}
            .phi-hero-card.streak {{ border-left: 3px solid var(--muted); }}
            .phi-hero-card.last-session {{ border-left: 3px solid var(--green); }}
            .phi-hero-value {{
                margin: 0.35rem 0 0.15rem;
                color: var(--green);
                font-family: 'JetBrains Mono', monospace;
                font-size: clamp(1.6rem, 3vw, 2.4rem);
                font-weight: 750;
                letter-spacing: -0.02em;
                line-height: 1;
            }}
            .phi-hero-value small {{ font-size: 0.6em; color: var(--muted); }}
            @media (max-width: 980px) {{
                .phi-hero-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
                .phi-hero-grid-bottom {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
                .phi-home-hero-copy {{ align-items: start; flex-direction: column; }}
            }}
            @media (max-width: 640px) {{
                .phi-hero-grid {{ grid-template-columns: 1fr; }}
                .phi-hero-grid-bottom {{ grid-template-columns: 1fr; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ── Load data once ────────────────────────────────────────────────────────────
with st.spinner("Loading your health data…"):
    _auto_sync_steps()
    calorie_goal, step_goal, target_weight, window = sidebar_settings()
    snapshot = load_snapshot(days=window)

summary = kpi_summary(snapshot, calorie_goal, step_goal, target_weight)
readiness = summary["readiness_report"]
workout_today = _workout_logged_today(snapshot)
render_sidebar_command(snapshot, summary, calorie_goal, step_goal)

# ── Page body ─────────────────────────────────────────────────────────────────

# ── Page body ─────────────────────────────────────────────────────────────────
page_header(
    "Personal Health Intelligence",
    "A focused command center for today's training, nutrition, recovery, and activity.",
)

# Calculate logging streak across workouts, food, and water logs
water_df = database.get_water_history()
streak = calculate_logging_streak(snapshot.workouts, snapshot.food, water_df)

# Render hero
render_hero(summary, readiness, streak, snapshot, water_df)

st.components.v1.html(
    """
    <script>
    (function(){
        var el = parent.document.querySelector('.phi-typewriter');
        if(!el)return;
        var P=["Today's command center","PHI · All systems nominal","Calibrating readiness\u2026","Ready. Let's train."];
        var i=0,j=0,d=1,S;
        function T(){
            var s=P[i];
            if(d===1){
                if(j<s.length){j++;el.textContent=s.slice(0,j);S=setTimeout(T,45+Math.random()*55);}
                else{el.textContent=s;d=-1;S=setTimeout(T,2500);}
            }else{
                if(j>0){j--;el.textContent=s.slice(0,j);S=setTimeout(T,20+Math.random()*25);}
                else{d=1;i=(i+1)%P.length;el.textContent='';S=setTimeout(T,400);}
            }
        }
        setTimeout(T,1200);
    })();
    </script>
    """,
    height=0,
)


overview, training, recovery, body_activity = st.tabs(
    ["Overview", "Training", "Recovery", "Body & Activity"]
)
render_secondary_layer(snapshot, calorie_goal, step_goal)

with training:
    st.subheader("Training progression")
    render_workout_progression(snapshot, key_prefix="training_tab")
    st.markdown("---")
    st.subheader("Recent log")
    render_training_table(snapshot, key="training_detail_table")

with recovery:
    render_recovery_matrix(snapshot, calorie_goal, step_goal, key="recovery_matrix_detail")

with body_activity:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Body composition signal")
        render_weight_chart(snapshot, key="body_weight_chart")
    with c2:
        st.subheader("Activity signal")
        render_steps_chart(snapshot, step_goal, key="activity_detail_chart")
    st.markdown("---")
    render_activity_sync_panel(snapshot, step_goal, sync_google_fit_data)
