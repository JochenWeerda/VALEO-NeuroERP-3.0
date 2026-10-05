"""DOM-INV-004.3 — Inventur-Differenzbeleg-Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.inventory_stock_balance import current_stock, signed_delta

logger = logging.getLogger(__name__)


class CountCloseError(Exception):
    """Raised when count close constraints are violated."""


def differenz_buchen(
    db: Session,
    count_id: str,
    tenant_id: str,
    operator_id: str = "system",
) -> Dict[str, Any]:
    """Erzeuge automatische Bestandskorrekturen für alle Zähldifferenzen.

    Nur für Inventuren im Status 'posted'.
    Idempotent: Zeilen mit bestehendem Korrektur-Ref werden übersprungen.
    """
    count_row = db.execute(
        text("SELECT * FROM domain_inventory.inventory_counts WHERE id = :id"),
        {"id": count_id},
    ).mappings().first()
    if not count_row:
        raise CountCloseError(f"Inventur {count_id} nicht gefunden")

    count = dict(count_row)
    if count.get("tenant_id") and count["tenant_id"] != tenant_id:
        raise CountCloseError(f"Inventur {count_id} gehört nicht zu Tenant {tenant_id}")

    status = (count.get("status") or "").lower()
    if status != "posted":
        raise CountCloseError(
            f"Differenzbeleg erfordert Status 'posted' (aktuell: {count.get('status')!r})"
        )

    lines = db.execute(
        text(
            "SELECT * FROM domain_inventory.inventory_count_lines "
            "WHERE inventory_count_id = :cid"
        ),
        {"cid": count_id},
    ).mappings().all()

    created: List[str] = []
    skipped: List[str] = []

    for line in lines:
        line_dict = dict(line)
        expected = float(line_dict.get("expected_qty") or 0)
        counted = float(line_dict.get("counted_qty") or 0)
        delta = round(counted - expected, 3)
        if delta == 0:
            continue

        line_id = str(line_dict.get("id", ""))

        # idempotency: check if correction already exists for this line
        existing = db.execute(
            text(
                "SELECT id FROM domain_inventory.inventory_stock_movements "
                "WHERE source_document_id = :ref "
                "AND source_document_type = 'INVENTUR_DIFFERENZ' "
                "AND tenant_id = :tid LIMIT 1"
            ),
            {"ref": line_id, "tid": tenant_id},
        ).mappings().first()
        if existing:
            skipped.append(line_id)
            continue

        corr_id = str(uuid.uuid4())
        article_id = str(line_dict.get("article_id") or "")
        warehouse_id = str(count.get("warehouse_id") or "")
        movement_type = "ZUGANG" if delta > 0 else "ABGANG"
        # previous_stock/new_stock, auto_created, ownership_type und
        # storage_fee_relevant sind NOT NULL ohne Default.
        prev_stock = current_stock(
            db,
            tenant_id=tenant_id,
            article_id=article_id,
            warehouse_id=warehouse_id,
        )
        try:
            db.execute(
                text("""
                    INSERT INTO domain_inventory.inventory_stock_movements
                        (id, tenant_id, article_id, warehouse_id, movement_type,
                         quantity, unit, source_document_id, source_document_type,
                         notes, previous_stock, new_stock,
                         auto_created, ownership_type, storage_fee_relevant)
                    VALUES (:id, :tenant_id, :article_id, :warehouse_id, :movement_type,
                            :quantity, 'kg', :ref_id, 'INVENTUR_DIFFERENZ',
                            :notes, :previous_stock, :new_stock,
                            true, 'owned', false)
                """),
                {
                    "id": corr_id,
                    "tenant_id": tenant_id,
                    "article_id": article_id,
                    "warehouse_id": warehouse_id,
                    "movement_type": movement_type,
                    "quantity": abs(delta),
                    "ref_id": line_id,
                    "notes": f"Inventur-Differenzbeleg {count_id}: delta={delta}",
                    "previous_stock": prev_stock,
                    "new_stock": prev_stock + signed_delta(movement_type, abs(delta)),
                },
            )
            created.append(line_id)
        except Exception as exc:
            logger.warning("differenz_buchen: Fehler bei Zeile %s: %s", line_id, exc)
            db.rollback()
            raise CountCloseError(f"Fehler beim Anlegen des Differenzbelegs für Zeile {line_id}: {exc}") from exc

    db.commit()
    logger.info(
        "differenz_buchen: Inventur %s — %d Korrekturen angelegt, %d übersprungen",
        count_id,
        len(created),
        len(skipped),
    )
    return {
        "count_id": count_id,
        "corrections_created": len(created),
        "lines_skipped_idempotent": len(skipped),
        "correction_line_ids": created,
    }
