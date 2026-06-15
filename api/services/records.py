from __future__ import annotations

import json
from typing import Any


def epley_1rm(weight: float, reps: int) -> float:
    if weight <= 0 or reps <= 0:
        return 0.0
    return weight if reps == 1 else weight * (1 + reps / 30)


def top_set(row: dict[str, Any]) -> tuple[float, int]:
    set_data = row.get("set_data")
    if isinstance(set_data, str):
        try:
            set_data = json.loads(set_data)
        except json.JSONDecodeError:
            set_data = None

    pairs: list[tuple[float, int]] = []
    if isinstance(set_data, list):
        pairs = [
            (float(item.get("weight", 0) or 0), int(item.get("reps", 0) or 0))
            for item in set_data
        ]

    if not pairs:
        pairs = [(float(row.get("weight", 0) or 0), int(row.get("reps", 0) or 0))]

    return max(pairs, default=(0.0, 0))


def record_board(workouts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for row in workouts:
        exercise = str(row.get("exercise", "")).strip()
        if not exercise or exercise == "Session Duration":
            continue
        weight, reps = top_set(row)
        estimated_1rm = epley_1rm(weight, reps)
        current = records.get(exercise)
        if current is None or estimated_1rm > current["estimated_1rm"]:
            records[exercise] = {
                "exercise": exercise,
                "weight": weight,
                "reps": reps,
                "estimated_1rm": round(estimated_1rm, 1),
                "date": row.get("date"),
            }

    return sorted(records.values(), key=lambda item: item["estimated_1rm"], reverse=True)
