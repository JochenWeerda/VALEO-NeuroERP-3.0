"""DOM-AGRAR-004.4 — Selbstabrechnung-Lifecycle-Service (Status-Maschine + Storno)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Valid transitions: (from_status, to_status)
VALID_TRANSITIONS = {
    ("DRAFT", "ISSUED"),
    ("DRAFT", "CANCELLED"),
    ("ISSUED", "PAID"),
    ("ISSUED", "DISPUTED"),
    ("ISSUED", "CANCELLED"),
    ("DISPUTED", "RESOLVED"),
    ("DISPUTED", "CANCELLED"),
}

STORNO_FROM_STATES = {"DRAFT", "ISSUED"}


class SelbstabrechnungError(Exception):
    """Raised when self-billing lifecycle constraints are violated."""


def _fetch_rechnung(db: Session, rechnung_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text(
            "SELECT * FROM domain_agrar.agrar_selbstabrechnungen WHERE id = :id"
        ),
        {"id": rechnung_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_status_change(
    db: Session,
    rechnung_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str = "system",
    reason: Optional[str] = None,
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_agrar.agrar_selbstabrechnung_status_log
                (id, rechnung_id, old_status, new_status, operator, reason, tenant_id)
            VALUES (:id, :rechnung_id, :old_status, :new_status, :operator, :reason, :tenant_id)
        """),
        {
            "id": str(uuid.uuid4()),
            "rechnung_id": rechnung_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "reason": reason,
            "tenant_id": tenant_id,
        },
    )


def transition_status(
    db: Session,
    rechnung_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Transition a Selbstabrechnung to a new status (fail-closed state machine)."""
    rechnung = _fetch_rechnung(db, rechnung_id)
    if not rechnung:
        raise SelbstabrechnungError(f"Selbstabrechnung {rechnung_id} nicht gefunden")
    if rechnung.get("tenant_id") and rechnung["tenant_id"] != tenant_id:
        raise SelbstabrechnungError(f"Rechnung {rechnung_id} gehört nicht zu Tenant {tenant_id}")

    current = (rechnung.get("status") or "DRAFT").upper()
    target = new_status.upper()

    if (current, target) not in VALID_TRANSITIONS:
        raise SelbstabrechnungError(
            f"Ungültiger Statusübergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_TRANSITIONS)}"
        )

    db.execute(
        text(
            "UPDATE domain_agrar.agrar_selbstabrechnungen SET status = :status WHERE id = :id"
        ),
        {"status": target, "id": rechnung_id},
    )
    _log_status_change(db, rechnung_id, current, target, tenant_id, operator, reason)
    db.commit()
    return {**rechnung, "status": target, "previous_status": current}


def storno_selbstabrechnung(
    db: Session,
    rechnung_id: str,
    tenant_id: str,
    grund: Optional[str] = None,
    operator: str = "system",
) -> Dict[str, Any]:
    """Storno einer Selbstabrechnung (idempotent).

    Setzt Status auf CANCELLED und schreibt Storno-Log.
    Idempotent: bereits cancellierte Rechnung wird zurückgegeben.
    """
    rechnung = _fetch_rechnung(db, rechnung_id)
    if not rechnung:
        raise SelbstabrechnungError(f"Selbstabrechnung {rechnung_id} nicht gefunden")
    if rechnung.get("tenant_id") and rechnung["tenant_id"] != tenant_id:
        raise SelbstabrechnungError(f"Rechnung {rechnung_id} gehört nicht zu Tenant {tenant_id}")

    current = (rechnung.get("status") or "DRAFT").upper()

    # idempotent
    if current == "CANCELLED":
        logger.info("selbstabrechnung storno: %s bereits storniert — idempotent", rechnung_id)
        return {**rechnung, "idempotent": True}

    if current not in STORNO_FROM_STATES:
        raise SelbstabrechnungError(
            f"Storno nur aus Status DRAFT oder ISSUED möglich (aktuell: {current})"
        )

    db.execute(
        text(
            "UPDATE domain_agrar.agrar_selbstabrechnungen SET status = 'CANCELLED' WHERE id = :id"
        ),
        {"id": rechnung_id},
    )
    _log_status_change(
        db, rechnung_id, current, "CANCELLED", tenant_id, operator,
        reason=grund or "STORNO",
    )
    db.commit()
    logger.info("selbstabrechnung storno: %s von %s auf CANCELLED", rechnung_id, current)
    return {**rechnung, "status": "CANCELLED", "previous_status": current, "idempotent": False}
