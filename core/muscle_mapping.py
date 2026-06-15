from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MUSCLE_MAP_PATH = ROOT / "muscle_map.json"

CANONICAL_MUSCLE_GROUPS = [
    "Chest",
    "Back",
    "Shoulders",
    "Biceps",
    "Triceps",
    "Quads",
    "Hamstrings",
    "Glutes",
    "Calves",
    "Core",
    "Forearms",
]

STIMULUS_TYPES = ["push", "pull", "legs", "isolation", "core", "carry", "conditioning", "unknown"]

GROUP_ALIASES = {
    "arms": "Biceps",
    "abs": "Core",
    "abdom": "Core",
    "oblique": "Core",
    "hip flexor": "Core",
    "iliopsoas": "Core",
    "core": "Core",
    "legs": "Quads",
    "quadriceps": "Quads",
    "quad": "Quads",
    "vastus": "Quads",
    "delts": "Shoulders",
    "deltoid": "Shoulders",
    "rear delt": "Shoulders",
    "anterior delt": "Shoulders",
    "lateral delt": "Shoulders",
    "rotator cuff": "Shoulders",
    "infraspinatus": "Shoulders",
    "supraspinatus": "Shoulders",
    "trapezius": "Back",
    "trap": "Back",
    "rhomboid": "Back",
    "latissimus": "Back",
    "lat ": "Back",
    "teres": "Back",
    "erector": "Back",
    "biceps": "Biceps",
    "brachialis": "Biceps",
    "triceps": "Triceps",
    "anconeus": "Triceps",
    "glute": "Glutes",
    "adductor": "Glutes",
    "hamstring": "Hamstrings",
    "semitendinosus": "Hamstrings",
    "semimembranosus": "Hamstrings",
    "biceps femoris": "Hamstrings",
    "calf": "Calves",
    "gastrocnemius": "Calves",
    "soleus": "Calves",
    "tibialis": "Calves",
    "forearm": "Forearms",
    "brachioradialis": "Forearms",
    "pectoralis": "Chest",
    "pec ": "Chest",
    "serratus": "Chest",
}

EXERCISE_ALIASES = {
    "wide grip rows": "Wide Grip Cable Row (Machine)",
    "tricep pushdown": "Tricep Rope Pushdowns",
    "triceps pushdown": "Tricep Rope Pushdowns",
    "overhead tricep extension db": "Over Head Tricep Extension DB",
    "seated hamstring curls": "Seated Hamstring Leg Curl",
    "lateral raise": "Lateral Raises",
}


