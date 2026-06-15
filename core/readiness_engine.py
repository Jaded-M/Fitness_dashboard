from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import pandas as pd

from core.muscle_mapping import (
    CANONICAL_MUSCLE_GROUPS,
    exercise_muscle_profile,
    exercise_stimulus_type,
    load_muscle_map,
    unmapped_exercises,
)


RECOVERY_WINDOWS = {
    "Chest": 72,
    "Back": 72,
    "Shoulders": 60,
    "Biceps": 48,
    "Triceps": 48,
    "Quads": 72,
    "Hamstrings": 72,
    "Glutes": 72,
    "Calves": 36,
    "Core": 36,
    "Forearms": 36,
}


@dataclass(frozen=True)
class ReadinessInputs:
    workouts: pd.DataFrame
    food: pd.DataFrame
    steps: pd.DataFrame
    checkins: pd.DataFrame
    calorie_goal: int = 2300
    step_goal: int = 8000
    today: date = field(default_factory=date.today)


def _empty_result() -> dict[str, Any]:
    muscle_status = [
        {"muscle": muscle, "fatigue": 0.0, "readiness": 100.0, "status": "Ready", "load_7d": 0.0, "last_trained": None}
        for muscle in CANONICAL_MUSCLE_GROUPS
    ]
    return {
        "score": 50,
        "label": "Needs training data",
        "training_load_score": 50,
        "recovery_score": 100,
        "activity_score": 50,
        "nutrition_score": 50,
        "subjective_score": 50,
        "days_since_training": None,
        "muscle_status": muscle_status,
        "fatigued_muscles": [],
        "recovered_muscles": [m["muscle"] for m in muscle_status],
        "recommended_split": "Log one mapped workout to calibrate the engine.",
        "key_action": "Log a mapped workout with sets, reps, weight, and RPE.",
        "warnings": ["Readiness is using baseline assumptions until more logs are available."],
        "insights": ["Connect workout logs to the muscle atlas for precise fatigue intelligence."],
        "undertrained_muscles": [],
        "imbalance_risks": [],
        "unmapped_exercises": [],
    }


def _set_volume(row: pd.Series) -> tuple[float, float]:
    set_data = row.get("set_data")
    if isinstance(set_data, str) and set_data.strip():
        try:
            sets = json.loads(set_data)
            if isinstance(sets, list) and sets:
                volume = sum(float(s.get("weight", 0) or 0) * int(s.get("reps", 0) or 0) for s in sets)
                avg_rpe = sum(float(s.get("rpe", row.get("rpe", 7)) or 7) for s in sets) / len(sets)
                return volume, avg_rpe
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    volume = float(row.get("Weight", row.get("weight", 0)) or 0) * float(row.get("Reps", row.get("reps", 0)) or 0)
    return volume, float(row.get("rpe", 7) or 7)


def _training_rows(workouts: pd.DataFrame) -> pd.DataFrame:
    if workouts.empty:
        return pd.DataFrame()
    df = workouts.copy()
    workout_col = "Workout" if "Workout" in df.columns else "exercise"
    date_col = "Date" if "Date" in df.columns else "date"
    df = df[df[workout_col] != "Session Duration"].copy()
    if df.empty:
        return df
    df["Date"] = pd.to_datetime(df[date_col], errors="coerce")
    df["Workout"] = df[workout_col].astype(str)
    return df.dropna(subset=["Date"])


