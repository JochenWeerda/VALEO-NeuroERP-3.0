"""Futterproduktion bucht ueber den kanonischen Buchungsdienst (Konsolidierung, 25.11.2026) - gegen die echte DB.

Ersetzt wird nur die Verknuepfung Einzelfuttermittel -> Artikel (Stammdatensuche); der Buchungsweg ist echt.
Bis 25.11.2026: eigenes SQL mit previous/new_stock = 0, Verbrauch ueber den Bestand machte ihn negativ.
"""
from __future__ import annotations

import uuid
from decimal import Decimal as D

import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.services.feed_inventory_link_service import FeedInventoryLinkError, FeedInventoryLinkService

pytestmark = pytest.mark.integration


@pytest.fixture
def haus(monkeypatch):
    t = f"fu-{uuid.uuid4().hex[:6]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit, current_stock) "
                        "VALUES (:id, :t, 'SOJA', 'Sojaschrot', 't', 10)"), {"id": artikel, "t": t})
        db.execute(text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                        "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
        db.execute(text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
            "movement_type, quantity, unit, previous_stock, new_stock, movement_date, ownership_type, "
            "storage_fee_relevant) VALUES (:id, :t, :a, :w, 'in', 10, 't', 0, 10, CURRENT_DATE, 'owned', false)"),
            {"id": str(uuid.uuid4()), "t": t, "a": artikel, "w": lager})
        db.commit()
    monkeypatch.setattr(FeedInventoryLinkService, "ensure_article_link", lambda self, ef_id: {"article_id": artikel})
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


def _verbrauch(h, menge: str, auftrag: str = "PA-1"):
    with SessionLocal() as db:
        ergebnis = FeedInventoryLinkService(db, h["t"]).book_snapshot_movements(
            snapshot=[{"einzelfutter_id": "EF-SOJA", "name": "Sojaschrot", "menge_t": menge}], direction=-1,
            production_order_id=auftrag, booked_by="mischer", warehouse_id=h["lager"])
        db.commit()
        return ergebnis


def _verlauf(h) -> list[tuple[D, D]]:
    with SessionLocal() as db:
        return [(D(str(r[0])), D(str(r[1]))) for r in db.execute(text(
            "SELECT previous_stock, new_stock FROM domain_inventory.inventory_stock_movements "
            "WHERE tenant_id = :t AND source_document_type = 'feed_production'"), {"t": h["t"]}).fetchall()]


def test_verbrauch_bucht_echten_verlauf_und_einmal(haus):
    _verbrauch(haus, "4")
    _verbrauch(haus, "4")  # gleiche Produktionsposition nochmal

    assert _verlauf(haus) == [(D("10"), D("6"))]
    with SessionLocal() as db:
        assert D(str(db.execute(text("SELECT current_stock FROM domain_inventory.articles WHERE id = :a"),
                                {"a": haus["artikel"]}).scalar_one())) == D("6")


def test_verbrauch_ueber_den_bestand_wird_abgewiesen(haus):
    with pytest.raises(FeedInventoryLinkError, match="Insufficient stock"):
        _verbrauch(haus, "12", auftrag="PA-2")
    assert _verlauf(haus) == []
