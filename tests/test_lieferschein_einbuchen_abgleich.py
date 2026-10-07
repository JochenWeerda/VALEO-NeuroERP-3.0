"""Eingangslieferschein: im Mandanten, ganz oder gar nicht eingebucht, einmal abgeglichen.

Bis zum 07.10.2026:

* nahm jeder Lieferschein-Weg den Mandanten aus ``Query("system")``;
* buchte "Einbuchen" jede Position mit eigenem Commit — scheiterte eine, waren die
  anderen gebucht und der Lieferschein "erledigt"; ein zweiter Aufruf buchte alles
  noch einmal; Artikel wurden ohne Mandant aufgeloest;
* zaehlte jeder weitere Abgleich die Liefermenge erneut auf die Bestellung, und
  eine Bestellung stand auf "geliefert", ohne dass Ware im Lager war;
* schrieb der WMS-Buchungsdienst die Bin-Menge mit Vorzeichen ins Bestandsbuch:
  ``pick_out`` mit ``-5`` zaehlte als Zugang, der Artikelbestand lief nicht mit.
"""

from __future__ import annotations

import os
import uuid
from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"ls-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"ls-b-{uuid.uuid4().hex[:6]}"
LIEFERANT = str(uuid.uuid4())
WEG = "/api/v1/einkauf/lieferscheine"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            spalte = v.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_name = 'einkauf_lieferscheine' "
                "AND column_name = 'abgleich_bestellung_id'"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration lieferschein_abgleich_20261007 nicht angewandt")
    return motor


@pytest.fixture(scope="module")
def stamm(engine):
    from sqlalchemy import text

    artikel, fremdartikel = str(uuid.uuid4()), str(uuid.uuid4())
    lager, zone, platz = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:i, :h, :n, 'Saatzucht Nord')"), {"i": LIEFERANT, "h": HAUS_A, "n": f"LF-{LIEFERANT[:6]}"})
        # Artikelnummern sind (noch) systemweit eindeutig; ueber Mandanten greift nur die
        # Artikel-Id, die eine Position ebenfalls tragen darf.
        for a, haus in ((artikel, HAUS_A), (fremdartikel, HAUS_B)):
            v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, current_stock) "
                           "VALUES (:i, :n, 'Saatweizen', :h, 0)"), {"i": a, "n": f"SW-{a[:8]}-{haus}", "h": haus})
        v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                       "VALUES (:i, :c, 'Halle 2', :h, true)"), {"i": lager, "c": f"H-{lager[:8]}", "h": HAUS_A})
        v.execute(text("INSERT INTO domain_inventory.warehouse_zones (id, warehouse_id, zone_code, name, tenant_id) "
                       "VALUES (:i, :w, 'Z1', 'Zone 1', :h)"), {"i": zone, "w": lager, "h": HAUS_A})
        v.execute(text("INSERT INTO domain_inventory.warehouse_bins (id, zone_id, warehouse_id, bin_code, tenant_id, "
                       " capacity_kg) VALUES (:i, :z, :w, 'B-01', :h, 100000)"),
                  {"i": platz, "z": zone, "w": lager, "h": HAUS_A})
    yield {"artikel": artikel, "fremdartikel": fremdartikel, "lager": lager, "platz": platz, "nummer": f"SW-{artikel[:8]}-{HAUS_A}"}
    with engine.begin() as v:
        aufraeumen(v)
        v.execute(text("DELETE FROM domain_inventory.warehouse_bins WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_inventory.warehouse_zones WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_inventory.warehouses WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_inventory.articles WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = :i"), {"i": LIEFERANT})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


def aufraeumen(v):
    from sqlalchemy import text

    h = {"h": [HAUS_A, HAUS_B]}
    v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = ANY(:h)"), h)
    v.execute(text("DELETE FROM domain_inventory.bin_stock WHERE tenant_id = ANY(:h)"), h)
    v.execute(text("DELETE FROM einkauf_lieferscheine WHERE tenant_id = ANY(:h)"), h)
    v.execute(text("DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                   "(SELECT id FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h))"), h)
    v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)"), h)
    v.execute(text("UPDATE domain_inventory.articles SET current_stock = 0 WHERE tenant_id = ANY(:h)"), h)


@pytest.fixture(autouse=True)
def leer(engine, stamm):
    with engine.begin() as v:
        aufraeumen(v)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str = HAUS_A) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def wert(engine, sql: str, **p):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), p).scalar()