def _muscle_load(workouts: pd.DataFrame, today: date) -> tuple[list[dict[str, Any]], list[str], dict[str, float]]:
    real = _training_rows(workouts)
    if real.empty:
        baseline = _empty_result()
        return baseline["muscle_status"], [], {"weekly_volume": 0.0, "sessions_7d": 0, "days_since_training": None}

    muscle_map = load_muscle_map()
    missing = unmapped_exercises(sorted(real["Workout"].unique().tolist()), muscle_map)
    now = pd.Timestamp(today)
    start_14 = now - pd.Timedelta(days=13)
    recent = real[real["Date"] >= start_14].copy()

    loads = {muscle: 0.0 for muscle in CANONICAL_MUSCLE_GROUPS}
    loads_7d = {muscle: 0.0 for muscle in CANONICAL_MUSCLE_GROUPS}
    fatigue = {muscle: 0.0 for muscle in CANONICAL_MUSCLE_GROUPS}
    last_trained: dict[str, pd.Timestamp] = {}
    weekly_volume = 0.0

    for _, row in recent.iterrows():
        profile = exercise_muscle_profile(row["Workout"], muscle_map)
        if not profile:
            continue
        volume, avg_rpe = _set_volume(row)
        if volume <= 0:
            volume = float(row.get("Sets", row.get("sets", 1)) or 1) * 100.0

        rpe_factor = max(avg_rpe, 5.0) / 8.0
        stimulus = exercise_stimulus_type(row["Workout"], muscle_map)
        stimulus_factor = 1.18 if stimulus in {"push", "pull", "legs"} else 0.9
        days_ago = max((now.normalize() - row["Date"].normalize()).days, 0)
        recency = 0.5 ** (days_ago / 2.5)

        if days_ago <= 6:
            weekly_volume += volume

        for muscle, weight in profile.items():
            if muscle not in fatigue:
                continue
            contribution = volume * weight * rpe_factor * stimulus_factor
            loads[muscle] += contribution
            if days_ago <= 6:
                loads_7d[muscle] += contribution
            fatigue[muscle] += contribution * recency / 45.0
            if muscle not in last_trained or row["Date"] > last_trained[muscle]:
                last_trained[muscle] = row["Date"]

    status_rows = []
    for muscle in CANONICAL_MUSCLE_GROUPS:
        raw_fatigue = min(fatigue[muscle], 100.0)
        readiness = max(0.0, 100.0 - raw_fatigue)
        last = last_trained.get(muscle)
        if last is not None:
            hours_since = max((pd.Timestamp(today) - last).total_seconds() / 3600.0, 0)
            window = RECOVERY_WINDOWS.get(muscle, 48)
            readiness = min(100.0, max(readiness, (hours_since / window) * 100.0))

        if readiness >= 76:
            status = "Ready"
        elif readiness >= 55:
            status = "Manage load"
        else:
            status = "Fatigued"

        status_rows.append(
            {
                "muscle": muscle,
                "fatigue": round(raw_fatigue, 1),
                "readiness": round(readiness, 1),
                "status": status,
                "load_7d": round(loads_7d[muscle], 1),
                "last_trained": last.date().isoformat() if last is not None else None,
            }
        )

    last_session = real["Date"].max()
    days_since_training = max((now.normalize() - last_session.normalize()).days, 0)
    context = {
        "weekly_volume": weekly_volume,
        "sessions_7d": int(real[real["Date"] >= now - pd.Timedelta(days=6)]["Date"].dt.date.nunique()),
        "days_since_training": int(days_since_training),
    }
    return status_rows, missing, context


def _daily_scores(inputs: ReadinessInputs) -> dict[str, int]:
    today_ts = pd.Timestamp(inputs.today)
    last_7 = today_ts - pd.Timedelta(days=6)

    if inputs.steps.empty:
        activity_score = 50
    else:
        steps = inputs.steps.copy()
        steps["date"] = pd.to_datetime(steps["date"], errors="coerce")
        recent = steps[steps["date"] >= last_7]
        daily = recent.groupby(recent["date"].dt.date)["steps"].sum()
        avg_steps = float(daily.mean()) if len(daily) else 0.0
        activity_score = int(min((avg_steps / max(inputs.step_goal, 1)) * 100, 100))

    if inputs.food.empty:
        nutrition_score = 50
    else:
        food = inputs.food.copy()
        food["date"] = pd.to_datetime(food["date"], errors="coerce")
        recent = food[food["date"] >= last_7]
        daily_calories = recent.groupby(recent["date"].dt.date)["calories"].sum()
        daily_protein = recent.groupby(recent["date"].dt.date)["protein"].sum()
        adherence = daily_calories.between(inputs.calorie_goal * 0.85, inputs.calorie_goal * 1.10).mean() if len(daily_calories) else 0.0
        protein_score = min((float(daily_protein.mean()) if len(daily_protein) else 0.0) / 120.0, 1.0)
        nutrition_score = int((adherence * 65) + (protein_score * 35))

    subjective_score = 50
    if not inputs.checkins.empty:
        checkins = inputs.checkins.copy()
        checkins["date"] = pd.to_datetime(checkins["date"], errors="coerce")
        recent = checkins.dropna(subset=["date"]).sort_values("date").tail(1)
        if not recent.empty:
            row = recent.iloc[0]
            energy = float(row.get("energy", 3) or 3) / 5.0
            mood = float(row.get("mood", 3) or 3) / 5.0
            sleep = min(float(row.get("sleep_hours", 7) or 7) / 8.0, 1.0)
            subjective_score = int(((energy * 0.36) + (mood * 0.24) + (sleep * 0.40)) * 100)

    return {
        "activity_score": activity_score,
        "nutrition_score": nutrition_score,
        "subjective_score": subjective_score,
    }


def _label(score: int) -> str:
    if score >= 82:
        return "Primed"
    if score >= 68:
        return "Ready"
    if score >= 52:
        return "Controlled"
    if score >= 38:
        return "Compromised"
    return "Recovery priority"


