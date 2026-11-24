"""Doppelte Bestandsbewegungen technisch ausgeschlossen (Schnitt 2b-2, 24.11.2026) - gegen die echte Datenbank.

Beide Buchungswege - Belegfluss (``docflow_lagerzugang``) und Lagerplatz (``WarehouseService``) - beanspruchen vor
allen Wirkungen den Buchungsschluessel ihres Vorgangs. Geprueft: Wiederholung, Storno, parallele Zweitbuchung,
Transaktionsabbruch, und dass verschiedene Vorgaenge weiter getrennt buchen.
"""
from __future__ import annotations

import threading
import uuid
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.docflow_lagerzugang import buche_lagerzugang, storniere_lagerzugang
from app.services.warehouse_service import WarehouseService

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"id-{uuid.uuid4().hex[:6]}"
    artikel, lager, zone, platz = (str(uuid.uuid4()) for _ in range(4))
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'DUENGER', 'Duenger', 'kg')"), {"id": artikel, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouse_zones (id, warehouse_id, zone_code, name, tenant_id) "
                        "VALUES (:id, :w, 'Z1', 'Zone 1', :t)"), {"id": zone, "w": lager, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouse_bins (id, zone_id, warehouse_id, bin_code, tenant_id) "
                        "VALUES (:id, :z, :w, 'P1', :t)"), {"id": platz, "z": zone, "w": lager, "t": t})
        db.commit()
    try:
        yield {"t": t, "artikel": artikel, "lager": lager, "platz": platz}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.bin_stock WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouse_bins WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouse_zones WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _bewegungen(h) -> list[tuple[str, D]]:
    with SessionLocal() as db:
        return [(r[0], D(str(r[1]))) for r in db.execute(text(
            "SELECT movement_type, quantity FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t "
            "ORDER BY created_at, id"), {"t": h["t"]}).fetchall()]


def _bestand(h) -> tuple[D, D]:
    with SessionLocal() as db:
        artikel = db.execute(text("SELECT COALESCE(current_stock, 0) FROM domain_inventory.articles WHERE id = :a"),
                             {"a": h["artikel"]}).scalar()
        platz = db.execute(text("SELECT COALESCE(SUM(quantity_kg), 0) FROM domain_inventory.bin_stock "
                                "WHERE tenant_id = :t"), {"t": h["t"]}).scalar()
        return D(str(artikel)), D(str(platz))


def _wareneingang(h):
    kopf = {"id": str(uuid.uuid4()), "doc_number": "WE-ID-1"}
    positionen = [{"id": str(uuid.uuid4()), "line_number": 1, "article_number": "DUENGER", "quantity": 500,
                   "unit": "kg", "line_total_net": "250.00"}]
    return kopf, positionen


def test_wareneingang_wiederholt_bucht_einmal_und_storno_einmal(haus):
    kopf, positionen = _wareneingang(haus)
    for _ in range(3):  # Ereignis dreimal zugestellt
        with SessionLocal() as db:
            buche_lagerzugang(db, haus["t"], kopf, positionen, "L1", "test")
            db.commit()
    for _ in range(2):  # Storno zweimal ausgeloest
        with SessionLocal() as db:
            storniere_lagerzugang(db, haus["t"], kopf, "Test", "test")
            db.commit()

    assert _bewegungen(haus) == [("einlagerung", D("500")), ("abgang", D("500"))]
    assert _bestand(haus)[0] == D("0")


def test_lagerplatzbuchung_mit_schluessel_einmal(haus):
    with SessionLocal() as db:
        dienst = WarehouseService(db, haus["t"])
        erste = dienst.book_stock_movement(haus["platz"], haus["artikel"], None, None, D("40"), None, "einlagerung",
                                           buchungsschluessel="wms:einlagerung-1")
        zweite = dienst.book_stock_movement(haus["platz"], haus["artikel"], None, None, D("40"), None, "einlagerung",
                                            buchungsschluessel="wms:einlagerung-1")
        andere = dienst.book_stock_movement(haus["platz"], haus["artikel"], None, None, D("10"), None, "einlagerung",
                                            buchungsschluessel="wms:einlagerung-2")

    assert erste == zweite != andere
    assert len(_bewegungen(haus)) == 2
    assert _bestand(haus) == (D("50"), D("50"))


def test_parallele_zweitbuchung_bucht_nichts(haus):
    start = threading.Barrier(2)
    ergebnisse: list[str] = []
    fehler: list[BaseException] = []

    def buche():
        try:
            with SessionLocal() as db:
                start.wait(timeout=10)
                ergebnisse.append(WarehouseService(db, haus["t"]).book_stock_movement(
                    haus["platz"], haus["artikel"], None, None, D("25"), None, "einlagerung",
                    buchungsschluessel="wms:parallel-1"))
        except BaseException as f:  # noqa: BLE001 - im Test sammeln und unten melden
            fehler.append(f)

    faeden = [threading.Thread(target=buche) for _ in range(2)]
    for f in faeden:
        f.start()
    for f in faeden:
        f.join(timeout=30)

    assert not fehler, fehler
    assert len(set(ergebnisse)) == 1 and len(ergebnisse) == 2
    assert len(_bewegungen(haus)) == 1
    assert _bestand(haus) == (D("25"), D("25"))


def test_abbruch_nimmt_den_anspruch_zurueck(haus):
    with SessionLocal() as db:
        WarehouseService(db, haus["t"]).book_stock_movement(
            haus["platz"], haus["artikel"], None, None, D("30"), None, "einlagerung", commit=False,
            buchungsschluessel="wms:abbruch-1")
        db.rollback()  # Transaktionsabbruch nach allen Wirkungen
    assert _bewegungen(haus) == [] and _bestand(haus) == (D("0"), D("0"))

    with SessionLocal() as db:
        WarehouseService(db, haus["t"]).book_stock_movement(
            haus["platz"], haus["artikel"], None, None, D("30"), None, "einlagerung",
            buchungsschluessel="wms:abbruch-1")

    assert len(_bewegungen(haus)) == 1
    assert _bestand(haus) == (D("30"), D("30"))
