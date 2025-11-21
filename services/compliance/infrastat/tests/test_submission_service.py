from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.config import settings
from app.db import models
from app.schemas.submission import SubmissionRequest
from app.services.submission_service import SubmissionService


class DummyEventBus:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def publish(self, event_type: str, tenant: str, data: dict[str, Any]) -> None:
        self.events.append({"event_type": event_type, "tenant": tenant, "data": data})


class DummyIdevClient:
    def __init__(self, *, fail_times: int = 0) -> None:
        self.upload_calls: list[tuple[str, str]] = []
        self._fail_times = fail_times
        self._counter = 0

    async def upload(self, payload: str, submission_id: str) -> dict[str, Any]:
        self.upload_calls.append((payload, submission_id))
        if self._counter < self._fail_times:
            self._counter += 1
            raise RuntimeError("temporary outage")
        return {"status": "delivered", "success": True, "reference_number": "REF-123"}


class DummyFailingClient(DummyIdevClient):
    async def upload(self, payload: str, submission_id: str) -> dict[str, Any]:
        self.upload_calls.append((payload, submission_id))
        raise RuntimeError("permanent outage")


class FakeAsyncSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.flushed = False

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed = True


@pytest.fixture(autouse=True)
def enable_real_submission() -> None:
    settings.SUBMISSION_ENABLED = True


def _build_batch() -> models.DeclarationBatch:
    batch = models.DeclarationBatch(
        tenant_id="tenant-a",
        flow_type="dispatch",
        reference_period=date(2025, 9, 1),
        metadata={},
        status=models.DeclarationStatus.READY,
        item_count=1,
    )
    batch.id = uuid4()
    batch.lines = [
        SimpleNamespace(
            sequence_no=1,
            commodity_code="12099190",
            country_of_origin="DE",
            country_of_destination="FR",
            net_mass_kg=100.0,
            supplementary_units=None,
            invoice_value_eur=1500.0,
            statistical_value_eur=None,
            nature_of_transaction="11",
            transport_mode="3",
            delivery_terms="DAP",
        )
    ]
    return batch


@pytest.mark.asyncio
async def test_submission_success_triggers_events_and_retry() -> None:
    session = FakeAsyncSession()
    bus = DummyEventBus()
    idev_client = DummyIdevClient(fail_times=1)
    service = SubmissionService(session, event_bus=bus, idev_client=idev_client)  # type: ignore[arg-type]

    batch = _build_batch()

    response = await service.submit(batch, SubmissionRequest(dry_run=False))

    assert response.success is True
    assert batch.status == models.DeclarationStatus.SUBMITTED
    assert len(bus.events) == 2
    assert bus.events[0]["event_type"] == "intrastat.submission.started"
    assert bus.events[1]["event_type"] == "intrastat.submission.completed"
    assert len(idev_client.upload_calls) == 2  # ein Retry


@pytest.mark.asyncio
async def test_submission_dry_run_skips_events() -> None:
    session = FakeAsyncSession()
    bus = DummyEventBus()
    idev_client = DummyIdevClient()
    service = SubmissionService(session, event_bus=bus, idev_client=idev_client)  # type: ignore[arg-type]

    batch = _build_batch()

    response = await service.submit(batch, SubmissionRequest(dry_run=True))

    assert response.dry_run is True
    assert bus.events == []
    assert batch.status == models.DeclarationStatus.READY


@pytest.mark.asyncio
async def test_submission_failure_emits_failed_event() -> None:
    session = FakeAsyncSession()
    bus = DummyEventBus()
    idev_client = DummyFailingClient()
    service = SubmissionService(session, event_bus=bus, idev_client=idev_client)  # type: ignore[arg-type]

    batch = _build_batch()

    response = await service.submit(batch, SubmissionRequest(dry_run=False))

    assert response.success is False
    assert batch.status == models.DeclarationStatus.ERROR
    assert any(event["event_type"] == "intrastat.submission.failed" for event in bus.events)
