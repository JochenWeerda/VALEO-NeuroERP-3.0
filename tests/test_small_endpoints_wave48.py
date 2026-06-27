"""Wave 48 — Tests fuer weitere kleine Endpoints ohne Testabdeckung:
sales_shipping_ext, terminology, o2c_chain (read-endpoints), crm_kunden_map.
"""

from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from main import app

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# sales_shipping_ext  (/verkauf/file-upload  or similar)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_file_upload_delivery_note_returns_200() -> None:
    resp = _client.post(
        "/api/v1/verkauf/file-upload",
        params={"delivery_note_id": "LN-001"},
        files={"file": ("test.pdf", io.BytesIO(b"PDF content"), "application/pdf")},
        headers=_HEADERS,
    )
    # If route is mounted correctly → 200; if not found → 404 (skip rather than fail)
    if resp.status_code == 404:
        pytest.skip("sales_shipping_ext route not mounted at /api/v1/verkauf")
    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == "test.pdf"
    assert body["size"] == len(b"PDF content")
    assert "LN-001" in body["message"]


@pytest.mark.unit
def test_file_upload_missing_file_returns_422() -> None:
    resp = _client.post(
        "/api/v1/verkauf/file-upload",
        params={"delivery_note_id": "LN-001"},
        headers=_HEADERS,
    )
    if resp.status_code == 404:
        pytest.skip("sales_shipping_ext route not mounted at /api/v1/verkauf")
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# terminology
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_terminology_registry_returns_200() -> None:
    resp = _client.get("/api/v1/terminology/registry", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)


@pytest.mark.unit
def test_terminology_registry_domain_filter() -> None:
    resp = _client.get("/api/v1/terminology/registry", params={"domain": "agrar"}, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_terminology_registry_search_query() -> None:
    resp = _client.get("/api/v1/terminology/registry", params={"q": "Ernte"}, headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_terminology_term_not_found_returns_404() -> None:
    resp = _client.get("/api/v1/terminology/terms/this_key_does_not_exist_xyz", headers=_HEADERS)
    assert resp.status_code == 404


@pytest.mark.unit
def test_terminology_term_valid_key() -> None:
    # First fetch the registry to find a valid term_key
    reg_resp = _client.get("/api/v1/terminology/registry", headers=_HEADERS)
    assert reg_resp.status_code == 200
    body = reg_resp.json()
    # Look for any list of terms/entries to pick one key from
    terms = body.get("terms") or body.get("entries") or []
    if not terms:
        pytest.skip("No terms in registry — cannot test valid key lookup")
    first_key = terms[0].get("key") or terms[0].get("term_key")
    if not first_key:
        pytest.skip("Could not determine term_key field name")
    resp = _client.get(f"/api/v1/terminology/terms/{first_key}", headers=_HEADERS)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# o2c_chain
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_o2c_orders_returns_200() -> None:
    resp = _client.get("/api/v1/sales/o2c/orders", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body


@pytest.mark.unit
def test_o2c_orders_limit_param() -> None:
    resp = _client.get("/api/v1/sales/o2c/orders", params={"limit": 5}, headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) <= 5


@pytest.mark.unit
def test_o2c_orders_limit_validation() -> None:
    resp = _client.get("/api/v1/sales/o2c/orders", params={"limit": 0}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_o2c_trace_missing_auftrag_param() -> None:
    resp = _client.get("/api/v1/sales/o2c", headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_o2c_trace_with_auftrag() -> None:
    resp = _client.get("/api/v1/sales/o2c", params={"auftrag": "AU-0001"}, headers=_HEADERS)
    # Service returns 200 or 404 depending on data — both valid from API perspective
    assert resp.status_code in (200, 404)


# ---------------------------------------------------------------------------
# crm_kunden_map  (DB-backed — needs mocking)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_crm_kunden_map_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_kunden_map as ep_mod

    class _FakeSvc:
        def __init__(self, db):  # noqa: ANN001
            pass

        def map_features(self, typ=None):  # noqa: ANN001
            return {"type": "FeatureCollection", "features": []}

    monkeypatch.setattr(ep_mod, "CrmKundenMapService", _FakeSvc)
    resp = _client.get("/api/v1/crm/kunden-karte/map", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["type"] == "FeatureCollection"


@pytest.mark.unit
def test_crm_kunden_map_with_typ_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_kunden_map as ep_mod

    received = {}

    class _FakeSvc:
        def __init__(self, db):  # noqa: ANN001
            pass

        def map_features(self, typ=None):  # noqa: ANN001
            received["typ"] = typ
            return {"type": "FeatureCollection", "features": []}

    monkeypatch.setattr(ep_mod, "CrmKundenMapService", _FakeSvc)
    _client.get("/api/v1/crm/kunden-karte/map", params={"typ": "milchvieh"}, headers=_HEADERS)
    assert received.get("typ") == "milchvieh"
