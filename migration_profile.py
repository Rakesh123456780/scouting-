import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scoutiq.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print("No database found. Skipping.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(users)")
    cols = [col[1] for col in cur.fetchall()]
    
    new_cols = [
        ("full_name", "TEXT"),
        ("company", "TEXT"),
        ("industry", "TEXT"),
        ("bio", "TEXT"),
        ("plan", "TEXT DEFAULT 'Free'")
    ]
    
    for name, type_def in new_cols:
        if name not in cols:
            print(f"Adding column {name}...")
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN {name} {type_def}")
            except Exception as e:
                print(f"Error adding {name}: {e}")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
