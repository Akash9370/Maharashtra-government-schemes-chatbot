# check_categories.py
from app.crud import get_all_schemes
from app.categories import detect_category

schemes = get_all_schemes()
counts = {}
for s in schemes:
    text = " ".join([s.name or "", s.eligibility or "", s.benefits or "", s.description or ""])
    cat = detect_category(text)
    counts[cat] = counts.get(cat, 0) + 1

for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{cat}: {n}")