"""
# ════════════════════════════════════════════════════════════════
# SCRIPT: core/sanitize_db.py
# ════════════════════════════════════════════════════════════════
# // WHAT IT DOES:
#    This is a ONE-TIME migration script that cleans up your gym.db
#    by merging duplicate exercise names into their canonical form.
#
# // HOW IT WORKS:
#    1. Creates a BACKUP of your database (gym_backup.db) — safety first.
#    2. Reads a "merge map" dictionary — old_name: new_name.
#    3. For each entry, runs an SQL UPDATE to rename exercises in bulk.
#    4. Deletes known junk entries (test data, walking, etc).
#    5. Prints a before/after summary so you can verify nothing was lost.
#
# // WHY WE DO IT THIS WAY:
#    SQL UPDATE is atomic — it either renames ALL matching rows or NONE.
#    This is much safer than reading rows into Python, modifying them,
#    and writing them back (which risks data corruption if it crashes mid-way).
#
# // HOW TO RUN:
#    python core/sanitize_db.py
#
# // IMPORTANT:
#    Run this ONCE. After that, the EXERCISE_LIBRARY in Fitness.py
#    will use the canonical names, preventing future duplicates.
# ════════════════════════════════════════════════════════════════
"""

import sqlite3
import shutil
import os

# ────────────────────────────────────────────────────────────
# STEP 1: CONFIGURATION
# ────────────────────────────────────────────────────────────
# The path to your database file.
# We use os.path.join so it works on both Windows and Mac.
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "gym.db")
BACKUP_PATH = os.path.join(os.path.dirname(__file__), "..", "gym_backup.db")

# ────────────────────────────────────────────────────────────
# STEP 2: THE MERGE MAP
# ────────────────────────────────────────────────────────────
# This dictionary maps OLD exercise names → their CANONICAL name.
#
# // PYTHON CONCEPT: Dictionary (dict)
# A dict is like a lookup table. The KEY (left side) is what we're
# searching for in the database. The VALUE (right side) is what we
# replace it with.
#
# // WHY THESE SPECIFIC MERGES?
# These were identified by scanning gym.db and finding exercises
# that are the same movement but saved under different names
# (typos, abbreviations, or name changes over time).
MERGE_MAP = {
    # Bicep variants — "Hammer Curl" is actually what you call "Seated Bicep Curl"
    "Hammer Curl":            "Seated Bicep Curl",

    # Shoulder press — library had a different name than muscle_map.json
    "Shoulder Press Machine": "Machine Shoulder Press",

    # Tricep variants — three names for the same cable pushdown
    "Tricep Pushdown":        "Tricep Rope Pushdowns",
    "Tricep Rope Pushdown":   "Tricep Rope Pushdowns",

    # Pec Deck variants — two names for the same fly machine
    "Pec Deck / Cable Fly":   "Pec Deck Fly (Machine/Cable)",
    "Pec Deck Fly":           "Pec Deck Fly (Machine/Cable)",

    # Leg variants — short names that should match the full muscle_map name
    "Calves":                 "Calf Raises",
    "Hamstring Curl":         "Seated Hamstring Leg Curl",
    "Leg Extension":          "Seated Leg Extension",
    "Seated Hamstring Curl":  "Seated Hamstring Leg Curl",

    # Row variants — "Seated Row" and "Machine Row" are both the wide grip row machine
    "Seated Row":             "Wide Grip Cable Row (Machine)",
    "Machine Row":            "Wide Grip Cable Row (Machine)",
}

# ────────────────────────────────────────────────────────────
# STEP 3: JUNK ENTRIES TO DELETE
# ────────────────────────────────────────────────────────────
# These are test/junk entries that shouldn't be in your training data.
# We delete them outright instead of renaming.
JUNK_EXERCISES = [
    "My Custom Exercise",
    "Walking (Target 7-10k)",
    "Wrist Extension and Wrist Curls",
]

# ════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════════════════════════

