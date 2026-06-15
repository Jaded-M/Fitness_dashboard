from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import database
from core.readiness_engine import ReadinessInputs, calculate_readiness


@dataclass
class HealthSnapshot:
    workouts: pd.DataFrame
    food: pd.DataFrame
    steps: pd.DataFrame
    measurements: pd.DataFrame
    checkins: pd.DataFrame


def _workout_frame() -> pd.DataFrame:
    df = database.get_all_workouts()
    if df.empty:
        return df

    df = df.rename(
        columns={
            "id": "ID",
            "date": "Date",
            "split": "Split",
            "exercise": "Workout",
            "weight": "Weight",
            "sets": "Sets",
            "reps": "Reps",
        }
    )
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Weight", "Sets", "Reps", "rpe", "duration"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df.dropna(subset=["Date"])


def load_snapshot(days: int = 90) -> HealthSnapshot:
    database.init_db()
    end = date.today()
    start = end - timedelta(days=days)

    workouts = _workout_frame()
    food = database.get_food_logs()
    steps = database.get_steps_data(start.isoformat(), end.isoformat())
    measurements = database.get_measurements()
    checkins = database.get_checkins()

    if not food.empty:
        food["date"] = pd.to_datetime(food["date"], errors="coerce")
    if not steps.empty:
        steps["date"] = pd.to_datetime(steps["date"], errors="coerce")
    if not checkins.empty:
        checkins["date"] = pd.to_datetime(checkins["date"], errors="coerce")

    return HealthSnapshot(workouts, food, steps, measurements, checkins)


def today_totals(snapshot: HealthSnapshot) -> dict:
    today = pd.Timestamp(date.today())
    food = snapshot.food
    steps = snapshot.steps

    day_food = food[food["date"].dt.normalize() == today] if not food.empty else pd.DataFrame()
    day_steps = steps[steps["date"].dt.normalize() == today] if not steps.empty else pd.DataFrame()

    return {
        "calories": int(day_food["calories"].sum()) if not day_food.empty else 0,
        "protein": int(day_food["protein"].sum()) if not day_food.empty else 0,
        "steps": int(day_steps["steps"].sum()) if not day_steps.empty else 0,
    }


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def kpi_summary(snapshot: HealthSnapshot, calorie_goal: int = 2300, step_goal: int = 8000, target_weight: float = 72.1) -> dict:
    workouts = snapshot.workouts
    food = snapshot.food
    steps = snapshot.steps
    measurements = snapshot.measurements
    totals = today_totals(snapshot)

    real_workouts = workouts[workouts["Workout"] != "Session Duration"].copy() if not workouts.empty else pd.DataFrame()
    last_7 = pd.Timestamp(date.today() - timedelta(days=6))

    if not real_workouts.empty:
        week_workouts = real_workouts[real_workouts["Date"] >= last_7].copy()
        sessions_7d = week_workouts["Date"].dt.date.nunique()
        week_workouts.loc[:, "Volume"] = week_workouts["Weight"] * week_workouts["Reps"]
        weekly_volume = int(week_workouts["Volume"].sum())
    else:
        sessions_7d = 0
        weekly_volume = 0

    if not food.empty:
        recent_food = food[food["date"] >= last_7]
        daily_cals = recent_food.groupby(recent_food["date"].dt.date)["calories"].sum()
        calorie_adherence = int((daily_cals.between(calorie_goal * 0.85, calorie_goal * 1.08).mean() * 100)) if len(daily_cals) else 0
    else:
        calorie_adherence = 0

    if not steps.empty:
        recent_steps = steps[steps["date"] >= last_7]
        daily_steps = recent_steps.groupby(recent_steps["date"].dt.date)["steps"].sum()
        avg_steps = int(daily_steps.mean()) if len(daily_steps) else 0
        activity_score = int((daily_steps.ge(step_goal).mean() * 100)) if len(daily_steps) else 0
    else:
        avg_steps = 0
        activity_score = 0

    latest_weight = None
    weight_delta = None
    weekly_weight_change = None
    weight_trend_direction = "No trend"
    goal_eta = "Need more data"
    if not measurements.empty and "Weight" in measurements.columns:
        weights = measurements.sort_values("Date")
        valid = weights[weights["Weight"].notna() & (weights["Weight"] > 0)]
        if not valid.empty:
            latest_weight = float(valid["Weight"].iloc[-1])
            if len(valid) > 1:
                weight_delta = latest_weight - float(valid["Weight"].iloc[0])
                trend = valid[["Date", "Weight"]].copy()
                trend["Trend"] = trend["Weight"].rolling(window=7, min_periods=1).mean()
                if len(trend) >= 2:
                    days_between = max((trend["Date"].iloc[-1] - trend["Date"].iloc[0]).days, 1)
                    weekly_weight_change = ((trend["Trend"].iloc[-1] - trend["Trend"].iloc[0]) / days_between) * 7
                    if weekly_weight_change <= -0.15:
                        weight_trend_direction = "Trending down"
                    elif weekly_weight_change >= 0.15:
                        weight_trend_direction = "Trending up"
                    else:
                        weight_trend_direction = "Stable"
                    if latest_weight > target_weight and weekly_weight_change < -0.05:
                        weeks_left = int((latest_weight - target_weight) / abs(weekly_weight_change))
                        goal_eta = f"{weeks_left} week(s)"
                    elif latest_weight <= target_weight:
                        goal_eta = "Goal reached"

    readiness_report = readiness_summary(snapshot, calorie_goal, step_goal)
    readiness = readiness_report["score"]
    readiness_label = readiness_report["label"]
    readiness_parts = [
        f"recovery {readiness_report['recovery_score']}%",
        f"load {readiness_report['training_load_score']}%",
        f"fuel {readiness_report['nutrition_score']}%",
    ]

    return {
        "today_calories": totals["calories"],
        "today_protein": totals["protein"],
        "today_steps": totals["steps"],
        "sessions_7d": sessions_7d,
        "weekly_volume": weekly_volume,
        "calorie_adherence": calorie_adherence,
        "avg_steps": avg_steps,
        "activity_score": activity_score,
        "latest_weight": latest_weight,
        "weight_delta": weight_delta,
        "weekly_weight_change": weekly_weight_change,
        "weight_trend_direction": weight_trend_direction,
        "goal_eta": goal_eta,
        "readiness": readiness,
        "readiness_label": readiness_label,
        "readiness_parts": readiness_parts,
        "readiness_report": readiness_report,
    }


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def readiness_summary(snapshot: HealthSnapshot, calorie_goal: int = 2300, step_goal: int = 8000) -> dict:
    return calculate_readiness(
        ReadinessInputs(
            workouts=snapshot.workouts,
            food=snapshot.food,
            steps=snapshot.steps,
            checkins=snapshot.checkins,
            calorie_goal=calorie_goal,
            step_goal=step_goal,
        )
    )


