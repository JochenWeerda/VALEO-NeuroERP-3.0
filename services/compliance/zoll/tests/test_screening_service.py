from __future__ import annotations

import pytest

from app.integrations.event_bus import EventBus
from app.integrations.sanctions_provider import SanctionsProvider
from app.schemas.screening import ScreeningRequest, ScreeningSubject
from app.services.screening_service import ScreeningService


class FakeSession:
    def add_all(self, _):
        return None

    async def flush(self):  ***REMOVED*** pragma: no cover
        return None


class DummyEventBus(EventBus):
    def __init__(self) -> None:  ***REMOVED*** type: ignore[override]
        self.events = []

    async def publish(self, event_type, tenant, data):  ***REMOVED*** type: ignore[override]
        self.events.append((event_type, tenant, data))


@pytest.mark.asyncio
async def test_screening_returns_matches(monkeypatch):
    provider = SanctionsProvider()
    provider._cache = [{"name": "ACME Corp", "list": "EU List", "id": "123"}]  ***REMOVED*** type: ignore[attr-defined]

    bus = DummyEventBus()
    service = ScreeningService(FakeSession(), provider=provider, event_bus=bus)  ***REMOVED*** type: ignore[arg-type]
    payload = ScreeningRequest(
        tenant_id="tenant-a",
        subject=ScreeningSubject(name="ACME Corp", subject_type="customer"),
    )

    response = await service.screen_subject(payload)
    assert response.status == "blocked"
    assert response.matches and response.matches[0].list_name == "EU List"
    assert bus.events and bus.events[0][0] == "export.screening.failed"
