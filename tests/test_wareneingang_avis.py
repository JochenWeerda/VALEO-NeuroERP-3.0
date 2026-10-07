"""Wareneingang aus dem Anlieferavis: Bestellung beliefert, Ware im Lager.

Bis zum 07.10.2026 meldete die Maskenaktion "Wareneingang buchen" Erfolg ohne
Buchung; danach war sie eine benannte Luecke. Der vorhandene WE-Dienst buchte
gegen eine Stummel-Tabelle ohne Bestellnummer und ohne Lagerzugang.

Was gilt: Das Avis fuehrt ueber ``bestell_nr`` zur kanonischen Bestellung
(``domain_einkauf.bestellungen``). Lieferschein-Nummer und Lager fragt die Maske
deklarativ. In **einem** Commit: je offene Position Liefermenge fortgeschrieben
und ein Lagerzugang gebucht (Bestandsbuch + Artikelbestand), Bestellung und Avis
erhalten ihren Status. Teillieferungen bleiben beim Lieferschein-Abgleich.
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

HAUS_A = f"we-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"we-b-{uuid.uuid4().hex[:6]}"
LIEFERANT = str(uuid.uuid4())
AKTION = "/api/v1/einkauf/anlieferavis/{}/actions/wareneingang"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM einkauf_anlieferavis LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture(scope="module")
def stamm(engine):
    from sqlalchemy import text

    artikel = [str(uuid.uuid4()), str(uuid.uuid4())]
    lager, fremdlager = str(uuid.uuid4()), str(uuid.uuid4())
    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                       "VALUES (:i, :h, :n, 'Duenger Nord')"), {"i": LIEFERANT, "h": HAUS_A, "n": f"LF-{LIEFERANT[:6]}"})
        for nr, a in enumerate(artikel, start=1):
            v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, current_stock) "
                           "VALUES (:i, :n, :b, :h, 0)"), {"i": a, "n": f"WE-{a[:6]}", "b": f"KAS Sorte {nr}", "h": HAUS_A})
        v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                       "VALUES (:i, :c, 'Halle Nord', :h, true)"), {"i": lager, "c": f"L-{lager[:6]}", "h": HAUS_A})
        v.execute(text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                       "VALUES (:i, :c, 'Fremdhalle', :h, true)"), {"i": fremdlager, "c": f"L-{fremdlager[:6]}", "h": HAUS_B})
    yield {"artikel": artikel, "lager": lager, "fremdlager": fremdlager}
    with engine.begin() as v:
        for tabelle in ("domain_crm.crm_action_audit_log", "public.outbox_events"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE article_id = ANY(:a)"),
                  {"a": artikel})
        aufraeumen(v)
        v.execute(text("DELETE FROM domain_inventory.articles WHERE id = ANY(:a)"), {"a": artikel})
        v.execute(text("DELETE FROM domain_inventory.warehouses WHERE id = ANY(:l)"), {"l": [lager, fremdlager]})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = :i"), {"i": LIEFERANT})


def aufraeumen(v):
    from sqlalchemy import text

    v.execute(text("DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                   "(SELECT id FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h))"), {"h": [HAUS_A, HAUS_B]})
    v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
    v.execute(text("DELETE FROM einkauf_anlieferavis WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def leer(engine, stamm):
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_inventory.inventory_stock_movements WHERE article_id = ANY(:a)"),
                  {"a": stamm["artikel"]})
        v.execute(text("UPDATE domain_inventory.articles SET current_stock = 0 WHERE id = ANY(:a)"),
                  {"a": stamm["artikel"]})
        aufraeumen(v)
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def avis_mit_bestellung(engine, stamm, *, mit_artikel: bool = True, geliefert: float = 0) -> tuple[str, str]:
    from sqlalchemy import text

    bestellung, avis = str(uuid.uuid4()), str(uuid.uuid4())
    nummer = f"EK-{bestellung[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, 'versendet')"),
                  {"i": bestellung, "h": HAUS_A, "n": nummer, "l": LIEFERANT})
        for nr, (artikel, menge) in enumerate(zip(stamm["artikel"], (12, 30)), start=1):
            v.execute(text("INSERT INTO domain_einkauf.bestellung_positionen (id, bestellung_id, pos_nr, article_id, "
                           " artikel_nr, artikel_bezeichnung, menge, menge_geliefert, menge_offen, einheit, status) "
                           "VALUES (:i, :b, :p, :a, :nr, :bez, :m, :g, :o, 't', 'offen')"),
                      {"i": str(uuid.uuid4()), "b": bestellung, "p": nr, "a": artikel if mit_artikel else None,
                       "nr": f"WE-{artikel[:6]}", "bez": f"KAS Sorte {nr}", "m": menge, "g": geliefert,
                       "o": menge - geliefert})
        v.execute(text("INSERT INTO einkauf_anlieferavis (id, tenant_id, lieferant_id, lieferant_name, avis_nummer, "
                       " bestell_nr, erwartetes_datum, status) VALUES (:i, :h, :l, 'Duenger Nord', :a, :n, CURRENT_DATE, 'offen')"),
                  {"i": avis, "h": HAUS_A, "l": LIEFERANT, "a": f"AV-{avis[:6]}", "n": nummer})
    return avis, bestellung


def wert(engine, sql: str, **p):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), p).scalar()


def bestand(engine, artikel: str, lager: str) -> float:
    from app.core.database import SessionLocal
    from app.services.inventory_stock_balance import current_stock

    with SessionLocal() as db:
        return current_stock(db, tenant_id=HAUS_A, article_id=artikel, warehouse_id=lager)


def buchen(client, avis: str, lager: str, haus: str = HAUS_A, **extra):
    nutzlast = {"_mode": "execute", "lieferschein_nr": "LS-4711", "lager_id": lager, **extra}
    return client.post(AKTION.format(avis), headers=kopf(haus), json=nutzlast).json()


class TestBuchung:
    def test_ware_im_lager_und_bestellung_beliefert(self, engine, stamm, client):
        avis, bestellung = avis_mit_bestellung(engine, stamm)
        antwort = buchen(client, avis, stamm["lager"])
        assert antwort["success"] is True, antwort
        a1, a2 = stamm["artikel"]
        assert bestand(engine, a1, stamm["lager"]) == pytest.approx(12.0)
        assert bestand(engine, a2, stamm["lager"]) == pytest.approx(30.0)
        # Der Artikelbestand laeuft mit, wie im Buchungsdienst.
        assert float(wert(engine, "SELECT current_stock FROM domain_inventory.articles WHERE id = :i", i=a2)) == 30.0
        assert wert(engine, "SELECT SUM(menge_offen) FROM domain_einkauf.bestellung_positionen WHERE bestellung_id = :b",
                    b=bestellung) == 0
        assert wert(engine, "SELECT status FROM domain_einkauf.bestellungen WHERE id = :b", b=bestellung) == "geliefert"
        assert wert(engine, "SELECT status FROM einkauf_anlieferavis WHERE id = :a", a=avis) == "ERHALTEN"
        assert wert(engine, "SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements "
                    "WHERE reference_number = 'LS-4711' AND tenant_id = :h", h=HAUS_A) == 2

    def test_nur_das_offene_wird_eingelagert(self, engine, stamm, client):
        avis, _ = avis_mit_bestellung(engine, stamm, geliefert=5)
        assert buchen(client, avis, stamm["lager"])["success"] is True
        assert bestand(engine, stamm["artikel"][0], stamm["lager"]) == pytest.approx(7.0)

    def test_kein_zweiter_wareneingang(self, engine, stamm, client):
        avis, _ = avis_mit_bestellung(engine, stamm)
        assert buchen(client, avis, stamm["lager"])["success"] is True
        zweite = buchen(client, avis, stamm["lager"])
        assert zweite["success"] is False
        assert bestand(engine, stamm["artikel"][0], stamm["lager"]) == pytest.approx(12.0)


class TestGrenzen:
    def test_ohne_lieferschein_oder_lager_nichts(self, engine, stamm, client):
        avis, _ = avis_mit_bestellung(engine, stamm)
        antwort = client.post(AKTION.format(avis), headers=kopf(HAUS_A), json={"_mode": "execute"}).json()
        assert antwort["success"] is False
        assert bestand(engine, stamm["artikel"][0], stamm["lager"]) == 0

    def test_ein_fremdes_lager_wird_nicht_beliefert(self, engine, stamm, client):
        avis, _ = avis_mit_bestellung(engine, stamm)
        antwort = buchen(client, avis, stamm["fremdlager"])
        assert antwort["success"] is False
        assert wert(engine, "SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements "
                    "WHERE warehouse_id = :l", l=stamm["fremdlager"]) == 0

    def test_eine_position_ohne_artikel_haelt_alles_an(self, engine, stamm, client):
        avis, bestellung = avis_mit_bestellung(engine, stamm, mit_artikel=False)
        antwort = buchen(client, avis, stamm["lager"])
        assert antwort["success"] is False
        assert "Artikel" in antwort["error"]
        assert wert(engine, "SELECT SUM(menge_geliefert) FROM domain_einkauf.bestellung_positionen "
                    "WHERE bestellung_id = :b", b=bestellung) == 0

    def test_ein_fremder_mandant_bucht_nichts(self, engine, stamm, client):
        avis, _ = avis_mit_bestellung(engine, stamm)
        antwort = buchen(client, avis, stamm["fremdlager"], haus=HAUS_B)
        assert antwort["success"] is False
        assert bestand(engine, stamm["artikel"][0], stamm["lager"]) == 0

    def test_ohne_bestellbezug_nichts(self, engine, stamm, client):
        from sqlalchemy import text

        avis, _ = avis_mit_bestellung(engine, stamm)
        with engine.begin() as v:
            v.execute(text("UPDATE einkauf_anlieferavis SET bestell_nr = 'EK-gibt-es-nicht' WHERE id = :a"), {"a": avis})
        assert buchen(client, avis, stamm["lager"])["success"] is False


class TestMaske:
    def test_die_maske_fragt_lieferschein_und_lager(self):
        from app.core.screen_definitions import get_screen_definition

        aktion = next(a for a in get_screen_definition("einkauf/anlieferavis")["actions"] if a["key"] == "wareneingang")
        assert aktion["commandEndpoint"] == "/api/v1/einkauf/anlieferavis/{entity_id}/actions/wareneingang"
        felder = {f["key"]: f for f in aktion["inputFields"]}
        assert felder["lieferschein_nr"]["required"] is True
        assert felder["lager_id"]["optionsSource"]["endpoint"] == "/api/v1/inventory/warehouses/"
        assert "stubReason" not in aktion

    def test_die_lagerauswahl_kennt_nur_eigene_lager(self, engine, stamm, client):
        antwort = client.get("/api/v1/inventory/warehouses/", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        kennungen = [w["id"] for w in antwort.json()["items"]]
        assert stamm["lager"] in kennungen and stamm["fremdlager"] not in kennungen
        # Ein Query-Parameter waehlt keinen fremden Mandanten.
        fremd = client.get(f"/api/v1/inventory/warehouses/?tenant_id={HAUS_B}", headers=kopf(HAUS_A)).json()
        assert stamm["fremdlager"] not in [w["id"] for w in fremd["items"]]
