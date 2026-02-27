import gzip
import json
import pandas as pd

REVIEW_PATH = "C:/Users/Chandu/Downloads/Grocery_and_Gourmet_Food.jsonl.gz"
OUTPUT_PATH = "clean_reviews.csv"

clean_rows = []

def safe_get(d, key, default=None):
    return d[key] if key in d else default

print("Loading & cleaning reviews... This may take some minutes.\n")

with gzip.open(REVIEW_PATH, "rt", encoding="utf-8") as f:
    for i, line in enumerate(f):
        try:
            data = json.loads(line)

            clean_rows.append({
                "asin": safe_get(data, "asin"),
                "review_text": safe_get(data, "reviewText"),
                "summary": safe_get(data, "summary"),
                "rating": safe_get(data, "overall"),
                "verified": safe_get(data, "verified"),
                "review_time": safe_get(data, "reviewTime")
            })

            if (i + 1) % 100000 == 0:
                print(f"Processed {i+1:,} reviews...")

        except Exception as e:
            print("Error parsing line:", e)
            continue

df = pd.DataFrame(clean_rows)

df.dropna(subset=["review_text"], inplace=True)

df.reset_index(drop=True, inplace=True)

print("\nSaving cleaned file...")
df.to_csv(OUTPUT_PATH, index=False)

print(f"Saved: {OUTPUT_PATH}")
print(f"Total reviews cleaned: {len(df):,}")
