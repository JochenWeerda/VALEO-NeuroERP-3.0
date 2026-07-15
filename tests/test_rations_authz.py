"""Serverseitige Rollenregression fuer alle Feed-Advice-Router."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import (
    rations_controlling,
    rations_integrations,
    rations_lifecycle,
    rations_readiness,
)
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id


_CONTEXT: dict[str, Any] = {"roles": [], "db": object()}
_APP = FastAPI()
_APP.include_router(rations_lifecycle.router)
_APP.include_router(rations_readiness.router)
_APP.include_router(rations_controlling.router)
_APP.include_router(rations_integrations.router)
_APP.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
_APP.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
_APP.dependency_overrides[get_db] = lambda: _CONTEXT["db"]


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(_APP) as value:
        yield value


def _as(roles: list[str], db: Any = None) -> None:
    _CONTEXT["roles"] = roles
    _CONTEXT["db"] = db if db is not None else object()


MUTATION_REQUESTS = [
    ("/lifecycle/groups", {"name": "Hochleistung", "animal_count": 80}),
    ("/lifecycle/rations", {"group_id": "group-1", "name": "Ration A", "snapshot": {"components": []}}),
    ("/lifecycle/rations/ration-1/versions", {"snapshot": {"components": []}, "expected_latest_version_no": 1}),
    ("/lifecycle/versions/version-1/transitions", {"target_status": "in_review", "expected_status": "draft"}),
    ("/readiness/evaluate", {"snapshot": {"components": []}}),
    ("/controlling/observations", {
        "group_id": "group-1", "observation_date": "2026-07-15", "source_ref": "manual-2026-07-15",
    }),
    ("/integrations/icar-ade/import", {"payload": {"event_id": "mlp-1"}}),
    ("/integrations/herd-data/connections", {
        "herd_id": "herd-1",
        "base_url": "https://provider.invalid",
        "endpoint_templates": {
            "group_kpi": "/groups", "health_alert": "/alerts", "genetic_profile": "/genetics",
        },
        "contract_ref": "contract-1",
        "consent_ref": "consent-1",
    }),
    ("/integrations/herd-data/connections/connection-1/sync", {}),
    ("/integrations/herd-data/mock-import", {
        "connection_id": "connection-1", "kind": "group_kpi", "payload": {}, "persist": False,
    }),
]


@pytest.mark.parametrize(("path", "body"), MUTATION_REQUESTS)
def test_every_feed_advice_mutation_rejects_user_without_domain_role(client: TestClient, path: str, body: dict[str, Any]) -> None:
    _as([])
    response = client.post(path, json=body)
    assert response.status_code == 403, (path, response.text)


READ_REQUESTS = [
    "/lifecycle/groups",
    "/lifecycle/rations",
    "/lifecycle/active-rations",
    "/lifecycle/rations/ration-1",
    "/lifecycle/rations/ration-1/versions",
    "/lifecycle/rations/ration-1/audit",
    "/readiness/materials",
    "/controlling/series",
    "/integrations/imports",
    "/integrations/herd-data/connections",
    "/integrations/herd-data/observations",
]


@pytest.mark.parametrize("path", READ_REQUESTS)
def test_every_feed_advice_read_rejects_user_without_domain_role(client: TestClient, path: str) -> None:
    _as([])
    response = client.get(path)
    assert response.status_code == 403, (path, response.text)


def test_reader_may_evaluate_readiness(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    service = SimpleNamespace(evaluate=lambda snapshot, as_of=None: {"status": "ready", "snapshot": snapshot})
    monkeypatch.setattr(rations_readiness, "RationsReadinessService", lambda db, tenant_id: service)
    _as(["FUTTERMITTEL_LESEN"])
    response = client.post("/readiness/evaluate", json={"snapshot": {"components": []}})
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_writer_may_record_controlling_observation(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    service = SimpleNamespace(record=lambda payload: {"id": "observation-1", **payload})
    monkeypatch.setattr(rations_controlling, "RationsControllingService", lambda db, tenant_id, actor: service)
    _as(["FUTTERMITTEL_BEARBEITEN"])
    response = client.post("/controlling/observations", json={
        "group_id": "group-1", "observation_date": "2026-07-15", "source_ref": "manual-1",
    })
    assert response.status_code == 201
    assert response.json()["id"] == "observation-1"


class _ConnectionResult:
    def mappings(self) -> "_ConnectionResult":
        return self

    def first(self) -> dict[str, Any]:
        return {"id": "connection-1", "provider": "ddw", "herd_id": "herd-1"}


class _ConnectionDb:
    def execute(self, statement: Any, params: dict[str, Any]) -> _ConnectionResult:
        return _ConnectionResult()

    def commit(self) -> None:
        return None


def test_connector_configuration_requires_admin_and_accepts_admin(client: TestClient) -> None:
    body = {
        "herd_id": "herd-1",
        "base_url": "https://provider.invalid",
        "endpoint_templates": {
            "group_kpi": "/groups", "health_alert": "/alerts", "genetic_profile": "/genetics",
        },
        "contract_ref": "contract-1",
        "consent_ref": "consent-1",
    }
    _as(["FUTTERMITTEL_BEARBEITEN"], _ConnectionDb())
    forbidden = client.post("/integrations/herd-data/connections", json=body)
    _as(["FUTTERMITTEL_ADMIN"], _ConnectionDb())
    allowed = client.post("/integrations/herd-data/connections", json=body)
    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["id"] == "connection-1"
