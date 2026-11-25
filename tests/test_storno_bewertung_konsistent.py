"""Storno einer Lagerbewegung und gleitender Durchschnitt passen zusammen (24.11.2026) - gegen die echte DB.

Der Korrektur-Storno markierte bis 24.11.2026 auch die **Originalbewegung** mit ``storno_ref`` (Verweis auf den
Storno). Die Bestandsbewertung liest ``storno_ref`` als "diese Bewegung ist ein Storno": der stornierte Zugang zaehlte
als Abgang und sein Storno noch einmal - der Bestand fiel doppelt. Der Verweis gilt nur vorwaerts (Storno -> Original).
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.bestandsbewertung import gleitender_durchschnitt
from app.services.inventory_correction_service import storno_korrektur

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"sb-{uuid.uuid4().hex[:6]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'RAPS', 'Raps', 't')"), {"id": artikel, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
        db.commit()
    try:
        yield {"t": t, "artikel": artikel, "lager": lager}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _zugang(h, menge: str, preis: str, tag: int) -> str:
    kennung = str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            "movement_type, quantity, unit, unit_cost, previous_stock, new_stock, movement_date, ownership_type, "
            "storage_fee_relevant) VALUES (:id, :t, :a, :w, 'einlagerung', :m, 't', :p, 0, 0, :d, 'owned', false)"),
            {"id": kennung, "t": h["t"], "a": h["artikel"], "w": h["lager"], "m": menge, "p": preis,
             "d": date(2026, 11, tag)})
        db.commit()
    return kennung


def test_storno_eines_zugangs_haelt_den_durchschnitt_richtig(haus):
    _zugang(haus, "10", "100", 1)
    zweiter = _zugang(haus, "10", "200", 2)

    with SessionLocal() as db:
        storno_korrektur(db, korrektur_id=zweiter, tenant_id=haus["t"], bemerkung="Fehlbuchung")
    with SessionLocal() as db:
        schnitt = gleitender_durchschnitt(db, haus["t"], haus["artikel"])
        original_markiert = db.execute(text("SELECT storno_ref FROM domain_inventory.inventory_stock_movements "
                                            "WHERE id = :id"), {"id": zweiter}).scalar()

    assert (schnitt.bestand, schnitt.preis) == (D("10"), D("100"))
    assert original_markiert is None  # Verweis nur vorwaerts: Storno -> Original
