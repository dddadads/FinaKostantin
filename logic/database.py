import sqlite3
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "data", "finance.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL NOT NULL,
            tag TEXT NOT NULL,
            extra_info TEXT,
            date TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    try:
        cursor.execute("SELECT tag FROM transactions LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE transactions ADD COLUMN tag TEXT NOT NULL DEFAULT 'Обычный'")
        cursor.execute("ALTER TABLE transactions ADD COLUMN extra_info TEXT")
    conn.commit()
    conn.close()

def register_user(name, password, initial_balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, password, balance) VALUES (?, ?, ?)", (name, password, initial_balance))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        return None
    finally:
        conn.close()

def get_last_user_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, balance, id FROM users ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0], row[1], row[2]
        return None
    except sqlite3.OperationalError:
        return None

def add_transaction(user_id, amount, tag, extra_info):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, tag, extra_info) VALUES (?, ?, ?, ?)",
            (user_id, amount, tag, extra_info)
        )
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]
        conn.commit()
        return new_balance
    except sqlite3.Error:
        return None
    finally:
        conn.close()

def get_transactions(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT amount, tag, extra_info, date FROM transactions WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
