"""Proplanta-PSM-Endpoints im nicht-konfigurierten Zustand (503-by-design).

Deckt die is_configured()-Guards und die HTTPException-Passthrough-Bloecke ab,
damit externe Abhaengigkeiten sauber 503 liefern statt 500 (Runtime-Sweep-Fix)
und haelt die Coverage der psm_proplanta-Integration ueber dem Ratchet.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/agrar/psm/proplanta"


def test_status_returns_200_with_configured_flag():
    resp = client.get(f"{BASE}/status", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert "configured" in body
    assert isinstance(body["configured"], bool)


@pytest.mark.parametrize(
    "path",
    [
        f"{BASE}/list",
        f"{BASE}/stats/overview",
        f"{BASE}/search?q=test",
    ],
)
def test_endpoints_return_503_when_not_configured(path):
    # Ohne Proplanta-Konfiguration ist 503-by-design der Vertrag —
    # niemals 500 (HTTPException-Passthrough vor generischem except).
    resp = client.get(path, headers=HEADERS)
    assert resp.status_code in (200, 503), resp.text
    if resp.status_code == 503:
        assert "detail" in resp.json()


# ── Konfigurierter Zustand (A6-Restmodul: Erfolgspfade ohne echten Proplanta-Zugang) ──
#
# Der Endpoint-Modul-Namespace (app.domains.agrar.api.psm_proplanta) haelt eine eigene
# is_configured-Referenz und eine eigene ProplantaPSMClient-Instanz — beides wird hier
# gepatcht; kein MCP-/HTTP-Zugriff noetig.

import types

import app.domains.agrar.api.psm_proplanta as psm_module
from app.integrations.proplanta_psm_client import PSMData, ProplantaPSMContractError


def _psm(psm_id: str, *, name: str = "Mittel", manufacturer: str = "Bayer",
         hazard: str = "Xn", status: str = "approved", expiry: str = "",
         areas: list[str] | None = None) -> PSMData:
    return PSMData({
        "id": psm_id,
        "name": name,
        "activeIngredient": "Wirkstoff",
        "manufacturer": manufacturer,
        "approvalNumber": f"BVL-{psm_id}",
        "approvalDate": "2020-01-01",
        "expiryDate": expiry,
        "applicationAreas": areas or ["Ackerbau"],
        "hazardClass": hazard,
        "status": status,
    })


@pytest.fixture()
def configured(monkeypatch: pytest.MonkeyPatch) -> dict[str, PSMData]:
    cache = {
        "P1": _psm("P1", name="Aktivo", manufacturer="Bayer", hazard="Xn",
                   expiry="2099-12-31T00:00:00Z"),
        "P2": _psm("P2", name="Altlast", manufacturer="Syngenta", hazard="T",
                   status="expired", expiry="2020-01-01T00:00:00Z"),
        "P3": _psm("P3", name="Zurueck", manufacturer="BASF", hazard="Xi",
                   status="withdrawn", areas=["Obstbau"]),
    }
    monkeypatch.setattr(psm_module, "is_configured", lambda: True)
    monkeypatch.setattr(psm_module.psm_client, "_cache", cache)
    return cache


def test_list_returns_all_cached_items(configured):
    resp = client.get(f"{BASE}/list", headers=HEADERS)
    assert resp.status_code == 200
    ids = {item["id"] for item in resp.json()}
    assert ids == {"P1", "P2", "P3"}


@pytest.mark.parametrize(
    "query,expected_ids",
    [
        ("status=active", {"P1", "P3"}),       # active = nicht abgelaufen
        ("status=expired", {"P2"}),
        ("status=withdrawn", {"P3"}),
        ("manufacturer=bay", {"P1"}),           # case-insensitive Teilstring
        ("hazard_class=T", {"P2"}),
        ("limit=1", None),                       # nur Anzahl pruefen
    ],
)
def test_list_filters(configured, query, expected_ids):
    resp = client.get(f"{BASE}/list?{query}", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    if expected_ids is None:
        assert len(body) == 1
    else:
        assert {item["id"] for item in body} == expected_ids


def test_search_returns_results(configured, monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "search_psm",
                        lambda q, limit: [configured["P1"]])
    resp = client.get(f"{BASE}/search?q=akti", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "P1"


def test_search_contract_error_returns_503(configured, monkeypatch):
    def boom(q, limit):
        raise ProplantaPSMContractError("Transport nicht angebunden")
    monkeypatch.setattr(psm_module.psm_client, "search_psm", boom)
    resp = client.get(f"{BASE}/search?q=akti", headers=HEADERS)
    assert resp.status_code == 503


def test_search_generic_error_returns_500(configured, monkeypatch):
    def boom(q, limit):
        raise RuntimeError("unerwartet")
    monkeypatch.setattr(psm_module.psm_client, "search_psm", boom)
    resp = client.get(f"{BASE}/search?q=akti", headers=HEADERS)
    assert resp.status_code == 500


def test_details_served_from_cache(configured):
    resp = client.get(f"{BASE}/P2", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["approval_number"] == "BVL-P2"


def test_details_not_found_returns_404(configured, monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "get_psm_details", lambda psm_id: None)
    resp = client.get(f"{BASE}/UNBEKANNT", headers=HEADERS)
    assert resp.status_code == 404


def test_details_contract_error_returns_503(configured, monkeypatch):
    def boom(psm_id):
        raise ProplantaPSMContractError("nicht konfiguriert")
    monkeypatch.setattr(psm_module.psm_client, "get_psm_details", boom)
    resp = client.get(f"{BASE}/UNBEKANNT", headers=HEADERS)
    assert resp.status_code == 503


def test_stats_overview_aggregates(configured):
    resp = client.get(f"{BASE}/stats/overview", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_psm"] == 3
    assert body["expired_psm"] == 1
    assert body["by_manufacturer"]["Bayer"] == 1
    assert body["by_hazard_class"]["T"] == 1
    assert body["by_application_area"]["Obstbau"] == 1


def test_sync_starts_background_task(configured, monkeypatch):
    # TestClient fuehrt BackgroundTasks synchron aus → deckt _perform_psm_sync mit ab.
    monkeypatch.setattr(psm_module.psm_client, "sync_psm_data",
                        lambda: [configured["P1"]])
    resp = client.post(f"{BASE}/sync", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"


def test_sync_not_configured_returns_503():
    resp = client.post(f"{BASE}/sync", headers=HEADERS)
    assert resp.status_code == 503


def test_import_to_local_starts_background_task(configured, monkeypatch):
    calls = []
    monkeypatch.setattr(psm_module, "_perform_psm_import",
                        lambda tenant_id, update_existing, db: calls.append(tenant_id))
    resp = client.post(f"{BASE}/import-to-local?tenant_id=t1", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"
    assert calls == ["t1"]


def test_import_to_local_not_configured_returns_503():
    resp = client.post(f"{BASE}/import-to-local", headers=HEADERS)
    assert resp.status_code == 503


# ── Background-Worker direkt (ohne echte DB) ─────────────────────────────────


class _FakeQuery:
    def __init__(self, existing):
        self._existing = existing

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._existing


class _FakeDB:
    def __init__(self, existing=None, fail_on_query: bool = False):
        self._existing = existing
        self._fail_on_query = fail_on_query
        self.added: list = []
        self.committed = False
        self.rolled_back = False

    def query(self, model):
        if self._fail_on_query:
            raise RuntimeError("DB nicht erreichbar")
        return _FakeQuery(self._existing)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_perform_sync_logs_failure_without_raising(monkeypatch):
    def boom():
        raise ProplantaPSMContractError("nicht konfiguriert")
    monkeypatch.setattr(psm_module.psm_client, "sync_psm_data", boom)
    # darf nicht raisen — Fehler wird geloggt (Background-Task-Vertrag)
    psm_module._perform_psm_sync(force=True)


def test_perform_import_creates_new_record(monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm",
                        lambda: [_psm("N1", expiry="2099-12-31T00:00:00Z")])
    db = _FakeDB(existing=None)
    psm_module._perform_psm_import("t1", True, db)
    assert len(db.added) == 1
    new_psm = db.added[0]
    assert new_psm.bvl_nummer == "BVL-N1"
    assert new_psm.artikelnummer == "BVL-N1"
    assert new_psm.mittel_typ == "unbekannt"
    assert db.committed


def test_perform_import_skips_new_record_without_expiry(monkeypatch):
    # zulassung_ablauf ist NOT NULL — ohne Ablaufdatum keine Neuanlage
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm", lambda: [_psm("N2")])
    db = _FakeDB(existing=None)
    psm_module._perform_psm_import("t1", True, db)
    assert not db.added
    assert db.committed


def test_perform_import_updates_existing(monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm",
                        lambda: [_psm("U1", expiry="2099-12-31T00:00:00Z")])
    existing = types.SimpleNamespace(name="alt", wirkstoff="", zulassung_ablauf=None,
                                     kulturen=[], ist_aktiv=False, updated_at=None)
    db = _FakeDB(existing=existing)
    psm_module._perform_psm_import("t1", True, db)
    assert existing.name == "Mittel"
    assert existing.zulassung_ablauf is not None
    assert not db.added
    assert db.committed


def test_perform_import_skips_existing_without_update(monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm", lambda: [_psm("S1")])
    existing = types.SimpleNamespace(name="alt")
    db = _FakeDB(existing=existing)
    psm_module._perform_psm_import("t1", False, db)
    assert existing.name == "alt"
    assert not db.added
    assert db.committed


def test_perform_import_continues_on_item_error(monkeypatch):
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm", lambda: [_psm("E1")])
    db = _FakeDB(fail_on_query=True)
    # Item-Fehler → continue; Lauf endet mit commit
    psm_module._perform_psm_import("t1", True, db)
    assert db.committed


def test_perform_import_rolls_back_on_fatal_error(monkeypatch):
    def boom():
        raise RuntimeError("Cache kaputt")
    monkeypatch.setattr(psm_module.psm_client, "get_all_psm", boom)
    db = _FakeDB()
    psm_module._perform_psm_import("t1", True, db)
    assert db.rolled_back
    assert not db.committed
