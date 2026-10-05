"""DOM-CONTROLLING-004.4 — Kostenstellen-Abschluss Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_KST_TRANSITIONS = {
    ("OFFEN", "IN_BEARBEITUNG"),
    ("IN_BEARBEITUNG", "ABGESCHLOSSEN"),
}


class KSTAbschlussError(Exception):
    """Raised when Kostenstellen-Abschluss constraints are violated."""


def _fetch_abschluss(db: Session, kst_id: str, periode: str, tenant_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("""
            SELECT * FROM domain_controlling.controlling_kst_abschluss
            WHERE kostenstelle_id = :kst AND periode = :periode AND tenant_id = :tid
        """),
        {"kst": kst_id, "periode": periode, "tid": tenant_id},
    ).mappings().first()
    return dict(row) if row else None


def advance_kst_abschluss(
    db: Session,
    kostenstelle_id: str,
    periode: str,
    tenant_id: str,
    new_status: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Schreitet Kostenstellen-Abschluss vorwärts (idempotent wenn bereits ABGESCHLOSSEN)."""
    target = new_status.upper()
    existing = _fetch_abschluss(db, kostenstelle_id, periode, tenant_id)

    if existing:
        current = (existing.get("status") or "OFFEN").upper()
        if current == "ABGESCHLOSSEN":
            return {**existing, "idempotent": True}
        if current == target:
            return {**existing, "idempotent": True}
        if (current, target) not in VALID_KST_TRANSITIONS:
            raise KSTAbschlussError(
                f"Ungültiger KST-Abschluss-Übergang {current} → {target}"
            )
        extras: Dict[str, Any] = {}
        if target == "ABGESCHLOSSEN":
            extras["abgeschlossen_am"] = "NOW()"

        set_clauses = "status = :status, operator = :operator"
        params: Dict[str, Any] = {"status": target, "operator": operator, "id": existing["id"]}
        if target == "ABGESCHLOSSEN":
            set_clauses += ", abgeschlossen_am = NOW()"

        db.execute(
            text(f"UPDATE domain_controlling.controlling_kst_abschluss SET {set_clauses} WHERE id = :id"),  # nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.
            params,
        )
        db.commit()
        logger.info("kst_abschluss %s/%s: %s → %s", kostenstelle_id, periode, current, target)
        return {**existing, "status": target, "previous_status": current, "idempotent": False}

    # create new entry in OFFEN if first call
    if target not in {"OFFEN", "IN_BEARBEITUNG"}:
        raise KSTAbschlussError(
            f"Erster Abschluss-Eintrag muss OFFEN oder IN_BEARBEITUNG sein (angefordert: {target})"
        )
    entry_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_controlling.controlling_kst_abschluss
                (id, tenant_id, kostenstelle_id, periode, status, operator, created_at)
            VALUES (:id, :tid, :kst, :periode, :status, :operator, NOW())
        """),
        {
            "id": entry_id, "tid": tenant_id, "kst": kostenstelle_id,
            "periode": periode, "status": target, "operator": operator,
        },
    )
    db.commit()
    logger.info("kst_abschluss neu: %s/%s Status=%s", kostenstelle_id, periode, target)
    return {
        "id": entry_id, "kostenstelle_id": kostenstelle_id, "periode": periode,
        "status": target, "previous_status": None, "idempotent": False,
    }
