from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import activities
from app.integrations import crm_core_client
from app.integrations.crm_core_client import CRMCoreActivity
from testgrenze import ersetze_mandant, ersetze_nutzer

TENANT = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
ACTIVITY = "aaaaaaaa-0000-4000-8000-00000000000a"


def _complete(coroutine):
    # All awaited dependencies in these two tests are immediate fakes; no event loop or network.
    try:
        coroutine.send(None)
    except StopIteration as finished:
        return finished.value
    finally:
        coroutine.close()
    raise AssertionError("An isolated dependency unexpectedly suspended")


def _activity(tenant_id: str = TENANT) -> CRMCoreActivity:
    return CRMCoreActivity(
        id=ACTIVITY,
        tenant_id=tenant_id,
        type="call",
        title="Rueckruf",
        status="planned",
        scheduled_at="2026-10-29T09:00:00",
    )


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(activities.router, prefix="/api/v1/crm/activities")
    ersetze_mandant(app, TENANT)
    ersetze_nutzer(app, "CRM_BEARBEITEN")
    return TestClient(app)


def test_core_list_contract_contains_tenant_and_capped_paging(monkeypatch):
    captured: dict[str, str | int] = {}

    class FakeService:
        async def list_activities(self, params: dict[str, str | int]) -> dict:
            assert params["tenant_id"] == TENANT
            assert int(params["skip"]) >= 0
            assert int(params["limit"]) <= 200
            return {"items": [], "total": 0}

    async def fake_request(method: str, path: str, **kwargs):
        assert method == "GET"
        assert path == "/api/v1/activities"
        captured.update(kwargs["params"])
        return await FakeService().list_activities(kwargs["params"])

    monkeypatch.setattr(crm_core_client, "_request", fake_request)

    async def invoke():
        return await crm_core_client.list_activities(tenant_id=TENANT, skip=40, limit=1000)

    assert _complete(invoke()) == ([], 0)
    seen: dict[str, str] = {}

    def mock_core(request: httpx.Request) -> httpx.Response:
        seen.update(dict(request.url.params))
        return httpx.Response(200, json={"items": [], "total": 0})

    with httpx.Client(base_url="http://crm-core.test", transport=httpx.MockTransport(mock_core)) as client:
        response = client.get("/api/v1/activities", params=captured)

    assert response.status_code == 200
    assert seen == {"tenant_id": TENANT, "skip": "40", "limit": "200"}


def test_core_client_rejects_missing_tenant_before_request(monkeypatch):
    request = AsyncMock()
    monkeypatch.setattr(crm_core_client, "_request", request)

    async def invoke():
        with pytest.raises(ValueError, match="tenant_id is required"):
            await crm_core_client.list_activities(tenant_id=" ")

    _complete(invoke())


def test_list_uses_verified_tenant_and_reports_core_total(client):
    async def fake_service(*, tenant_id: str, **kwargs):
        assert tenant_id == TENANT
        return [_activity()], 321

    with patch.object(
        activities.crm_core_client, "list_activities", new_callable=AsyncMock, side_effect=fake_service,
    ) as call:
        response = client.get("/api/v1/crm/activities/?limit=200")

    assert response.status_code == 200, response.text
    assert response.json()["items"][0]["id"] == ACTIVITY
    assert response.json()["total"] == 321
    call.assert_awaited_once()


def test_foreign_row_fails_closed_without_returning_partial_total(client):
    async def fake_service(*, tenant_id: str, **kwargs):
        assert tenant_id == TENANT
        return [_activity(TENANT), _activity(OTHER)], 2

    with patch.object(activities.crm_core_client, "list_activities", fake_service):
        response = client.get("/api/v1/crm/activities/")

    assert response.status_code == 502
    assert response.json() == {"detail": "Activity list unavailable"}


def test_core_failure_is_generic_service_unavailable(client):
    async def fake_service(*, tenant_id: str, **kwargs):
        raise RuntimeError("sensitive downstream payload")

    with patch.object(activities.crm_core_client, "list_activities", fake_service):
        response = client.get("/api/v1/crm/activities/")

    assert response.status_code == 503
    assert response.json() == {"detail": "Activity list unavailable"}
    assert "sensitive downstream payload" not in response.text
