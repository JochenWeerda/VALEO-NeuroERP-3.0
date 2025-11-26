from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from app.db import models
from app.services.scheduler_tasks import ensure_periodic_batches, trigger_workflow_for_ready_batches


class DummyEventBus:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def publish(self, event_type: str, tenant: str, data: dict[str, Any]) -> None:
        self.events.append({"event_type": event_type, "tenant": tenant, "data": data})


class FakeResult:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def scalars(self) -> "FakeResult":
        return self

    def all(self) -> list[Any]:
        return self._items


class FakeAsyncSession:
    def __init__(self, lookup: list[Any]) -> None:
        self._lookup = lookup
        self.flushed = False

    async def execute(self, _stmt) -> FakeResult:  # pragma: no cover - behaviour controlled by lookup
        return FakeResult(self._lookup)

    async def flush(self) -> None:
        self.flushed = True


@pytest.mark.asyncio
async def test_trigger_workflow_for_ready_batches_publishes_event() -> None:
    batch = models.DeclarationBatch(
        tenant_id="tenant-a",
        flow_type="dispatch",
        reference_period=date(2025, 9, 1),
        metadata={},
        status=models.DeclarationStatus.READY,
        item_count=1,
    )
    session = FakeAsyncSession([batch])
    bus = DummyEventBus()

    await trigger_workflow_for_ready_batches(session, bus)  # type: ignore[arg-type]

    assert bus.events and bus.events[0]["data"]["batch_id"] == str(batch.id)


@pytest.mark.asyncio
async def test_ensure_periodic_batches_promotes_collecting_to_validating() -> None:
    batch = models.DeclarationBatch(
        tenant_id="tenant-a",
        flow_type="dispatch",
        reference_period=date(2025, 10, 1),
        metadata={},
        status=models.DeclarationStatus.COLLECTING,
        item_count=0,
    )
    session = FakeAsyncSession([batch])

    await ensure_periodic_batches(session, today=date(2025, 11, 10))

    assert batch.status == models.DeclarationStatus.VALIDATING
    assert session.flushed is True
