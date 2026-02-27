import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# -------------------------------------------------
# 1. LOAD RAW NUTRITION DATA
# -------------------------------------------------
INPUT_PATH = "C:/Users/Chandu/OneDrive/Desktop/NutriMatch/nutrients_csvfile.csv"
OUTPUT_PATH = "C:/Users/Chandu/OneDrive/Desktop/NutriMatch/final/clean_nutrition_dataset.csv"

nutri_df = pd.read_csv(INPUT_PATH)

# Normalize column names
nutri_df.columns = (
    nutri_df.columns
    .str.lower()
    .str.replace(".", "_", regex=False)
    .str.strip()
)

print("Columns after cleaning:")
print(nutri_df.columns.tolist())

# -------------------------------------------------
# 2. CLEAN NUMERIC COLUMNS
# -------------------------------------------------
numeric_cols = ["grams", "calories", "protein", "fat", "sat_fat", "fiber", "carbs"]

for col in numeric_cols:
    nutri_df[col] = pd.to_numeric(nutri_df[col], errors="coerce")

nutri_df[numeric_cols] = nutri_df[numeric_cols].fillna(0)

# -------------------------------------------------
# 3. CLEAN FOOD NAME (CANONICAL)
# -------------------------------------------------
nutri_df["food"] = (
    nutri_df["food"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# -------------------------------------------------
# 4. HEALTH SCORE ENGINEERING
# -------------------------------------------------
nutri_df["health_score"] = (
    (nutri_df["protein"] * 3) +
    (nutri_df["fiber"] * 4) -
    (nutri_df["fat"] * 1.5) -
    (nutri_df["sat_fat"] * 2.5) -
    (nutri_df["calories"] / 40)
)

scaler = MinMaxScaler()
nutri_df["health_score_norm"] = scaler.fit_transform(
    nutri_df[["health_score"]]
)

nutri_df["health_score_norm"] = (
    nutri_df["health_score_norm"] * 100
).round(2)

print("\nHealth score stats:")
print(nutri_df["health_score_norm"].describe())

# -------------------------------------------------
# 5. FINAL COLUMN ORDER
# -------------------------------------------------
final_cols = [
    "food",
    "measure",
    "grams",
    "calories",
    "protein",
    "fat",
    "sat_fat",
    "fiber",
    "carbs",
    "category",
    "health_score_norm"
]

nutri_df = nutri_df[final_cols]

# -------------------------------------------------
# 6. SAVE CLEAN DATASET
# -------------------------------------------------
nutri_df.to_csv(OUTPUT_PATH, index=False)

print(f"\n✅ Clean nutrition dataset saved to: {OUTPUT_PATH}")
print(nutri_df.head())
