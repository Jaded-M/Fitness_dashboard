"""
config.py — Central configuration and constants for the Elite Fitness Dashboard.
"""

# ============================================================
# 🎯 GOALS & TARGETS
# ============================================================
DEFAULT_CAL_GOAL        = 2300
DEFAULT_STEP_GOAL       = 8000    # Daily step target
DEFAULT_PROTEIN_TARGET  = 150     # Daily protein target in grams
DEFAULT_WATER_GOAL_L    = 3.0     # Daily water target in litres
STREAK_TOLERANCE_KCAL   = 150     # Hit your goal within +/- 150 kcal to keep streak alive
DEFAULT_WATER_GOAL      = 12      # Cups of water

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

# EXERCISE_LIBRARY has been moved to exercise_library.json
