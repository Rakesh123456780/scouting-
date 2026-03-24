import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE products SET category = 'Toys' WHERE category = 'Toys & Games'")
conn.commit()
conn.close()
