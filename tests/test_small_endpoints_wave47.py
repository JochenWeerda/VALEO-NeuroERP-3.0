"""Wave 47 — Tests fuer kleine Endpoints ohne Testabdeckung:
benchmark_cockpit, idempotency_monitoring, neuro_fast_track.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# benchmark_cockpit
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_benchmark_catalog_returns_200() -> None:
    resp = _client.get("/api/v1/benchmark/catalog", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_benchmark_catalog_custom_tenant() -> None:
    resp = _client.get(
        "/api/v1/benchmark/catalog",
        params={"tenant_id": "TENANT-XYZ", "genossenschaft_name": "Test eG"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_benchmark_read_model_returns_200() -> None:
    resp = _client.get("/api/v1/benchmark/read-model", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_benchmark_catalog_has_expected_structure() -> None:
    resp = _client.get("/api/v1/benchmark/catalog", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    # must have at least one field — exact schema depends on BenchmarkCockpitOut
    assert len(body) > 0


# ---------------------------------------------------------------------------
# idempotency_monitoring
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_idempotency_summary_returns_200() -> None:
    resp = _client.get("/api/v1/process/idempotency/summary", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_idempotency_audit_returns_200() -> None:
    resp = _client.get("/api/v1/process/idempotency/audit", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_idempotency_audit_with_filters() -> None:
    resp = _client.get(
        "/api/v1/process/idempotency/audit",
        params={"tenant_id": "t1", "command_name": "CreateOrder", "aggregate_type": "Order", "limit": 10},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_idempotency_audit_limit_validation() -> None:
    # limit < 1 → validation error
    resp = _client.get("/api/v1/process/idempotency/audit", params={"limit": 0}, headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# neuro_fast_track
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fast_track_whitelist_returns_200() -> None:
    resp = _client.get("/api/v1/neuro/fast-track/whitelist", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "paths" in body
    assert "count" in body
    assert body["count"] == len(body["paths"])


@pytest.mark.unit
def test_fast_track_check_default() -> None:
    resp = _client.get("/api/v1/neuro/fast-track/check", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "is_fast_track" in body


@pytest.mark.unit
def test_fast_track_check_known_get() -> None:
    resp = _client.get(
        "/api/v1/neuro/fast-track/check",
        params={"method": "GET", "path": "/api/v1/articles"},
        headers=_HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["method"] == "GET"
    assert body["path"] == "/api/v1/articles"


@pytest.mark.unit
def test_fast_track_classify_post_whitelist_path() -> None:
    resp = _client.post(
        "/api/v1/neuro/fast-track/classify",
        json={"method": "GET", "path": "/api/v1/articles", "has_ai_context": False},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_fast_track_classify_post_ai_context() -> None:
    resp = _client.post(
        "/api/v1/neuro/fast-track/classify",
        json={"method": "POST", "path": "/api/v1/orders/create", "has_ai_context": True},
        headers=_HEADERS,
    )
    assert resp.status_code == 200


@pytest.mark.unit
def test_fast_track_classify_missing_fields() -> None:
    resp = _client.post("/api/v1/neuro/fast-track/classify", json={}, headers=_HEADERS)
    assert resp.status_code == 422
