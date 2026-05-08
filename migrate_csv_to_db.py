import pandas as pd
from app.crud import add_scheme
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "info", "Scheme.csv")

print("Inside info folder:", os.listdir("info"))
print("Looking for file at:", csv_path)
print("File exists:", os.path.exists(csv_path))

df = pd.read_csv(csv_path)

for _, row in df.iterrows():
    name = row["Scheme Name"]
    eligibility = row["Eligibility Criteria"]
    benefits = row["Scheme Benefits"]

    add_scheme({
        "name": name,
        "description": f"{name}. Eligibility: {eligibility}. Benefits: {benefits}",
        "eligibility": eligibility,
        "benefits": benefits,
        "state": "Maharashtra",   # fixed for now
        "category": "General"     # default category
    })

print("Migration complete")