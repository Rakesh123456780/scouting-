import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")
conn = sqlite3.connect(DB_PATH)

updates = [
    ("Health", "Health & Beauty"),
    ("Home", "Home & Garden"),
    ("Sports", "Sports & Fitness"),
    ("Toys", "Toys & Games"),
    ("Automotive", "Automotive & Accessories")
]

for new_cat, old_cat in updates:
    conn.execute("UPDATE products SET category = ? WHERE category = ?", (new_cat, old_cat))

conn.commit()
conn.close()
