"""
Datenbank-Session-Handling für den Workflow-Service.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


# SQLAlchemy Engine & SessionFactory
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_session():
    """Kontextmanager für Sessions (kompatibel zu `with`)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


