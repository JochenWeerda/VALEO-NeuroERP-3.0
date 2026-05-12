"""Automatic Kontrakt-Movement synchronization.

When a delivery note or invoice is created/updated and has positions
with a kontrakt_nr, this service resolves the contract and books
corresponding movements.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.domains.operations.models import KonContract, KonContractLine, KonContractMovement

logger = logging.getLogger(__name__)


def sync_movements_for_delivery_note(
    db: Session,
    tenant_id: str,
    delivery_note_id: str,
    delivery_note_number: str,
    positions: list[dict],
    user_id: Optional[str] = None,
) -> list[str]:
    """Book movements for delivery note positions that reference a contract.

    Returns list of created movement_ids.
    """
    created = []
    for pos in positions:
        kontrakt_nr = pos.get("kontrakt_nr")
        if not kontrakt_nr:
            continue

        menge = Decimal(str(pos.get("menge", 0)))
        if menge <= 0:
            continue

        contract = (
            db.query(KonContract)
            .filter(KonContract.tenant_id == tenant_id, KonContract.contract_no == kontrakt_nr)
            .first()
        )
        if not contract:
            logger.warning("Movement sync: contract_no=%s not found for tenant=%s", kontrakt_nr, tenant_id)
            continue

        if contract.status not in ("OFFEN", "ERLEDIGT"):
            logger.warning("Movement sync: contract %s has status %s, skipping", kontrakt_nr, contract.status)
            continue

        article_id = pos.get("artikel_nr") or pos.get("artikel_id")
        line = _find_matching_line(db, tenant_id, contract.contract_id, article_id)

        existing = (
            db.query(KonContractMovement)
            .filter(
                KonContractMovement.tenant_id == tenant_id,
                KonContractMovement.contract_id == contract.contract_id,
                KonContractMovement.delivery_note_no == delivery_note_number,
            )
            .first()
        )
        if existing:
            existing.quantity = float(menge)
            existing.unit_price = float(pos.get("netto_preis") or pos.get("listenpreis") or 0)
            existing.movement_date = datetime.utcnow()
            existing.updated_by = user_id
            created.append(existing.movement_id)
            continue

        movement = KonContractMovement(
            movement_id=uuid7(),
            contract_id=contract.contract_id,
            line_id=line.line_id if line else None,
            delivery_note_no=delivery_note_number,
            movement_date=datetime.utcnow(),
            quantity=float(menge),
            unit_price=float(pos.get("netto_preis") or pos.get("listenpreis") or 0),
            is_invoiced=False,
            is_archived=False,
            tenant_id=tenant_id,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(movement)
        created.append(movement.movement_id)

    return created


def sync_invoice_flag(
    db: Session,
    tenant_id: str,
    delivery_note_number: str,
    invoice_number: str,
) -> int:
    """Mark movements linked to a delivery note as invoiced.

    Returns number of updated movements.
    """
    movements = (
        db.query(KonContractMovement)
        .filter(
            KonContractMovement.tenant_id == tenant_id,
            KonContractMovement.delivery_note_no == delivery_note_number,
        )
        .all()
    )
    count = 0
    for m in movements:
        if not m.is_invoiced:
            m.is_invoiced = True
            m.invoice_no = invoice_number
            count += 1
    return count


def _find_matching_line(
    db: Session,
    tenant_id: str,
    contract_id: str,
    article_id: Optional[str],
) -> Optional[KonContractLine]:
    """Find the best matching contract line for a given article."""
    lines = (
        db.query(KonContractLine)
        .filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id)
        .order_by(KonContractLine.position_no.asc())
        .all()
    )
    if not lines:
        return None
    if article_id:
        match = next((line_item for line_item in lines if line_item.article_id == article_id), None)
        if match:
            return match
    return lines[0]
