"""Reusable non-AI dashboard widgets for PHI."""
from __future__ import annotations

import datetime
import math

import pandas as pd
import streamlit as st


def render_readiness_ring(score: int, label: str) -> None:
    """Animated SVG readiness ring."""
    if score >= 75:
        color, glow, accent = "#2f9f68", "rgba(47,159,104,0.26)", "#197f96"
    elif score >= 50:
        color, glow, accent = "#c98a18", "rgba(201,138,24,0.26)", "#cf7240"
    else:
        color, glow, accent = "#d95f5f", "rgba(217,95,95,0.26)", "#7469c9"

    radius = 56
    center = 76
    circumference = 2 * math.pi * radius
    dash_offset = circumference * (1 - min(max(score, 0), 100) / 100)
    inner_radius = 43
    inner_circumference = 2 * math.pi * inner_radius
    inner_offset = inner_circumference * (1 - min(max(score, 0), 100) / 100)

    st.markdown(
        f"""
        <div class="phi-ring-wrap">
            <svg class="phi-ring" width="176" height="176" viewBox="0 0 152 152"
                 style="filter:drop-shadow(0 0 18px {glow});">
                <defs>
                    <radialGradient id="phiRingCore" cx="50%" cy="45%" r="58%">
                        <stop offset="0%" stop-color="rgba(255,255,255,0.72)"/>
                        <stop offset="58%" stop-color="rgba(47,159,104,0.08)"/>
                        <stop offset="100%" stop-color="rgba(237,243,238,0.28)"/>
                    </radialGradient>
                    <linearGradient id="phiRingGradient" x1="10%" y1="10%" x2="90%" y2="90%">
                        <stop offset="0%" stop-color="{accent}"/>
                        <stop offset="52%" stop-color="{color}"/>
                        <stop offset="100%" stop-color="#17201c"/>
                    </linearGradient>
                    <filter id="phiRingGlow">
                        <feGaussianBlur stdDeviation="3.5" result="blur"/>
                        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                    </filter>
                </defs>
                <circle cx="{center}" cy="{center}" r="66" fill="url(#phiRingCore)"
                        stroke="rgba(35,49,43,0.08)" stroke-width="1"/>
                <circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="rgba(35,49,43,0.08)" stroke-width="8"/>
                <circle cx="{center}" cy="{center}" r="{radius}" fill="none" stroke="url(#phiRingGradient)" 
                        stroke-width="8" stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
                        stroke-linecap="round" style="transform-origin: 50% 50%; transform: rotate(-90deg); filter: url(#phiRingGlow); animation: phi-ring-draw 1.2s cubic-bezier(0.1, 0.8, 0.2, 1) forwards;"/>
                <circle cx="{center}" cy="{center}" r="{inner_radius}" fill="none" stroke="rgba(35,49,43,0.08)" stroke-width="2"/>
                <circle cx="{center}" cy="{center}" r="{inner_radius}" fill="none" stroke="{accent}" 
                        stroke-width="3" stroke-dasharray="{inner_circumference}" stroke-dashoffset="{inner_offset}"
                        stroke-linecap="round" style="transform-origin: 50% 50%; transform: rotate(90deg); opacity:0.8; animation: phi-ring-draw 1.6s cubic-bezier(0.1, 0.8, 0.2, 1) forwards;"/>
                <g opacity="0.72" stroke="rgba(35,49,43,0.20)" stroke-width="1.2">
                    <line x1="{center}" y1="10" x2="{center}" y2="18"/>
                    <line x1="{center}" y1="134" x2="{center}" y2="142"/>
                    <line x1="10" y1="{center}" x2="18" y2="{center}"/>
                    <line x1="134" y1="{center}" x2="142" y2="{center}"/>
                </g>
                <circle cx="{center}" cy="{center}" r="31" fill="rgba(255,255,255,0.72)"
                        stroke="rgba(35,49,43,0.10)" stroke-width="1"/>
                <text x="{center}" y="{center - 8}" text-anchor="middle" dominant-baseline="central"
                      fill="{color}" font-size="22" font-weight="850"
                      font-family="Space Grotesk,Manrope,sans-serif">{score}%</text>
                <text x="{center}" y="{center + 15}" text-anchor="middle" dominant-baseline="central"
                      fill="#8f9aad" font-size="8.5" font-weight="800"
                      font-family="Manrope,sans-serif" letter-spacing="0.12em">READINESS</text>
            </svg>
            <div>
                <div class="phi-label">Today's status</div>
                <div class="phi-ring-label">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def compute_active_streak(
    workout_df: pd.DataFrame,
    steps_df: pd.DataFrame,
    step_goal: int = 8000,
    steps_min_pct: float = 0.50,
) -> dict:
    """Calculate a streak that counts workout days and active-rest days."""
    today = datetime.date.today()
    steps_min = int(step_goal * steps_min_pct)

    step_lookup: dict[datetime.date, int] = {}
    if not steps_df.empty and "date" in steps_df.columns:
        steps = steps_df.copy()
        steps["date"] = pd.to_datetime(steps["date"]).dt.date
        step_lookup = steps.groupby("date")["steps"].sum().to_dict()

    gym_days: set[datetime.date] = set()
    if not workout_df.empty and "Date" in workout_df.columns:
        workouts = workout_df.copy()
        workouts["Date"] = pd.to_datetime(workouts["Date"], errors="coerce").dt.date
        gym_days = set(workouts["Date"].dropna())

    def day_level(day: datetime.date) -> int:
        if day in gym_days:
            return 3
        day_steps = step_lookup.get(day, 0)
        if day_steps >= step_goal:
            return 2
        if day_steps >= steps_min:
            return 1
        return 0

    streak = 0
    flame_sum = 0
    cursor = today
    while True:
        level = day_level(cursor)
        if level == 0:
            break
        streak += 1
        flame_sum += level
        cursor -= datetime.timedelta(days=1)
        if streak > 365:
            break

    today_level = day_level(today)
    type_map = {3: "Workout day", 2: "Active rest", 1: "Light activity", 0: "Rest day"}
    return {
        "streak": streak,
        "flame_level": today_level,
        "avg_flame": flame_sum / streak if streak else 0.0,
        "today_qualifies": today_level > 0,
        "today_type": type_map[today_level],
    }


def render_streak_card(
    workout_df: pd.DataFrame,
    steps_df: pd.DataFrame,
    step_goal: int = 8000,
) -> None:
    """Render a compact streak card with no external calls."""
    data = compute_active_streak(workout_df, steps_df, step_goal)
    streak = data["streak"]
    flame_level = data["flame_level"]
    today_type = data["today_type"]

    badge = ""
    if streak >= 30:
        badge = "30-day rhythm"
    elif streak >= 14:
        badge = "2-week rhythm"
    elif streak >= 7:
        badge = "1-week rhythm"

    intensity = ["Rest", "Light", "Active", "Training"][flame_level]
    tone = ["", "warn", "good", "risk"][flame_level]
    st.markdown(
        f"""
        <div class="phi-mini-widget {tone}">
            <div>
                <div class="phi-label">Active streak</div>
                <div class="phi-widget-value">{streak}<span>days</span></div>
                <div class="phi-caption">{today_type}{' / ' + badge if badge else ''}</div>
            </div>
            <div class="phi-widget-orb">{intensity}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_water_widget(goal: int = 10) -> None:
    """Render today's hydration status without external services."""
    import database

    today = datetime.date.today()
    water_df = database.get_water_history()
    cups = 0
    if not water_df.empty and "date" in water_df.columns:
        water = water_df.copy()
        water["date"] = pd.to_datetime(water["date"], errors="coerce").dt.date
        cups = int(water.loc[water["date"] == today, "cups"].sum())

    filled = min(max(cups, 0), goal)
    bars = "".join(
        f'<span class="{"filled" if index < filled else ""}"></span>'
        for index in range(goal)
    )
    tone = "good" if cups >= goal else "warn" if cups >= goal * 0.6 else ""
    st.markdown(
        f"""
        <div class="phi-mini-widget {tone}">
            <div>
                <div class="phi-label">Hydration</div>
                <div class="phi-widget-value">{cups}<span>/ {goal} cups</span></div>
                <div class="phi-caption">Today water intake</div>
            </div>
            <div class="phi-hydration-bars">{bars}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )




def check_new_pr(exercise: str, new_weight: float) -> None:
    """Toast when a just-logged lift exceeds the previous personal best."""
    import database

    prev_pr = database.get_personal_best(exercise)
    if prev_pr is not None and new_weight > prev_pr:
        st.toast(f"New PR on {exercise}: {new_weight:.1f} kg (was {prev_pr:.1f} kg)")
        st.balloons()


def render_kpi_strip(streak: int, water_cups: int, steps: int, readiness_score: int) -> None:
    """Horizontal 4-tile KPI strip for the top of the command center."""
    
    # Logic for styling and tone
    streak_tone = "good" if streak >= 3 else ""
    water_tone = "good" if water_cups >= 8 else ("warn" if water_cups >= 4 else "")
    step_tone = "good" if steps >= 10000 else ""
    readiness_tone = "good" if readiness_score >= 75 else ("warn" if readiness_score >= 50 else "risk")

    html = f"""
    <div class="phi-kpi-strip">
        <div class="phi-kpi-tile {streak_tone}">
            <div class="phi-kpi-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c-4 5-8 7-8 12a8 8 0 1 0 16 0c0-5-4-7-8-12z"/><path d="M12 2v6"/><path d="M16 12a4 4 0 0 1-8 0"/></svg>
            </div>
            <div>
                <div class="phi-kpi-title">Active Streak</div>
                <div class="phi-kpi-value">{streak}<span>days</span></div>
            </div>
        </div>
        <div class="phi-kpi-tile {water_tone}">
            <div class="phi-kpi-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/></svg>
            </div>
            <div>
                <div class="phi-kpi-title">Hydration</div>
                <div class="phi-kpi-value">{water_cups}<span>cups</span></div>
            </div>
        </div>
        <div class="phi-kpi-tile {step_tone}">
            <div class="phi-kpi-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13 4v16"/><path d="M17 4v16"/><path d="M19 4H5v16h14z"/></svg>
            </div>
            <div>
                <div class="phi-kpi-title">Steps Today</div>
                <div class="phi-kpi-value">{steps:,}<span>steps</span></div>
            </div>
        </div>
        <div class="phi-kpi-tile {readiness_tone}">
            <div class="phi-kpi-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
            <div>
                <div class="phi-kpi-title">Readiness</div>
                <div class="phi-kpi-value">{readiness_score}<span>%</span></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
def calculate_logging_streak(workouts_df: pd.DataFrame, food_df: pd.DataFrame, water_df: pd.DataFrame) -> int:
    """Return number of consecutive days (up to today or yesterday) with any log.
    A day counts if there is at least one entry in any of the provided dataframes.
    """
    # Extract date series from each dataframe, ensure they are datetime.date
    dates = set()
    if not workouts_df.empty and "Date" in workouts_df.columns:
        wk = workouts_df.copy()
        wk["Date"] = pd.to_datetime(wk["Date"], errors="coerce").dt.date
        dates.update(wk["Date"].dropna().unique())
    if not food_df.empty and "date" in food_df.columns:
        fd = food_df.copy()
        fd["date"] = pd.to_datetime(fd["date"], errors="coerce").dt.date
        dates.update(fd["date"].dropna().unique())
    if not water_df.empty and "date" in water_df.columns:
        wd = water_df.copy()
        wd["date"] = pd.to_datetime(wd["date"], errors="coerce").dt.date
        dates.update(wd["date"].dropna().unique())
    # Start streak from today, fallback to yesterday if today missing
    today = datetime.date.today()
    streak = 0
    cursor = today
    # If today has no entry, start from yesterday
    if cursor not in dates:
        cursor = today - datetime.timedelta(days=1)
    while cursor in dates:
        streak += 1
        cursor -= datetime.timedelta(days=1)
    return streak
