from .db import SessionLocal
from .models import Scheme


def add_scheme(data: dict):
    db = SessionLocal()

    new_scheme = Scheme(
        name=data["name"],
        description=data["description"],
        eligibility=data["eligibility"],
        benefits=data["benefits"],
        state=data["state"],
        category=data["category"]
    )

    db.add(new_scheme)
    db.commit()
    db.refresh(new_scheme)
    db.close()

    return new_scheme

def get_all_schemes():
    db = SessionLocal()
    data = db.query(Scheme).all()
    db.close()
    return data

def scheme_exists(name: str):
    db = SessionLocal()
    exists = db.query(Scheme).filter(Scheme.name.ilike(name)).first()
    db.close()
    return exists is not None

def delete_scheme(scheme_id: int):
    db = SessionLocal()
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if scheme:
        db.delete(scheme)
        db.commit()
        db.close()
        return True

    db.close()
    return False

def update_scheme(scheme_id: int, data: dict):
    db = SessionLocal()
    scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()

    if not scheme:
        db.close()
        return False

    for key, value in data.items():
        setattr(scheme, key, value)

    db.commit()
    db.close()
    return True