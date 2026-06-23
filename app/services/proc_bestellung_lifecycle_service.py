"""DOM-PROC-004.2 — Bestellung Lifecycle Service (Statusmaschine)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_BESTELLUNG_TRANSITIONS = {
    ("DRAFT", "FREIGEGEBEN"),
    ("DRAFT", "STORNIERT"),
    ("FREIGEGEBEN", "VERSANDT"),
    ("FREIGEGEBEN", "STORNIERT"),
    ("VERSANDT", "WE_ERHALTEN"),
}


class BestellungLifecycleError(Exception):
    """Raised when Bestellung lifecycle constraints are violated."""


def _fetch_bestellung(db: Session, bestellung_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_procurement.proc_purchase_orders WHERE id = :id"),
        {"id": bestellung_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_bestellung_transition(
    db: Session,
    bestellung_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    reason: Optional[str],
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_procurement.proc_bestellung_status_log
                (id, bestellung_id, tenant_id, old_status, new_status, operator, reason, created_at)
            VALUES (:id, :bestellung_id, :tenant_id, :old_status, :new_status, :operator, :reason, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "bestellung_id": bestellung_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "reason": reason,
        },
    )


def transition_bestellung_status(
    db: Session,
    bestellung_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Wechselt Bestellungs-Status (fail-closed Statusmaschine)."""
    bestellung = _fetch_bestellung(db, bestellung_id)
    if not bestellung:
        raise BestellungLifecycleError(f"Bestellung {bestellung_id} nicht gefunden")
    if bestellung.get("tenant_id") and bestellung["tenant_id"] != tenant_id:
        raise BestellungLifecycleError(f"Bestellung {bestellung_id} gehört nicht zu Tenant {tenant_id}")

    current = (bestellung.get("status") or "DRAFT").upper()
    target = new_status.upper()

    if (current, target) not in VALID_BESTELLUNG_TRANSITIONS:
        raise BestellungLifecycleError(
            f"Ungültiger Bestellungs-Übergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_BESTELLUNG_TRANSITIONS)}"
        )

    if target == "FREIGEGEBEN" and not operator:
        raise BestellungLifecycleError("Freigabe-Operator ist Pflicht")

    db.execute(
        text("UPDATE domain_procurement.proc_purchase_orders SET status = :status WHERE id = :id"),
        {"status": target, "id": bestellung_id},
    )
    _log_bestellung_transition(db, bestellung_id, current, target, tenant_id, operator, reason)
    db.commit()
    logger.info("bestellung %s: %s → %s von %s", bestellung_id, current, target, operator)
    return {**bestellung, "status": target, "previous_status": current}
