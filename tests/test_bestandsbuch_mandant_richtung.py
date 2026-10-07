"""Bestandsbuch: Mandant aus dem Kontext, Richtung aus der Tabelle, Storno statt Loeschen.

Bis zum 07.10.2026:

* nahm jeder Inventar-Weg den Mandanten aus einem ``tenant_id``-Query-Parameter;
  beim Dev-Token galt sonst immer der Standardmandant, der Header zaehlte nicht;
* verlangte das Anlegen einer Lagerbewegung fuer ``out`` eine **negative** Menge —
  die Richtungstabelle rechnet ``out`` als ``-quantity``, ein Abgang haette den
  Bestand in jeder Auswertung erhoeht; die Erfassungsmaske schickt positive Mengen
  und scheiterte immer;
* loeschte ``DELETE`` eine gebuchte Bewegung ohne Gegenbuchung;
* korrigierte der Storno das Bestandsbuch, nicht aber den Artikelbestand;
* liess eine einzige Altzeile (``wareneingang``, ``eigen``) die Bewegungsliste mit
  500 scheitern, weil das Lesemodell die Schreibmuster erbte.
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

HAUS_A = f"bb-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"bb-b-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/inventory/stock-movements"


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
    fremdartikel, fremdlager = str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        for a, haus in ((artikel, HAUS_A), (fremdartikel, HAUS_B)):
            v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, current_stock) "
                           "VALUES (:i, :n, 'Weizen A', :h, 0)"), {"i": a, "n": f"BB-{a[:8]}", "h": haus})
        for l, haus in ((lager, HAUS_A), (fremdlager, HAUS_B)):
            v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                           "VALUES (:i, :c, 'Silo 1', :h, true)"), {"i": l, "c": f"S-{l[:8]}", "h": haus})
    yield {"artikel": artikel, "lager": lager, "fremdartikel": fremdartikel, "fremdlager": fremdlager}
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = ANY(:h)"),
                  {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_inventory.articles WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_inventory.warehouses WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def leer(engine, stamm):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = ANY(:h)"),
                  {"h": [HAUS_A, HAUS_B]})
        v.execute(text("UPDATE domain_inventory.articles SET current_stock = 0 WHERE tenant_id = ANY(:h)"),
                  {"h": [HAUS_A, HAUS_B]})
    yield


@pytest.fixture(autouse=True)
def echte_anmeldung(_enable_dev_token):
    """Der echte Dev-Token-Weg: Die Inventar-Rollenpruefung liest die Token-Claims,
    die der conftest-Ersatz fuer ``require_bearer_token`` nie setzt."""
    from app.core import security
    from app.main import app

    app.dependency_overrides.pop(security.require_bearer_token, None)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def wert(engine, sql: str, **p):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), p).scalar()


def buchbestand(stamm) -> float:
    from app.core.database import SessionLocal
    from app.services.inventory_stock_balance import current_stock

    with SessionLocal() as db:
        return current_stock(db, tenant_id=HAUS_A, article_id=stamm["artikel"], warehouse_id=stamm["lager"])


def artikelbestand(engine, stamm) -> float:
    return float(wert(engine, "SELECT current_stock FROM domain_inventory.articles WHERE id = :i", i=stamm["artikel"]))


def buchen(client, stamm, typ: str, menge: float, haus: str = HAUS_A):
    return client.post(f"{WEG}/", headers=kopf(haus), json={
        "article_id": stamm["artikel"], "warehouse_id": stamm["lager"], "movement_type": typ, "quantity": menge,
    })


class TestRichtung:
    def test_ein_abgang_mit_positiver_menge_senkt_beide_bestaende(self, engine, client, stamm):
        assert buchen(client, stamm, "in", 10).status_code == 201
        antwort = buchen(client, stamm, "out", 4)
        assert antwort.status_code == 201, antwort.text
        assert float(antwort.json()["quantity"]) == 4
        assert buchbestand(stamm) == 6
        assert artikelbestand(engine, stamm) == 6

    def test_eine_negative_abgangsmenge_wird_als_betrag_gelesen(self, engine, client, stamm):
        buchen(client, stamm, "in", 10)
        assert buchen(client, stamm, "out", -3).status_code == 201
        assert buchbestand(stamm) == 7

    def test_kein_abgang_ueber_den_bestand(self, engine, client, stamm):
        buchen(client, stamm, "in", 2)
        antwort = buchen(client, stamm, "out", 5)
        assert antwort.status_code == 400
        assert buchbestand(stamm) == 2
        assert artikelbestand(engine, stamm) == 2

    def test_eine_umlagerung_steht_in_der_richtungstabelle(self, engine, client, stamm):
        buchen(client, stamm, "in", 10)
        antwort = buchen(client, stamm, "transfer", -4)
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["movement_type"] == "umbuchung"
        assert buchbestand(stamm) == 6

    def test_die_artikelsumme_liest_die_richtung(self, client, stamm):
        buchen(client, stamm, "in", 10)
        buchen(client, stamm, "out", 4)
        summe = client.get(f"{WEG}/summary/article/{stamm['artikel']}", headers=kopf(HAUS_A)).json()
        assert summe["total_quantity_in"] == 10
        assert summe["total_quantity_out"] == 4
        assert summe["net_quantity_change"] == 6


class TestMandant:
    def test_fremder_artikel_wird_nicht_gebucht(self, client, stamm):
        antwort = client.post(f"{WEG}/", headers=kopf(HAUS_A), json={
            "article_id": stamm["fremdartikel"], "warehouse_id": stamm["lager"], "movement_type": "in", "quantity": 1,
        })
        assert antwort.status_code == 400

    def test_der_query_parameter_waehlt_keinen_fremden_mandanten(self, client, stamm):
        kennung = buchen(client, stamm, "in", 5).json()["id"]
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_A)).status_code == 200
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404
        assert client.get(f"{WEG}/{kennung}?tenant_id={HAUS_A}", headers=kopf(HAUS_B)).status_code == 404
        liste = client.get(f"{WEG}/?tenant_id={HAUS_A}", headers=kopf(HAUS_B)).json()["items"]
        assert kennung not in [b["id"] for b in liste]

    def test_der_header_bestimmt_den_mandanten_beim_buchen(self, engine, client, stamm):
        kennung = buchen(client, stamm, "in", 5).json()["id"]
        assert wert(engine, "SELECT tenant_id FROM domain_inventory.inventory_stock_movements WHERE id = :i",
                    i=kennung) == HAUS_A

    def test_lager_lesen_und_aendern_nur_im_eigenen_mandanten(self, client, stamm):
        weg = f"/api/v1/inventory/warehouses/{stamm['fremdlager']}"
        assert client.get(weg, headers=kopf(HAUS_A)).status_code == 404
        assert client.get(f"{weg}?tenant_id={HAUS_B}", headers=kopf(HAUS_A)).status_code == 404
        assert client.put(weg, headers=kopf(HAUS_A), json={"name": "x"}).status_code == 404
        assert client.get(weg, headers=kopf(HAUS_B)).status_code == 200

    def test_bestandsabfrage_unter_lager_nimmt_den_header(self, client, stamm):
        buchen(client, stamm, "in", 5)
        fremd = client.get(f"/api/v1/lager/bestaende?tenant_id={HAUS_A}&article_id={stamm['artikel']}",
                           headers=kopf(HAUS_B))
        assert fremd.status_code == 200
        assert fremd.json() == []


class TestLesemodell:
    def test_altzeilen_brechen_die_liste_nicht(self, engine, client, stamm):
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(text(
                "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
                " movement_type, quantity, previous_stock, new_stock, auto_created, ownership_type, storage_fee_relevant) "
                "VALUES (:i, :h, :a, :l, 'wareneingang', 3, 0, 3, false, 'owned', false)"
            ), {"i": str(uuid.uuid4()), "h": HAUS_A, "a": stamm["artikel"], "l": stamm["lager"]})
        antwort = client.get(f"{WEG}/", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        assert [b["movement_type"] for b in antwort.json()["items"]] == ["wareneingang"]


class TestStornoStattLoeschen:
    def test_delete_loescht_keine_buchung(self, engine, client, stamm):
        kennung = buchen(client, stamm, "in", 5).json()["id"]
        antwort = client.delete(f"{WEG}/{kennung}", headers=kopf(HAUS_A))
        assert antwort.status_code == 409
        assert "storniert" in antwort.json()["detail"]
        assert wert(engine, "SELECT count(*) FROM domain_inventory.inventory_stock_movements WHERE id = :i",
                    i=kennung) == 1
        assert buchbestand(stamm) == 5

    def test_fremder_mandant_bekommt_404(self, client, stamm):
        kennung = buchen(client, stamm, "in", 5).json()["id"]
        assert client.delete(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404

    def test_der_storno_korrigiert_auch_den_artikelbestand(self, engine, client, stamm):
        from app.core.database import SessionLocal
        from app.services.inventory_correction_service import storno_korrektur

        buchen(client, stamm, "in", 10)
        kennung = buchen(client, stamm, "out", 4).json()["id"]
        with SessionLocal() as db:
            storno_korrektur(db, kennung, HAUS_A, bemerkung="Fehlbuchung")
        assert buchbestand(stamm) == 10
        assert artikelbestand(engine, stamm) == 10


def test_kein_inventarweg_nimmt_den_mandanten_aus_dem_query():
    from pathlib import Path

    for datei in (*Path("app/domains/inventory/api").glob("*.py"), Path("app/api/v1/endpoints/inventory_operations.py")):
        quelle = datei.read_text(encoding="utf-8-sig")
        assert "tenant_id: Optional[str] = Query(" not in quelle, datei
        assert "x_tenant_id: Optional[str] = None" not in quelle, datei
        assert "tenant_id or DEFAULT_TENANT" not in quelle, datei
