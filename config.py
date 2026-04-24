"""
config.py — Central configuration and constants for the Elite Fitness Dashboard.
"""

# ============================================================
# 🎯 GOALS & TARGETS
# ============================================================
DEFAULT_CAL_GOAL      = 2300
STREAK_TOLERANCE_KCAL = 150   # Hit your goal within +/- 150 kcal to keep streak alive
DEFAULT_WATER_GOAL    = 12    # Cups of water

# ============================================================
# 🥩 MACRO SPLIT (Percentage of total calories)
# ============================================================
MACRO_SPLIT_PROTEIN = 0.30
MACRO_SPLIT_CARBS   = 0.40
MACRO_SPLIT_FATS    = 0.30

# ============================================================
# 🏋️ EXERCISE DATA
# ============================================================
# Junk entries to filter out of the database when generating lists
JUNK_FILTER = [
    "Session Duration", "Walking", "Custom Ex", "Other",
    "n/a", "N/A", "test", "Trial", "Warm up", "Yoga"
]

# The "Playbook" — Grouped exercises to make logging faster.
EXERCISE_LIBRARY = {
    "UPPER A (Chest + Shoulders + Arms)": [
        "Machine Shoulder Press", "Incline Dumbbell/Chest Machine",
        "Chest Supported Row (Seated)", "Lat Pulldown",
        "Wide Grip Cable Row (Machine)", "Seated Bicep Curl",
        "Bicep Hammer Curls", "Tricep Rope Pushdowns"
    ],
    "LOWER A (Quads + Base)": [
        "Leg Press", "Smith Machine Squats", "Goblet Squat",
        "Seated Hamstring Leg Curl", "Seated Leg Extension", "Calf Raises"
    ],
    "UPPER B (Back + Shoulders + Arms)": [
        "Machine Shoulder Press", "Wide Grip Cable Row (Machine)",
        "Lat Pulldown", "Flat Chest Press Machine", "Seated Bicep Curl",
        "Over Head Tricep Extension DB", "Face Pulls", "Lateral Raises"
    ],
    "LOWER B (Posterior + Control)": [
        "Leg Press", "Goblet Squat", "Seated Hamstring Leg Curl",
        "Seated Leg Extension", "Calf Raises", "Cable Crunch"
    ],
}
