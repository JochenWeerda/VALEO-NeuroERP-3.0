"""DOM-HRM-004.3 — HRM Abwesenheitsantrag Lifecycle (Urlaub/AU/Sonderurlaub)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_ABWESENHEIT_TRANSITIONS = {
    ("BEANTRAGT", "GENEHMIGT"),
    ("BEANTRAGT", "ABGELEHNT"),
    ("BEANTRAGT", "ZURUECKGEZOGEN"),
    ("GENEHMIGT", "STORNIERT"),
    ("GENEHMIGT", "VERBRAUCHT"),
}

ABWESENHEIT_TYPEN = {"URLAUB", "KRANKHEIT", "SONDERURLAUB", "FORTBILDUNG", "ELTERNZEIT"}


class AbwesenheitError(Exception):
    pass


def create_abwesenheitsantrag(
    db: Session,
    tenant_id: str,
    mitarbeiter_id: str,
    abwesenheit_typ: str,
    von_datum: str,
    bis_datum: str,
    arbeitstage: int,
    kommentar: str = "",
    operator: str = "system",
) -> Dict[str, Any]:
    if abwesenheit_typ not in ABWESENHEIT_TYPEN:
        raise AbwesenheitError(f"Unbekannter Abwesenheits-Typ: {abwesenheit_typ}")
    if arbeitstage <= 0:
        raise AbwesenheitError("Anzahl Arbeitstage muss > 0 sein")

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_hrm.hrm_abwesenheiten
                (id, tenant_id, mitarbeiter_id, abwesenheit_typ, von_datum, bis_datum,
                 arbeitstage, kommentar, status, operator, created_at)
            VALUES (:id, :tenant_id, :mitarbeiter_id, :abwesenheit_typ, :von_datum, :bis_datum,
                    :arbeitstage, :kommentar, 'BEANTRAGT', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "mitarbeiter_id": mitarbeiter_id,
            "abwesenheit_typ": abwesenheit_typ,
            "von_datum": von_datum,
            "bis_datum": bis_datum,
            "arbeitstage": arbeitstage,
            "kommentar": kommentar,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hrm.hrm_abwesenheiten WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_abwesenheit(
    db: Session,
    abwesenheit_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    ablehnungs_grund: str = "",
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_hrm.hrm_abwesenheiten
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": abwesenheit_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise AbwesenheitError(f"Abwesenheit {abwesenheit_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_ABWESENHEIT_TRANSITIONS:
        raise AbwesenheitError(f"Ungültiger Übergang {old_status} → {new_status}")

    db.execute(
        text("""
            UPDATE domain_hrm.hrm_abwesenheiten
            SET status = :new_status, ablehnungs_grund = :grund, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tid
        """),
        {
            "new_status": new_status,
            "grund": ablehnungs_grund,
            "id": abwesenheit_id,
            "tid": tenant_id,
        },
    )
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_hrm.hrm_abwesenheiten WHERE id = :id"),
        {"id": abwesenheit_id},
    ).mappings().first()
    return dict(updated)
