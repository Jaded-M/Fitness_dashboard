from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from supabase_client import OWNER_USER_ID, supabase_client


PAGE_SIZE = 1000


def fetch_all_exercise_rows() -> list[dict]:
    rows: list[dict] = []
    start = 0

    while True:
        query = supabase_client.table("workouts").select("exercise")
        if OWNER_USER_ID:
            query = query.eq("user_id", OWNER_USER_ID)

        response = query.range(start, start + PAGE_SIZE - 1).execute()
        batch = response.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        start += PAGE_SIZE

    return rows


def main() -> None:
    exercises = {
        str(row.get("exercise", "")).strip()
        for row in fetch_all_exercise_rows()
        if str(row.get("exercise", "")).strip()
    }

    for exercise in sorted(exercises, key=str.casefold):
        print(exercise)


if __name__ == "__main__":
    main()