def calculate_readiness(inputs: ReadinessInputs) -> dict[str, Any]:
    muscle_status, missing, training_context = _muscle_load(inputs.workouts, inputs.today)
    if inputs.workouts.empty:
        base = _empty_result()
        daily = _daily_scores(inputs)
        base.update(daily)
        base["score"] = int((daily["activity_score"] * 0.25) + (daily["nutrition_score"] * 0.25) + (daily["subjective_score"] * 0.30) + 20)
        base["label"] = _label(base["score"])
        return base

    recovered = [m["muscle"] for m in muscle_status if m["readiness"] >= 76]
    fatigued = [m["muscle"] for m in muscle_status if m["readiness"] < 55]
    undertrained = [
        m["muscle"]
        for m in sorted(muscle_status, key=lambda item: (item["load_7d"], item["muscle"]))
        if m["load_7d"] <= 0 and m["readiness"] >= 76
    ]
    recovery_score = int(sum(m["readiness"] for m in muscle_status) / max(len(muscle_status), 1))

    sessions = training_context["sessions_7d"]
    days_since_training = training_context.get("days_since_training")
    training_load_score = 82
    if sessions == 0:
        if days_since_training is None:
            training_load_score = 42
        elif days_since_training >= 7:
            training_load_score = 18
        elif days_since_training >= 4:
            training_load_score = 28
        else:
            training_load_score = 42
    elif sessions > 5:
        training_load_score = 58
    if days_since_training is not None:
        if days_since_training >= 7:
            training_load_score = min(training_load_score, 18)
        elif days_since_training >= 4:
            training_load_score = min(training_load_score, 38)
        elif days_since_training >= 3:
            training_load_score = min(training_load_score, 62)
    if len(fatigued) >= 4:
        training_load_score -= 14
    training_load_score = max(min(training_load_score, 100), 0)

    daily = _daily_scores(inputs)
    score = int(
        recovery_score * 0.36
        + training_load_score * 0.22
        + daily["activity_score"] * 0.16
        + daily["nutrition_score"] * 0.14
        + daily["subjective_score"] * 0.12
    )
    if days_since_training is not None:
        if days_since_training >= 7:
            score = min(score, 52)
        elif days_since_training >= 4:
            score = min(score, 60)
        elif days_since_training >= 3:
            score = min(score, 66)

    warnings = []
    if len(fatigued) >= 3:
        warnings.append(f"High localized fatigue in {', '.join(fatigued[:4])}.")
    if sessions > 5:
        warnings.append("Training frequency is high this week; keep intensity controlled.")
    if days_since_training is not None and days_since_training >= 3:
        warnings.append(
            f"No training logged for {days_since_training} day(s); recovery is high, but training rhythm is low."
        )
    if missing:
        warnings.append(f"{len(missing)} logged exercise(s) are not mapped to the muscle atlas.")
    if daily["nutrition_score"] < 55:
        warnings.append("Nutrition support is limiting recovery confidence.")
    if daily["subjective_score"] < 55:
        warnings.append("Sleep, mood, or energy check-in is suppressing readiness.")

    imbalance_risks = []
    load_by_muscle = {row["muscle"]: row["load_7d"] for row in muscle_status}
    if load_by_muscle.get("Chest", 0) > load_by_muscle.get("Back", 0) * 1.8 and load_by_muscle.get("Chest", 0) > 0:
        imbalance_risks.append("Pressing load is outpacing back work.")
    if load_by_muscle.get("Quads", 0) > load_by_muscle.get("Hamstrings", 0) * 1.8 and load_by_muscle.get("Quads", 0) > 0:
        imbalance_risks.append("Quad work is outpacing posterior-chain work.")
    if load_by_muscle.get("Biceps", 0) > load_by_muscle.get("Triceps", 0) * 2.0 and load_by_muscle.get("Biceps", 0) > 0:
        imbalance_risks.append("Arm work is biased toward biceps.")

    balanced_targets = [
        row["muscle"]
        for row in sorted(muscle_status, key=lambda item: (item["load_7d"], -item["readiness"]))
        if row["readiness"] >= 68 and row["muscle"] not in fatigued
    ]
    if balanced_targets:
        recommended = f"Bias next session toward {', '.join(balanced_targets[:3])}."
    else:
        recommended = "Use a low-intensity recovery session or rest day."
    if fatigued:
        recommended += f" Avoid heavy loading for {', '.join(fatigued[:3])}."

    if days_since_training is not None and days_since_training >= 4:
        key_action = "Rebuild rhythm with a low-to-moderate full-body session."
    elif score < 45:
        key_action = "Prioritize recovery: sleep, steps, protein, and low-intensity movement."
    elif fatigued:
        key_action = f"Train around fatigue: emphasize {', '.join(balanced_targets[:2] or recovered[:2])}."
    elif undertrained:
        key_action = f"Close the gap with {', '.join(undertrained[:2])} work."
    else:
        key_action = "Proceed with the recommended split and keep RPE controlled."

    insights = [
        f"{len(recovered)} muscle group(s) are ready; {len(fatigued)} need load management.",
        f"Seven-day training exposure: {int(training_context['weekly_volume']):,} kg x reps across {sessions} day(s).",
    ]
    if days_since_training is not None:
        insights.append(f"Last logged training session was {days_since_training} day(s) ago.")
    if not warnings:
        insights.append("No major imbalance or overtraining signal detected.")

    return {
        "score": max(min(score, 100), 0),
        "label": _label(score),
        "training_load_score": training_load_score,
        "recovery_score": recovery_score,
        "days_since_training": days_since_training,
        **daily,
        "muscle_status": muscle_status,
        "fatigued_muscles": fatigued,
        "recovered_muscles": recovered,
        "recommended_split": recommended,
        "key_action": key_action,
        "warnings": warnings,
        "insights": insights,
        "undertrained_muscles": undertrained,
        "imbalance_risks": imbalance_risks,
        "unmapped_exercises": missing,
    }
