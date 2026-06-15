import sqlite3

conn = sqlite3.connect('fitness.db')
c = conn.cursor()

# Define the mapping of duplicate names to standardized names
mapping = {
    "Chest Supported Row's": "Chest Supported Row",
    "Flat Machine Chest Press": "Flat Chest Press Machine",
    "Machine Chest Press": "Flat Chest Press Machine",
    "Goblet Squats": "Goblet Squat",
    "Lateral Raises": "Lateral Raise",
    "Preacher Hammer Curls": "Preacher Hammer Curl",
    "Seated Bicep Curls": "Seated Bicep Curl",
    "Seated Hamstring Leg Curl": "Seated Hamstring Curls",
    "Tricep Rope Pushdowns": "Tricep Pushdown",
    "Wide Grip Cable Row (Machine)": "Wide Grip Rows",
    "Over Head Tricep Extension DB": "Overhead Tricep Extension",
    "Leg Press (Wide Stance - Abductors and Glutes)": "Leg Press"
}

print("Updating duplicates in the database...")
for old_name, new_name in mapping.items():
    c.execute("UPDATE workouts SET exercise = ? WHERE exercise = ?", (new_name, old_name))
    print(f"Updated '{old_name}' -> '{new_name}' ({c.rowcount} rows)")

conn.commit()
conn.close()
print("Done! Duplicates have been merged.")
