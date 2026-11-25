"""Bestandsvortrag ueber den kanonischen Buchungsdienst (Konsolidierung, 25.11.2026) - gegen die echte DB.

Bis 25.11.2026 setzte der Vortrag ``current_stock`` absolut auf die Zeilenmenge: bei zwei Lagern blieb nur die letzte
Zeile im Artikelbestand stehen, das Journal (``opening_balance`` = +Menge) zaehlte beide.
"""
from __future__ import annotations

import uuid
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.inventory_auxiliary_service import InventoryAuxiliaryService

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"bv-{uuid.uuid4().hex[:6]}"
    artikel, lager_a, lager_b = (str(uuid.uuid4()) for _ in range(3))
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'MAIS', 'Mais', 't')"), {"id": artikel, "t": t})
        for lager, code in ((lager_a, "LA"), (lager_b, "LB")):
            db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                            "VALUES (:id, :t, :c, :c)"), {"id": lager, "t": t, "c": code})
        db.commit()
    try:
        yield {"t": t, "artikel": artikel, "a": lager_a, "b": lager_b}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _vortrag(h):
    return {"id": f"vortrag-{h['t']}", "batch_type": "opening_balance", "payload": [
        {"line_id": "zeile-a", "article_id": h["artikel"], "warehouse_id": h["a"], "counted_qty": 30},
        {"line_id": "zeile-b", "article_id": h["artikel"], "warehouse_id": h["b"], "counted_qty": 12},
    ]}


def test_vortrag_ueber_zwei_lager_summiert_und_bucht_einmal(haus):
    for _ in range(2):  # Freigabe zweimal angewendet
        with SessionLocal() as db:
            InventoryAuxiliaryService(db, haus["t"])._apply(_vortrag(haus), "pruefer")
            db.commit()

    with SessionLocal() as db:
        bestand = db.execute(text("SELECT current_stock FROM domain_inventory.articles WHERE id = :a"),
                             {"a": haus["artikel"]}).scalar_one()
        journal = db.execute(text("SELECT COUNT(*), SUM(quantity) FROM domain_inventory.inventory_stock_movements "
                                  "WHERE tenant_id = :t AND movement_type = 'opening_balance'"),
                             {"t": haus["t"]}).one()

    assert D(str(bestand)) == D("42")
    assert (journal[0], D(str(journal[1]))) == (2, D("42"))