def weekly_report(snapshot: HealthSnapshot, calorie_goal: int = 2300, step_goal: int = 8000, target_weight: float = 72.1) -> dict:
    summary = kpi_summary(snapshot, calorie_goal, step_goal, target_weight)
    readiness = summary["readiness_report"]
    return {
        "headline": f"{summary['readiness_label']} week at {summary['readiness']} readiness",
        "training": f"{summary['sessions_7d']} training day(s), {summary['weekly_volume']:,} kg x reps",
        "nutrition": f"{readiness['recovery_score']}% recovery, {summary['calorie_adherence']}% calorie adherence",
        "activity": f"{summary['avg_steps']:,} average steps, {summary['activity_score']}% target hit rate",
    }


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def habit_consistency(snapshot: HealthSnapshot, calorie_goal: int = 2300, step_goal: int = 8000, target_weight: float = 72.1) -> dict:
    summary = kpi_summary(snapshot, calorie_goal, step_goal, target_weight)
    logged_food_days = 0 if snapshot.food.empty else snapshot.food["date"].dt.date.nunique()
    logged_step_days = 0 if snapshot.steps.empty else snapshot.steps["date"].dt.date.nunique()
    logged_checkin_days = 0 if snapshot.checkins.empty else snapshot.checkins["date"].dt.date.nunique()

    return {
        "nutrition": summary["calorie_adherence"],
        "activity": summary["activity_score"],
        "training_days": summary["sessions_7d"],
        "logged_food_days": min(logged_food_days, 7),
        "logged_step_days": min(logged_step_days, 7),
        "logged_checkin_days": min(logged_checkin_days, 7),
    }


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def workout_highlights(snapshot: HealthSnapshot) -> dict:
    workouts = snapshot.workouts
    if workouts.empty:
        return {
            "best_lift": "No workouts yet",
            "top_exercise": "No pattern yet",
            "volume_note": "Log workouts to unlock progression.",
        }

    real = workouts[workouts["Workout"] != "Session Duration"].copy()
    if real.empty:
        return {
            "best_lift": "No exercises yet",
            "top_exercise": "No pattern yet",
            "volume_note": "Log exercises to unlock progression.",
        }

    real["Volume"] = real["Weight"] * real["Reps"]
    best_row = real.loc[real["Weight"].idxmax()]
    top_exercise = real["Workout"].value_counts().idxmax()
    last_14 = real[real["Date"] >= pd.Timestamp(date.today() - timedelta(days=13))]
    volume_note = f"{int(last_14['Volume'].sum()):,} kg x reps in the last 14 days"

    return {
        "best_lift": f"{best_row['Workout']} at {float(best_row['Weight']):.1f} kg",
        "top_exercise": str(top_exercise),
        "volume_note": volume_note,
    }


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def daily_nutrition(snapshot: HealthSnapshot, days: int = 30) -> pd.DataFrame:
    if snapshot.food.empty:
        return pd.DataFrame(columns=["Date", "Calories", "Protein"])

    start = pd.Timestamp(date.today() - timedelta(days=days - 1))
    df = snapshot.food[snapshot.food["date"] >= start].copy()
    daily = df.groupby(df["date"].dt.date).agg(
        Calories=("calories", "sum"),
        Protein=("protein", "sum"),
    ).reset_index()
    daily["Date"] = pd.to_datetime(daily["date"])
    return daily[["Date", "Calories", "Protein"]].sort_values("Date")


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def daily_steps(snapshot: HealthSnapshot, days: int = 30) -> pd.DataFrame:
    if snapshot.steps.empty:
        return pd.DataFrame(columns=["Date", "Steps"])

    start = pd.Timestamp(date.today() - timedelta(days=days - 1))
    df = snapshot.steps[snapshot.steps["date"] >= start].copy()
    daily = df.groupby(df["date"].dt.date)["steps"].sum().reset_index()
    daily.columns = ["Date", "Steps"]
    daily["Date"] = pd.to_datetime(daily["Date"])
    return daily.sort_values("Date")


@st.cache_data(ttl=120, show_spinner=False, hash_funcs={HealthSnapshot: id})
def weight_trend(snapshot: HealthSnapshot) -> pd.DataFrame:
    if snapshot.measurements.empty or "Weight" not in snapshot.measurements.columns:
        return pd.DataFrame(columns=["Date", "Weight", "Trend"])
    df = snapshot.measurements[["Date", "Weight"]].dropna().sort_values("Date").copy()
    df = df[df["Weight"] > 0]
    df["Trend"] = df["Weight"].rolling(window=7, min_periods=1).mean()
    return df
