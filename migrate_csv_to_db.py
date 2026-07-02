import pandas as pd
from app.crud import add_scheme, get_all_schemes
from app.db import engine
from app.models import Base
from app.categories import detect_category
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "info", "Scheme.csv")

print("Inside info folder:", os.listdir("info"))
print("Looking for file at:", csv_path)
print("File exists:", os.path.exists(csv_path))

# Make sure the table actually exists before we touch it
Base.metadata.create_all(bind=engine)

df = pd.read_csv(csv_path)

# Drop rows with no scheme name (fixes the 3 blank/None rows from the CSV)
df = df.dropna(subset=["Scheme Name"])
df = df[df["Scheme Name"].str.strip() != ""]

# Build a set of names already in the DB so re-running this script is safe
existing_names = {s.name for s in get_all_schemes()}

added = 0
skipped = 0

for _, row in df.iterrows():
    name = str(row["Scheme Name"]).strip()

    if name in existing_names:
        skipped += 1
        continue

    eligibility = str(row["Eligibility Criteria"]) if pd.notna(row["Eligibility Criteria"]) else ""
    benefits = str(row["Scheme Benefits"]) if pd.notna(row["Scheme Benefits"]) else ""
    description = f"{name}. Eligibility: {eligibility}. Benefits: {benefits}"

    category = detect_category(f"{name} {eligibility} {benefits}")

    add_scheme({
        "name": name,
        "description": description,
        "eligibility": eligibility,
        "benefits": benefits,
        "state": "Maharashtra",
        "category": category,       # real category now, not always "General"
    })

    existing_names.add(name)
    added += 1

print(f"Migration complete — added {added}, skipped {skipped} already-existing")