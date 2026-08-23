"""DOM-COMPLIANCE-004.2 — PCN-Meldung Lifecycle Service (Status-Maschine)."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    ("DRAFT", "VALIDATED"),
    ("DRAFT", "WITHDRAWN"),
    ("VALIDATED", "SUBMITTED"),
    ("VALIDATED", "WITHDRAWN"),
    ("SUBMITTED", "CLOSED"),
}

WITHDRAW_FROM_STATES = {"DRAFT", "VALIDATED"}


class PCNError(Exception):
    """Raised when PCN lifecycle constraints are violated."""


def _fetch_meldung(db: Session, meldung_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_compliance.compliance_pcn_meldungen WHERE id = :id"),
        {"id": meldung_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_pcn_transition(
    db: Session,
    meldung_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    reason: Optional[str],
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_compliance.compliance_pcn_status_log
                (id, meldung_id, old_status, new_status, operator, reason, tenant_id, created_at)
            VALUES (:id, :meldung_id, :old_status, :new_status, :operator, :reason, :tenant_id, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "meldung_id": meldung_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "reason": reason,
            "tenant_id": tenant_id,
        },
    )


def create_pcn_meldung(
    db: Session,
    tenant_id: str,
    artikel_id: str,
    meldungstyp: str,
    operator: str = "system",
    bemerkung: Optional[str] = None,
) -> Dict[str, Any]:
    """Legt eine neue PCN-Meldung im Status DRAFT an."""
    meldung_id = str(uuid.uuid4())
    # auto-generate meldung_nummer: PCN-YYYYMMDD-UUID[:8]
    meldung_nummer = f"PCN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{meldung_id[:8].upper()}"

    db.execute(
        text("""
            INSERT INTO domain_compliance.compliance_pcn_meldungen
                (id, tenant_id, meldung_nummer, artikel_id, meldungstyp, status, bemerkung, created_at)
            VALUES (:id, :tenant_id, :meldung_nummer, :artikel_id, :meldungstyp, 'DRAFT', :bemerkung, NOW())
        """),
        {
            "id": meldung_id,
            "tenant_id": tenant_id,
            "meldung_nummer": meldung_nummer,
            "artikel_id": artikel_id,
            "meldungstyp": meldungstyp,
            "bemerkung": bemerkung,
        },
    )
    _log_pcn_transition(db, meldung_id, "—", "DRAFT", tenant_id, operator, "Neuanlage")
    db.commit()
    logger.info("pcn_meldung created: %s (%s)", meldung_nummer, meldung_id)
    return {
        "id": meldung_id,
        "meldung_nummer": meldung_nummer,
        "artikel_id": artikel_id,
        "meldungstyp": meldungstyp,
        "status": "DRAFT",
        "tenant_id": tenant_id,
    }


def transition_pcn_status(
    db: Session,
    meldung_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Zustandsübergang für eine PCN-Meldung (fail-closed)."""
    meldung = _fetch_meldung(db, meldung_id)
    if not meldung:
        raise PCNError(f"PCN-Meldung {meldung_id} nicht gefunden")
    if meldung.get("tenant_id") != tenant_id:
        raise PCNError(f"Meldung {meldung_id} gehört nicht zu Tenant {tenant_id}")

    current = (meldung.get("status") or "DRAFT").upper()
    target = new_status.upper()

    if (current, target) not in VALID_TRANSITIONS:
        raise PCNError(
            f"Ungültiger PCN-Statusübergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_TRANSITIONS)}"
        )

    extras: Dict[str, Any] = {}
    if target == "SUBMITTED":
        extras["eingereicht_am"] = datetime.now(timezone.utc).isoformat()
    elif target == "CLOSED":
        extras["abgeschlossen_am"] = datetime.now(timezone.utc).isoformat()

    set_clauses = "status = :status"
    params: Dict[str, Any] = {"status": target, "id": meldung_id}
    if "eingereicht_am" in extras:
        set_clauses += ", eingereicht_am = NOW()"
    if "abgeschlossen_am" in extras:
        set_clauses += ", abgeschlossen_am = NOW()"

    db.execute(
        text(f"UPDATE domain_compliance.compliance_pcn_meldungen SET {set_clauses} WHERE id = :id"),  # nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.
        params,
    )
    _log_pcn_transition(db, meldung_id, current, target, tenant_id, operator, reason)
    db.commit()
    logger.info("pcn_meldung %s: %s → %s", meldung_id, current, target)
    return {**meldung, "status": target, "previous_status": current, **extras}


def withdraw_pcn_meldung(
    db: Session,
    meldung_id: str,
    tenant_id: str,
    grund: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Zieht eine PCN-Meldung zurück (aus DRAFT oder VALIDATED)."""
    meldung = _fetch_meldung(db, meldung_id)
    if not meldung:
        raise PCNError(f"PCN-Meldung {meldung_id} nicht gefunden")
    if meldung.get("tenant_id") != tenant_id:
        raise PCNError(f"Meldung {meldung_id} gehört nicht zu Tenant {tenant_id}")

    current = (meldung.get("status") or "DRAFT").upper()
    if current == "WITHDRAWN":
        return {**meldung, "idempotent": True}
    if current not in WITHDRAW_FROM_STATES:
        raise PCNError(f"Rückzug nur aus DRAFT oder VALIDATED möglich (aktuell: {current})")

    db.execute(
        text("UPDATE domain_compliance.compliance_pcn_meldungen SET status = 'WITHDRAWN' WHERE id = :id"),
        {"id": meldung_id},
    )
    _log_pcn_transition(db, meldung_id, current, "WITHDRAWN", tenant_id, operator, grund)
    db.commit()
    logger.info("pcn_meldung %s zurückgezogen aus %s", meldung_id, current)
    return {**meldung, "status": "WITHDRAWN", "previous_status": current, "idempotent": False}
