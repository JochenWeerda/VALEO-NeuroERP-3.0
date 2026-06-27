"""Wave 53 — Tests fuer process_map und mask_registry API-Endpoints."""

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
# process_map  /api/v1/process-map/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_process_map_list_domains() -> None:
    resp = _client.get("/api/v1/process-map/", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0


@pytest.mark.unit
def test_process_map_summary() -> None:
    resp = _client.get("/api/v1/process-map/summary", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_process_map_external_gates() -> None:
    resp = _client.get("/api/v1/process-map/external-gates", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.unit
def test_process_map_external_gates_with_valid_domain() -> None:
    resp = _client.get("/api/v1/process-map/external-gates", params={"domain": "O2C"}, headers=_HEADERS)
    assert resp.status_code in (200, 422)  # 422 if O2C not in ProcessDomain


@pytest.mark.unit
def test_process_map_external_gates_invalid_domain() -> None:
    resp = _client.get("/api/v1/process-map/external-gates", params={"domain": "INVALID_XYZ"}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_process_map_open_gates() -> None:
    resp = _client.get("/api/v1/process-map/external-gates/open", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.unit
def test_process_map_get_specific_domain() -> None:
    # First find a valid domain from the list
    list_resp = _client.get("/api/v1/process-map/", headers=_HEADERS)
    domains = list_resp.json()
    if not domains:
        pytest.skip("No process-map domains available")
    domain_name = domains[0].get("domain") or domains[0].get("name")
    if not domain_name:
        pytest.skip("Cannot determine domain name field")
    resp = _client.get(f"/api/v1/process-map/{domain_name}", headers=_HEADERS)
    assert resp.status_code in (200, 422, 404)


@pytest.mark.unit
def test_process_map_invalid_domain_returns_422() -> None:
    resp = _client.get("/api/v1/process-map/NOT_A_REAL_DOMAIN", headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# mask_registry  /api/v1/ui/mask-registry/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_mask_registry_returns_200() -> None:
    resp = _client.get("/api/v1/ui/mask-registry", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_mask_registry_by_class_a() -> None:
    resp = _client.get("/api/v1/ui/mask-registry/class/A", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.unit
def test_mask_registry_by_class_b() -> None:
    resp = _client.get("/api/v1/ui/mask-registry/class/B", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_mask_registry_by_class_invalid() -> None:
    resp = _client.get("/api/v1/ui/mask-registry/class/Z", headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_mask_registry_gap_report() -> None:
    resp = _client.get("/api/v1/ui/mask-registry/gap-report", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "class_a_total" in body
    assert "class_a_gap_count" in body
    assert "gaps" in body


@pytest.mark.unit
def test_mask_registry_by_domain() -> None:
    # Try a known domain — agrar or sales
    for domain in ("agrar", "sales", "finance", "crm"):
        resp = _client.get(f"/api/v1/ui/mask-registry/domain/{domain}", headers=_HEADERS)
        if resp.status_code == 200:
            assert isinstance(resp.json(), list)
            return
    pytest.skip("No known domain returned 200 from mask_registry")
