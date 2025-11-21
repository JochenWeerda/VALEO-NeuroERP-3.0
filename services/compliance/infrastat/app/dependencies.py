"""Dependency Injection für den InfraStat-Service."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.etl.validator import InfrastatValidator
from app.integration import EventBus
from app.services.idev_client import IdevClient
from app.services.ingestion_service import InfrastatIngestionService
from app.services.submission_service import SubmissionService

logger = logging.getLogger(__name__)

_event_bus: EventBus | None = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


@lru_cache
def _load_reference_codes() -> tuple[set[str], set[str]]:
    commodity_codes: set[str] = set()
    country_codes: set[str] = set()

    taric_path = Path(settings.TARIC_DATA_PATH)
    if taric_path.exists():
        with taric_path.open(encoding="utf-8") as handle:
            for line in handle:
                code = line.strip().split(";")[0]
                if code:
                    commodity_codes.add(code.replace(" ", ""))

    country_path = Path(settings.COUNTRY_CODES_PATH)
    if country_path.exists():
        with country_path.open(encoding="utf-8") as handle:
            for line in handle:
                code = line.strip().split(";")[0]
                if len(code) == 2:
                    country_codes.add(code.upper())

    return commodity_codes, country_codes


def get_validator() -> InfrastatValidator:
    commodity_codes, country_codes = _load_reference_codes()
    return InfrastatValidator(valid_commodity_codes=commodity_codes, valid_country_codes=country_codes)


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


def get_event_bus() -> EventBus | None:
    return _event_bus


async def get_ingestion_service(session: AsyncSession = None) -> InfrastatIngestionService:
    if session is None:
        async for dependency_session in get_db_session():
            return InfrastatIngestionService(dependency_session)
    return InfrastatIngestionService(session)


async def get_submission_service(session: AsyncSession = None) -> SubmissionService:
    idev_client = IdevClient.from_settings(settings)
    if session is None:
        async for dependency_session in get_db_session():
            return SubmissionService(dependency_session, event_bus=_event_bus, idev_client=idev_client)
    return SubmissionService(session, event_bus=_event_bus, idev_client=idev_client)


async def shutdown_event_bus() -> None:
    global _event_bus
    if _event_bus:
        await _event_bus.close()
        _event_bus = None

