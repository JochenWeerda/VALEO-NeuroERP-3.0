"""DOM-SALES-004.3 — Lieferschein-Closing-Flow Service."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_LS_TRANSITIONS = {
    ("OFFEN", "KOMMISSIONIERT"),
    ("KOMMISSIONIERT", "VERSANDT"),
    ("VERSANDT", "QUITTIERT"),
}


class LSCloseError(Exception):
    """Raised when Lieferschein-Close constraints are violated."""


def _fetch_lieferschein(db: Session, ls_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_sales.sales_delivery_notes WHERE id = :id"),
        {"id": ls_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_ls_close(
    db: Session,
    ls_id: str,
    tenant_id: str,
    aktion: str,
    operator: str,
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_sales.sales_lieferschein_close_log
                (id, lieferschein_id, tenant_id, aktion, operator, zeitstempel, created_at)
            VALUES (:id, :ls_id, :tenant_id, :aktion, :operator, NOW(), NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "ls_id": ls_id,
            "tenant_id": tenant_id,
            "aktion": aktion,
            "operator": operator,
        },
    )


def advance_lieferschein(
    db: Session,
    ls_id: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
    quittiert_von: Optional[str] = None,
) -> Dict[str, Any]:
    """Schreitet Lieferschein-Status vorwärts (fail-closed)."""
    ls = _fetch_lieferschein(db, ls_id)
    if not ls:
        raise LSCloseError(f"Lieferschein {ls_id} nicht gefunden")
    if ls.get("tenant_id") and ls["tenant_id"] != tenant_id:
        raise LSCloseError(f"Lieferschein {ls_id} gehört nicht zu Tenant {tenant_id}")

    current = (ls.get("status") or "OFFEN").upper()
    target = new_status.upper()

    # idempotent if already QUITTIERT
    if current == "QUITTIERT":
        return {**ls, "idempotent": True}

    if (current, target) not in VALID_LS_TRANSITIONS:
        raise LSCloseError(
            f"Ungültiger LS-Übergang {current} → {target}. "
            f"Erlaubt: {sorted(VALID_LS_TRANSITIONS)}"
        )

    params: Dict[str, Any] = {"status": target, "id": ls_id}
    set_clauses = "status = :status"

    if target == "QUITTIERT":
        set_clauses += ", quittiert_am = NOW()"
        if quittiert_von:
            set_clauses += ", quittiert_von = :quittiert_von"
            params["quittiert_von"] = quittiert_von

    db.execute(
        text(f"UPDATE domain_sales.sales_delivery_notes SET {set_clauses} WHERE id = :id"),  # nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.
        params,
    )
    _log_ls_close(db, ls_id, tenant_id, target, operator)
    db.commit()
    logger.info("lieferschein %s: %s → %s", ls_id, current, target)
    return {**ls, "status": target, "previous_status": current, "idempotent": False}
