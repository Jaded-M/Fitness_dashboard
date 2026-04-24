import sqlite3

conn = sqlite3.connect('gym.db')
cursor = conn.cursor()

# List all tables
cursor.execute("ID", "Date", "Split", "Exercise", "Sets", "Reps", "Weight (kg)")
print(cursor.fetchall())

# Read a table
cursor.execute("SELECT * FROM Exercise")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()