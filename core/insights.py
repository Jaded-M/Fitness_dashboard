"""
# ════════════════════════════════════════════════════════════════
# MODULE: core/insights.py — The Intelligence Engine
# ════════════════════════════════════════════════════════════════
# // WHAT IT DOES:
#    This is the "brain" of the app. It takes raw workout data and
#    produces ACTIONABLE INTELLIGENCE — things like:
#      - "Try 62.5kg × 8 today" (progressive overload advisor)
#      - "You haven't trained Lower B in 14 days" (balance warning)
#      - "When steps > 8000 and calories < 2000, weight drops 0.3kg/week"
#
# // HOW IT WORKS:
#    Each function takes a DataFrame (a table of data) and returns
#    either a dictionary of results or a list of warning strings.
#    No Streamlit UI code here — this is pure math and logic.
#
# // WHY SEPARATE FROM THE UI:
#    Separation of Concerns. If the math is wrong, you fix it HERE.
#    If the button looks wrong, you fix it in Fitness.py.
#    They never interfere with each other.
#
# // LEARNING NOTES:
#    This module introduces two important Python/Data Science concepts:
#    1. Rolling Averages (smoothing noisy data)
#    2. Correlation (measuring if two things are related)
# ════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_overload_target(exercise_name, workout_df):
    """
    // WHAT IT DOES:
    //   Looks at your last session for this exercise and suggests
    //   what you should aim for today to progressively overload.
    //
    // HOW IT WORKS:
    //   Strategy 1: Add reps (same weight, +1-2 reps)
    //   Strategy 2: Add weight (if you already hit max reps, bump weight +2.5kg)
    //
    // THE SCIENCE:
    //   Progressive overload means doing slightly MORE than last time.
    //   This is the #1 principle of muscle growth. Without it, your body
    //   has no reason to adapt and get stronger.
    //
    // RETURNS:
    //   A dictionary with keys:
    //     'last_weight', 'last_reps', 'last_sets', 'last_date',
    //     'suggestion_text' (human-readable one-liner),
    //     'has_history' (True/False — did we find past data?)
    """

    # ── Filter to just this exercise ──────────────────────────
    # .copy() creates an independent copy so we don't accidentally
    # modify the original DataFrame (a common Python gotcha).
    ex_df = workout_df[workout_df["Workout"] == exercise_name].copy()

    # If no history exists, return a "no data" result
    if ex_df.empty:
        return {
            "has_history": False,
            "suggestion_text": "First time logging this exercise. Start light and find your working weight!",
            "last_weight": 0, "last_reps": 0, "last_sets": 0, "last_date": "—"
        }

    # ── Get the most recent session ────────────────────────────
    # .sort_values() arranges rows by date, ascending=False means newest first.
    # .iloc[0] grabs the first row (= most recent session).
    ex_df = ex_df.sort_values("Date", ascending=False)
    last = ex_df.iloc[0]

    last_weight = float(last.get("Weight", 0))
    last_reps   = int(last.get("Reps", 0))
    last_sets   = int(last.get("Sets", 0))
    last_date   = str(last.get("Date", "—"))[:10]   # [:10] trims the time portion

    # ── Build the suggestion ───────────────────────────────────
    # RULE: If you hit 12+ reps last time, you're ready to add weight.
    # Otherwise, try to add 1-2 reps at the same weight.
    #
    # 2.5kg is the standard "minimum jump" for most gym equipment.
    # For dumbbells it might be 1kg or 2kg — but 2.5 is a safe default.
    if last_reps >= 12:
        # You've maxed out the rep range — time to go heavier
        new_weight = last_weight + 2.5
        suggestion = f"Weight UP: {new_weight}kg x 8-10 reps (+2.5kg)"
    elif last_reps >= 8:
        # In the sweet spot — try for more reps at same weight
        target_reps = last_reps + 1
        suggestion = f"Rep UP: {last_weight}kg x {target_reps} reps (+1 rep)"
    else:
        # Low rep range — keep the same weight and aim for 8
        suggestion = f"Build: {last_weight}kg x 8 reps (target 8+ before adding weight)"

    return {
        "has_history": True,
        "last_weight": last_weight,
        "last_reps": last_reps,
        "last_sets": last_sets,
        "last_date": last_date,
        "suggestion_text": suggestion,
    }


def get_balance_warnings(workout_df, days=14):
    """
    // WHAT IT DOES:
    //   Checks the last N days and warns you if any split is
    //   being neglected compared to others.
    //
    // HOW IT WORKS:
    //   Counts how many UNIQUE dates each split was trained.
    //   If any split has 0 sessions while others have 2+,
    //   it generates a warning string.
    //
    // THE SCIENCE:
    //   Muscle imbalances cause injuries. If you always train
    //   chest but never train back, your shoulders will round
    //   forward and you'll get posture problems + impingement.
    //
    // RETURNS:
    //   A list of warning strings. Empty list = everything balanced.
    """
    warnings = []

    if workout_df.empty:
        return warnings

    # ── Filter to recent data ──────────────────────────────────
    # datetime.now() gives the current date+time.
    # timedelta(days=14) creates a "14 days" duration object.
    # Subtracting it gives us "14 days ago."
    cutoff = datetime.now() - timedelta(days=days)

    # We filter rows where the Date column is >= the cutoff.
    # This is called "boolean indexing" — the condition inside []
    # creates a True/False mask, and pandas only keeps the True rows.
    recent = workout_df[workout_df["Date"] >= cutoff].copy()

    if recent.empty:
        warnings.append(f"No workouts logged in the last {days} days. Time to get back in the gym!")
        return warnings

    # ── Count sessions per split ───────────────────────────────
    # .nunique() counts UNIQUE values — so if you trained "Upper A"
    # on 3 different dates, it returns 3 (not the total number of rows).
    split_counts = recent.groupby("Split")["Date"].apply(
        lambda dates: dates.dt.date.nunique()
    )

    # ── Compare splits ─────────────────────────────────────────
    max_sessions = split_counts.max()

    for split_name, count in split_counts.items():
        if split_name == "Session Duration":
            continue  # Skip the internal tracking split

        if count == 0 and max_sessions >= 2:
            warnings.append(f"⚠️ **{split_name}** — 0 sessions in {days} days. Other splits have {max_sessions}.")
        elif count == 1 and max_sessions >= 3:
            warnings.append(f"⚡ **{split_name}** — only 1 session in {days} days. Consider adding another.")

    return warnings


def get_estimated_1rm(weight, reps):
    """
    // WHAT IT DOES:
    //   Estimates your theoretical 1-Rep Max (the heaviest weight
    //   you could lift for exactly 1 rep) from a multi-rep set.
    //
    // HOW IT WORKS:
    //   Uses the Epley Formula: 1RM = weight × (1 + reps/30)
    //   This is the most widely used formula in strength sports.
    //
    // THE SCIENCE:
    //   Your muscles can lift more weight for fewer reps.
    //   If you can bench 60kg for 10 reps, your 1RM is ~80kg.
    //   Tracking 1RM over time shows TRUE strength gains,
    //   even if your rep scheme changes.
    //
    // EXAMPLE:
    //   get_estimated_1rm(60, 10)  →  80.0
    //   get_estimated_1rm(70, 5)   →  81.7
    //   Both sessions show similar strength — just different strategies!
    """
    if reps <= 0 or weight <= 0:
        return 0

    # The Epley Formula
    # For 1 rep: returns the weight itself (1 + 1/30 ≈ 1.033)
    # For 10 reps: returns weight × 1.333
    return round(weight * (1 + reps / 30), 1)


def get_correlations(workout_df, food_df=None, steps_df=None, weight_df=None):
    """
    // WHAT IT DOES:
    //   Finds CORRELATIONS between your lifestyle metrics:
    //   - Do high-step days lead to weight loss?
    //   - Does eating more protein correlate with higher gym volume?
    //   - Does calorie deficit + high training = fastest fat loss?
    //
    // HOW IT WORKS:
    //   We align all data by date, then compute Pearson correlations.
    //
    // PYTHON CONCEPT — Correlation (r value):
    //   r = +1.0  →  perfect positive relationship (A goes up, B goes up)
    //   r = -1.0  →  perfect negative relationship (A goes up, B goes down)
    //   r =  0.0  →  no relationship at all
    //   |r| > 0.5 →  "strong" in social science
    //   |r| > 0.3 →  "moderate" — worth paying attention to
    //
    // CAUTION — CORRELATION ≠ CAUSATION:
    //   Just because two things move together doesn't mean one CAUSES
    //   the other. Ice cream sales and drowning deaths are correlated
    //   (both rise in summer), but ice cream doesn't cause drowning.
    //   We label findings as "correlation" not "proof."
    //
    // RETURNS:
    //   A list of insight strings (human-readable findings).
    //   Empty list if not enough data.
    """
    insights = []

    if workout_df is None or workout_df.empty:
        return insights

    # ── Build a daily summary ──────────────────────────────────
    # We need one row per day with: total_volume, calories, steps, weight
    # .groupby() groups all rows with the same date together,
    # then .agg() computes summary stats for each group.
    real = workout_df[workout_df["Workout"] != "Session Duration"].copy()
    real["Volume"] = real["Weight"] * real["Reps"]

    daily_training = real.groupby(real["Date"].dt.date).agg(
        total_volume=("Volume", "sum"),
        total_sets=("Sets", "sum"),
        max_weight=("Weight", "max"),
    ).reset_index()
    daily_training.columns = ["date", "total_volume", "total_sets", "max_weight"]

    # ── Merge with nutrition data if available ──────────────────
    if food_df is not None and not food_df.empty and "date" in food_df.columns:
        food_copy = food_df.copy()
        food_copy["date"] = pd.to_datetime(food_copy["date"]).dt.date

        daily_food = food_copy.groupby("date").agg(
            total_calories=("calories", "sum"),
            total_protein=("protein", "sum"),
        ).reset_index()

        # pd.merge() joins two tables on a shared column (like a VLOOKUP).
        # how="outer" keeps ALL dates from both tables (filling NaN where missing).
        daily_training = pd.merge(daily_training, daily_food, on="date", how="outer")

    # ── Merge with steps data if available ──────────────────────
    if steps_df is not None and not steps_df.empty:
        steps_copy = steps_df.copy()
        if "date" in steps_copy.columns:
            steps_copy["date"] = pd.to_datetime(steps_copy["date"]).dt.date
            daily_training = pd.merge(daily_training, steps_copy, on="date", how="outer")

    # ── Merge with weight/measurements data if available ────────
    if weight_df is not None and not weight_df.empty:
        weight_copy = weight_df.copy()
        if "Date" in weight_copy.columns:
            weight_copy["date"] = pd.to_datetime(weight_copy["Date"]).dt.date
            weight_copy = weight_copy[["date", "Weight"]].rename(columns={"Weight": "body_weight"})
            daily_training = pd.merge(daily_training, weight_copy, on="date", how="outer")

    # ── Calculate correlations ─────────────────────────────────
    # .corr() computes the Pearson correlation matrix.
    # We only care about correlations that are "moderate" (|r| > 0.3).
    numeric_cols = daily_training.select_dtypes(include=[np.number]).columns.tolist()

    if len(numeric_cols) >= 2 and len(daily_training) >= 7:
        corr_matrix = daily_training[numeric_cols].corr()

        # ── Extract interesting pairs ──────────────────────────
        # We look at each pair of columns and report strong correlations.
        interesting_pairs = [
            ("total_volume", "total_calories", "Training Volume", "Calorie Intake"),
            ("total_volume", "total_protein", "Training Volume", "Protein Intake"),
            ("total_sets", "total_calories", "Total Sets", "Calorie Intake"),
        ]

        # Add steps-related pairs if steps data exists
        if "steps" in numeric_cols:
            interesting_pairs.extend([
                ("steps", "total_volume", "Daily Steps", "Training Volume"),
                ("steps", "total_calories", "Daily Steps", "Calorie Intake"),
            ])

        # Add weight-related pairs if weight data exists
        if "body_weight" in numeric_cols:
            interesting_pairs.extend([
                ("body_weight", "total_calories", "Body Weight", "Calorie Intake"),
                ("body_weight", "steps", "Body Weight", "Daily Steps"),
            ])

        for col1, col2, label1, label2 in interesting_pairs:
            if col1 in corr_matrix.columns and col2 in corr_matrix.columns:
                r = corr_matrix.loc[col1, col2]

                # Only report correlations that are worth talking about
                if abs(r) >= 0.3 and not pd.isna(r):
                    direction = "increases" if r > 0 else "decreases"
                    strength  = "strongly" if abs(r) >= 0.6 else "moderately"
                    insights.append(
                        f"📊 **{label1}** {strength} correlates with **{label2}** "
                        f"(r={r:.2f}). When {label1} goes up, {label2} {direction}."
                    )

    # ── Add summary stat ────────────────────────────────────────
    if len(daily_training) >= 7:
        avg_vol = daily_training["total_volume"].mean()
        if not pd.isna(avg_vol):
            insights.append(
                f"📈 Your average daily training volume is **{int(avg_vol):,} kg·reps**."
            )

    if not insights:
        insights.append("📊 Not enough data yet for correlation analysis. Keep logging — need at least 7 days of data.")

    return insights


def get_weekly_summary(workout_df):
    """
    // WHAT IT DOES:
    //   Generates a plain-English weekly performance summary.
    //   Used to display a "This Week at a Glance" card on the dashboard.
    //
    // HOW IT WORKS:
    //   1. Filters workout data to the last 7 days ("this week")
    //   2. Also filters to 8–14 days ago ("last week") for comparison
    //   3. Calculates: session count, total volume, best lift
    //   4. Compares this week vs last week to get the trend (+/-)
    //   5. Returns a dictionary with all stats + a one-line summary string
    //
    // PYTHON CONCEPTS IN THIS FUNCTION:
    //   - timedelta: creates a duration you can add/subtract from a date
    //   - groupby + agg: summarise rows by a shared column value
    //   - Conditional expressions: "A if condition else B" (one-line if/else)
    //   - f-strings: embed variables directly inside strings with {}
    //
    // RETURNS:
    //   A dictionary with these keys:
    //     sessions_this_week  (int)
    //     volume_this_week    (int, kg·reps)
    //     volume_last_week    (int, kg·reps)
    //     volume_delta_pct    (float, % change — positive = improvement)
    //     best_lift_name      (str, exercise name)
    //     best_lift_weight    (float, kg)
    //     summary_line        (str, human-readable one-liner)
    //   Returns None if there is not enough data.
    """
    if workout_df is None or workout_df.empty:
        return None

    # ── Step 1: Define time windows ────────────────────────────────────────
    # datetime.now() = right now
    # timedelta(days=7) = a 7-day duration object
    # Subtracting it gives us "7 days ago"
    now         = datetime.now()
    week_start  = now - timedelta(days=7)   # 7 days ago  (start of "this week")
    lweek_start = now - timedelta(days=14)  # 14 days ago (start of "last week")

    # Filter rows: keep only real exercises (not the session duration hack)
    real = workout_df[workout_df["Workout"] != "Session Duration"].copy()

    # Ensure Date column is datetime so we can compare with timedelta
    real["Date"] = pd.to_datetime(real["Date"])

    # ── Step 2: Slice into "this week" and "last week" ─────────────────────
    # Boolean indexing: the condition inside [] creates a True/False mask
    this_week = real[real["Date"] >= week_start]
    last_week = real[(real["Date"] >= lweek_start) & (real["Date"] < week_start)]

    # If nothing logged this week, return early with a friendly nudge
    if this_week.empty:
        return {
            "sessions_this_week": 0,
            "volume_this_week": 0,
            "volume_last_week": 0,
            "volume_delta_pct": 0,
            "best_lift_name": "—",
            "best_lift_weight": 0,
            "summary_line": "No workouts logged this week yet. Time to get back in the gym! 💪"
        }

    # ── Step 3: Calculate this week's stats ───────────────────────────────
    # Volume = sets × reps × weight moved (a proxy for total work done)
    this_week = this_week.copy()
    this_week["Volume"] = this_week["Weight"] * this_week["Reps"]

    # .dt.date strips the time portion so "2025-01-01 09:00" becomes "2025-01-01"
    # .nunique() counts distinct values — so 3 training days = 3, not 30 sets
    sessions = this_week["Date"].dt.date.nunique()
    vol_this  = int(this_week["Volume"].sum())

    # ── Step 4: Calculate last week's volume for comparison ───────────────
    if not last_week.empty:
        last_week = last_week.copy()
        last_week["Volume"] = last_week["Weight"] * last_week["Reps"]
        vol_last = int(last_week["Volume"].sum())
    else:
        vol_last = 0

    # ── Step 5: Calculate % change ────────────────────────────────────────
    # Avoid division by zero: only calculate delta if last week had volume
    if vol_last > 0:
        # (new - old) / old × 100 = percentage change
        delta_pct = ((vol_this - vol_last) / vol_last) * 100
    else:
        delta_pct = 0.0

    # ── Step 6: Find the best lift this week ──────────────────────────────
    # .loc[] with idxmax() finds the ROW where Weight is highest
    best_row = this_week.loc[this_week["Weight"].idxmax()]
    best_lift_name   = best_row["Workout"]
    best_lift_weight = float(best_row["Weight"])

    # ── Step 7: Build the plain-English summary line ───────────────────────
    # Conditional expression:  value_if_true  if  condition  else  value_if_false
    trend_emoji = "📈" if delta_pct >= 0 else "📉"
    trend_text  = f"+{delta_pct:.0f}%" if delta_pct >= 0 else f"{delta_pct:.0f}%"

    if sessions >= 4:
        status = "Elite week. 🔥"
    elif sessions >= 2:
        status = "Solid consistency. Keep it up."
    else:
        status = "Light week. Try to add a session."

    summary_line = (
        f"{sessions} session{'s' if sessions != 1 else ''} this week · "
        f"{vol_this:,} kg·reps ({trend_emoji} {trend_text} vs last week) · "
        f"Best: {best_lift_name} {best_lift_weight:.0f}kg · {status}"
    )

    return {
        "sessions_this_week": sessions,
        "volume_this_week":   vol_this,
        "volume_last_week":   vol_last,
        "volume_delta_pct":   round(delta_pct, 1),
        "best_lift_name":     best_lift_name,
        "best_lift_weight":   best_lift_weight,
        "summary_line":       summary_line,
    }

def get_training_streak(workout_df):
    """
    Calculates the number of consecutive weeks with at least 1 workout.
    """
    if workout_df is None or workout_df.empty:
        return 0
        
    df = workout_df[workout_df["Workout"] != "Session Duration"].copy()
    if df.empty:
        return 0
        
    df["Date"] = pd.to_datetime(df["Date"])
    # Get unique ISO year-week strings for all workouts
    weeks = df["Date"].dt.strftime('%G-%V').unique()
    weeks = sorted(weeks, reverse=True)
    
    current_week = datetime.now().strftime('%G-%V')
    last_week = (datetime.now() - timedelta(days=7)).strftime('%G-%V')
    
    streak = 0
    # Streak starts if we worked out this week or last week
    if current_week in weeks or last_week in weeks:
        # We need a continuous sequence
        expected_date = datetime.now()
        # If we haven't worked out this week yet but did last week, start from last week
        if current_week not in weeks and last_week in weeks:
            expected_date = expected_date - timedelta(days=7)
            
        for _ in range(520): # Max 10 years
            expected_week = expected_date.strftime('%G-%V')
            if expected_week in weeks:
                streak += 1
                expected_date -= timedelta(days=7)
            else:
                break
                
    return streak
