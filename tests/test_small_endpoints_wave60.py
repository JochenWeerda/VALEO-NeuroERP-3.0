"""Wave 60 — Tests fuer crm_duplicates, milchvieh_crosssell, contract_pricing_api."""

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
# crm_duplicates  /api/v1/crm/duplicates/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_crm_duplicates_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_duplicates as ep_mod

    class _FakeDupSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def find_duplicates(self, limit_groups): return {"groups": [], "total": 0}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmDuplicateService", _FakeDupSvc)
    resp = _client.get("/api/v1/crm/duplicates", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "groups" in body


@pytest.mark.unit
def test_crm_duplicates_limit_validation() -> None:
    resp = _client.get("/api/v1/crm/duplicates", params={"limit": 0}, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_crm_merge_preview_merge_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_duplicates as ep_mod
    from app.services.crm_merge_service import MergeError

    class _FakeMergeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def preview(self, master, dup): raise MergeError("Kein Profil")  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmMergeService", _FakeMergeSvc)
    payload = {"masterNr": "KN-001", "duplicateNr": "KN-002"}
    resp = _client.post("/api/v1/crm/duplicates/merge-preview", json=payload, headers=_HEADERS)
    assert resp.status_code == 422


@pytest.mark.unit
def test_crm_merge_preview_success(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.crm_duplicates as ep_mod

    class _FakeMergeSvc:
        def __init__(self, db, tid): pass  # noqa: ANN001
        def preview(self, master, dup): return {"master": master, "duplicate": dup, "safe": True}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "CrmMergeService", _FakeMergeSvc)
    payload = {"masterNr": "KN-001", "duplicateNr": "KN-002"}
    resp = _client.post("/api/v1/crm/duplicates/merge-preview", json=payload, headers=_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["safe"] is True


@pytest.mark.unit
def test_crm_merge_missing_fields() -> None:
    resp = _client.post("/api/v1/crm/duplicates/merge", json={}, headers=_HEADERS)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# milchvieh_crosssell  /api/v1/agrar/milchvieh-crosssell/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_milchvieh_crosssell_list_returns_200(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.milchvieh_crosssell as ep_mod

    class _FakeSvc:
        def __init__(self, db): pass  # noqa: ANN001
        def list_items(self, hygiene_bedarf=None, min_kuehe=None, sort="kraftfutter"):  # noqa: ANN001
            return []

    monkeypatch.setattr(ep_mod, "MilchviehCrossSellService", _FakeSvc)
    resp = _client.get("/api/v1/agrar/milchvieh-crosssell", headers=_HEADERS)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.unit
def test_milchvieh_crosssell_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.milchvieh_crosssell as ep_mod

    class _FakeSvc:
        def __init__(self, db): pass  # noqa: ANN001
        def summary(self): return {"total_betriebe": 0, "gesamt_potenzial_eur": 0}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "MilchviehCrossSellService", _FakeSvc)
    resp = _client.get("/api/v1/agrar/milchvieh-crosssell/summary", headers=_HEADERS)
    assert resp.status_code == 200


@pytest.mark.unit
def test_milchvieh_crosssell_map(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.api.v1.endpoints.milchvieh_crosssell as ep_mod

    class _FakeSvc:
        def __init__(self, db): pass  # noqa: ANN001
        def map_features(self, **kw): return {"type": "FeatureCollection", "features": []}  # noqa: ANN001

    monkeypatch.setattr(ep_mod, "MilchviehCrossSellService", _FakeSvc)
    resp = _client.get("/api/v1/agrar/milchvieh-crosssell/map", headers=_HEADERS)
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# contract_pricing_api  /api/v1/contract-pricing/*
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_contract_pricing_create_price_matrix() -> None:
    payload = {
        "tenant_id": "T001",
        "wirtschaftsjahr": 2026,
        "eintraege": [
            {
                "sorte": "Weizen",
                "qualitaet": "A",
                "preis_eur_t": 200.0,
                "gueltig_von": "2026-01-01",
                "gueltig_bis": "2026-12-31",
                "preis_typ": "fest",
            }
        ],
    }
    resp = _client.post("/api/v1/contract-pricing/price-matrix", json=payload, headers=_HEADERS)
    assert resp.status_code == 201
    body = resp.json()
    assert "matrix_id" in body or "tenant_id" in body


@pytest.mark.unit
def test_contract_pricing_create_lot() -> None:
    payload = {
        "tenant_id": "T001",
        "kontrakt_id": "KON-001",
        "lieferant_id": "LF-001",
        "menge_t": 100.0,
        "sorte": "Gerste",
        "qualitaet": "B",
        "vereinbarter_preis_eur_t": 180.0,
        "preis_typ": "fest",
        "lieferdatum_soll": "2026-08-01",
    }
    resp = _client.post("/api/v1/contract-pricing/lots", json=payload, headers=_HEADERS)
    assert resp.status_code == 201
    body = resp.json()
    assert "lot_id" in body or "kontrakt_id" in body


@pytest.mark.unit
def test_contract_pricing_create_lot_missing_fields() -> None:
    resp = _client.post("/api/v1/contract-pricing/lots", json={}, headers=_HEADERS)
    assert resp.status_code == 422
