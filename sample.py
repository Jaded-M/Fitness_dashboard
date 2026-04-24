import sqlite3
import pandas as pd

conn = sqlite3.connect('gym.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        split TEXT,
        exercise TEXT,
        sets INTEGER,
        reps INTEGER,
        weight INTEGER,
        duration INTEGER,
        notes TEXT
    )
''')

conn.commit()
conn.close()


