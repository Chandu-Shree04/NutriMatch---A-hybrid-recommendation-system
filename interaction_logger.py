# interaction_logger.py
import sqlite3
from datetime import datetime
from pathlib import Path

# -----------------------------
# DATABASE PATH (SINGLE SOURCE)
# -----------------------------
DB_PATH = Path("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/nutrimatchDB.db")


def get_connection():
    """
    Streamlit-safe SQLite connection
    """
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------
# ENSURE TABLE EXISTS
# -----------------------------
def init_interaction_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            interaction_weight REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# LOG INTERACTION
# -----------------------------
def log_interaction(user_id, food_name, interaction_type):
    """
    Log a user-food interaction.

    interaction_type:
    - view
    - recommend
    - select
    - like
    """

    # Safety checks
    if user_id is None or not food_name:
        return

    weights = {
        "view": 0.2,
        "recommend": 0.5,
        "select": 0.7,
        "like": 1.0
    }

    weight = weights.get(interaction_type, 0.1)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_interactions
        (user_id, food_name, interaction_type, interaction_weight, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        food_name,
        interaction_type,
        weight,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


# Initialize table ON IMPORT
init_interaction_table()
