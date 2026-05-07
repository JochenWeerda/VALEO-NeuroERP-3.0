"""Factory für Privacy-Erasure-Repository (DB vs. Memory-Singleton)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.services.privacy_erasure.db_repository import DbPrivacyErasureRepository
from app.services.privacy_erasure.protocol import PrivacyErasurePersistence
from app.services.privacy_erasure.store import InMemoryPrivacyRepository

_MEMORY_SINGLETON: InMemoryPrivacyRepository | None = None


def build_privacy_erasure_repository(db: AsyncSession | None) -> PrivacyErasurePersistence:
    """Production: `database` + gültige `AsyncSession`; `memory`: geteilter Prozess-Store."""
    global _MEMORY_SINGLETON
    if settings.PRIVACY_ERASURE_PERSISTENCE == "memory":
        if _MEMORY_SINGLETON is None:
            _MEMORY_SINGLETON = InMemoryPrivacyRepository()
        return _MEMORY_SINGLETON
    if db is None:
        raise ValueError("AsyncSession ist für database-Persistenz erforderlich")
    return DbPrivacyErasureRepository(db)


def reset_privacy_erasure_memory_repository() -> None:
    """Dev/Tests für Memory-Singleton."""
    global _MEMORY_SINGLETON
    if _MEMORY_SINGLETON is not None:
        _MEMORY_SINGLETON.clear()
    _MEMORY_SINGLETON = None
