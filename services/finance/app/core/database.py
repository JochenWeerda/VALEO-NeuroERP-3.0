"""SQLAlchemy Session & Basiskomponenten."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session, sessionmaker

from services.finance.app.core.config import settings


class Base(DeclarativeBase):
    """Gemeinsame Basisklasse für alle Modelle."""


engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False))


def get_db() -> Generator[Session, None, None]:
    """FastAPI-Dependency für DB-Sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

