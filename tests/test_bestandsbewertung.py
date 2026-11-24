"""Gleitender Durchschnittspreis und Einstandspreis beim Einlagern - gegen die echte Datenbank (M3, 24.11.2026)."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.bestandsbewertung import BewertungNichtBestimmbar, bewerte, gleitender_durchschnitt
from app.services.docflow_lagerzugang import buche_lagerzugang, einstandspreis, storniere_lagerzugang

pytestmark = pytest.mark.integration
D = Decimal


@pytest.fixture
def haus():
    mandant = f"bw-{uuid.uuid4().hex[:6]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": mandant})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'WEIZEN', 'Weizen', 't')"), {"id": artikel, "t": mandant})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": mandant})
        db.commit()
    try:
        yield {"mandant": mandant, "artikel": artikel, "lager": lager}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _bewegung(haus, art: str, menge: str, preis: str | None, tag: int, einheit: str = "t",
              storno_ref: str | None = None) -> str:
    kennung = str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            "movement_type, quantity, unit, unit_cost, previous_stock, new_stock, movement_date, ownership_type, "
            "storage_fee_relevant, storno_ref) VALUES (:id, :t, :a, :w, :art, :m, :e, :p, 0, 0, :d, 'owned', false, :s)"),
            {"id": kennung, "t": haus["mandant"], "a": haus["artikel"], "w": haus["lager"], "art": art, "m": menge,
             "e": einheit, "p": preis, "d": date(2026, 11, tag), "s": storno_ref})
        db.commit()
    return kennung


def _schnitt(haus, stichtag=None):
    with SessionLocal() as db:
        return gleitender_durchschnitt(db, haus["mandant"], haus["artikel"], stichtag)


def test_zugaenge_verschieben_den_schnitt_abgaenge_nicht(haus):
    _bewegung(haus, "einlagerung", "10", "100", 1)
    _bewegung(haus, "einlagerung", "10", "200", 2)
    assert _schnitt(haus).preis == D("150")
    _bewegung(haus, "abgang", "5", None, 3)
    assert (_schnitt(haus).preis, _schnitt(haus).bestand) == (D("150"), D("15"))
    _bewegung(haus, "einlagerung", "5", "300", 4)
    assert _schnitt(haus).preis == D("187.5")


def test_stichtag_bewertet_den_damaligen_schnitt(haus):
    _bewegung(haus, "einlagerung", "10", "100", 1)
    _bewegung(haus, "einlagerung", "10", "200", 5)
    assert _schnitt(haus, date(2026, 11, 3)).preis == D("100")


def test_storno_eines_zugangs_nimmt_seinen_wert_zurueck(haus):
    _bewegung(haus, "einlagerung", "10", "100", 1)
    zweiter = _bewegung(haus, "einlagerung", "10", "200", 2)
    _bewegung(haus, "abgang", "10", "200", 3, storno_ref=zweiter)
    assert (_schnitt(haus).preis, _schnitt(haus).bestand) == (D("100"), D("10"))


def test_ohne_einstandspreis_kein_schnitt_und_keine_bewertung(haus):
    _bewegung(haus, "einlagerung", "10", None, 1)
    assert _schnitt(haus).preis is None
    with SessionLocal() as db:
        assert bewerte(db, haus["mandant"], haus["artikel"], D("2"), "t") is None


def test_zugang_ohne_preis_aendert_den_schnitt_nicht(haus):
    _bewegung(haus, "einlagerung", "10", "100", 1)
    _bewegung(haus, "einlagerung", "10", None, 2)
    _bewegung(haus, "einlagerung", "20", "200", 3)
    # Bestand 20 zum Schnitt 100, dann +20 zu 200 -> 150
    assert _schnitt(haus).preis == D("150")


def test_andere_einheit_wird_mit_preis_umgerechnet(haus):
    _bewegung(haus, "einlagerung", "2000", "0.10", 1, einheit="kg")  # 2 t zu 0,10 EUR/kg = 100 EUR/t
    assert _schnitt(haus).preis == D("100")
    with SessionLocal() as db:
        assert bewerte(db, haus["mandant"], haus["artikel"], D("15"), "dt") == D("150.00")  # 1,5 t


def test_unbekannte_einheit_ist_nicht_bestimmbar(haus):
    _bewegung(haus, "einlagerung", "3", "10", 1, einheit="Sack")
    with pytest.raises(BewertungNichtBestimmbar):
        _schnitt(haus)


def test_einstandspreis_aus_dem_nettowert_der_position():
    assert einstandspreis({"line_total_net": "1900.00"}, D("10")) == D("190")
    assert einstandspreis({"line_total_net": None}, D("10")) is None
    assert einstandspreis({"line_total_net": "0"}, D("10")) is None


def test_einlagern_und_storno_schreiben_den_einstandspreis(haus):
    kopf = {"id": str(uuid.uuid4()), "doc_number": "WE-1"}
    positionen = [{"line_number": 1, "article_number": "WEIZEN", "quantity": 50, "unit": "dt",
                   "line_total_net": "1000.00"}]  # 5 t fuer 1.000 EUR = 200 EUR/t
    with SessionLocal() as db:
        buche_lagerzugang(db, haus["mandant"], kopf, positionen, "L1", "test")
        db.commit()
    assert _schnitt(haus).preis == D("200")
    with SessionLocal() as db:
        storniere_lagerzugang(db, haus["mandant"], kopf, "Testlauf", "test")
        db.commit()
    assert (_schnitt(haus).preis, _schnitt(haus).bestand) == (D("200"), D("0"))
