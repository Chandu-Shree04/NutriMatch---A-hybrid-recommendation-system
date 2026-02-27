import pandas as pd
import json, gzip, os
from NM_sentiment import get_sentiment


META_PATH = r"C:/Users/Chandu/Downloads/meta_Grocery_and_Gourmet_Food.jsonl.gz"
REV_PATH  = r"C:/Users/Chandu/Downloads/Grocery_and_Gourmet_Food.jsonl.gz"
OUT_DIR   = r"C:/Users/Chandu/OneDrive/Desktop/NutriMatch/final"
os.makedirs(OUT_DIR, exist_ok=True)

print("\n========== LOADING METADATA ==========\n")

meta = []
with gzip.open(META_PATH, "rt", encoding="utf-8") as f:
    for line in f:
        try:
            meta.append(json.loads(line))
        except:
            continue

meta_df = pd.DataFrame(meta)
print("Metadata rows:", len(meta_df))
print("Metadata columns:", meta_df.columns.tolist())

meta_clean = meta_df.copy()

if "parent_asin" in meta_clean.columns:
    meta_clean["asin"] = meta_clean["parent_asin"]
else:
    meta_clean["asin"] = None

meta_clean["asin"] = meta_clean["asin"].astype(str)

required_meta_cols = ["asin", "title", "description", "categories", "price"]

for col in required_meta_cols:
    if col not in meta_clean.columns:
        meta_clean[col] = None

def clean_categories(cat):
    if isinstance(cat, list) and len(cat) > 0:
        if isinstance(cat[0], list):
            return " > ".join(str(x) for x in cat[0])
        else:
            return " > ".join(str(x) for x in cat)
    return None

meta_clean["categories_clean"] = meta_clean["categories"].apply(clean_categories)

meta_clean["title_clean"] = meta_clean["title"].fillna("").astype(str).str.lower().str.strip()
meta_clean["desc_clean"]  = meta_clean["description"].fillna("").astype(str).str.lower().str.strip()

clean_meta = meta_clean.loc[:, ["asin", "title", "description",
                                "categories_clean", "price",
                                "title_clean", "desc_clean"]]

clean_meta = clean_meta.rename(columns={"categories_clean": "categories"})

clean_meta = clean_meta[clean_meta["asin"].notna()]
print("\nFinal metadata rows:", len(clean_meta))

meta_out = os.path.join(OUT_DIR, "clean_metadata.csv")
clean_meta.to_csv(meta_out, index=False)
print("✔ Saved clean metadata ->", meta_out)

print("\n========== LOADING REVIEWS ==========\n")

recs = []
with gzip.open(REV_PATH, "rt", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            recs.append(json.loads(line))
        except:
            continue

        if (i + 1) % 200000 == 0:
            print(f"Loaded {i+1:,} reviews...")

reviews_df = pd.DataFrame(recs)
print("Total reviews loaded:", len(reviews_df))
print("Review columns:", reviews_df.columns.tolist())

if "asin" not in reviews_df.columns:
    possible_keys = ["product_asin", "asin13", "ASIN"]
    for key in possible_keys:
        if key in reviews_df.columns:
            reviews_df = reviews_df.rename(columns={key: "asin"})
            break

reviews_df["asin"] = reviews_df["asin"].astype(str)

meta_asins = set(clean_meta["asin"].astype(str))
reviews_filtered = reviews_df[reviews_df["asin"].isin(meta_asins)].copy()

print("Reviews AFTER filtering to metadata ASINs:", len(reviews_filtered))

candidates = ["reviewText", "review_text", "text", "review"]
review_text_col = None

for c in candidates:
    if c in reviews_filtered.columns:
        review_text_col = c
        break

if review_text_col is None:
    for c in reviews_filtered.columns:
        if reviews_filtered[c].dtype == object:
            if reviews_filtered[c].astype(str).str.len().mean() > 20:
                review_text_col = c
                break

print("Using review text column:", review_text_col)

def simple_clean(s):
    if pd.isna(s):
        return ""
    return str(s).replace("\n", " ").strip().lower()

reviews_filtered["review_clean"] = reviews_filtered[review_text_col].apply(simple_clean)

reviews_filtered = reviews_filtered[reviews_filtered["review_clean"].str.len() > 0]
print("Reviews after removing empty text:", len(reviews_filtered))

rev_out = os.path.join(OUT_DIR, "filtered_reviews.csv")
reviews_filtered.to_csv(rev_out, index=False)
print("✔ Saved filtered reviews ->", rev_out)

print("\n========== MERGING REVIEWS + METADATA ==========\n")

clean_meta["asin"] = clean_meta["asin"].astype(str)
reviews_filtered["asin"] = reviews_filtered["asin"].astype(str)

merged = reviews_filtered.merge(
    clean_meta,
    on="asin",
    how="left",
    suffixes=("_rev", "_meta")
)
merged["sentiment"] = merged["review_clean"].apply(get_sentiment)


print("Merged total rows:", len(merged))

title_col = None
for col in ["title", "title_meta", "title_rev"]:
    if col in merged.columns:
        title_col = col
        break

if title_col:
    print("Rows with metadata title:", merged[title_col].notna().sum())
else:
    print("⚠ No title column found after merge")

merged_out = os.path.join(OUT_DIR, "merged_reviews_metadata.csv")
merged.to_csv(merged_out, index=False)
print("✔ Saved merged dataset ->", merged_out)

print("\n========== SAMPLE OUTPUT ==========\n")

if title_col:
    print("Top reviewed products:")
    print(merged[title_col].value_counts().head(10))

print("\nSample merged row:")
print(merged.iloc[0].to_dict())
                     