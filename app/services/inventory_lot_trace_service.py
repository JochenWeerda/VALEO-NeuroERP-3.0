"""DOM-INV-004.2 — Chargen-/MHD-Traceability Service (FEFO)."""
from __future__ import annotations

import logging
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class LotTraceError(Exception):
    """Raised when lot operations violate business rules."""


def create_lot(
    db: Session,
    tenant_id: str,
    article_id: str,
    warehouse_id: str,
    lot_number: str,
    initial_qty: float,
    unit: str = "kg",
    mhd: Optional[date] = None,
) -> Dict[str, Any]:
    """Register a new inventory lot."""
    lot_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_lots
                (id, tenant_id, article_id, warehouse_id, lot_number, mhd,
                 initial_qty, current_qty, unit, status)
            VALUES (:id, :tenant_id, :article_id, :warehouse_id, :lot_number,
                    :mhd, :initial_qty, :initial_qty, :unit, 'AKTIV')
        """),
        {
            "id": lot_id,
            "tenant_id": tenant_id,
            "article_id": article_id,
            "warehouse_id": warehouse_id,
            "lot_number": lot_number,
            "mhd": mhd,
            "initial_qty": initial_qty,
            "unit": unit,
        },
    )
    # record IN movement
    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_lot_movements
                (id, lot_id, tenant_id, movement_type, quantity)
            VALUES (:id, :lot_id, :tenant_id, 'IN', :quantity)
        """),
        {"id": str(uuid.uuid4()), "lot_id": lot_id, "tenant_id": tenant_id, "quantity": initial_qty},
    )
    db.commit()
    return {
        "id": lot_id,
        "tenant_id": tenant_id,
        "article_id": article_id,
        "warehouse_id": warehouse_id,
        "lot_number": lot_number,
        "mhd": mhd.isoformat() if mhd else None,
        "initial_qty": initial_qty,
        "current_qty": initial_qty,
        "unit": unit,
        "status": "AKTIV",
    }


def list_lots_fefo(
    db: Session,
    tenant_id: str,
    article_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    include_exhausted: bool = False,
) -> List[Dict[str, Any]]:
    """Return lots sorted FEFO (earliest MHD first; NULL MHD last)."""
    conditions = ["tenant_id = :tenant_id"]
    params: Dict[str, Any] = {"tenant_id": tenant_id}
    if article_id:
        conditions.append("article_id = :article_id")
        params["article_id"] = article_id
    if warehouse_id:
        conditions.append("warehouse_id = :warehouse_id")
        params["warehouse_id"] = warehouse_id
    if not include_exhausted:
        conditions.append("status = 'AKTIV'")
    where = " AND ".join(conditions)
    rows = db.execute(
        text(
            f"SELECT * FROM domain_inventory.inventory_lots "  # nosec S608 — reviewed-safe
            f"WHERE {where} ORDER BY mhd ASC NULLS LAST, created_at ASC"
        ),
        params,
    ).mappings().all()
    return [dict(r) for r in rows]


def consume_lot(
    db: Session,
    lot_id: str,
    tenant_id: str,
    quantity: float,
    reference_id: Optional[str] = None,
    reference_type: Optional[str] = None,
) -> Dict[str, Any]:
    """Consume quantity from a lot (FEFO-safe, fail-closed).

    Raises LotTraceError for: lot not found, wrong tenant, expired, insufficient stock.
    """
    row = db.execute(
        text("SELECT * FROM domain_inventory.inventory_lots WHERE id = :id"),
        {"id": lot_id},
    ).mappings().first()
    if not row:
        raise LotTraceError(f"Lot {lot_id} nicht gefunden")
    lot = dict(row)

    if lot.get("tenant_id") and lot["tenant_id"] != tenant_id:
        raise LotTraceError(f"Lot {lot_id} gehört nicht zu Tenant {tenant_id}")

    # expiry check (fail-closed)
    mhd = lot.get("mhd")
    if mhd is not None:
        if isinstance(mhd, str):
            mhd = date.fromisoformat(mhd)
        if mhd < date.today():
            # mark lot as expired
            db.execute(
                text("UPDATE domain_inventory.inventory_lots SET status = 'ABGELAUFEN' WHERE id = :id"),
                {"id": lot_id},
            )
            db.commit()
            raise LotTraceError(
                f"Lot {lot_id} ist abgelaufen (MHD {mhd}) — Verbrauch nicht erlaubt"
            )

    current_qty = float(lot.get("current_qty") or 0)
    if quantity > current_qty:
        raise LotTraceError(
            f"Unterdeckung: angefordert {quantity}, verfügbar {current_qty} im Lot {lot_id}"
        )

    new_qty = current_qty - quantity
    new_status = "ERSCHÖPFT" if new_qty <= 0 else "AKTIV"

    db.execute(
        text(
            "UPDATE domain_inventory.inventory_lots "
            "SET current_qty = :qty, status = :status WHERE id = :id"
        ),
        {"qty": round(new_qty, 3), "status": new_status, "id": lot_id},
    )
    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_lot_movements
                (id, lot_id, tenant_id, movement_type, quantity, reference_id, reference_type)
            VALUES (:id, :lot_id, :tenant_id, 'OUT', :quantity, :ref_id, :ref_type)
        """),
        {
            "id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "tenant_id": tenant_id,
            "quantity": quantity,
            "ref_id": reference_id,
            "ref_type": reference_type,
        },
    )
    db.commit()
    return {
        "lot_id": lot_id,
        "consumed_qty": quantity,
        "remaining_qty": round(new_qty, 3),
        "status": new_status,
    }
