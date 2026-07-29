from __future__ import annotations

from datetime import date, timedelta
import os
from typing import Any

import pandas as pd
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

import database


CALORIE_GOAL_DEFAULT = 2300
PROTEIN_TARGET_DEFAULT = 153
STEP_GOAL_DEFAULT = 10000


def _goal_context() -> dict[str, int]:
    return {
        "calorie_goal": int(st.session_state.get("calorie_goal", CALORIE_GOAL_DEFAULT)),
        "protein_target": int(st.session_state.get("protein_target", PROTEIN_TARGET_DEFAULT)),
        "step_goal": int(st.session_state.get("step_goal", STEP_GOAL_DEFAULT)),
    }


def _as_date_frame(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return pd.DataFrame()
    frame = df.copy()
    frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame.dropna(subset=[column])


def _filter_by_day(df: pd.DataFrame, column: str, day: date) -> pd.DataFrame:
    frame = _as_date_frame(df, column)
    if frame.empty:
        return pd.DataFrame()
    target = pd.Timestamp(day).normalize()
    return frame[frame[column].dt.normalize() == target].copy()


def _filter_since(df: pd.DataFrame, column: str, start: date, end: date) -> pd.DataFrame:
    frame = _as_date_frame(df, column)
    if frame.empty:
        return pd.DataFrame()
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    dates = frame[column].dt.normalize()
    return frame[(dates >= start_ts) & (dates <= end_ts)].copy()


def _num(value: Any, default: float = 0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any) -> int:
    return int(round(_num(value)))


def _real_workouts(workouts: pd.DataFrame) -> pd.DataFrame:
    if workouts.empty:
        return pd.DataFrame()
    real = workouts.copy()
    if "Workout" in real.columns:
        real = real[real["Workout"] != "Session Duration"].copy()
    return real


def _workout_volume(workouts: pd.DataFrame) -> pd.Series:
    if workouts.empty:
        return pd.Series(dtype=float)
    weight = pd.to_numeric(workouts["Weight"], errors="coerce").fillna(0) if "Weight" in workouts else pd.Series(0, index=workouts.index)
    reps = pd.to_numeric(workouts["Reps"], errors="coerce").fillna(0) if "Reps" in workouts else pd.Series(0, index=workouts.index)
    return weight * reps


def _food_daily_text(food: pd.DataFrame, calorie_goal: int, protein_target: int) -> str:
    if food.empty:
        return f"No food logged. Targets: {calorie_goal} kcal, {protein_target}g protein."

    calories = _safe_int(food.get("calories", pd.Series(dtype=float)).sum())
    protein = _safe_int(food.get("protein", pd.Series(dtype=float)).sum())
    carbs = _safe_int(food.get("carbs", pd.Series(dtype=float)).sum()) if "carbs" in food else 0
    fats = _safe_int(food.get("fats", pd.Series(dtype=float)).sum()) if "fats" in food else 0
    fiber = _safe_int(food.get("fiber", pd.Series(dtype=float)).sum()) if "fiber" in food else 0
    items = []
    if "food_item" in food.columns:
        items = [str(item) for item in food["food_item"].dropna().head(12).tolist()]
    return (
        f"{calories} kcal vs {calorie_goal} goal; {protein}g protein vs {protein_target}g target; "
        f"{carbs}g carbs, {fats}g fats, {fiber}g fiber. Foods: {', '.join(items) if items else 'not itemized'}."
    )


def _food_weekly_text(food: pd.DataFrame, calorie_goal: int, protein_target: int) -> str:
    if food.empty:
        return f"No food logged in the last 7 days. Targets: {calorie_goal} kcal, {protein_target}g protein."

    grouped = food.groupby(food["date"].dt.date).agg({"calories": "sum", "protein": "sum"}).sort_index()
    avg_calories = _safe_int(grouped["calories"].mean())
    avg_protein = _safe_int(grouped["protein"].mean())
    protein_adherence = _safe_int((grouped["protein"] >= protein_target).mean() * 100)
    best_day = grouped["protein"].idxmax()
    worst_day = grouped["protein"].idxmin()
    day_lines = [
        f"{day}: {_safe_int(row['calories'])} kcal, {_safe_int(row['protein'])}g protein"
        for day, row in grouped.iterrows()
    ]
    return (
        f"Average {avg_calories} kcal/day vs {calorie_goal}; average {avg_protein}g protein/day vs "
        f"{protein_target}; protein adherence {protein_adherence}%. Best protein day: {best_day} "
        f"({_safe_int(grouped.loc[best_day, 'protein'])}g). Worst protein day: {worst_day} "
        f"({_safe_int(grouped.loc[worst_day, 'protein'])}g). Daily totals: {'; '.join(day_lines)}."
    )


def _steps_daily_text(steps: pd.DataFrame, step_goal: int) -> str:
    if steps.empty:
        return f"No steps logged. Goal: {step_goal} steps."
    total_steps = _safe_int(steps.get("steps", pd.Series(dtype=float)).sum())
    active_minutes = _safe_int(steps.get("active_minutes", pd.Series(dtype=float)).sum()) if "active_minutes" in steps else 0
    return f"{total_steps} steps vs {step_goal} goal; {active_minutes} active minutes."


def _steps_weekly_text(steps: pd.DataFrame, step_goal: int) -> str:
    if steps.empty:
        return f"No steps logged in the last 7 days. Goal: {step_goal} steps/day."
    grouped = steps.groupby(steps["date"].dt.date)["steps"].sum().sort_index()
    average = _safe_int(grouped.mean())
    hit_rate = _safe_int((grouped >= step_goal).mean() * 100)
    best_day = grouped.idxmax()
    worst_day = grouped.idxmin()
    day_lines = [f"{day}: {_safe_int(value)}" for day, value in grouped.items()]
    return (
        f"Average {average} steps/day vs {step_goal}; goal hit rate {hit_rate}%. "
        f"Best day: {best_day} ({_safe_int(grouped.loc[best_day])}). Worst day: {worst_day} "
        f"({_safe_int(grouped.loc[worst_day])}). Daily steps: {'; '.join(day_lines)}."
    )


def _checkin_daily_text(checkins: pd.DataFrame) -> str:
    if checkins.empty:
        return "No check-in logged."
    row = checkins.sort_values("date").iloc[-1]
    sleep = row.get("sleep_hours", "not logged")
    mood = row.get("mood", "not logged")
    energy = row.get("energy", "not logged")
    note = row.get("note", "")
    return f"Sleep {sleep} hours; mood {mood}/5; energy {energy}/5; note: {note or 'none'}."


def _checkin_weekly_text(checkins: pd.DataFrame) -> str:
    if checkins.empty:
        return "No check-ins logged in the last 7 days."
    lines = []
    if "sleep_hours" in checkins:
        sleep = pd.to_numeric(checkins["sleep_hours"], errors="coerce").dropna()
        if not sleep.empty:
            lines.append(f"Average sleep {sleep.mean():.1f} hours over {len(sleep)} logged day(s)")
            if len(sleep) >= 2:
                trend = "up" if sleep.iloc[-1] > sleep.iloc[0] else "down" if sleep.iloc[-1] < sleep.iloc[0] else "stable"
                lines.append(f"sleep trend {trend}")
    for metric in ["mood", "energy"]:
        if metric in checkins:
            values = pd.to_numeric(checkins[metric], errors="coerce").dropna()
            if not values.empty:
                lines.append(f"average {metric} {values.mean():.1f}/5")
    return "; ".join(lines) + "." if lines else "Check-ins logged, but sleep/mood/energy values are unavailable."


def _recovery_weekly_text(checkins: pd.DataFrame, summary: dict, readiness: dict) -> str:
    current = _readiness_text(summary, readiness)
    if checkins.empty:
        return f"No check-ins available for a 7-day recovery trend. {current}"

    frame = checkins.copy().sort_values("date")
    energy = pd.to_numeric(frame["energy"], errors="coerce") if "energy" in frame else pd.Series(dtype=float)
    mood = pd.to_numeric(frame["mood"], errors="coerce") if "mood" in frame else pd.Series(dtype=float)
    sleep = pd.to_numeric(frame["sleep_hours"], errors="coerce") if "sleep_hours" in frame else pd.Series(dtype=float)

    frame["recovery_proxy"] = (
        energy.reindex(frame.index).fillna(3).clip(1, 5) * 12
        + mood.reindex(frame.index).fillna(3).clip(1, 5) * 8
        + (sleep.reindex(frame.index).fillna(7).clip(0, 9) / 9 * 40)
    )
    valid = frame[frame["recovery_proxy"].notna()]
    if valid.empty:
        return f"No usable check-in values for a 7-day recovery trend. {current}"

    best = valid.loc[valid["recovery_proxy"].idxmax()]
    worst = valid.loc[valid["recovery_proxy"].idxmin()]
    first = valid["recovery_proxy"].iloc[0]
    last = valid["recovery_proxy"].iloc[-1]
    trend = "up" if last > first else "down" if last < first else "stable"
    return (
        f"Check-in recovery proxy trend {trend}: {_safe_int(first)} to {_safe_int(last)}. "
        f"Best day {best['date'].date()} ({_safe_int(best['recovery_proxy'])}); "
        f"worst day {worst['date'].date()} ({_safe_int(worst['recovery_proxy'])}). {current}"
    )


def _workout_daily_text(workouts: pd.DataFrame) -> str:
    if workouts.empty:
        return "No workout logged."
    real = _real_workouts(workouts)
    if real.empty:
        return "No exercise sets logged."
    volume = _safe_int(_workout_volume(real).sum())
    exercises = real.get("Workout", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()
    sets = _safe_int(real.get("Sets", pd.Series(dtype=float)).sum()) if "Sets" in real else len(real)
    return f"{sets} set(s), {len(exercises)} exercise(s), {volume} kg x reps volume. Exercises: {', '.join(exercises[:12])}."


def _workout_weekly_text(workouts: pd.DataFrame) -> str:
    if workouts.empty:
        return "No workouts logged in the last 7 days."
    real = _real_workouts(workouts)
    if real.empty:
        return "No exercise sets logged in the last 7 days."
    real["Volume"] = _workout_volume(real)
    sessions = real["Date"].dt.date.nunique() if "Date" in real else 0
    volume = _safe_int(real["Volume"].sum())
    top = real.groupby("Workout")["Volume"].sum().sort_values(ascending=False).head(5) if "Workout" in real else pd.Series(dtype=float)
    top_text = "; ".join(f"{name}: {_safe_int(value)}" for name, value in top.items()) if not top.empty else "not available"
    return f"{sessions} training day(s), {len(real)} logged set row(s), {volume} kg x reps total volume. Top volume lifts: {top_text}."


def _body_weekly_text(snapshot) -> str:
    measurements = getattr(snapshot, "measurements", pd.DataFrame())
    if measurements.empty or "Weight" not in measurements.columns or "Date" not in measurements.columns:
        return "No weight data available."
    frame = _filter_since(measurements, "Date", date.today() - timedelta(days=6), date.today())
    frame = frame[pd.to_numeric(frame["Weight"], errors="coerce").notna()]
    if frame.empty:
        return "No weight entries in the last 7 days."
    frame = frame.sort_values("Date")
    start_weight = _num(frame["Weight"].iloc[0])
    end_weight = _num(frame["Weight"].iloc[-1])
    return f"Weight moved from {start_weight:.1f} kg to {end_weight:.1f} kg ({end_weight - start_weight:+.1f} kg)."


def _readiness_text(summary: dict, readiness: dict) -> str:
    parts = [
        f"Current score: {readiness.get('score', summary.get('readiness', 'not available'))}",
        f"label: {readiness.get('label', summary.get('readiness_label', 'not available'))}",
        f"recovery: {readiness.get('recovery_score', 'not available')}",
        f"training load: {readiness.get('training_load_score', 'not available')}",
        f"activity: {readiness.get('activity_score', 'not available')}",
        f"nutrition: {readiness.get('nutrition_score', 'not available')}",
        f"subjective: {readiness.get('subjective_score', 'not available')}",
        f"recommended action: {readiness.get('key_action', readiness.get('recommended_split', 'not available'))}",
    ]
    return "; ".join(parts) + "."


def _call_llm(system_prompt: str, user_content: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "PHI report unavailable: OPENROUTER_API_KEY not set."

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "inclusionai/ling-3.0-flash:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 1024
        },
        timeout=30
    )

    if response.status_code != 200:
        return f"PHI report unavailable: {response.status_code} {response.text}"

    return response.json()["choices"][0]["message"]["content"]


def generate_daily_report(summary, readiness, snapshot) -> str:
    goals = _goal_context()
    yesterday = date.today() - timedelta(days=1)

    food = _filter_by_day(database.get_food_logs(), "date", yesterday)
    steps = _filter_by_day(database.get_steps_data(yesterday.isoformat(), yesterday.isoformat()), "date", yesterday)
    checkins = _filter_by_day(database.get_checkins(), "date", yesterday)
    workouts = _filter_by_day(getattr(snapshot, "workouts", pd.DataFrame()), "Date", yesterday)

    system_prompt = (
        "You are PHI, a personal health intelligence system. "
        "Generate a concise daily briefing (max 150 words) covering: "
        "TRAINING: what was logged yesterday "
        "NUTRITION: calories and protein vs targets "
        "SLEEP: hours and quality from check-in "
        "STEPS: vs goal "
        "TODAY: one specific action based on readiness "
        "Be specific to the actual numbers. No generic advice."
    )
    user_text = "\n".join(
        [
            f"Date covered: {yesterday}",
            f"Goals: {goals['calorie_goal']} calories, {goals['protein_target']}g protein, {goals['step_goal']} steps.",
            f"Training: {_workout_daily_text(workouts)}",
            f"Nutrition: {_food_daily_text(food, goals['calorie_goal'], goals['protein_target'])}",
            f"Sleep/check-in: {_checkin_daily_text(checkins)}",
            f"Steps: {_steps_daily_text(steps, goals['step_goal'])}",
            f"Readiness today: {_readiness_text(summary, readiness)}",
        ]
    )
    return _call_llm(system_prompt, user_text)


def generate_weekly_report(summary, readiness, snapshot) -> str:
    goals = _goal_context()
    end = date.today()
    start = end - timedelta(days=6)

    food = _filter_since(database.get_food_logs(), "date", start, end)
    steps = _filter_since(database.get_steps_data(start.isoformat(), end.isoformat()), "date", start, end)
    checkins = _filter_since(database.get_checkins(), "date", start, end)
    workouts = _filter_since(getattr(snapshot, "workouts", pd.DataFrame()), "Date", start, end)

    system_prompt = (
        "You are PHI, a personal health intelligence system. "
        "Generate a weekly performance report (max 400 words) covering: "
        "TRAINING: volume, consistency, progression highlights "
        "NUTRITION: average calories, protein adherence %, best/worst days "
        "SLEEP: average hours, trend "
        "RECOVERY: readiness trend, best and worst days "
        "BODY: weight trend if available "
        "NEXT WEEK: 3 specific actionable recommendations "
        "Be specific to the actual numbers. Format with clear sections."
    )
    user_text = "\n".join(
        [
            f"Date range covered: {start} to {end}",
            f"Goals: {goals['calorie_goal']} calories/day, {goals['protein_target']}g protein/day, {goals['step_goal']} steps/day.",
            f"Training: {_workout_weekly_text(workouts)}",
            f"Nutrition: {_food_weekly_text(food, goals['calorie_goal'], goals['protein_target'])}",
            f"Sleep/check-ins: {_checkin_weekly_text(checkins)}",
            f"Steps: {_steps_weekly_text(steps, goals['step_goal'])}",
            f"Recovery/readiness: {_recovery_weekly_text(checkins, summary, readiness)}",
            f"Body: {_body_weekly_text(snapshot)}",
        ]
    )
    return _call_llm(system_prompt, user_text)
