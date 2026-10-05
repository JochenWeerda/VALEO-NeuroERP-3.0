"""Bestandssaldo aus inventory_stock_movements.

Entstanden in SPEC-P1-06-W8, weil ``previous_stock`` und ``new_stock`` in
``domain_inventory.inventory_stock_movements`` NOT NULL ohne Default sind und
jeder Schreibpfad sie selbst liefern muss.

Seit DOM-INV-005 fuehrt dieses Modul die Vokabularlisten nicht mehr selbst,
sondern holt Richtung und SQL-Fragment aus
:mod:`app.services.inventory_movement_direction` - der einen Stelle, die
festlegt, welcher ``movement_type`` den Bestand erhoeht, senkt oder unberuehrt
laesst.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.inventory_movement_direction import (
    INBOUND_TYPES,
    OUTBOUND_TYPES,
    direction_sql,
    signed_quantity,
)

__all__ = [
    "INBOUND_TYPES",
    "OUTBOUND_TYPES",
    "current_stock",
    "signed_delta",
    "signed_quantity",
]

_BALANCE_SQL = text(
    f"""
    SELECT COALESCE(SUM({direction_sql()}), 0)
    FROM domain_inventory.inventory_stock_movements
    WHERE tenant_id = :tenant_id
      AND article_id = :article_id
      AND warehouse_id = :warehouse_id
    """  # nosec B608 - Fragment aus Modulkonstanten, Werte via Bind-Params
)


def current_stock(
    db: Session,
    *,
    tenant_id: str,
    article_id: str,
    warehouse_id: str,
) -> float:
    """Aktueller Buchbestand einer Artikel-/Lagerkombination."""
    value = db.execute(
        _BALANCE_SQL,
        {
            "tenant_id": tenant_id,
            "article_id": article_id,
            "warehouse_id": warehouse_id,
        },
    ).scalar()
    return float(value or 0)


def signed_delta(movement_type: str, quantity: float) -> float:
    """Bestandswirksame Menge einer Bewegung.

    Alias auf :func:`~app.services.inventory_movement_direction.signed_quantity`;
    bleibt erhalten, weil die Korrekturdienste ihn unter diesem Namen nutzen.
    """
    return signed_quantity(movement_type, quantity)
