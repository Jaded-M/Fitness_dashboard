from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

import json
import database
from components.widgets import check_new_pr
from core.muscle_mapping import canonical_exercise_name, dedupe_exercise_names, exercise_muscle_profile

# ── Constants ────────────────────────────────────────────────────────────────
_SESSION_KEY = "phi_wl_session"
_SPLITS = ["Upper A", "Lower A", "Upper B", "Lower B", "Full Body", "Conditioning", "Custom"]
_SPLIT_MAP = {
    "Upper A": "UPPER A (Chest + Shoulders + Arms)",
    "Lower A": "LOWER A (Quads + Base)",
    "Upper B": "UPPER B (Back + Shoulders + Arms)",
    "Lower B": "LOWER B (Posterior + Control)",
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _exercise_options(split: str = "") -> list[str]:
    """Split-specific library first, then DB history, then custom sentinel."""
    with open("exercise_library.json", "r", encoding="utf-8") as f:
        exercise_library = json.load(f)
    split_key = _SPLIT_MAP.get(split, "")
    curated = dedupe_exercise_names(list(exercise_library.get(split_key, [])))
    from_db = dedupe_exercise_names(database.get_unique_exercises())
    combined = dedupe_exercise_names(curated + [e for e in from_db if e not in curated])
    return combined + ["Custom..."]


def _empty_set(prev: dict | None = None, idx: int = 1) -> dict:
    """Return a new set row, autofilling weight/reps/RPE from the previous set."""
    if prev:
        return {
            "Set": idx,
            "Weight (kg)": float(prev.get("Weight (kg)", 0.0)),
            "Reps": int(prev.get("Reps", 8)),
            "RPE": float(prev.get("RPE", 7.0)),
            "Note": "",
        }
    return {"Set": idx, "Weight (kg)": 0.0, "Reps": 8, "RPE": 7.0, "Note": ""}


def _init_session() -> None:
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = {
            "date": date.today(),
            "split": "Upper A",
            "exercises": [],
        }


def _save_session(session: dict) -> None:
    """Persist every exercise+sets block to the database."""
    log_date = session["date"]
    split    = session["split"]
    saved    = 0
    for ex in session["exercises"]:
        name = ex.get("custom_name", "").strip() if ex.get("name") == "Custom..." else canonical_exercise_name(ex.get("name", "")).strip()
        if not name or not ex.get("sets"):
            continue
        sets_data = [
            {
                "weight": float(s.get("Weight (kg)", 0)),
                "reps":   int(s.get("Reps", 0)),
                "rpe":    float(s.get("RPE", 7)),
                "note":   str(s.get("Note", "")),
            }
            for s in ex["sets"]
            if int(s.get("Reps", 0)) > 0  # skip empty rows
        ]
        if sets_data:
            database.add_workout_with_sets(log_date, split, name, sets_data)
            saved += 1
    return saved


def _last_session_hint(exercise_name: str) -> None:
    """One-line caption showing the last session's sets and the PR."""
    if not exercise_name or exercise_name == "Custom...":
        return
    last = database.get_last_session_for_exercise(exercise_name)
    pr   = database.get_personal_best(exercise_name)
    if not last and pr is None:
        return
    parts = " · ".join(
        f"{float(s.get('weight', s.get('Weight (kg)', 0))):.1f}×{int(s.get('reps', s.get('Reps', 0)))}" for s in last[:5]
    ) if last else "—"
    pr_text = f"PR {pr:.1f} kg" if pr else ""
    st.caption(f"Last session: {parts}" + (f"  ·  {pr_text}" if pr_text else ""))


def _muscle_profile_hint(exercise_name: str) -> None:
    if not exercise_name or exercise_name == "Custom...":
        return
    profile = exercise_muscle_profile(exercise_name)
    if not profile:
        st.caption("Atlas mapping needed: this exercise will not affect readiness until mapped.")
        return
    ordered = sorted(profile.items(), key=lambda item: item[1], reverse=True)
    muscles = " · ".join(group for group, _ in ordered[:4])
    st.caption(f"Readiness impact: {muscles}")


# ── Callbacks for stable dialog state ─────────────────────────────────────────

def _cb_add_set(i: int):
    df_key = f"ws_df_{i}"
    editor_key = f"ws_sets_{i}"
    if df_key not in st.session_state:
        return
    base_df = st.session_state[df_key].copy()
    edits = st.session_state.get(editor_key, {}).get("edited_rows", {})
    for row_idx_str, row_edits in edits.items():
        row_idx = int(row_idx_str)
        if row_idx < len(base_df):
            for col, val in row_edits.items():
                base_df.at[row_idx, col] = val
    prev = base_df.iloc[-1].to_dict() if len(base_df) > 0 else None
    new_idx = len(base_df) + 1
    new_row = pd.DataFrame([_empty_set(prev, new_idx)])
    st.session_state[df_key] = pd.concat([base_df, new_row], ignore_index=True)
    if editor_key in st.session_state:
        del st.session_state[editor_key]

def _cb_remove_set(i: int):
    df_key = f"ws_df_{i}"
    editor_key = f"ws_sets_{i}"
    if df_key not in st.session_state:
        return
    base_df = st.session_state[df_key].copy()
    edits = st.session_state.get(editor_key, {}).get("edited_rows", {})
    for row_idx_str, row_edits in edits.items():
        row_idx = int(row_idx_str)
        if row_idx < len(base_df):
            for col, val in row_edits.items():
                base_df.at[row_idx, col] = val
    if len(base_df) > 1:
        st.session_state[df_key] = base_df.iloc[:-1]
        if editor_key in st.session_state:
            del st.session_state[editor_key]

def _cb_add_exercise():
    session = st.session_state[_SESSION_KEY]
    session["exercises"].append({"name": _exercise_options(session["split"])[0], "sets": [_empty_set(idx=1)]})

def _cb_remove_exercise(i: int):
    session = st.session_state[_SESSION_KEY]
    session["exercises"].pop(i)
    # Clean up associated dataframe state
    df_key = f"ws_df_{i}"
    if df_key in st.session_state:
        del st.session_state[df_key]


# ── Main dialog ───────────────────────────────────────────────────────────────

@st.dialog("Log Workout Session", width="large")
def workout_dialog():
    _init_session()
    session = st.session_state[_SESSION_KEY]
    exs     = session["exercises"]

    # ── Header ────────────────────────────────────────────────
    hc1, hc2 = st.columns(2)
    with hc1:
        session["date"] = st.date_input("Date", session["date"], key="ws_date")
    with hc2:
        split_idx = _SPLITS.index(session["split"]) if session["split"] in _SPLITS else 0
        session["split"] = st.selectbox("Split", _SPLITS, index=split_idx, key="ws_split")

    if not exs:
        st.markdown(
            "<p style='color:#64748b;font-size:0.88rem;padding:1rem 0;text-align:center'>"
            "No exercises added. Use <strong>Add Exercise</strong> below to begin.</p>",
            unsafe_allow_html=True,
        )

    # ── Exercise blocks ───────────────────────────────────────
    to_remove = None

    for i, ex in enumerate(exs):
        st.markdown(
            f"<div style='border-top:1px solid rgba(148,163,184,0.15);margin:0.75rem 0 0.5rem'></div>",
            unsafe_allow_html=True,
        )

        # Exercise selector row
        nc, rc = st.columns([5, 1])
        with nc:
            opts    = _exercise_options(session["split"])
            cur     = ex.get("name", opts[0] if opts else "")
            sel_idx = opts.index(cur) if cur in opts else 0
            chosen  = st.selectbox(
                f"Exercise {i + 1}",
                opts,
                index=sel_idx,
                key=f"ws_ex_{i}",
            )
            ex["name"] = chosen

        with rc:
            st.markdown("<div style='margin-top:1.75rem'></div>", unsafe_allow_html=True)
            st.button("Remove", key=f"ws_rm_ex_{i}", on_click=_cb_remove_exercise, args=(i,), use_container_width=True)

        # Custom name input
        if chosen == "Custom...":
            ex["custom_name"] = st.text_input(
                "Exercise name",
                value=ex.get("custom_name", ""),
                placeholder="e.g. Bulgarian Split Squat",
                key=f"ws_custom_{i}",
                label_visibility="collapsed",
            )

        # Last session / PR hint
        display_name = ex.get("custom_name", "") if chosen == "Custom..." else chosen
        _last_session_hint(display_name)
        _muscle_profile_hint(display_name)

        # ── Sets table ─────────────────────────────────────────
        df_key = f"ws_df_{i}"
        if df_key not in st.session_state:
            if not ex.get("sets"):
                ex["sets"] = [_empty_set(idx=1)]
            sets_df = pd.DataFrame(ex["sets"])
            for col, dtype in [("Weight (kg)", float), ("Reps", int), ("RPE", float)]:
                sets_df[col] = pd.to_numeric(sets_df.get(col, 0), errors="coerce").fillna(0)
            if "Note" not in sets_df.columns:
                sets_df["Note"] = ""
            sets_df["Set"] = range(1, len(sets_df) + 1)
            st.session_state[df_key] = sets_df[["Set", "Weight (kg)", "Reps", "RPE", "Note"]]

        edited = st.data_editor(
            st.session_state[df_key],
            key=f"ws_sets_{i}",
            hide_index=True,
            use_container_width=True,
            column_config={
                "Set": st.column_config.NumberColumn(
                    "Set", disabled=True, width="small"
                ),
                "Weight (kg)": st.column_config.NumberColumn(
                    "Weight (kg)", min_value=0.0, max_value=500.0,
                    step=2.5, format="%.1f", width="small",
                ),
                "Reps": st.column_config.NumberColumn(
                    "Reps", min_value=0, max_value=100, step=1, format="%d", width="small",
                ),
                "RPE": st.column_config.NumberColumn(
                    "RPE", min_value=5.0, max_value=10.0, step=0.5, format="%.1f", width="small",
                ),
                "Note": st.column_config.TextColumn(
                    "Note", max_chars=120, width="medium",
                ),
            },
            num_rows="fixed",
        )
        ex["sets"] = edited.to_dict("records")

        # Row controls
        ac, dc, _ = st.columns([1, 1, 5])
        with ac:
            st.button("+ Add Set", key=f"ws_add_set_{i}", on_click=_cb_add_set, args=(i,), use_container_width=True)
        with dc:
            st.button("Remove Last", key=f"ws_rm_set_{i}", on_click=_cb_remove_set, args=(i,), use_container_width=True, disabled=len(st.session_state[df_key]) <= 1)

    # ── Footer ────────────────────────────────────────────────
    st.markdown(
        "<div style='border-top:1px solid rgba(148,163,184,0.15);margin:1rem 0 0.5rem'></div>",
        unsafe_allow_html=True,
    )
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        st.button("+ Add Exercise", key="ws_add_ex", on_click=_cb_add_exercise, use_container_width=True)
    with fc2:
        if st.button("Clear Session", key="ws_clear", use_container_width=True):
            del st.session_state[_SESSION_KEY]
            st.rerun()
    with fc3:
        has_data = any(
            (ex.get("name") and ex.get("name") != "Custom..." or ex.get("custom_name"))
            and ex.get("sets")
            for ex in exs
        )
        if st.button("Save Session", key="ws_save", type="primary",
                     use_container_width=True, disabled=not has_data):
            n = _save_session(session)
            # PR detection — compare each exercise's top set against all-time best
            for ex in exs:
                ename = (
                    ex.get("custom_name", "").strip()
                    if ex.get("name") == "Custom..."
                    else ex.get("name", "").strip()
                )
                if not ename or not ex.get("sets"):
                    continue
                max_wt = max(
                    (float(s.get("Weight (kg)", 0)) for s in ex["sets"]),
                    default=0.0,
                )
                if max_wt > 0:
                    check_new_pr(ename, max_wt)
            del st.session_state[_SESSION_KEY]
            st.toast(f"Session saved — {n} exercise(s) logged.")
            st.rerun()


# ── Other quick-log dialogs ───────────────────────────────────────────────────

@st.dialog("Log meal")
def meal_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_food_date")
    meal = st.radio("Meal", ["Breakfast", "Lunch", "Snack", "Dinner"], horizontal=True, key="ql_meal")
    name = st.text_input("Food", placeholder="Chicken rice bowl", key="ql_food")
    c1, c2 = st.columns(2)
    calories = c1.number_input("Calories", 0, 5000, 450, step=25, key="ql_calories")
    protein  = c2.number_input("Protein g", 0, 400, 30, key="ql_protein")
    c3, c4, c5 = st.columns(3)
    carbs = c3.number_input("Carbs g",  0, 600, 45, key="ql_carbs")
    fats  = c4.number_input("Fats g",   0, 300, 12, key="ql_fats")
    fiber = c5.number_input("Fiber g",  0, 100,  4, key="ql_fiber")
    if st.button("Save meal", type="primary", use_container_width=True):
        if not name.strip() or calories <= 0:
            st.warning("Food name and calories are required.")
            return
        database.add_food_log(log_date, name.strip(), calories, protein, carbs, fats, fiber, meal)
        st.toast("Meal saved.")
        st.rerun()


@st.dialog("Log weight")
def weight_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_weight_date")
    weight = st.number_input("Weight kg", 0.0, 300.0, 80.0, step=0.1, format="%.1f", key="ql_weight_kg")
    waist  = st.number_input("Waist inches (optional)", 0.0, 100.0, 0.0, step=0.1, key="ql_waist")
    if st.button("Save weight", type="primary", use_container_width=True):
        if weight <= 0:
            st.warning("Enter a weight above zero.")
            return
        database.add_measurement(log_date, weight, waist or None)
        st.toast("Weight saved.")
        st.rerun()


@st.dialog("Log activity")
def steps_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_steps_date")
    steps    = st.number_input("Steps", 0, 100_000, 8000, step=500, key="ql_steps")
    distance = round(steps * 0.00076, 2)
    active_m = round(steps / 100, 0)
    st.caption(f"Estimated distance: {distance} km  ·  Active minutes: {int(active_m)}")
    if st.button("Save activity", type="primary", use_container_width=True):
        database.add_steps(log_date.isoformat(), steps, distance, active_m)
        st.toast("Activity saved.")
        st.rerun()


@st.dialog("Daily check-in")
def checkin_dialog():
    log_date = st.date_input("Date", date.today(), key="ql_checkin_date")
    c1, c2, c3 = st.columns(3)
    mood  = c1.slider("Mood",   1, 5, 3, key="ql_mood")
    energy = c2.slider("Energy", 1, 5, 3, key="ql_energy")
    sleep = c3.number_input("Sleep hours", 0.0, 16.0, 7.0, step=0.25, key="ql_sleep")
    note  = st.text_area("Note", placeholder="How did today feel?", key="ql_note")
    if st.button("Save check-in", type="primary", use_container_width=True):
        database.add_checkin(log_date.isoformat(), mood, energy, sleep, note.strip())
        st.toast("Check-in saved.")
        st.rerun()


def render_quick_actions():
    st.markdown(
        """
        <div class="phi-action-bar">
            <div class="phi-action-bar-label">Log Today</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("🏋️ Workout", type="primary", use_container_width=True):
        workout_dialog()
    if c2.button("Meal", use_container_width=True):
        meal_dialog()
    if c3.button("⚖️ Weight", use_container_width=True):
        weight_dialog()
    if c4.button("👟 Activity", use_container_width=True):
        steps_dialog()
    if c5.button("📝 Check-in", use_container_width=True):
        checkin_dialog()
    st.markdown("</div>", unsafe_allow_html=True)
