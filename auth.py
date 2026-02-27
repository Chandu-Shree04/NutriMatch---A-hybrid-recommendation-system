# auth.py
import sqlite3
import bcrypt
from pathlib import Path

# -------------------------------
# DATABASE CONFIG
# -------------------------------
DB_PATH = Path("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/nutrimatchDB.db")


def get_connection():
    """
    Create a SQLite connection (Streamlit-safe).
    """
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -------------------------------
# INITIALIZE USERS TABLE
# -------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Initialize DB on import
init_db()


# -------------------------------
# SIGN UP
# -------------------------------
def signup_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


# -------------------------------
# LOGIN
# -------------------------------
def login_user(username, password):
    if not username or not password:
        return False, "Please enter both username and password."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, password_hash FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False, "Invalid username or password."

    user_id, stored_hash = row

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return True, user_id

    return False, "Invalid username or password."
