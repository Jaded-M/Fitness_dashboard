from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from supabase_client import OWNER_USER_ID, supabase_client


EXERCISE_MERGES = [
    ("Lateral Raise", "Lateral Raises"),
    ("Leg Extension", "Seated Leg Extension"),
    ("Over Head Tricep Extension DB", "Overhead Tricep Extension DB"),
    ("Seated Hamstring Curls", "Seated Hamstring Leg Curl"),
    ("Tricep Pushdown", "Tricep Rope Pushdowns"),
    ("Wide Grip Rows", "Wide Grip Cable Row (Machine)"),
]


def update_exercise_name(old_name: str, new_name: str) -> int:
    query = (
        supabase_client.table("workouts")
        .update({"exercise": new_name})
        .eq("exercise", old_name)
    )
    if OWNER_USER_ID:
        query = query.eq("user_id", OWNER_USER_ID)

    response = query.execute()
    return len(response.data or [])


def main() -> None:
    for old_name, new_name in EXERCISE_MERGES:
        updated = update_exercise_name(old_name, new_name)
        print(f"{old_name} -> {new_name}: updated {updated} row(s)")


if __name__ == "__main__":
    main()
