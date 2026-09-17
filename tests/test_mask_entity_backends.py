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
    from app.infrastructure.models.crm_consent import CrmConsent

    assert CrmConsent.__tablename__ == "crm_contact_consents"
    assert CrmConsent.__table_args__[-1]["schema"] == "domain_crm"
    from app.infrastructure.models.crm_consent import CrmConsentHistory

    assert CrmConsentHistory.__tablename__ == "crm_contact_consent_history"
    assert "/api/v1/banken/konten/{konto_id}" in paths
    assert "/api/v1/futter/mischfuttermittel/{misch_id}" in paths


def test_crm_contact_consents_migration_laesst_partner_tabelle_in_ruhe() -> None:
    from pathlib import Path

    source = Path("alembic/versions/crm_consents_20260917.py").read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS domain_crm.crm_contact_consents" in source
    assert "CREATE TABLE IF NOT EXISTS domain_crm.crm_consents" not in source
    assert "ON domain_crm.crm_contact_consents (tenant_id, contact_id)" in source
    assert "ON domain_crm.crm_consents (tenant_id, contact_id)" not in source


def test_mask_bridges_haengen_hinter_sales_beleg() -> None:
    from pathlib import Path

    consents = Path("alembic/versions/crm_consents_20260917.py").read_text(encoding="utf-8")
    sales = Path("alembic/versions/sales_beleg_druck_buchung_20260917.py").read_text(encoding="utf-8")
    bridges = Path("alembic/versions/mask_frontend_bridges_20260917.py").read_text(
        encoding="utf-8"
    )
    assert 'down_revision = "screen_definition_drafts_20260916"' in consents
    assert 'down_revision = "crm_consents_20260917"' in sales
    assert 'down_revision = "sales_beleg_druck_buchung_20260917"' in bridges
