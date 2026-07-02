import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # folder this file lives in (app/)
PROJECT_ROOT = os.path.dirname(BASE_DIR)                         # one level up = project root
DB_PATH = os.path.join(PROJECT_ROOT, "schemes.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)