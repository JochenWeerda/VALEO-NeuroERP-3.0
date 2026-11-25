"""Inventurdifferenzen ueber den kanonischen Buchungsdienst (Konsolidierung, 25.11.2026) - gegen die echte DB.

Bis 25.11.2026 schrieb die Inventur eigenes SQL: previous/new_stock = 0, Artikelbestand ohne Mandantenfilter, ein
fehlendes Lager wurde zur Kennung 'INVENTUR'. Jetzt: echter Bestandsverlauf, Mandant, Buchungsschluessel je Zeile.
"""
from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal

pytestmark = pytest.mark.integration


@pytest.fixture
def inventur():
    t = f"iv-{uuid.uuid4().hex[:6]}"
    artikel, lager, zaehlung, zaehler = (str(uuid.uuid4()) for _ in range(4))
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'GERSTE', 'Gerste', 't')"), {"id": artikel, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
        db.execute(text(  # Buchbestand vor der Inventur: 20 t
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            "movement_type, quantity, unit, previous_stock, new_stock, movement_date, ownership_type, "
            "storage_fee_relevant) VALUES (:id, :t, :a, :w, 'in', 20, 't', 0, 20, CURRENT_DATE, 'owned', false)"),
            {"id": str(uuid.uuid4()), "t": t, "a": artikel, "w": lager})
        db.execute(text("INSERT INTO domain_shared.users (id, keycloak_id, username, email) "
                        "VALUES (:id, :id, :id, :mail)"), {"id": zaehler, "mail": f"{zaehler}@test.invalid"})
        db.execute(text("INSERT INTO domain_inventory.inventory_counts (id, tenant_id, warehouse_id, counted_by, status) "
                        "VALUES (:id, :t, :w, :u, 'counted')"), {"id": zaehlung, "t": t, "w": lager, "u": zaehler})
        db.execute(text("INSERT INTO domain_inventory.inventory_count_lines (id, tenant_id, inventory_count_id, "
                        "article_id, warehouse_id, expected_qty, counted_qty) VALUES (:id, :t, :c, :a, :w, 20, 17)"),
                   {"id": str(uuid.uuid4()), "t": t, "c": zaehlung, "a": artikel, "w": lager})
        db.commit()
    try:
        yield {"t": t, "artikel": artikel, "zaehlung": zaehlung, "zaehler": zaehler}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.inventory_count_lines WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_counts WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.execute(text("DELETE FROM domain_shared.users WHERE id = :u"), {"u": zaehler})
            db.commit()


def test_inventurdifferenz_bucht_echten_bestandsverlauf(inventur):
    from app.api.v1.endpoints.inventory_counts import post_inventory_count

    with SessionLocal() as db:
        ergebnis = asyncio.run(post_inventory_count(inventur["zaehlung"], tenant_id=inventur["t"], db=db))
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT movement_type, quantity, previous_stock, new_stock FROM domain_inventory.inventory_stock_movements "
            "WHERE tenant_id = :t AND movement_type = 'adjustment'"), {"t": inventur["t"]}).fetchall()

    assert ergebnis.total_adjustments == 1
    assert [(r[0], D(str(r[1])), D(str(r[2])), D(str(r[3]))) for r in zeilen] == \
        [("adjustment", D("-3"), D("20"), D("17"))]
