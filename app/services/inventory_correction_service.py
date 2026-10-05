"""DOM-INV-004.4 — Bestandskorrektur-Storno-Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.inventory_stock_balance import current_stock, signed_delta

logger = logging.getLogger(__name__)


class CorrectionError(Exception):
    """Raised when correction storno constraints are violated."""


def storno_korrektur(
    db: Session,
    korrektur_id: str,
    tenant_id: str,
    bemerkung: Optional[str] = None,
) -> Dict[str, Any]:
    """Storniere eine Bestandskorrektur (Gegenbuchung, idempotent).

    Idempotent: wenn bereits ein Storno existiert, wird dieser zurückgegeben.
    Das Original bekommt status='storniert'.
    """
    original = db.execute(
        text("SELECT * FROM domain_inventory.inventory_stock_movements WHERE id = :id"),
        {"id": korrektur_id},
    ).mappings().first()
    if not original:
        raise CorrectionError(f"Korrektur {korrektur_id} nicht gefunden")

    orig = dict(original)
    if orig.get("tenant_id") and orig["tenant_id"] != tenant_id:
        raise CorrectionError(f"Korrektur {korrektur_id} gehört nicht zu Tenant {tenant_id}")

    if (orig.get("source_document_type") or "").upper() == "STORNO":
        raise CorrectionError(
            f"Korrektur {korrektur_id} ist selbst ein Storno und kann nicht storniert werden"
        )

    # idempotency: check if storno already exists
    existing_storno = db.execute(
        text(
            "SELECT * FROM domain_inventory.inventory_stock_movements "
            "WHERE storno_ref = :ref AND source_document_type = 'STORNO' AND tenant_id = :tid "
            "LIMIT 1"
        ),
        {"ref": korrektur_id, "tid": tenant_id},
    ).mappings().first()
    if existing_storno:
        logger.info("storno_korrektur: Storno bereits vorhanden für %s — idempotent return", korrektur_id)
        return {**dict(existing_storno), "idempotent": True}

    # create reversal
    storno_id = str(uuid.uuid4())
    orig_qty = float(orig.get("quantity") or 0)
    orig_movement_type = orig.get("movement_type", "ABGANG")
    # negate: ZUGANG → ABGANG, ABGANG → ZUGANG
    storno_movement_type = "ABGANG" if orig_movement_type == "ZUGANG" else "ZUGANG"

    # previous_stock/new_stock sind NOT NULL ohne Default, ebenso auto_created,
    # ownership_type und storage_fee_relevant.
    article_id = str(orig.get("article_id") or "")
    warehouse_id = str(orig.get("warehouse_id") or "")
    prev_stock = current_stock(
        db,
        tenant_id=tenant_id,
        article_id=article_id,
        warehouse_id=warehouse_id,
    )
    new_stock = prev_stock + signed_delta(storno_movement_type, orig_qty)

    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
                (id, tenant_id, article_id, warehouse_id, movement_type,
                 quantity, unit, source_document_type, source_document_id,
                 storno_ref, notes, previous_stock, new_stock,
                 auto_created, ownership_type, storage_fee_relevant)
            VALUES (:id, :tenant_id, :article_id, :warehouse_id, :movement_type,
                    :quantity, :unit, 'STORNO', :storno_ref,
                    :storno_ref, :notes, :previous_stock, :new_stock,
                    true, :ownership_type, false)
        """),
        {
            "id": storno_id,
            "tenant_id": tenant_id,
            "article_id": article_id,
            "warehouse_id": warehouse_id,
            "movement_type": storno_movement_type,
            "quantity": orig_qty,
            "unit": orig.get("unit", "kg"),
            "storno_ref": korrektur_id,
            "notes": bemerkung or f"Storno von {korrektur_id}",
            "previous_stock": prev_stock,
            "new_stock": new_stock,
            "ownership_type": orig.get("ownership_type") or "owned",
        },
    )
    # mark original as storniert
    db.execute(
        text(
            "UPDATE domain_inventory.inventory_stock_movements "
            "SET storno_ref = :storno_id WHERE id = :orig_id"
        ),
        {"storno_id": storno_id, "orig_id": korrektur_id},
    )
    db.commit()
    logger.info("storno_korrektur: Storno %s für Korrektur %s angelegt", storno_id, korrektur_id)
    return {
        "id": storno_id,
        "storno_ref": korrektur_id,
        "tenant_id": tenant_id,
        "article_id": orig.get("article_id"),
        "warehouse_id": orig.get("warehouse_id"),
        "movement_type": storno_movement_type,
        "quantity": orig_qty,
        "source_document_type": "STORNO",
        "source_document_id": korrektur_id,
        "previous_stock": prev_stock,
        "new_stock": new_stock,
        "unit": orig.get("unit", "kg"),
        "idempotent": False,
    }
