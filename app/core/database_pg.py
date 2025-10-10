"""
PostgreSQL Database Connection
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Database URL aus ENV
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://valeo_dev:valeo_dev_2024!@localhost:5432/valeo_neuro_erp"
)

# Engine erstellen
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# SessionLocal für Dependency Injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency für FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

