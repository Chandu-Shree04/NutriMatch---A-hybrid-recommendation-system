import pandas as pd
import json
import gzip

meta_path = "C:/Users/Chandu/Downloads/meta_Grocery_and_Gourmet_Food.jsonl.gz"
meta = []
with gzip.open(meta_path, "rt", encoding="utf-8") as f:
    for line in f:
        meta.append(json.loads(line))
meta_df = pd.DataFrame(meta)

print("Meta columns:", meta_df.columns.tolist())

working = meta_df.copy()

if "parent_asin" in working.columns:
    working = working.rename(columns={"parent_asin": "asin"})

for col in ["asin", "title", "description", "main_category", "categories", "price", "features"]:
    if col not in working.columns:
        working[col] = None  

def clean_categories(cat):
    if isinstance(cat, list) and len(cat) > 0:
        try:
            if isinstance(cat[0], list):
                return " > ".join([str(x) for x in cat[0]])
            else:
                return " > ".join([str(x) for x in cat])
        except Exception:
            return str(cat)
    elif isinstance(cat, str):
        return cat
    else:
        return None

working.loc[:, "categories_clean"] = working["categories"].apply(clean_categories)

clean_meta = working.loc[:, ["asin", "title", "description", "main_category", "categories_clean", "price", "features"]].copy()
clean_meta = clean_meta.rename(columns={"categories_clean": "categories"})

clean_meta.loc[:, "title_clean"] = clean_meta["title"].fillna("").astype(str).str.lower().str.strip()
clean_meta.loc[:, "desc_clean"] = clean_meta["description"].fillna("").astype(str).str.lower().str.strip()

clean_meta.to_csv("C:/Users/Chandu/OneDrive/Desktop/NutriMatch/clean_metadata.csv", index=False)
print("Saved clean_metadata.csv with rows:", len(clean_meta))
