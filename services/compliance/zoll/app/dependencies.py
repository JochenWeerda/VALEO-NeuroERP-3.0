"""Dependency Injection für den Zoll-Service."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.integrations.event_bus import EventBus
from app.integrations.sanctions_provider import SanctionsProvider
from app.services.permit_service import PermitService
from app.services.preference_service import PreferenceService
from app.services.screening_service import ScreeningService

logger = logging.getLogger(__name__)

_event_bus: EventBus | None = None
_sanctions_provider: SanctionsProvider | None = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def configure_event_bus() -> None:
    global _event_bus
    if not settings.EVENT_BUS_ENABLED or _event_bus is not None:
        return
    bus = EventBus(settings.EVENT_BUS_URL, settings.EVENT_BUS_SUBJECT_PREFIX)
    try:
        await bus.connect()
    except Exception as exc:  # noqa: BLE001
        logger.warning("EventBus konnte nicht verbunden werden: %s", exc)
        return
    _event_bus = bus


async def configure_sanctions_provider() -> None:
    global _sanctions_provider
    if _sanctions_provider is None:
        _sanctions_provider = SanctionsProvider()
        await _sanctions_provider.refresh()


def get_event_bus() -> EventBus | None:
    return _event_bus


def _get_sanctions_provider() -> SanctionsProvider:
    global _sanctions_provider
    if _sanctions_provider is None:
        _sanctions_provider = SanctionsProvider()
    return _sanctions_provider


async def get_screening_service(session: AsyncSession = None) -> ScreeningService:
    provider = _get_sanctions_provider()
    bus = get_event_bus()
    if session is None:
        async for dependency_session in get_db_session():
            return ScreeningService(dependency_session, provider=provider, event_bus=bus)
    return ScreeningService(session, provider=provider, event_bus=bus)


async def get_permit_service(session: AsyncSession = None) -> PermitService:
    if session is None:
        async for dependency_session in get_db_session():
            return PermitService(dependency_session)
    return PermitService(session)


async def get_preference_service(session: AsyncSession = None) -> PreferenceService:
    if session is None:
        async for dependency_session in get_db_session():
            return PreferenceService(dependency_session)
    return PreferenceService(session)


async def refresh_sanctions_data() -> bool:
    provider = _get_sanctions_provider()
    return await provider.refresh()


async def shutdown_event_bus() -> None:
    global _event_bus
    if _event_bus:
        await _event_bus.close()
        _event_bus = None
