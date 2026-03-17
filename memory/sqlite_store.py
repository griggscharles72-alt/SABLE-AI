import sqlite3
from pathlib import Path

DB_PATH = Path("state/sable.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    conn.commit()
    return conn

def add_task(name):
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def list_tasks():
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, status FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    add_task("Test task")
    print(list_tasks())
