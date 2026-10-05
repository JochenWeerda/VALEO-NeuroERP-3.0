"""Vertraege fuer die Frontend-Pfade, die bisher ohne Route waren."""

from __future__ import annotations

from app.core import security
from app.core.config import settings
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer jwt-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}


def _disable_dev_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
    monkeypatch.setattr(security, "_validate_jwt", lambda token: {"sub": "test-user"})


def _headers(monkeypatch) -> dict[str, str]:
    _disable_dev_token(monkeypatch)
    return {**AUTH_HEADERS, **TENANT_HEADER}


def test_ai_ask_returns_summary(monkeypatch):
    response = client.post(
        "/api/v1/ai/ask",
        headers=_headers(monkeypatch),
        json={"prompt": "Wie buche ich einen Auftrag?", "context": {"domain": "sales"}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "Auftrag" in payload["summary"] or "Prozesskette" in payload["summary"]
    assert payload["confidence"] > 0
    assert payload["sources"]


def test_preise_berechnen_returns_kalkulationsweg(monkeypatch):
    response = client.post(
        "/api/v1/preise/berechnen",
        headers=_headers(monkeypatch),
        json={"artikel_id": "A-1", "menge_kg": 10, "kundengruppe": "GROSSHANDEL"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["netto_preis"] > 0
    assert payload["brutto_preis"] >= payload["netto_preis"]
    assert payload["kalkulationsweg"]


def test_preise_konditionen_ist_ein_objekt(monkeypatch, require_db):
    response = client.get("/api/v1/preise/konditionen", headers=_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert "basispreis" in payload
    assert payload["status"] in {"aktiv", "abgelaufen"}


def test_operations_exceptions_ist_liste(monkeypatch, require_db):
    response = client.get("/api/v1/operations/exceptions", headers=_headers(monkeypatch))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_qualitaet_reklamationen_ist_liste(monkeypatch, require_db):
    response = client.get("/api/v1/qualitaet/reklamationen", headers=_headers(monkeypatch))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_agrar_biostimulanzien_hat_items(monkeypatch, require_db):
    response = client.get("/api/v1/agrar/biostimulanzien?limit=25", headers=_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert isinstance(payload["items"], list)


def test_agrar_kunden_ist_liste(monkeypatch, require_db):
    response = client.get("/api/v1/agrar/kunden", headers=_headers(monkeypatch))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_sales_quotations_print_route_existiert(monkeypatch, require_db):
    response = client.post(
        "/api/v1/sales/quotations/unbekannt/print",
        headers=_headers(monkeypatch),
    )
    assert response.status_code in {400, 404}


def test_einkauf_lieferschein_print_route_existiert(monkeypatch, require_db):
    response = client.post(
        "/api/v1/einkauf/lieferscheine/unbekannt/print",
        headers=_headers(monkeypatch),
    )
    assert response.status_code in {404, 503}


def test_pos_gift_cards_ist_liste(monkeypatch, require_db):
    response = client.get("/api/v1/pos/gift-cards", headers=_headers(monkeypatch))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_finance_stats_hat_open_items(monkeypatch, require_db):
    response = client.get("/api/v1/finance/stats", headers=_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert "open_items" in payload
    assert "open_amount" in payload


def test_fibu_cockpit_hat_mandantenkontext(monkeypatch, require_db):
    response = client.get("/api/v1/finance/followup/fibu/cockpit", headers=_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == 1
    assert "dunning" in payload
    assert "annual_close" in payload


def test_rag_search_ist_liste(monkeypatch, require_db):
    response = client.get("/api/v1/rag/search?query=weizen", headers=_headers(monkeypatch))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analytics_contract_positions_hat_data(monkeypatch, require_db):
    response = client.get("/api/v1/analytics/cubes/contract-positions", headers=_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert isinstance(payload["data"], list)


def test_bruecken_lesen_echte_tabellennamen() -> None:
    from pathlib import Path

    source = Path("app/api/v1/endpoints/mask_frontend_bridges.py").read_text(encoding="utf-8")
    assert "FROM domain_erp.journal_entries" in source
    assert "FROM domain_crm.crm_segment_members" in source
    assert "FROM domain_inventory.agrar_contracts" in source
    assert "domain_finance.journal_entries" not in source
    assert "domain_crm.segment_members" not in source
    assert "domain_agrar.contracts" not in source
