"""Async SQLAlchemy session helpers for CRM Core."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL.unicode_string(),
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )


engine: AsyncEngine = _create_engine()
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
