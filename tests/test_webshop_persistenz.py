"""Webshop-Anbindung speichert in der Datenbank und legt Auftraege nur echt an (20.10.2026).

Vorher legte keine Migration die Webshop-Tabellen an: Konfigurationen und Bestellungen lagen im Arbeitsspeicher.
"Verarbeiten" meldete "Auftrag im ERP angelegt" mit erfundener Nummer — auch fuer unbekannte Bestellungen, und obwohl
das Anlegen des Auftrags ohne Kunde jedes Mal scheiterte (Fehler verschluckt). Diese Vertraege halten fest:

* Import ist idempotent ueber die externe Bestellnummer und meldet fachliche Blocker;
* Bestellungen und Protokoll liegen in der Datenbank, mandantengenau;
* Verarbeiten legt einen echten Auftrag fuer den per E-Mail zugeordneten Kunden an, sonst Blocker
  KUNDE_NICHT_ZUGEORDNET; unbekannte Bestellungen ergeben 404.

Geprueft gegen eine frische Pruefstand-Datenbank (``TEST_DATABASE_URL``/``DATABASE_URL``).
"""
from __future__ import annotations

import os
import uuid

import pytest
from fastapi import Request  # Modulebene: FastAPI loest die Annotation hier auf

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

HAUS_A = f"shop-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"shop-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_shared.webshop_bestellungen LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar oder nicht migriert: {fehler}")
    with motor.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) ON CONFLICT (id) DO NOTHING"),
                      {"id": haus, "n": f"Pruefbetrieb {haus}"})
    yield motor
    with motor.begin() as v:
        for tabelle in ("domain_crm.sales_orders", "domain_crm.customers", "domain_shared.webshop_bestellungen",
                        "domain_shared.webshop_sync_log", "domain_shared.webshop_configs"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def gepruefte_person():
    from app.auth.deps import get_current_user
    from app.core.security import require_bearer_token
    from app.main import app
    from testgrenze import ALLE_FACHROLLEN, mandant_aus_kopf

    def geprueft(request: Request) -> str:
        tenant = mandant_aus_kopf(request)
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": "verkauf", "tenant_id": tenant, "roles": list(ALLE_FACHROLLEN)}
        return "pruefstand"

    app.dependency_overrides[require_bearer_token] = geprueft
    app.dependency_overrides[get_current_user] = lambda: {"sub": "verkauf", "roles": list(ALLE_FACHROLLEN)}
    yield
    app.dependency_overrides.pop(require_bearer_token, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def bestellung(nr: str, email: str = "hof@example.invalid", **abweichung) -> dict:
    daten = {
        "externe_bestellnr": nr, "shop_system": "SHOPWARE6", "kunde_email": email, "kunde_name": "Hof Janssen",
        "artikel_positionen": [{"artikel_nr": "ART-1", "menge": 2, "preis_brutto": 10.0}],
        "gesamtbetrag_brutto": 20.0, "bestelldatum": "2026-10-20", "status": "NEU",
    }
    daten.update(abweichung)
    return daten


def test_import_ist_idempotent_meldet_blocker_und_liegt_in_der_datenbank(engine, client):
    from sqlalchemy import text

    kopf = {"X-Tenant-ID": HAUS_A}
    erster = client.post("/api/v1/webshop/bestellungen/import", headers=kopf,
                         json=[bestellung("WS-1"), bestellung("WS-2", gesamtbetrag_brutto=99.0)])
    assert erster.status_code == 200, erster.text
    assert erster.json()["neue_bestellungen"] == 2 and erster.json()["fehler"] == 1
    zweiter = client.post("/api/v1/webshop/bestellungen/import", headers=kopf, json=[bestellung("WS-1")])
    assert zweiter.json()["duplikate"] == ["WS-1"] and zweiter.json()["neue_bestellungen"] == 0
    with engine.connect() as v:
        anzahl = v.execute(text("SELECT count(*) FROM domain_shared.webshop_bestellungen WHERE tenant_id = :h"),
                           {"h": HAUS_A}).scalar()
        protokoll = v.execute(text("SELECT count(*) FROM domain_shared.webshop_sync_log WHERE tenant_id = :h"),
                              {"h": HAUS_A}).scalar()
    assert anzahl == 2 and protokoll == 2
    assert client.get("/api/v1/webshop/bestellungen", headers={"X-Tenant-ID": HAUS_B}).json() == []


def test_verarbeiten_ohne_zugeordneten_kunden_legt_keinen_auftrag_an(engine, client):
    from sqlalchemy import text

    kopf = {"X-Tenant-ID": HAUS_A}
    client.post("/api/v1/webshop/bestellungen/import", headers=kopf,
                json=[bestellung("WS-OHNE", email="unbekannt@example.invalid")])
    antwort = client.post("/api/v1/webshop/bestellungen/WS-OHNE/verarbeiten", headers=kopf).json()
    assert antwort["verarbeitet"] is False and "KUNDE_NICHT_ZUGEORDNET" in antwort["blockers"]
    with engine.connect() as v:
        assert v.execute(text("SELECT count(*) FROM domain_crm.sales_orders WHERE tenant_id = :h"),
                         {"h": HAUS_A}).scalar() == 0


def test_verarbeiten_legt_den_auftrag_fuer_den_kunden_an(engine, client):
    from sqlalchemy import text

    kunde = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, email) "
                       "VALUES (:i, :h, :n, 'Hof Janssen', 'kunde@example.invalid')"),
                  {"i": kunde, "h": HAUS_A, "n": f"K-{kunde[:6]}"})
    kopf = {"X-Tenant-ID": HAUS_A}
    client.post("/api/v1/webshop/bestellungen/import", headers=kopf,
                json=[bestellung("WS-MIT", email="Kunde@example.invalid")])
    antwort = client.post("/api/v1/webshop/bestellungen/WS-MIT/verarbeiten", headers=kopf).json()
    assert antwort["verarbeitet"] is True, antwort
    with engine.connect() as v:
        auftrag = v.execute(text("SELECT customer_id, total_amount FROM domain_crm.sales_orders "
                                 "WHERE tenant_id = :h AND order_number = :nr"),
                            {"h": HAUS_A, "nr": antwort["auftrag_nr"]}).mappings().first()
    assert str(auftrag["customer_id"]) == kunde and float(auftrag["total_amount"]) == 20.0
    erneut = client.post("/api/v1/webshop/bestellungen/WS-MIT/verarbeiten", headers=kopf).json()
    assert erneut["auftrag_nr"] == antwort["auftrag_nr"]


def test_unbekannte_bestellung_ergibt_404(client):
    antwort = client.post("/api/v1/webshop/bestellungen/GIBT-ES-NICHT/verarbeiten", headers={"X-Tenant-ID": HAUS_A})
    assert antwort.status_code == 404
