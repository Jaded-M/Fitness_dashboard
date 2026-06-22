import json
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase_client import OWNER_USER_ID, supabase_client

DB_NAME = "fitness.db" # Left for legacy compatibility checks if any
PAGE_SIZE = 1000


def _report_error(context: str, exc: Exception) -> None:
    st.error(f"{context} failed: {exc}")


def _with_user(data: dict) -> dict:
    return {"user_id": OWNER_USER_ID, **data} if OWNER_USER_ID else data


def _apply_owner_filter(query):
    return query.eq("user_id", OWNER_USER_ID) if OWNER_USER_ID else query


def _fetch_all_rows(table_name: str, columns: str = "*", order_by: str | None = None, desc: bool = False, query_fn=None):
    rows = []
    start = 0

    while True:
        query = supabase_client.table(table_name).select(columns)
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        if query_fn is not None:
            query = query_fn(query)
        if order_by:
            query = query.order(order_by, desc=desc)

        response = query.range(start, start + PAGE_SIZE - 1).execute()
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    return rows

def init_db():
    """No-op for Supabase."""
    pass

# ================================================================
# WORKOUTS
# ================================================================

def add_workout(date, split, exercise, sets, reps, weight, rpe, fatigue, duration=0, set_data=None):
    """Add a workout log (legacy single-set format)."""
    data = {
        "date": str(date),
        "split": split,
        "exercise": exercise,
        "sets": int(float(sets or 0)),
        "reps": int(float(reps or 0)),
        "weight": float(weight or 0),
        "rpe": float(rpe or 0),
        "fatigue": fatigue,
        "duration": int(float(duration or 0)),
        "set_data": set_data
    }
    if weight and (float(weight) < 0 or reps < 0):
        st.error("Please enter a valid weight")
        return
    try:
        supabase_client.table("workouts").insert(_with_user(data)).execute()
    except Exception as exc:
        _report_error("Saving workout", exc)
        return
    get_all_workouts.clear()
    get_unique_exercises.clear()
    get_best_lifts.clear()
    get_exercise_history.clear()

def add_workout_with_sets(log_date, split: str, exercise: str, sets_data: list) -> None:
    """Save a workout with full per-set detail stored as JSON in set_data."""
    if not sets_data:
        return
    weights    = [float(s.get("weight", 0)) for s in sets_data]
    reps_list  = [int(s.get("reps", 0))     for s in sets_data]
    rpe_list   = [float(s.get("rpe", 7))    for s in sets_data]
    max_weight = max(weights)  if weights   else 0.0
    total_reps = sum(reps_list)
    avg_rpe    = sum(rpe_list) / len(rpe_list) if rpe_list else 7.0
    
    data = {
        "date": str(log_date),
        "split": split,
        "exercise": exercise,
        "sets": len(sets_data),
        "reps": total_reps,
        "weight": max_weight,
        "rpe": avg_rpe,
        "fatigue": "Medium",
        "duration": 0,
        "set_data": sets_data
    }
    try:
        supabase_client.table("workouts").insert(_with_user(data)).execute()
    except Exception as exc:
        _report_error("Saving workout session", exc)
        return
    get_all_workouts.clear()
    get_unique_exercises.clear()
    get_best_lifts.clear()
    get_exercise_history.clear()

@st.cache_data(ttl=300)
def get_all_workouts():
    try:
        return pd.DataFrame(_fetch_all_rows("workouts", order_by="date", desc=True))
    except Exception as e:
        _report_error("Loading workouts", e)
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_unique_exercises():
    try:
        df = pd.DataFrame(_fetch_all_rows("workouts", columns="exercise"))
        if df.empty: return []
        return df["exercise"].dropna().astype(str).value_counts().index.tolist()
    except Exception as e:
        _report_error("Loading exercise library", e)
        return []

def delete_workout_by_id(workout_id):
    try:
        query = supabase_client.table("workouts").delete().eq("id", workout_id)
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        query.execute()
    except Exception as exc:
        _report_error("Deleting workout", exc)
        return
    get_all_workouts.clear()
    get_unique_exercises.clear()
    get_best_lifts.clear()
    get_exercise_history.clear()

