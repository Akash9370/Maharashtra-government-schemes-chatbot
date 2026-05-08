from app.crud import get_all_schemes
from collections import defaultdict

schemes = get_all_schemes()

print(f"Total schemes: {len(schemes)}")

# 1. Check None/empty names
print("\n--- Empty / None Names ---")
for s in schemes:
    if not s.name or str(s.name).strip().lower() == "none":
        print(f"ID: {s.id} | Name: {s.name} | Category: {s.category}")

# 2. Exact duplicate names
name_map = defaultdict(list)

for s in schemes:
    clean_name = (s.name or "").strip().lower()
    name_map[clean_name].append(s)

print("\n--- Exact Duplicate Names ---")
for name, items in name_map.items():
    if name and len(items) > 1:
        print(f"\nDuplicate: {name}")
        for s in items:
            print(f"  ID: {s.id} | Name: {s.name}")

# 3. Suspicious test schemes
print("\n--- Test / Temporary Schemes ---")
for s in schemes:
    name = (s.name or "").lower()
    if "test" in name or "unique" in name:
        print(f"ID: {s.id} | Name: {s.name} | Category: {s.category}")