def normalize_name(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_group(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "Unknown"

    raw_lower = raw.lower()
    for token, canonical in GROUP_ALIASES.items():
        if token in raw_lower:
            return canonical

    for group in CANONICAL_MUSCLE_GROUPS:
        if group.lower() in raw_lower:
            return group

    return raw.title()


@lru_cache(maxsize=1)
def load_muscle_map() -> dict[str, dict[str, Any]]:
    if not MUSCLE_MAP_PATH.exists():
        return {}
    with MUSCLE_MAP_PATH.open("r", encoding="utf-8") as handle:
        return normalize_muscle_map(json.load(handle))


def save_muscle_map(data: dict[str, dict[str, Any]]) -> None:
    load_muscle_map.cache_clear()
    with MUSCLE_MAP_PATH.open("w", encoding="utf-8") as handle:
        json.dump(normalize_muscle_map(data), handle, indent=4)


def _lookup_entry(exercise: str, muscle_map: dict[str, dict[str, Any]]) -> tuple[str | None, dict[str, Any] | None]:
    if exercise in muscle_map:
        return exercise, muscle_map[exercise]

    normalized = normalize_name(exercise)
    alias_target = EXERCISE_ALIASES.get(normalized)
    if alias_target and alias_target in muscle_map:
        return alias_target, muscle_map[alias_target]

    for name, entry in muscle_map.items():
        if normalize_name(name) == normalized:
            return name, entry

    return None, None


def normalize_muscle_list(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw_items = [item.strip() for item in values.split(",") if item.strip()]
    else:
        raw_items = [str(item).strip() for item in values if str(item).strip()]

    seen: set[str] = set()
    result: list[str] = []
    for item in raw_items:
        group = normalize_group(item)
        key = normalize_name(group)
        if key and key not in seen and group != "Unknown":
            seen.add(key)
            result.append(group)
    return result


def normalize_stimulus_type(value: Any) -> str:
    normalized = normalize_name(value)
    if normalized in STIMULUS_TYPES:
        return normalized
    if normalized in {"leg", "lower"}:
        return "legs"
    if normalized in {"iso", "isolation movement"}:
        return "isolation"
    return "unknown"


def normalize_muscle_entry(entry: dict[str, Any]) -> dict[str, Any]:
    normalized_primary = normalize_group(entry.get("primary_group") or entry.get("primary_muscle"))
    secondary = normalize_muscle_list(entry.get("secondary_muscles"))
    tertiary = normalize_muscle_list(entry.get("tertiary_muscles"))
    stimulus = normalize_stimulus_type(entry.get("stimulus_type"))
    notes = str(entry.get("notes") or "").strip()

    return {
        "primary_group": normalized_primary,
        "secondary_muscles": secondary,
        "tertiary_muscles": tertiary,
        "stimulus_type": stimulus,
        "notes": notes,
    }


def normalize_muscle_map(data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for exercise, entry in (data or {}).items():
        name = str(exercise or "").strip()
        if not name:
            continue
        normalized[name] = normalize_muscle_entry(entry or {})
    return normalized


def canonical_exercise_name(exercise: str, muscle_map: dict[str, dict[str, Any]] | None = None) -> str:
    """Return the atlas/library name for aliases so UI lists do not duplicate exercises."""
    mapping = muscle_map or load_muscle_map()
    name, _ = _lookup_entry(exercise, mapping)
    return name or str(exercise or "").strip()


def dedupe_exercise_names(exercises: list[str], muscle_map: dict[str, dict[str, Any]] | None = None) -> list[str]:
    mapping = muscle_map or load_muscle_map()
    seen: set[str] = set()
    result: list[str] = []
    for exercise in exercises:
        canonical = canonical_exercise_name(exercise, mapping)
        key = normalize_name(canonical)
        if not canonical or key in seen:
            continue
        seen.add(key)
        result.append(canonical)
    return result


def exercise_muscle_profile(exercise: str, muscle_map: dict[str, dict[str, Any]] | None = None) -> dict[str, float]:
    """Return canonical muscle group contribution weights for one exercise."""
    mapping = muscle_map or load_muscle_map()
    _, entry = _lookup_entry(exercise, mapping)
    if not entry:
        return {}

    profile: dict[str, float] = {}
    primary = normalize_group(entry.get("primary_group") or entry.get("primary_muscle"))
    if primary != "Unknown":
        profile[primary] = profile.get(primary, 0.0) + 1.0

    for muscle in entry.get("secondary_muscles") or []:
        group = normalize_group(muscle)
        if group != "Unknown":
            profile[group] = profile.get(group, 0.0) + 0.55

    for muscle in entry.get("tertiary_muscles") or []:
        group = normalize_group(muscle)
        if group != "Unknown":
            profile[group] = profile.get(group, 0.0) + 0.25

    return profile


def exercise_stimulus_type(exercise: str, muscle_map: dict[str, dict[str, Any]] | None = None) -> str:
    mapping = muscle_map or load_muscle_map()
    _, entry = _lookup_entry(exercise, mapping)
    return str((entry or {}).get("stimulus_type") or "unknown").lower()


def unmapped_exercises(exercises: list[str], muscle_map: dict[str, dict[str, Any]] | None = None) -> list[str]:
    mapping = muscle_map or load_muscle_map()
    missing = []
    for exercise in exercises:
        _, entry = _lookup_entry(exercise, mapping)
        if not entry:
            missing.append(exercise)
    return missing