@st.cache_data(ttl=300)
def get_best_lifts():
    try:
        df = pd.DataFrame(
            _fetch_all_rows(
                "workouts",
                columns="exercise, weight, reps",
                query_fn=lambda q: q.neq("exercise", "Session Duration"),
            )
        )
        if df.empty: return df
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.0)
        df["reps"] = pd.to_numeric(df["reps"], errors="coerce").fillna(0).astype(int)
        df = df.sort_values(["exercise", "weight", "reps"], ascending=[True, False, False])
        best_rows = df.groupby("exercise", as_index=False).first()
        sessions = df.groupby("exercise").size().rename("sessions").reset_index()
        merged = best_rows.merge(sessions, on="exercise", how="left")
        merged = merged.rename(columns={"weight": "best_weight", "reps": "best_reps"})
        return merged.sort_values("best_weight", ascending=False)
    except Exception as e:
        _report_error("Loading personal records", e)
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_exercise_history(exercise_name, limit=5):
    try:
        query = supabase_client.table("workouts").select("date, sets, reps, weight, rpe, set_data").eq("exercise", exercise_name).neq("exercise", "Session Duration")
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        response = query.order("date", desc=True).limit(limit).execute()
        return pd.DataFrame(response.data)
    except Exception as exc:
        _report_error(f"Loading exercise history for {exercise_name}", exc)
        return pd.DataFrame()

def get_last_session_for_exercise(exercise_name: str) -> list:
    try:
        query = supabase_client.table("workouts").select("sets, reps, weight, rpe, set_data").eq("exercise", exercise_name).neq("exercise", "Session Duration")
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        response = query.order("date", desc=True).limit(1).execute()
        if not response.data:
            return []
        row = response.data[0]
        if row.get("set_data"):
            if isinstance(row["set_data"], list):
                return row["set_data"]
            elif isinstance(row["set_data"], str):
                return json.loads(row["set_data"])
                
        n = max(int(row["sets"]), 1)
        per_set_reps = max(int(row["reps"] / n), 1)
        return [{"weight": float(row["weight"]),
                 "reps": per_set_reps,
                 "rpe": float(row["rpe"] or 7),
                 "note": ""}] * n
    except Exception as exc:
        _report_error(f"Loading last session for {exercise_name}", exc)
        return []

def get_personal_best(exercise_name: str):
    try:
        query = supabase_client.table("workouts").select("weight").eq("exercise", exercise_name).neq("exercise", "Session Duration")
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        response = query.execute()
        weights = [r["weight"] for r in response.data if r["weight"] is not None]
        return max(weights) if weights else None
    except Exception as exc:
        _report_error(f"Loading personal best for {exercise_name}", exc)
        return None

def get_weekly_volume_by_split(weeks=4):
    try:
        days = weeks * 7
        cutoff = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        df = pd.DataFrame(
            _fetch_all_rows(
                "workouts",
                columns="date, split, weight, reps",
                query_fn=lambda q: q.neq("exercise", "Session Duration").gte("date", cutoff),
            )
        )
        if df.empty: return df
        df["date"] = pd.to_datetime(df["date"])
        df["week"] = df["date"].dt.strftime('%Y-W%V')
        df["volume"] = df["weight"] * df["reps"]
        
        grouped = df.groupby(["week", "split"]).agg(
            total_volume=("volume", "sum"),
            session_count=("date", "nunique")
        ).reset_index().sort_values("week", ascending=False)
        return grouped
    except Exception as exc:
        _report_error("Loading weekly volume", exc)
        return pd.DataFrame()

# ================================================================
# STEPS
# ================================================================

def add_steps(date, steps, distance=0, active_minutes=0):
    try:
        steps_int = int(float(steps))
    except (ValueError, TypeError):
        steps_int = 0
    try:
        active_mins_int = int(float(active_minutes))
    except (ValueError, TypeError):
        active_mins_int = 0
    try:
        distance_float = float(distance)
    except (ValueError, TypeError):
        distance_float = 0.0

    data = {"date": str(date), "steps": steps_int, "distance": distance_float, "active_minutes": active_mins_int}
    try:
        supabase_client.table("steps").upsert(_with_user(data), on_conflict="user_id,date" if OWNER_USER_ID else "date").execute()
    except Exception as exc:
        _report_error("Saving steps", exc)
        return
    get_steps_data.clear()

@st.cache_data(ttl=300)
def get_steps_data(start_date=None, end_date=None):
    try:
        def apply_filters(query):
            if start_date:
                query = query.gte("date", str(start_date))
            if end_date:
                query = query.lte("date", str(end_date))
            return query

        return pd.DataFrame(
            _fetch_all_rows(
                "steps",
                order_by="date",
                query_fn=apply_filters,
            )
        )
    except Exception as exc:
        _report_error("Loading steps", exc)
        return pd.DataFrame()

