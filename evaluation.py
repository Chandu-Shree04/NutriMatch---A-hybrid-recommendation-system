# evaluation.py
import sqlite3
import numpy as np
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "nutrimatchDB.db"


def precision_at_k(user_id, recommended_items, k=5):
    """
    recommended_items: list of food names
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT food_name
        FROM user_interactions
        WHERE user_id = ?
        AND interaction_type IN ('select', 'like')
    """, (user_id,))

    relevant_items = {row[0] for row in cursor.fetchall()}
    conn.close()

    if not relevant_items:
        return 0.0

    top_k = recommended_items[:k]
    hits = len(set(top_k) & relevant_items)

    return hits / k

from sklearn.metrics.pairwise import cosine_similarity

def diversity_at_k(nutrition_df, recommended_items, features):
    vectors = nutrition_df[
        nutrition_df["food"].isin(recommended_items)
    ][features].values

    if len(vectors) < 2:
        return 0.0

    similarity_matrix = cosine_similarity(vectors)
    upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]

    return 1 - np.mean(upper_triangle)

def novelty_score(nutrition_df, recommended_items):
    popularity = nutrition_df["food"].value_counts(normalize=True)

    scores = []
    for item in recommended_items:
        scores.append(1 - popularity.get(item, 0))

    return np.mean(scores)
