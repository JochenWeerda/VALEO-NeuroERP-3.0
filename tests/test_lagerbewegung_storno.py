"""Eine Lagerbewegung wird durch eine Gegenbuchung storniert — fuer jede Bewegungsart.

Bis zum 07.10.2026 meldete die Maskenaktion "stornieren" Erfolg, ohne zu buchen.
Der vorhandene Storno-Dienst (``inventory_correction_service``) kannte nur
``ZUGANG``/``ABGANG``: Ein Storno eines ``in`` wurde als ``ZUGANG`` gebucht und
erhoehte den Bestand ein zweites Mal. Sein Weg nahm den Mandanten aus einem
Query-Parameter.

Was gilt: Die Gegenbuchung traegt genau die negierte bestandswirksame Menge
(``inventory_movement_direction`` ist die eine Stelle fuer die Richtung). Eine
bestandsneutrale Bewegung wird nicht storniert, ein Storno nicht noch einmal, und
ein Storno, der den Bestand negativ machte, wird abgelehnt.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"st-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"st-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/lager/korrekturen/{}/storno"
AKTION = "/api/v1/lager/stock-movements/{}/actions/stornieren"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM domain_inventory.inventory_stock_movements LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture(scope="module")
def stamm(engine):
    from sqlalchemy import text

    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id) "
                       "VALUES (:i, :n, 'Pruefweizen', :h)"), {"i": artikel, "n": f"A-{artikel[:6]}", "h": HAUS_A})
        v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id) "
                       "VALUES (:i, :c, 'Pruefsilo', :h)"), {"i": lager, "c": f"L-{lager[:6]}", "h": HAUS_A})
    yield artikel, lager
    with engine.begin() as v:
        for tabelle in ("domain_crm.crm_action_audit_log", "public.outbox_events"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE article_id = :a"), {"a": artikel})
        v.execute(text("DELETE FROM domain_inventory.articles WHERE id = :a"), {"a": artikel})
        v.execute(text("DELETE FROM domain_inventory.warehouses WHERE id = :l"), {"l": lager})


@pytest.fixture(autouse=True)
def leer(engine, stamm):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE article_id = :a"), {"a": stamm[0]})
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def bewegung(engine, stamm, art: str, menge: float, haus: str = HAUS_A) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            " movement_type, quantity, unit, previous_stock, new_stock, ownership_type, storage_fee_relevant) "
            "VALUES (:i, :h, :a, :l, :t, :m, 'dt', 0, 0, 'owned', false)"
        ), {"i": kennung, "h": haus, "a": stamm[0], "l": stamm[1], "t": art, "m": menge})
    return kennung


def bestand(engine, stamm) -> float:
    from app.core.database import SessionLocal
    from app.services.inventory_stock_balance import current_stock

    with SessionLocal() as db:
        return current_stock(db, tenant_id=HAUS_A, article_id=stamm[0], warehouse_id=stamm[1])


class TestRichtung:
    @pytest.mark.parametrize("art,menge,vorher", [
        ("in", 40, 40.0), ("wareneingang", 40, 40.0), ("einlagerung", 40, 40.0),
        ("out", 15, -15.0), ("adjustment", -7, -7.0), ("adjustment", 7, 7.0),
    ])
    def test_der_storno_hebt_die_bewegung_genau_auf(self, engine, stamm, client, art, menge, vorher):
        bewegung(engine, stamm, "in", 100)
        ziel = bewegung(engine, stamm, art, menge)
        assert bestand(engine, stamm) == pytest.approx(100 + vorher)
        antwort = client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={"bemerkung": "Fehlbuchung"})
        assert antwort.status_code == 201, antwort.text
        assert bestand(engine, stamm) == pytest.approx(100.0)

    def test_eine_bestandsneutrale_bewegung_wird_nicht_storniert(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "reservation", 5)
        antwort = client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={})
        assert antwort.status_code == 422
        assert "bestandsneutral" in antwort.text


class TestGrenzen:
    def test_ein_storno_wird_nicht_noch_einmal_storniert(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 10)
        storno = client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={}).json()
        antwort = client.post(WEG.format(storno["id"]), headers=kopf(HAUS_A), json={})
        assert antwort.status_code == 422

    def test_zweimal_stornieren_bucht_einmal(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 10)
        bewegung(engine, stamm, "in", 50)
        client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={})
        zweite = client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={}).json()
        assert zweite["idempotent"] is True
        assert bestand(engine, stamm) == pytest.approx(50.0)

    def test_kein_negativer_bestand_durch_storno(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 30)
        bewegung(engine, stamm, "out", 25)
        antwort = client.post(WEG.format(ziel), headers=kopf(HAUS_A), json={})
        assert antwort.status_code == 422
        assert bestand(engine, stamm) == pytest.approx(5.0)

    def test_ein_fremder_mandant_storniert_nicht(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 10)
        assert client.post(WEG.format(ziel), headers=kopf(HAUS_B), json={}).status_code == 422
        assert bestand(engine, stamm) == pytest.approx(10.0)

    def test_der_mandant_kommt_nicht_aus_dem_query(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 10)
        antwort = client.post(WEG.format(ziel) + f"?x_tenant_id={HAUS_A}", headers=kopf(HAUS_B), json={})
        assert antwort.status_code == 422
        assert bestand(engine, stamm) == pytest.approx(10.0)


class TestMaskenaktion:
    def test_stornieren_aus_der_maske_bucht_gegen(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 12)
        antwort = client.post(AKTION.format(ziel), headers=kopf(HAUS_A), json={
            "_mode": "execute", "_auditReason": "Doppelt erfasst"}).json()
        assert antwort["success"] is True, antwort
        assert bestand(engine, stamm) == pytest.approx(0.0)

    def test_ohne_begruendung_kein_storno(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "in", 12)
        antwort = client.post(AKTION.format(ziel), headers=kopf(HAUS_A), json={"_mode": "execute"}).json()
        assert antwort["success"] is False
        assert bestand(engine, stamm) == pytest.approx(12.0)

    def test_der_trockenlauf_kennt_die_grenzen(self, engine, stamm, client):
        ziel = bewegung(engine, stamm, "reservation", 3)
        antwort = client.post(AKTION.format(ziel), headers=kopf(HAUS_A), json={"_mode": "dryRun"}).json()
        assert antwort["success"] is False

    def test_die_maske_zeigt_auf_den_weg(self):
        from app.core.screen_definitions import get_screen_definition

        aktion = next(a for a in get_screen_definition("lager/stock-movement")["actions"] if a["key"] == "stornieren")
        assert aktion.get("commandEndpoint") == "/api/v1/lager/stock-movements/{entity_id}/actions/stornieren"
        assert "stubReason" not in aktion