def delete_steps_by_date(date):
    try:
        query = supabase_client.table("steps").delete().eq("date", str(date))
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        query.execute()
    except Exception as exc:
        _report_error("Deleting steps", exc)
        return
    get_steps_data.clear()

# ================================================================
# NUTRITION
# ================================================================

def add_food_log(date, food_item, calories, protein=0, carbs=0, fats=0, fiber=0, meal_type="Snack"):
    data = {
        "date": str(date), "food_item": food_item, 
        "calories": int(float(calories or 0)), 
        "protein": int(float(protein or 0)), 
        "carbs": int(float(carbs or 0)), 
        "fats": int(float(fats or 0)), 
        "fiber": int(float(fiber or 0)), 
        "meal_type": meal_type
    }
    try:
        supabase_client.table("food_logs").insert(_with_user(data)).execute()
    except Exception as exc:
        _report_error("Saving food log", exc)
        return
    get_food_logs.clear()

def add_draft_food(food_item, calories, protein=0, carbs=0, fats=0, fiber=0):
    if "draft_foods" not in st.session_state:
        st.session_state.draft_foods = []
    st.session_state.draft_foods.append({
        "food_item": food_item, "calories": calories, "protein": protein, 
        "carbs": carbs, "fats": fats, "fiber": fiber
    })

def get_draft_foods():
    if "draft_foods" not in st.session_state:
        return pd.DataFrame(columns=["food_item", "calories", "protein", "carbs", "fats", "fiber"])
    return pd.DataFrame(st.session_state.draft_foods)

def clear_draft_foods():
    if "draft_foods" in st.session_state:
        st.session_state.draft_foods = []

@st.cache_data(ttl=300)
def get_food_logs():
    try:
        df = pd.DataFrame(_fetch_all_rows("food_logs", order_by="date", desc=True))
        num_cols = ["calories", "protein", "carbs", "fats", "fiber"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except Exception as exc:
        _report_error("Loading food logs", exc)
        return pd.DataFrame()

def log_water(date, cups=1):
    try:
        supabase_client.table("water_logs").insert(_with_user({"date": str(date), "cups": cups})).execute()
    except Exception as exc:
        _report_error("Saving water log", exc)
        return
    get_water_history.clear()

@st.cache_data(ttl=300)
def get_water_history():
    try:
        return pd.DataFrame(_fetch_all_rows("water_logs", order_by="date", desc=True))
    except Exception as exc:
        _report_error("Loading water logs", exc)
        return pd.DataFrame()

def delete_food_log(log_id):
    try:
        query = supabase_client.table("food_logs").delete().eq("id", log_id)
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)
        query.execute()
    except Exception as exc:
        _report_error("Deleting food log", exc)
        return
    get_food_logs.clear()

# ================================================================
# MEASUREMENTS
# ================================================================

def add_measurement(date, weight, waist=None, hips=None, thigh=None, chest=None, arms=None):
    data = {
        "date": str(date), "weight": weight, "waist": waist, 
        "hips": hips, "thigh": thigh, "chest": chest, "arms": arms
    }
    try:
        supabase_client.table("measurements").insert(_with_user(data)).execute()
    except Exception as exc:
        _report_error("Saving measurement", exc)
        return
    get_measurements.clear()

@st.cache_data(ttl=300)
def get_measurements():
    try:
        df = pd.DataFrame(_fetch_all_rows("measurements", order_by="date", desc=False))
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.rename(columns={
                "date": "Date", "weight": "Weight", "waist": "Waist",
                "hips": "Hips", "thigh": "Thigh", "chest": "Chest", "arms": "Arms",
            })
        return df
    except Exception as exc:
        _report_error("Loading measurements", exc)
        return pd.DataFrame()

# ================================================================
# DAILY CHECK-INS
# ================================================================

def add_checkin(date, mood=3, energy=3, sleep_hours=None, note=""):
    data = {
        "date": str(date), "mood": mood, "energy": energy, 
        "sleep_hours": sleep_hours, "note": note
    }
    try:
        supabase_client.table("checkins").insert(_with_user(data)).execute()
    except Exception as exc:
        _report_error("Saving check-in", exc)
        return
    get_checkins.clear()

@st.cache_data(ttl=300)
def get_checkins():
    try:
        return pd.DataFrame(_fetch_all_rows("checkins", order_by="date", desc=True))
    except Exception as exc:
        _report_error("Loading check-ins", exc)
        return pd.DataFrame()
