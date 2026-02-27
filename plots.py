import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# 1. NUTRITION RADAR CHART
# -------------------------------------------------
def nutrition_radar_chart(snack1, snack2):
    nutrients = ["protein", "fat", "carbs", "fiber", "calories"]

    try:
        v1 = np.array([snack1[n] for n in nutrients], dtype=float)
        v2 = np.array([snack2[n] for n in nutrients], dtype=float)
    except KeyError:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center")
        ax.axis("off")
        return fig

    max_vals = np.maximum(v1, v2)
    max_vals[max_vals == 0] = 1

    v1 /= max_vals
    v2 /= max_vals

    angles = np.linspace(0, 2 * np.pi, len(nutrients), endpoint=False)
    angles = np.append(angles, angles[0])
    v1 = np.append(v1, v1[0])
    v2 = np.append(v2, v2[0])

    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)

    ax.plot(angles, v1, label="Selected Snack")
    ax.fill(angles, v1, alpha=0.25)

    ax.plot(angles, v2, label="Recommended Snack")
    ax.fill(angles, v2, alpha=0.25)

    ax.set_thetagrids(angles[:-1] * 180 / np.pi, nutrients)
    ax.set_title("Nutritional Comparison (Normalized)")
    ax.legend()

    return fig


# -------------------------------------------------
# 2. NUTRITION BAR CHART
# -------------------------------------------------
def nutrition_bar_chart(snack):
    nutrients = ["protein", "fat", "carbs", "fiber", "calories"]
    values = [snack[n] for n in nutrients]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(nutrients, values, color="#66BB6A")
    ax.set_title("Nutritional Breakdown")
    ax.set_ylabel("Value (g / kcal)")
    return fig


# -------------------------------------------------
# 3. SENTIMENT PIE CHART
# -------------------------------------------------
def sentiment_pie_chart(reviews_df):
    fig, ax = plt.subplots()

    if reviews_df is None or reviews_df.empty or "sentiment" not in reviews_df.columns:
        ax.text(0.5, 0.5, "No sentiment data available", ha="center", va="center")
        ax.axis("off")
        return fig

    counts = reviews_df["sentiment"].str.lower().value_counts()

    sizes = [
        counts.get("positive", 0),
        counts.get("negative", 0),
        counts.get("neutral", 0),
    ]

    if sum(sizes) == 0:
        ax.text(0.5, 0.5, "No sentiment distribution", ha="center", va="center")
        ax.axis("off")
        return fig

    ax.pie(
        sizes,
        labels=["Positive", "Negative", "Neutral"],
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.set_title("Customer Sentiment Distribution")
    ax.axis("equal")

    return fig


# -------------------------------------------------
# 4. USER NUTRIENT PREFERENCE CHART
# -------------------------------------------------
def user_nutrient_preference_chart(prefs):
    fig, ax = plt.subplots()

    if prefs is None:
        ax.text(0.5, 0.5, "No preference data yet", ha="center", va="center")
        ax.axis("off")
        return fig

    nutrients = ["protein", "fiber", "fat", "calories"]
    values = [prefs.get(n, 0) for n in nutrients]

    ax.bar(nutrients, values, color="#4CAF50")
    ax.set_title("User Nutrient Preference Profile")
    ax.set_ylabel("Preference Strength")

    return fig