def run_sanitization():
    """
    // WHAT IT DOES: Executes the full cleanup pipeline.
    // HOW IT WORKS: Opens the DB, runs UPDATEs and DELETEs, prints results.
    // WHY A FUNCTION: Wrapping in a function means we can call it from
    //                 other scripts later if needed (testability).
    """

    # ── 1. BACKUP ──────────────────────────────────────────────
    # shutil.copy2() copies the file AND preserves its metadata (timestamps).
    # This is your insurance policy — if anything goes wrong, you can
    # restore gym_backup.db → gym.db and pretend this never happened.
    print("=" * 60)
    print("🔒 PHASE 0: DATABASE SANITIZATION")
    print("=" * 60)

    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Backup created: {BACKUP_PATH}")
    else:
        print(f"❌ Database not found at {DB_PATH}")
        return

    # ── 2. CONNECT ─────────────────────────────────────────────
    # sqlite3.connect() opens a connection to the database file.
    # Think of 'conn' as an open phone line to the database.
    # 'cursor' is the "voice" on that line — it sends SQL commands.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── 3. BEFORE COUNT ────────────────────────────────────────
    # We count unique exercise names BEFORE making changes.
    # This lets us print a "before vs after" comparison at the end.
    cursor.execute("SELECT COUNT(DISTINCT exercise) FROM workouts")
    before_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM workouts")
    before_total = cursor.fetchone()[0]

    print(f"\n📊 BEFORE: {before_count} unique exercises, {before_total} total logs")
    print("-" * 60)

    # ── 4. APPLY MERGES ────────────────────────────────────────
    # For each entry in MERGE_MAP, we run an SQL UPDATE statement.
    #
    # // SQL CONCEPT: UPDATE ... SET ... WHERE
    # UPDATE workouts           ← "go to the workouts table"
    # SET exercise = ?          ← "change the exercise column to this new value"
    # WHERE exercise = ?        ← "but ONLY on rows where exercise matches the old name"
    #
    # The '?' are called "parameterized queries" — they prevent SQL injection
    # (a security attack where someone types SQL code into an input field).
    # Even though we're the only users, it's good practice to ALWAYS use '?'.
    print("\n🔄 APPLYING MERGES:")
    for old_name, new_name in MERGE_MAP.items():
        # cursor.rowcount tells us how many rows were actually changed
        cursor.execute(
            "UPDATE workouts SET exercise = ? WHERE exercise = ?",
            (new_name, old_name)
        )
        changed = cursor.rowcount
        if changed > 0:
            print(f"   ✅ '{old_name}' → '{new_name}' ({changed} rows)")
        else:
            print(f"   ⏭️  '{old_name}' — no rows found (already clean)")

    # ── 5. DELETE JUNK ─────────────────────────────────────────
    # DELETE FROM workouts WHERE exercise = ?
    # This permanently removes rows. That's why we made a backup first!
    print("\n🗑️  DELETING JUNK:")
    for junk_name in JUNK_EXERCISES:
        cursor.execute(
            "DELETE FROM workouts WHERE exercise = ?",
            (junk_name,)
        )
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"   🗑️  Deleted '{junk_name}' ({deleted} rows)")
        else:
            print(f"   ⏭️  '{junk_name}' — not found")

    # ── 6. COMMIT ──────────────────────────────────────────────
    # conn.commit() is CRITICAL. Without it, all our changes are temporary
    # and would be lost when we close the connection.
    #
    # // DATABASE CONCEPT: Transactions
    # SQLite wraps all our changes in a "transaction." Think of it like
    # typing a long email — nothing is sent until you hit the "Send" button.
    # commit() IS that send button.
    conn.commit()

    # ── 7. AFTER COUNT ─────────────────────────────────────────
    cursor.execute("SELECT COUNT(DISTINCT exercise) FROM workouts")
    after_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM workouts")
    after_total = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print(f"📊 AFTER:  {after_count} unique exercises, {after_total} total logs")
    print(f"📉 Reduced from {before_count} → {after_count} unique names")
    print(f"🗑️  Removed {before_total - after_total} junk logs")
    print("=" * 60)

    # ── 8. PRINT FINAL EXERCISE LIST ───────────────────────────
    # This is your "receipt" — a clean list of every exercise now in your DB.
    # If something looks wrong, you can restore from gym_backup.db.
    print("\n📋 FINAL EXERCISE LIST:")
    cursor.execute(
        "SELECT exercise, COUNT(*) as cnt FROM workouts "
        "WHERE exercise != 'Session Duration' "
        "GROUP BY exercise ORDER BY cnt DESC"
    )
    for row in cursor.fetchall():
        print(f"   {row[0]:40s} | {row[1]:3d} logs")

    # ── 9. CLOSE ───────────────────────────────────────────────
    # Always close the connection when done. This frees up the file lock
    # so other programs (like Streamlit) can use the database.
    conn.close()
    print("\n✅ Sanitization complete. Backup at: gym_backup.db")


# ════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════
# // PYTHON CONCEPT: if __name__ == "__main__"
# This is a "guard clause." It means: "Only run this code if this
# file is executed DIRECTLY (python sanitize_db.py), not if it's
# imported by another file."
#
# Why? Because we might want to import MERGE_MAP from this file
# in Fitness.py later (to auto-correct names on save). If we didn't
# have this guard, importing would accidentally run the whole script!
if __name__ == "__main__":
    run_sanitization()
