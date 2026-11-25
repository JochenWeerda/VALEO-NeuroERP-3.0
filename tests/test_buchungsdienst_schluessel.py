"""Kanonischer Buchungsdienst mit Buchungsschluessel (Konsolidierung Schritt 1, 24.11.2026) - gegen die echte DB."""
from __future__ import annotations

import uuid
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.domains.inventory.application.services.inventory_service import InventoryService

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"bd-{uuid.uuid4().hex[:6]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'FUTTER', 'Futter', 'kg')"), {"id": artikel, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
        db.commit()
    try:
        yield {"t": t, "artikel": artikel, "lager": lager}
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                        "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": t})
            db.commit()


def _stand(h) -> tuple[int, D]:
    with SessionLocal() as db:
        bewegungen = db.execute(text("SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements "
                                     "WHERE tenant_id = :t"), {"t": h["t"]}).scalar_one()
        bestand = db.execute(text("SELECT COALESCE(current_stock, 0) FROM domain_inventory.articles WHERE id = :a"),
                             {"a": h["artikel"]}).scalar_one()
        return int(bewegungen), D(str(bestand))


def _buche(db, h, menge: str, schluessel: str | None, *, commit: bool = True):
    return InventoryService(db).process_stock_movement(
        h["artikel"], h["lager"], "in", D(menge), tenant_id=h["t"], buchungsschluessel=schluessel, commit=commit)


def test_gleicher_schluessel_bucht_einmal(haus):
    with SessionLocal() as db:
        erste = _buche(db, haus, "100", "test:beleg-1:1:in")
    with SessionLocal() as db:
        zweite = _buche(db, haus, "100", "test:beleg-1:1:in")

    assert str(erste.id) == str(zweite.id)
    assert _stand(haus) == (1, D("100"))


def test_ohne_schluessel_unveraendert(haus):
    with SessionLocal() as db:
        _buche(db, haus, "10", None)
        _buche(db, haus, "10", None)

    assert _stand(haus) == (2, D("20"))


def test_aufrufer_transaktion_rollt_alles_zurueck(haus):
    with SessionLocal() as db:
        _buche(db, haus, "50", "test:beleg-2:1:in", commit=False)
        db.rollback()
    assert _stand(haus) == (0, D("0"))

    with SessionLocal() as db:
        _buche(db, haus, "50", "test:beleg-2:1:in")
    assert _stand(haus) == (1, D("50"))
