"""Vertraege fuer Masken-Entity-Endpunkte, die nicht mehr am Stub haengen."""

from __future__ import annotations

from app.api.v1.endpoints import compat
from app.core import security
from app.core.config import settings
from app.core.screen_definitions import get_screen_definition
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer jwt-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}


def _disable_dev_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "API_DEV_TOKEN", None)
    monkeypatch.setattr(security, "_validate_jwt", lambda token: {"sub": "test-user"})


def test_native_entity_quellen_zeigen_nicht_auf_den_stub() -> None:
    for screen_id in (
        "agrar/duenger",
        "agrar/saatgut",
        "einkauf/anfrage",
        "einkauf/angebot",
        "einkauf/anlieferavis",
        "einkauf/auftragsbestaetigung",
        "finance/bankkonto",
        "finance/debitor",
        "finance/kreditor",
        "futtermittel/mischfuttermittel",
    ):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        entity = next(ds for ds in screen["dataSources"] if ds["key"] == "entity")
        assert "/api/v1/masks/" not in entity["endpoint"]
        assert "{entity_id}" in entity["endpoint"]


def test_get_einkauf_angebot_returns_contract_payload(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(
        compat,
        "_load_einkauf_angebot",
        lambda db, angebot_id: {
            "id": angebot_id,
            "angebotNummer": "ANG-2026-009",
            "lieferant": "Auricher Suessmost GmbH",
            "artikel": "NPK 15-15-15",
            "preis": 1840.0,
            "gueltigBis": "2026-10-01",
            "status": "GEPRUEFT",
        },
    )
    response = client.get(
        "/api/v1/einkauf/angebote/ang-1",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["angebotNummer"] == "ANG-2026-009"
    assert payload["preis"] == 1840.0


def test_get_einkauf_angebot_returns_404_when_unknown(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(compat, "_load_einkauf_angebot", lambda db, angebot_id: None)
    response = client.get(
        "/api/v1/einkauf/angebote/unbekannt",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Angebot not found"


def test_get_anlieferavis_returns_contract_payload(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(
        compat,
        "_load_einkauf_anlieferavis",
        lambda db, avis_id: {
            "id": avis_id,
            "avisNummer": "AVIS-44",
            "lieferant": "Nordsaat GmbH",
            "geplantesAnlieferDatum": "2026-09-20",
            "status": "GESENDET",
        },
    )
    response = client.get(
        "/api/v1/einkauf/anlieferavis/avis-1",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )
    assert response.status_code == 200
    assert response.json()["avisNummer"] == "AVIS-44"


def test_get_auftragsbestaetigung_returns_contract_payload(monkeypatch):
    _disable_dev_token(monkeypatch)
    monkeypatch.setattr(
        compat,
        "_load_einkauf_auftragsbestaetigung",
        lambda db, bestaetigung_id: {
            "id": bestaetigung_id,
            "bestaetigungsNummer": "AB-88",
            "bestellung": "PO-2026-188",
            "lieferant": "Nordsaat GmbH",
            "status": "offen",
        },
    )
    response = client.get(
        "/api/v1/einkauf/auftragsbestaetigungen/ab-1",
        headers={**AUTH_HEADERS, **TENANT_HEADER},
    )
    assert response.status_code == 200
    assert response.json()["bestaetigungsNummer"] == "AB-88"


def test_agrar_und_finance_routen_sind_registriert() -> None:
    paths = {getattr(route, "path", "") for route in app.routes}
    assert any(p.endswith("/agrar/duenger/{duenger_id}") for p in paths)
    assert any(p.endswith("/agrar/saatgut/{saatgut_id}") for p in paths)
    assert any(p.endswith("/agrar/duenger/stats/overview") for p in paths)
    assert "/api/v1/finance/debitoren/{debitor_id}" in paths
    assert "/api/v1/finance/kreditoren/{kreditor_id}" in paths
    assert "/api/v1/crm/consents/{consent_id}" in paths
    assert "/api/v1/crm/consents/contact/{contact_id}" in paths
    assert "/api/v1/banken/konten/{konto_id}" in paths
    assert "/api/v1/futter/mischfuttermittel/{misch_id}" in paths
