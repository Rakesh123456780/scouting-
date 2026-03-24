import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")
conn = sqlite3.connect(DB_PATH)

try:
    conn.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
    conn.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass # columns might already exist

conn.commit()
conn.close()