def lieferschein(engine, stamm, positionen: list[tuple[str | None, float]], haus: str = HAUS_A) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO einkauf_lieferscheine (id, tenant_id, lieferschein_nr, lieferschein_datum, "
                       " lieferant_id) VALUES (:i, :h, :n, CURRENT_DATE, :l)"),
                  {"i": kennung, "h": haus, "n": f"LS-{kennung[:8]}", "l": LIEFERANT})
        for nr, (artikel_nr, menge) in enumerate(positionen, start=1):
            v.execute(text("INSERT INTO einkauf_lieferschein_positionen (id, lieferschein_id, pos_nr, artikel_nr, menge) "
                           "VALUES (:i, :l, :p, :a, :m)"),
                      {"i": str(uuid.uuid4()), "l": kennung, "p": nr, "a": artikel_nr, "m": menge})
    return kennung


def bestellung(engine, stamm, menge: float = 40) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, 'versendet')"),
                  {"i": kennung, "h": HAUS_A, "n": f"EK-{kennung[:8]}", "l": LIEFERANT})
        v.execute(text("INSERT INTO domain_einkauf.bestellung_positionen (id, bestellung_id, pos_nr, article_id, "
                       " artikel_nr, artikel_bezeichnung, menge, menge_geliefert, menge_offen, einheit, status) "
                       "VALUES (:i, :b, 1, :a, :nr, 'Saatweizen', :m, 0, :m, 'kg', 'offen')"),
                  {"i": str(uuid.uuid4()), "b": kennung, "a": stamm["artikel"], "nr": stamm["nummer"], "m": menge})
    return kennung


def einbuchen(client, kennung: str, stamm, haus: str = HAUS_A):
    return client.post(f"{WEG}/{kennung}/einbuchen", headers=kopf(haus),
                       json={"warehouse_id": stamm["lager"], "default_bin_id": stamm["platz"]})


def buchbestand(stamm) -> float:
    from app.core.database import SessionLocal
    from app.services.inventory_stock_balance import current_stock

    with SessionLocal() as db:
        return current_stock(db, tenant_id=HAUS_A, article_id=stamm["artikel"], warehouse_id=stamm["lager"])


class TestMandant:
    def test_die_liste_zeigt_nur_den_eigenen_mandanten(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["nummer"], 5)])
        assert kennung in [z["id"] for z in client.get(WEG, headers=kopf(HAUS_A)).json()]
        assert kennung not in [z["id"] for z in client.get(f"{WEG}?tenant_id={HAUS_A}", headers=kopf(HAUS_B)).json()]
        assert client.get(f"{WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404

    def test_anlegen_nimmt_den_mandanten_aus_dem_header(self, engine, client):
        nummer = f"LS-H-{uuid.uuid4().hex[:6]}"
        antwort = client.post(f"{WEG}?tenant_id={HAUS_B}", headers=kopf(HAUS_A), json={
            "lieferschein_nr": nummer, "lieferschein_datum": "2026-10-07", "positionen": []})
        assert antwort.status_code == 201, antwort.text
        assert wert(engine, "SELECT tenant_id FROM einkauf_lieferscheine WHERE lieferschein_nr = :n", n=nummer) == HAUS_A


class TestEinbuchen:
    def test_bestandsbuch_lagerplatz_und_artikel_laufen_gemeinsam(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["nummer"], 25)])
        antwort = einbuchen(client, kennung, stamm)
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["movements_created"] == 1
        assert buchbestand(stamm) == 25
        assert float(wert(engine, "SELECT current_stock FROM domain_inventory.articles WHERE id = :i",
                          i=stamm["artikel"])) == 25

    def test_die_id_eines_fremden_artikels_wird_nicht_aufgeloest(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["fremdartikel"], 10)])
        antwort = einbuchen(client, kennung, stamm)
        assert antwort.status_code == 422
        assert float(wert(engine, "SELECT current_stock FROM domain_inventory.articles WHERE id = :i",
                          i=stamm["fremdartikel"])) == 0

    def test_ein_zweites_einbuchen_bucht_nichts(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["nummer"], 25)])
        assert einbuchen(client, kennung, stamm).status_code == 200
        assert einbuchen(client, kennung, stamm).status_code == 409
        assert buchbestand(stamm) == 25

    def test_eine_unbekannte_position_verhindert_die_ganze_buchung(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["nummer"], 10), ("GIBT-ES-NICHT", 5)])
        antwort = einbuchen(client, kennung, stamm)
        assert antwort.status_code == 422
        assert "GIBT-ES-NICHT" in antwort.json()["detail"]
        assert buchbestand(stamm) == 0
        assert wert(engine, "SELECT erledigt FROM einkauf_lieferscheine WHERE id = :i", i=kennung) is False

    def test_fremder_mandant_bucht_nicht_ein(self, engine, client, stamm):
        kennung = lieferschein(engine, stamm, [(stamm["nummer"], 10)])
        assert einbuchen(client, kennung, stamm, haus=HAUS_B).status_code == 404
        assert buchbestand(stamm) == 0


