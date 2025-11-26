from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from app.db import models
from app.etl.validator import InfrastatValidator
from app.schemas.declaration import DeclarationBatchCreate, DeclarationLineCreate
from app.services.ingestion_service import InfrastatIngestionService


class DummyEventBus:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def publish(self, event_type: str, tenant: str, data: dict[str, Any]) -> None:
        self.events.append({"event_type": event_type, "tenant": tenant, "data": data})


class FakeAsyncSession:
    def __init__(self) -> None:
        self.added: list[Any] = []

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    def add_all(self, objs: list[Any]) -> None:
        self.added.extend(objs)

    async def flush(self) -> None:  # pragma: no cover - nothing to do in fake session
        return None


@pytest.mark.asyncio
async def test_ingestion_sets_ready_status() -> None:
    session = FakeAsyncSession()
    service = InfrastatIngestionService(session)  # type: ignore[arg-type]
    validator = InfrastatValidator()
    event_bus = DummyEventBus()

    payload = DeclarationBatchCreate(
        tenant_id="tenant-a",
        flow_type="dispatch",
        reference_period=date(2025, 10, 1),
        lines=[
            DeclarationLineCreate(
                sequence_no=1,
                commodity_code="12099190",
                country_of_origin="DE",
                country_of_destination="FR",
                net_mass_kg=100.0,
                supplementary_units=None,
                invoice_value_eur=15000.0,
                statistical_value_eur=None,
                nature_of_transaction="11",
                transport_mode="3",
                delivery_terms="DAP",
                line_data={},
            )
        ],
    )

    batch, result = await service.ingest_and_validate(
        payload,
        validator,
        tenant_id="tenant-a",
        event_bus=event_bus,  # type: ignore[arg-type]
    )

    assert batch.status == models.DeclarationStatus.READY
    assert result.validation_error_count == 0
    assert result.ingested_lines == 1
    assert event_bus.events and event_bus.events[0]["event_type"] == "intrastat.validation.completed"


@pytest.mark.asyncio
async def test_ingestion_with_validation_errors_emits_failure_event() -> None:
    session = FakeAsyncSession()
    service = InfrastatIngestionService(session)  # type: ignore[arg-type]
    validator = InfrastatValidator()
    event_bus = DummyEventBus()

    payload = DeclarationBatchCreate(
        tenant_id="tenant-b",
        flow_type="arrival",
        reference_period=date(2025, 10, 1),
        lines=[
            DeclarationLineCreate(
                sequence_no=1,
                commodity_code="12099190",
                country_of_origin="DE",
                country_of_destination="FR",
                net_mass_kg=-5.0,  # invalid -> validation error
                supplementary_units=None,
                invoice_value_eur=15000.0,
                statistical_value_eur=None,
                nature_of_transaction="11",
                transport_mode="3",
                delivery_terms="DAP",
                line_data={},
            )
        ],
    )

    batch, result = await service.ingest_and_validate(
        payload,
        validator,
        tenant_id="tenant-b",
        event_bus=event_bus,  # type: ignore[arg-type]
    )

    assert batch.status == models.DeclarationStatus.ERROR
    assert result.validation_error_count == 1
    assert event_bus.events and event_bus.events[0]["event_type"] == "intrastat.validation.failed"
