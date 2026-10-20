"""Vertraege fuer die Frontend-Pfade, die bisher ohne Route waren."""

from __future__ import annotations

from app.core import security
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer jwt-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}


def _disable_dev_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
    monkeypatch.setattr(security, "_validate_jwt", lambda token: {"sub": "test-user"})


def _headers(monkeypatch) -> dict[str, str]:
    _disable_dev_token(monkeypatch)
    return {**AUTH_HEADERS, **TENANT_HEADER}


def _finanz_headers(monkeypatch) -> dict[str, str]:
    """Die Finanzwege der Bruecke pruefen seit 12.10.2026 eine Rolle.

    Hier meldet sich die ausdrueckliche Testidentitaet der ``conftest.py`` an (Rolle ``admin``); ein
    Nutzer ohne Rolle bekaeme an diesen Wegen 403.
    """
    return {"Authorization": "Bearer dev-token", **TENANT_HEADER}


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


def _preis_berechnen(schluessel, satz):
    """Die Bruecke direkt, mit ersetzter Preisfindung und ersetztem Steuerschluessel (kein Platzhalterpreis mehr)."""
    import asyncio
    from decimal import Decimal
    from unittest.mock import AsyncMock, MagicMock, patch

    from app.api.v1.endpoints import preis_kalkulation_bridge as bruecke
    from app.api.v1.endpoints.pricing import PriceCalculationResponse
    from app.finance.steuerschluessel import Steuerklaerung

    preis = PriceCalculationResponse(list_price=Decimal("20"), discount=Decimal("10"), net_price=Decimal("18"),
                                     source="price_list")
    db = MagicMock()
    db.execute.return_value.scalar.return_value = schluessel
    satz_fn = (lambda *a, **k: satz) if satz is not None else MagicMock(side_effect=Steuerklaerung("unbekannt"))
    with patch("app.api.v1.endpoints.pricing.calculate_price", AsyncMock(return_value=preis)),          patch("app.finance.steuerschluessel.satz_des_schluessels", satz_fn):
        return asyncio.run(bruecke.preise_berechnen(bruecke.PreisBerechnenIn(artikel_id="A-1", menge_kg=10),
                                                    db=db, tenant_id="t"))


def test_preise_berechnen_rechnet_aus_preisfindung_und_steuerschluessel():
    ergebnis = _preis_berechnen("U7", __import__("decimal").Decimal("7"))
    assert ergebnis["netto_preis"] == 180.0  # 10 x Nettopreis 18 aus der Preisliste, kein Basispreis 100
    assert ergebnis["mwst_betrag"] == 12.6 and ergebnis["brutto_preis"] == 192.6
    assert [s["schritt"].split(" ")[0] for s in ergebnis["kalkulationsweg"]] == ["Listenpreis", "Rabatt", "Umsatzsteuer"]


def test_preise_berechnen_nennt_ohne_gueltigen_schluessel_keine_steuer():
    ergebnis = _preis_berechnen(None, None)
    assert ergebnis["netto_preis"] == 180.0
    assert ergebnis["brutto_preis"] is None and ergebnis["mwst_betrag"] is None
    assert ergebnis["steuerhinweis"]


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
    response = client.get("/api/v1/finance/stats", headers=_finanz_headers(monkeypatch))
    assert response.status_code == 200
    payload = response.json()
    assert "open_items" in payload
    assert "open_amount" in payload


def test_fibu_cockpit_hat_mandantenkontext(monkeypatch, require_db):
    response = client.get("/api/v1/finance/followup/fibu/cockpit", headers=_finanz_headers(monkeypatch))
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
