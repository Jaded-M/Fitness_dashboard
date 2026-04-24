import sqlite3
import pandas as pd

conn = sqlite3.connect("fitness.db")
c = conn.cursor()
c.execute("PRAGMA table_info(steps)")
print("Table Info for 'steps':")
for row in c.fetchall():
    print(row)

c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'")
print("\nCreate SQL for 'steps':")
print(c.fetchone()[0])
conn.close()
