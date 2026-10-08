"""Lager: Code je Mandant, beide Lager-Router im Mandanten, Seed haengt nichts um.

Bis zum 08.10.2026:

* war ``warehouse_code`` systemweit eindeutig;
* lasen, aenderten und stilllegten ``/api/v1/warehouses/{id}`` jedes Lager ueber die
  Id allein; das Anlegen nahm den Mandanten aus dem Payload, die Liste aus dem Query;
* scheiterte ``POST /api/v1/inventory/warehouses`` immer (``tenant_id`` doppelt an das
  Modell uebergeben);
* suchte der Inventar-Seed Lager ueber den Code allein und haengte sie dem seedenden
  Mandanten um; feste Seed-Ids liessen den zweiten Mandanten auf den Primaerschluessel
  laufen.
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

HAUS_A = f"lm-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"lm-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            vorhanden = v.execute(text(
                "SELECT 1 FROM pg_constraint WHERE conname = 'uq_warehouses_mandant_code'"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration lagercode_mandant_20261008 nicht angewandt")
    return motor


@pytest.fixture
def verbindung(engine):
    """Aeussere Transaktion, am Ende verworfen."""
    from sqlalchemy import text

    v = engine.connect()
    aussen = v.begin()
    for haus in (HAUS_A, HAUS_B):
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                  {"i": haus, "n": f"Pruefbetrieb {haus}"})
    yield v
    aussen.rollback()
    v.close()


def lager(v, haus: str, code: str, kennung: str | None = None) -> str:
    from sqlalchemy import text

    kennung = kennung or str(uuid.uuid4())
    v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                   "VALUES (:i, :c, 'Halle', :h, true)"), {"i": kennung, "c": code, "h": haus})
    return kennung


class TestLagercode:
    def test_zwei_mandanten_fuehren_denselben_code(self, verbindung):
        code = f"H{uuid.uuid4().hex[:6]}"
        lager(verbindung, HAUS_A, code)
        lager(verbindung, HAUS_B, code)

    def test_im_selben_mandanten_eindeutig(self, verbindung):
        from sqlalchemy.exc import IntegrityError

        code = f"H{uuid.uuid4().hex[:6]}"
        lager(verbindung, HAUS_A, code)
        punkt = verbindung.begin_nested()
        with pytest.raises(IntegrityError):
            lager(verbindung, HAUS_A, code)
        punkt.rollback()


class TestSeed:
    def test_der_seed_haengt_kein_fremdes_lager_um(self, verbindung):
        from sqlalchemy import text

        from app.seeds.inventory_seed import WAREHOUSES, ensure_warehouses

        code = WAREHOUSES[0]["warehouse_code"]
        fremd = lager(verbindung, HAUS_A, code)
        ensure_warehouses(verbindung, HAUS_B)
        besitzer = dict(verbindung.execute(text(
            "SELECT id, tenant_id FROM domain_inventory.warehouses WHERE warehouse_code = :c "
            "AND tenant_id IN (:a, :b)"), {"c": code, "a": HAUS_A, "b": HAUS_B}).all())
        assert besitzer[fremd] == HAUS_A
        assert sorted(besitzer.values()) == sorted([HAUS_A, HAUS_B])

    def test_belegte_seed_id_fuehrt_nicht_auf_den_primaerschluessel(self, verbindung):
        from sqlalchemy import text

        from app.seeds.inventory_seed import WAREHOUSES, ensure_warehouses

        code = WAREHOUSES[0]["warehouse_code"]
        seed_id = f"seed-warehouse-{code.lower()}"
        if not verbindung.execute(text("SELECT 1 FROM domain_inventory.warehouses WHERE id = :i"),
                                  {"i": seed_id}).scalar():
            lager(verbindung, HAUS_A, code, kennung=seed_id)
        ensure_warehouses(verbindung, HAUS_B)
        neue_id = verbindung.execute(text(
            "SELECT id FROM domain_inventory.warehouses WHERE warehouse_code = :c AND tenant_id = :b"),
            {"c": code, "b": HAUS_B}).scalar()
        assert neue_id and neue_id != seed_id


@pytest.fixture
def client(engine, _enable_dev_token):
    from fastapi.testclient import TestClient

    from app.core import security
    from app.main import app

    # Echter Dev-Token-Weg: die Lager-Adminrolle liest die Token-Claims.
    app.dependency_overrides.pop(security.require_bearer_token, None)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def stamm_lager(engine):
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        lager(v, HAUS_A, f"H{kennung[:6]}", kennung)
    yield kennung
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_inventory.warehouses WHERE tenant_id IN (:a, :b)"),
                  {"a": HAUS_A, "b": HAUS_B})


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


class TestLagerRouter:
    def test_fremdes_lager_ist_unsichtbar_und_unveraenderlich(self, client, stamm_lager):
        weg = f"/api/v1/warehouses/{stamm_lager}"
        assert client.get(weg, headers=kopf(HAUS_A)).status_code == 200
        assert client.get(weg, headers=kopf(HAUS_B)).status_code == 404
        assert client.put(weg, headers=kopf(HAUS_B), json={"name": "x"}).status_code == 404
        assert client.delete(weg, headers=kopf(HAUS_B)).status_code == 404
        assert client.get(weg, headers=kopf(HAUS_A)).json()["is_active"] is True

    def test_die_liste_waehlt_den_mandanten_nicht_per_query(self, client, stamm_lager):
        ids = [z["id"] for z in client.get(f"/api/v1/warehouses/?tenant_id={HAUS_A}",
                                           headers=kopf(HAUS_B)).json()["items"]]
        assert stamm_lager not in ids

    @pytest.mark.parametrize("weg", ["/api/v1/warehouses/", "/api/v1/inventory/warehouses/"])
    def test_anlegen_im_mandanten_aus_dem_header(self, engine, client, stamm_lager, weg):
        from sqlalchemy import text

        code = f"N{uuid.uuid4().hex[:6]}"
        antwort = client.post(weg, headers=kopf(HAUS_B),
                              json={"warehouse_code": code, "name": "Neue Halle", "tenant_id": HAUS_A})
        assert antwort.status_code == 201, antwort.text
        with engine.connect() as v:
            assert v.execute(text("SELECT tenant_id FROM domain_inventory.warehouses WHERE warehouse_code = :c"),
                             {"c": code}).scalar() == HAUS_B
