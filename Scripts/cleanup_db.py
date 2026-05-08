from app.db import SessionLocal
from app.models import Scheme

IDS_TO_DELETE = [1, 17, 47, 77, 104, 105, 106, 107, 108, 109]

db = SessionLocal()

for scheme_id in IDS_TO_DELETE:
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if scheme:
        print(f"Deleting ID {scheme.id}: {scheme.name}")
        db.delete(scheme)

db.commit()
db.close()

print("Cleanup complete")