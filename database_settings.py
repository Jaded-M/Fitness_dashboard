"""
database_settings.py — Supabase-backed user goal persistence for the PHI dashboard.
"""

from config import DEFAULT_CAL_GOAL, DEFAULT_STEP_GOAL, DEFAULT_PROTEIN_TARGET
from supabase_client import get_supabase_client, get_current_user_id

_DEFAULTS = {
    "calorie_goal": DEFAULT_CAL_GOAL,
    "step_goal": DEFAULT_STEP_GOAL,
    "protein_target": DEFAULT_PROTEIN_TARGET,
}


def load_user_settings() -> dict:
    """Fetch calorie_goal, step_goal, protein_target for the current user.

    Returns a dict with those three keys. Falls back to config.py defaults
    if the user has no row yet or if Supabase is unreachable.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return dict(_DEFAULTS)

        client = get_supabase_client()
        result = (
            client.table("user_settings")
            .select("calorie_goal, step_goal, protein_target")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if result.data:
            return {
                "calorie_goal": result.data.get("calorie_goal", _DEFAULTS["calorie_goal"]),
                "step_goal": result.data.get("step_goal", _DEFAULTS["step_goal"]),
                "protein_target": result.data.get("protein_target", _DEFAULTS["protein_target"]),
            }
    except Exception:
        pass

    return dict(_DEFAULTS)


def save_user_settings(calorie_goal: int, step_goal: int, protein_target: int) -> None:
    """Upsert calorie_goal, step_goal, protein_target for the current user.

    Silently swallows any Supabase errors so a network hiccup never breaks the UI.
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return

        client = get_supabase_client()
        client.table("user_settings").upsert(
            {
                "user_id": user_id,
                "calorie_goal": int(calorie_goal),
                "step_goal": int(step_goal),
                "protein_target": int(protein_target),
            },
            on_conflict="user_id",
        ).execute()
    except Exception:
        pass
