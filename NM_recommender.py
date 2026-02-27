# NM_recommender.py
import pandas as pd
import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# ---------------------------------------------------
# PATHS
# ---------------------------------------------------
DB_PATH = Path("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/nutrimatchDB.db")
NUTRITION_PATH = Path(
    "C:/Users/Chandu/OneDrive/Desktop/NutriMatch/final/clean_nutrition_dataset.csv"
)

# ---------------------------------------------------
# LOAD NUTRITION DATA (READ-ONLY)
# ---------------------------------------------------
nutrition_df = pd.read_csv(NUTRITION_PATH)

NUTRITION_FEATURES = [
    "protein", "fat", "carbs", "fiber", "calories", "health_score_norm"
]

nutrition_df = nutrition_df.dropna(subset=NUTRITION_FEATURES).reset_index(drop=True)

X = nutrition_df[NUTRITION_FEATURES].values
X_norm = (X - X.mean(axis=0)) / X.std(axis=0)

# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ---------------------------------------------------
# USER INTERACTION HELPERS
# ---------------------------------------------------
def get_user_food_scores(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT food_name, SUM(interaction_weight) AS score
        FROM user_interactions
        WHERE user_id = ?
        GROUP BY food_name
        """,
        conn,
        params=(user_id,)
    )
    conn.close()

    if df.empty:
        return {}

    return dict(zip(df["food_name"], df["score"]))


def is_cold_start_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM user_interactions WHERE user_id = ?",
        (user_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()

    return count == 0

# ---------------------------------------------------
# COLD START RECOMMENDATIONS
# ---------------------------------------------------
def cold_start_recommendations(top_n=5):
    df = nutrition_df.copy()
    df["hybrid_score"] = df["health_score_norm"]
    df["confidence"] = 60.0  # baseline confidence

    return df.sort_values(
        "health_score_norm",
        ascending=False
    ).head(top_n)

# ---------------------------------------------------
# CONFIDENCE SCORE
# ---------------------------------------------------
def compute_confidence(row):
    similarity = row.get("similarity", 0)
    interaction = row.get("interaction_score", 0)
    health = row.get("health_score_norm", 0) / 100

    confidence = (
        0.5 * similarity +
        0.3 * interaction +
        0.2 * health
    )

    return round(confidence * 100, 1)

# ---------------------------------------------------
# HYBRID RECOMMENDER
# ---------------------------------------------------
def recommend_snacks(selected_food, user_id=None, top_n=5):

    # Cold-start handling
    if user_id and is_cold_start_user(user_id):
        return cold_start_recommendations(top_n)

    if selected_food not in nutrition_df["food"].values:
        return f"❌ '{selected_food}' not found in nutrition dataset."

    idx = nutrition_df[nutrition_df["food"] == selected_food].index[0]

    sim_scores = cosine_similarity([X_norm[idx]], X_norm)[0]

    df = nutrition_df.copy()
    df["similarity"] = sim_scores
    df["health_norm"] = df["health_score_norm"] / 100

    interaction_scores = {}
    if user_id is not None:
        interaction_scores = get_user_food_scores(user_id)

    df["interaction_score"] = df["food"].map(
        lambda f: interaction_scores.get(f, 0)
    )

    if df["interaction_score"].max() > 0:
        df["interaction_score"] /= df["interaction_score"].max()

    df["hybrid_score"] = (
        0.55 * df["similarity"] +
        0.25 * df["health_norm"] +
        0.20 * df["interaction_score"]
    )

    df = df[df["food"] != selected_food]
    df["confidence"] = df.apply(compute_confidence, axis=1)

    return df.sort_values(
        "hybrid_score",
        ascending=False
    ).head(top_n)[
        [
            "food",
            "protein",
            "fat",
            "carbs",
            "fiber",
            "calories",
            "health_score_norm",
            "similarity",
            "interaction_score",
            "hybrid_score",
            "confidence",
        ]
    ]

# ---------------------------------------------------
# USER NUTRIENT PREFERENCES
# ---------------------------------------------------
def get_user_nutrient_preferences(user_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT food_name, interaction_weight
        FROM user_interactions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return None

    totals = {n: 0 for n in NUTRITION_FEATURES}
    weight_sum = 0

    for food, w in rows:
        r = nutrition_df[nutrition_df["food"] == food]
        if r.empty:
            continue

        for n in NUTRITION_FEATURES:
            totals[n] += r.iloc[0][n] * w

        weight_sum += w

    if weight_sum == 0:
        return None

    for n in totals:
        totals[n] /= weight_sum

    return totals

# ---------------------------------------------------
# EXPLAINABILITY
# ---------------------------------------------------
def explain_recommendation(selected_row, recommended_row, user_prefs=None):
    reasons = []

    if recommended_row["protein"] > selected_row["protein"]:
        reasons.append("higher protein")

    if recommended_row["fiber"] > selected_row["fiber"]:
        reasons.append("more fiber")

    if recommended_row["calories"] < selected_row["calories"]:
        reasons.append("fewer calories")

    if recommended_row["fat"] < selected_row["fat"]:
        reasons.append("lower fat")

    if user_prefs:
        if recommended_row["protein"] >= user_prefs.get("protein", 0):
            reasons.append("matches your protein preference")

        if recommended_row["fiber"] >= user_prefs.get("fiber", 0):
            reasons.append("supports your fiber goals")

        if recommended_row["calories"] <= user_prefs.get("calories", float("inf")):
            reasons.append("fits your calorie tolerance")

    if not reasons:
        return "Recommended due to overall nutritional balance."

    return "Recommended because it has " + ", ".join(reasons) + "."
