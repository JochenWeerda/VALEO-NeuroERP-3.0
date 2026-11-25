"""Bestandskorrektur ueber den kanonischen Buchungsdienst (Konsolidierung Schritt 2, 24.11.2026) - echte DB.

Bis 24.11.2026 schrieb die Korrektur eigenes SQL mit ``previous_stock = new_stock = 0`` und ohne Unterdeckungspruefung.
"""
from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal as D

import pytest
from fastapi import HTTPException
from sqlalchemy import text

from app.core.database import SessionLocal

pytestmark = pytest.mark.integration


@pytest.fixture
def haus():
    t = f"kd-{uuid.uuid4().hex[:6]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": t})
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, 'WEIZEN', 'Weizen', 't')"), {"id": artikel, "t": t})
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


def _korrektur(h, menge: float):
    from app.api.v1.endpoints.inventory_operations import BestandskorrekturIn, create_bestandskorrektur

    with SessionLocal() as db:
        return asyncio.run(create_bestandskorrektur(
            BestandskorrekturIn(article_id=h["artikel"], warehouse_id=h["lager"], menge=menge, grund="messdifferenz"),
            tenant_id=h["t"], db=db))


def _journal(h) -> list[tuple[D, D, D]]:
    with SessionLocal() as db:
        return [(D(str(r[0])), D(str(r[1])), D(str(r[2]))) for r in db.execute(text(
            "SELECT quantity, previous_stock, new_stock FROM domain_inventory.inventory_stock_movements "
            "WHERE tenant_id = :t ORDER BY created_at, id"), {"t": h["t"]}).fetchall()]


def test_korrektur_schreibt_echten_vorher_und_nachher_bestand(haus):
    _korrektur(haus, 10)
    _korrektur(haus, -4)

    assert _journal(haus) == [(D("10"), D("0"), D("10")), (D("-4"), D("10"), D("6"))]
    with SessionLocal() as db:
        assert D(str(db.execute(text("SELECT current_stock FROM domain_inventory.articles WHERE id = :a"),
                                {"a": haus["artikel"]}).scalar_one())) == D("6")


def test_entnahme_ueber_den_bestand_wird_abgewiesen(haus):
    _korrektur(haus, 3)

    with pytest.raises(HTTPException) as fehler:
        _korrektur(haus, -5)

    assert fehler.value.status_code == 422
    assert len(_journal(haus)) == 1
