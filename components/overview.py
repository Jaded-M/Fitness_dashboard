from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.design_system import insight_card, stat_card
from services.health_data import HealthSnapshot, daily_nutrition, daily_steps, kpi_summary, weekly_report, weight_trend


CHART_CONFIG = {"displayModeBar": False, "responsive": True}


def _layout(height=330):
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": "#9aa7b8"},
        "margin": {"l": 10, "r": 10, "t": 30, "b": 10},
        "xaxis": {"showgrid": False, "zeroline": False},
        "yaxis": {"gridcolor": "rgba(148, 163, 184, 0.16)", "zeroline": False},
        "hoverlabel": {"bgcolor": "#111827", "font_color": "#ffffff"},
    }


def render_kpis(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    summary = kpi_summary(snapshot, calorie_goal, step_goal)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Today calories", f"{summary['today_calories']:,}", f"Goal {calorie_goal:,} kcal")
    with c2:
        stat_card("Today protein", f"{summary['today_protein']}g", "Fuel for training")
    with c3:
        stat_card("Today steps", f"{summary['today_steps']:,}", f"Goal {step_goal:,}")
    with c4:
        value = f"{summary['latest_weight']:.1f} kg" if summary["latest_weight"] else "No log"
        delta = summary["weight_delta"]
        caption = "Start logging weight" if delta is None else f"{delta:+.1f} kg across records"
        stat_card("Latest weight", value, caption)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Training days", summary["sessions_7d"], "last 7 days")
    with c6:
        st.metric("Weekly volume", f"{summary['weekly_volume']:,}", "kg x reps")
    with c7:
        st.metric("Calorie adherence", f"{summary['calorie_adherence']}%", "last 7 logged days")
    with c8:
        st.metric("Activity score", f"{summary['activity_score']}%", f"{summary['avg_steps']:,} avg steps")


def render_intelligence_strip(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    summary = kpi_summary(snapshot, calorie_goal, step_goal)
    report = weekly_report(snapshot, calorie_goal, step_goal)
    reasons = ", ".join(summary["readiness_parts"]) if summary["readiness_parts"] else "more logged data needed"

    c1, c2, c3 = st.columns([1, 1.2, 1.2])
    with c1:
        stat_card("Readiness", f"{summary['readiness']}%", f"{summary['readiness_label']} | {reasons}")
    with c2:
        insight_card("Weekly report", report["training"] + " | " + report["nutrition"], "good" if summary["readiness"] >= 70 else "")
    with c3:
        insight_card("Next best action", next_best_action(summary, calorie_goal, step_goal), "warn" if summary["readiness"] < 55 else "good")


def next_best_action(summary: dict, calorie_goal: int, step_goal: int) -> str:
    if summary["today_protein"] < 90:
        return "Log or eat a protein-forward meal next."
    if summary["today_steps"] < step_goal:
        return f"Add {step_goal - summary['today_steps']:,} steps to close the activity loop."
    if summary["sessions_7d"] < 3:
        return "Schedule one focused workout this week."
    if summary["today_calories"] == 0:
        return "Log the first meal so nutrition insights become accurate."
    return "Maintain the current rhythm and log a quick daily check-in."


def render_insights(snapshot: HealthSnapshot, calorie_goal: int, step_goal: int):
    summary = kpi_summary(snapshot, calorie_goal, step_goal)

    if summary["today_protein"] < 90:
        insight_card("Nutrition signal", "Protein is light today. Add a high-protein meal before the day closes.", "warn")
    else:
        insight_card("Nutrition signal", "Protein is in a strong range today. Keep meals boringly consistent.", "good")

    if summary["sessions_7d"] >= 3:
        insight_card("Training signal", "Training frequency is solid this week. Focus on quality progression, not more clutter.", "good")
    else:
        insight_card("Training signal", "You have room for one more focused session this week.", "warn")

    if summary["today_steps"] >= step_goal:
        insight_card("Activity signal", "Step target is already handled today. Good base activity.", "good")
    else:
        remaining = max(step_goal - summary["today_steps"], 0)
        insight_card("Activity signal", f"{remaining:,} steps left to hit today's movement target.", "")


def render_weight_chart(snapshot: HealthSnapshot, key: str = "weight_trend_chart"):
    df = weight_trend(snapshot)
    if df.empty:
        st.info("Log weight to unlock the trend chart.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Weight"],
            mode="markers",
            name="Daily weight",
            marker={"size": 8, "color": "rgba(37, 99, 235, 0.45)"},
            hovertemplate="%{x|%d %b}<br>%{y:.1f} kg<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Trend"],
            mode="lines",
            name="Smoothed trend",
            line={"color": "#f8fafc", "width": 3},
            hovertemplate="%{x|%d %b}<br>Trend %{y:.1f} kg<extra></extra>",
        )
    )
    fig.update_layout(**_layout(), title="Weight trend")
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_nutrition_chart(snapshot: HealthSnapshot, calorie_goal: int, key: str = "nutrition_adherence_chart"):
    df = daily_nutrition(snapshot)
    if df.empty:
        st.info("Log meals to see calorie and protein trends.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Calories"],
            name="Calories",
            marker_color="rgba(37, 99, 235, 0.32)",
            hovertemplate="%{x|%d %b}<br>%{y:,} kcal<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Protein"],
            name="Protein",
            yaxis="y2",
            mode="lines+markers",
            line={"color": "#059669", "width": 3},
            marker={"size": 7},
            hovertemplate="%{x|%d %b}<br>%{y}g protein<extra></extra>",
        )
    )
    fig.add_hline(y=calorie_goal, line_dash="dot", line_color="#d97706")
    layout = _layout()
    layout.update(
        title="Nutrition adherence",
        yaxis={"title": "Calories", "gridcolor": "rgba(148, 163, 184, 0.16)", "zeroline": False},
        yaxis2={"title": "Protein", "overlaying": "y", "side": "right", "showgrid": False},
        legend={"orientation": "h", "y": 1.05, "x": 0},
    )
    fig.update_layout(**layout)
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_steps_chart(snapshot: HealthSnapshot, step_goal: int, key: str = "activity_trend_chart"):
    df = daily_steps(snapshot)
    if df.empty:
        st.info("Log steps to see activity trends.")
        return

    colors = ["#059669" if steps >= step_goal else "#94a3b8" for steps in df["Steps"]]
    fig = go.Figure(
        go.Bar(
            x=df["Date"],
            y=df["Steps"],
            marker_color=colors,
            hovertemplate="%{x|%d %b}<br>%{y:,} steps<extra></extra>",
        )
    )
    fig.add_hline(y=step_goal, line_dash="dot", line_color="#2563eb")
    fig.update_layout(**_layout(), title="Activity trend")
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def render_training_table(snapshot: HealthSnapshot, key: str = "training_history_table"):
    if snapshot.workouts.empty:
        st.info("Log workouts to build your progression history.")
        return
    cols = ["Date", "Split", "Workout", "Sets", "Reps", "Weight"]
    df = snapshot.workouts[cols].copy().head(20)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d %b %Y")
    st.dataframe(df, width="stretch", hide_index=True, key=key)


def render_checkins(snapshot: HealthSnapshot, key: str = "checkins_table"):
    if snapshot.checkins.empty:
        st.info("Use daily check-ins to connect mood, sleep, and performance.")
        return
    df = snapshot.checkins.head(12).copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y")
    df = df.rename(columns={"date": "Date", "mood": "Mood", "energy": "Energy", "sleep_hours": "Sleep", "note": "Note"})
    st.dataframe(df[["Date", "Mood", "Energy", "Sleep", "Note"]], width="stretch", hide_index=True, key=key)
