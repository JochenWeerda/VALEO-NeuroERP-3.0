"""Async SQLAlchemy Sessionverwaltung."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _build_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL.unicode_string(),
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )


engine: AsyncEngine = _build_engine()
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency."""

    async with SessionLocal() as session:
        yield session

