import pandas as pd
import json
import gzip
import re

META_PATH = "C:/Users/Chandu/Downloads/meta_Grocery_and_Gourmet_Food.jsonl.gz"

meta = []
with gzip.open(META_PATH, "rt", encoding="utf-8") as f:
    for line in f:
        meta.append(json.loads(line))

meta_df = pd.DataFrame(meta)

print("Original columns:", list(meta_df.columns))

cols_we_need = [
    "parent_asin",
    "title",
    "description",
    "price",
    "average_rating",
    "rating_number",
    "categories"
]

clean_meta = meta_df[cols_we_need].copy()

def clean_price(p):
    if pd.isna(p):
        return None
    if isinstance(p, str):
        p = re.sub(r"[^0-9.]", "", p)
        try:
            return float(p)
        except:
            return None
    return p

clean_meta["price"] = clean_meta["price"].apply(clean_price)

def clean_categories(cat):
    if isinstance(cat, list) and len(cat) > 0:
        try:
            return cat[0][-1]  
        except:
            return None
    return None

clean_meta["categories_clean"] = clean_meta["categories"].apply(clean_categories)

def clean_text(t):
    if isinstance(t, str):
        t = t.lower()
        t = re.sub(r"[^a-z0-9 ]", "", t)
        return t.strip()
    return ""

clean_meta["title_clean"] = clean_meta["title"].apply(clean_text)

clean_meta["description"] = clean_meta["description"].fillna("")
clean_meta["average_rating"] = clean_meta["average_rating"].fillna(0).astype(float)
clean_meta["rating_number"] = clean_meta["rating_number"].fillna(0).astype(int)

print("\nCleaned Metadata Sample:")
print(clean_meta.head())

clean_meta.to_csv("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/clean_meta.csv", index=False)
print("\nSaved clean_meta.csv successfully!")