class TestAbgleich:
    def abgleich(self, client, kennung: str, best: str):
        return client.post(f"{WEG}/{kennung}/bestellung-abgleich", headers=kopf(), json={"bestellung_id": best})

    def test_erst_einbuchen_dann_abgleichen(self, engine, client, stamm):
        kennung, best = lieferschein(engine, stamm, [(stamm["nummer"], 40)]), bestellung(engine, stamm)
        antwort = self.abgleich(client, kennung, best)
        assert antwort.status_code == 409
        assert "eingebucht" in antwort.json()["detail"]
        assert wert(engine, "SELECT status FROM domain_einkauf.bestellungen WHERE id = :i", i=best) == "versendet"

    def test_einmal_abgleichen_schreibt_die_menge_einmal_fort(self, engine, client, stamm):
        kennung, best = lieferschein(engine, stamm, [(stamm["nummer"], 40)]), bestellung(engine, stamm)
        assert einbuchen(client, kennung, stamm).status_code == 200
        erster = self.abgleich(client, kennung, best)
        assert erster.status_code == 200, erster.text
        assert erster.json()["bestellung_status"] == "geliefert"
        assert self.abgleich(client, kennung, best).status_code == 409
        assert float(wert(engine, "SELECT menge_geliefert FROM domain_einkauf.bestellung_positionen "
                                  "WHERE bestellung_id = :b", b=best)) == 40
        assert wert(engine, "SELECT abgleich_bestellung_id FROM einkauf_lieferscheine WHERE id = :i", i=kennung) == best


class TestWmsRichtung:
    def test_eine_entnahme_steht_positiv_im_bestandsbuch_und_senkt_den_bestand(self, engine, stamm):
        from app.core.database import SessionLocal
        from app.services.warehouse_service import WarehouseService

        with SessionLocal() as db:
            dienst = WarehouseService(db, HAUS_A)
            dienst.book_stock_movement(stamm["platz"], stamm["artikel"], None, None, Decimal("30"), None, "EINLAGERUNG")
            kennung = dienst.book_stock_movement(stamm["platz"], stamm["artikel"], None, None, Decimal("-5"), None,
                                                 "pick_out")
        assert float(wert(engine, "SELECT quantity FROM domain_inventory.inventory_stock_movements WHERE id = :i",
                          i=kennung)) == 5
        assert buchbestand(stamm) == 25
        assert float(wert(engine, "SELECT current_stock FROM domain_inventory.articles WHERE id = :i",
                          i=stamm["artikel"])) == 25

    def test_eine_umlagerung_bucht_beide_seiten_mit_richtung(self, engine, stamm):
        from app.core.database import SessionLocal
        from app.services.warehouse_service import WarehouseService

        with SessionLocal() as db:
            dienst = WarehouseService(db, HAUS_A)
            dienst.book_stock_movement(stamm["platz"], stamm["artikel"], None, None, Decimal("30"), None, "EINLAGERUNG")
            ab = dienst.book_stock_movement(stamm["platz"], stamm["artikel"], None, None, Decimal("-10"), None,
                                            "transfer_out")
        assert wert(engine, "SELECT movement_type FROM domain_inventory.inventory_stock_movements WHERE id = :i",
                    i=ab) == "umbuchung_ausgang"
        assert buchbestand(stamm) == 20

    def test_vorzeichen_gegen_die_buchungsart_wird_abgelehnt(self, stamm):
        from app.core.database import SessionLocal
        from app.services.warehouse_service import WarehouseService

        with SessionLocal() as db:
            with pytest.raises(ValueError, match="Abgang"):
                WarehouseService(db, HAUS_A).book_stock_movement(
                    stamm["platz"], stamm["artikel"], None, None, Decimal("5"), None, "pick_out")

    def test_ein_fremder_lagerplatz_wird_nicht_bebucht(self, stamm):
        from app.core.database import SessionLocal
        from app.services.warehouse_service import WarehouseService

        with SessionLocal() as db:
            with pytest.raises(ValueError, match="Lagerplatz"):
                WarehouseService(db, HAUS_B).book_stock_movement(
                    stamm["platz"], stamm["fremdartikel"], None, None, Decimal("5"), None, "EINLAGERUNG")


def test_kein_lieferscheinweg_nimmt_den_mandanten_aus_dem_query():
    from pathlib import Path

    quelle = Path("app/api/v1/endpoints/einkauf_lieferschein.py").read_text(encoding="utf-8-sig")
    assert 'Query("system")' not in quelle
