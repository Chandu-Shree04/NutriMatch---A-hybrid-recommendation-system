# user_dashboard.py
import sqlite3
import pandas as pd
from pathlib import Path

# -----------------------------
# DATABASE PATH (SINGLE SOURCE)
# -----------------------------
DB_PATH = Path("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/nutrimatchDB.db")


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -----------------------------
# USER SUMMARY
# -----------------------------
def get_user_summary(user_id):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT
            COUNT(*) AS total_interactions,
            COUNT(DISTINCT food_name) AS unique_foods
        FROM user_interactions
        WHERE user_id = ?
        """,
        conn,
        params=(user_id,)
    )

    conn.close()

    if df.empty:
        return pd.Series(
            {"total_interactions": 0, "unique_foods": 0}
        )

    return df.iloc[0]


# -----------------------------
# TOP SNACKS
# -----------------------------
def get_top_snacks(user_id, limit=5):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT food_name, SUM(interaction_weight) AS score
        FROM user_interactions
        WHERE user_id = ?
        GROUP BY food_name
        ORDER BY score DESC
        LIMIT ?
        """,
        conn,
        params=(user_id, limit)
    )

    conn.close()

    return df if not df.empty else pd.DataFrame(
        columns=["food_name", "score"]
    )


# -----------------------------
# RECENT ACTIVITY
# -----------------------------
def get_recent_activity(user_id, limit=5):
    conn = get_connection()

    df = pd.read_sql(
        """
        SELECT food_name, interaction_type, timestamp
        FROM user_interactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        conn,
        params=(user_id, limit)
    )

    conn.close()

    return df if not df.empty else pd.DataFrame(
        columns=["food_name", "interaction_type", "timestamp"]
    )
