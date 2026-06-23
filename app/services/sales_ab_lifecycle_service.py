"""DOM-SALES-004.2 — Auftragsbestätigung Lifecycle Service (Statusmaschine)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_AB_TRANSITIONS = {
    ("DRAFT", "VERSANDT"),
    ("DRAFT", "ABGELEHNT"),
    ("VERSANDT", "ANGENOMMEN"),
    ("VERSANDT", "ABGELEHNT"),
}


class ABLifecycleError(Exception):
    """Raised when AB lifecycle constraints are violated."""


def _fetch_auftrag(db: Session, auftrag_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_sales.sales_orders WHERE id = :id"),
        {"id": auftrag_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_ab_transition(
    db: Session,
    auftrag_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    reason: Optional[str],
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_sales.sales_ab_status_log
                (id, auftrag_id, tenant_id, old_status, new_status, operator, reason, created_at)
            VALUES (:id, :auftrag_id, :tenant_id, :old_status, :new_status, :operator, :reason, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "auftrag_id": auftrag_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "reason": reason,
        },
    )


def transition_ab_status(
    db: Session,
    auftrag_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Wechselt AB-Status (fail-closed Statusmaschine)."""
    auftrag = _fetch_auftrag(db, auftrag_id)
    if not auftrag:
        raise ABLifecycleError(f"Auftrag {auftrag_id} nicht gefunden")
    if auftrag.get("tenant_id") and auftrag["tenant_id"] != tenant_id:
        raise ABLifecycleError(f"Auftrag {auftrag_id} gehört nicht zu Tenant {tenant_id}")

    current = (auftrag.get("status") or "DRAFT").upper()
    target = new_status.upper()

    if (current, target) not in VALID_AB_TRANSITIONS:
        raise ABLifecycleError(
            f"Ungültiger AB-Übergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_AB_TRANSITIONS)}"
        )

    if target == "ABGELEHNT" and not reason:
        raise ABLifecycleError("Ablehnungsgrund (reason) ist bei ABGELEHNT Pflicht")

    db.execute(
        text("UPDATE domain_sales.sales_orders SET status = :status WHERE id = :id"),
        {"status": target, "id": auftrag_id},
    )
    _log_ab_transition(db, auftrag_id, current, target, tenant_id, operator, reason)
    db.commit()
    logger.info("ab_status %s: %s → %s", auftrag_id, current, target)
    return {**auftrag, "status": target, "previous_status": current}
