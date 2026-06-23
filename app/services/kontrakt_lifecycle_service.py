"""DOM-CON-004.2 — Kontrakt-Lifecycle Service (Statusmaschine + Fixing + Settlement)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_KONTRAKT_TRANSITIONS = {
    ("ENTWURF", "FREIGEGEBEN"),
    ("ENTWURF", "STORNIERT"),
    ("FREIGEGEBEN", "AKTIV"),
    ("FREIGEGEBEN", "STORNIERT"),
    ("AKTIV", "TEIL_ERFUELLT"),
    ("AKTIV", "ERFUELLT"),
    ("AKTIV", "STORNIERT"),
    ("TEIL_ERFUELLT", "ERFUELLT"),
    ("TEIL_ERFUELLT", "STORNIERT"),
}


class KontraktLifecycleError(Exception):
    pass


def _fetch_kontrakt_lifecycle(db: Session, kontrakt_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_kontrakte.kontrakt_lifecycle WHERE kontrakt_id = :id"),
        {"id": kontrakt_id},
    ).mappings().first()
    return dict(row) if row else None


def _log_kontrakt_transition(
    db: Session,
    kontrakt_id: str,
    old_status: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    grund: str = "",
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_kontrakte.kontrakt_status_log
                (id, kontrakt_id, tenant_id, old_status, new_status, operator, grund, created_at)
            VALUES (:id, :kontrakt_id, :tenant_id, :old_status, :new_status, :operator, :grund, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "kontrakt_id": kontrakt_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "grund": grund,
        },
    )


def create_kontrakt_lifecycle(
    db: Session,
    kontrakt_id: str,
    tenant_id: str,
    kontrakt_nr: str,
    artikel_id: str,
    menge_t: float,
    preis_eur_t: float,
    lieferant_id: str,
    periode: str,
    operator: str = "system",
) -> Dict[str, Any]:
    existing = _fetch_kontrakt_lifecycle(db, kontrakt_id)
    if existing:
        return existing
    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_kontrakte.kontrakt_lifecycle
                (id, kontrakt_id, tenant_id, kontrakt_nr, artikel_id, menge_t,
                 preis_eur_t, lieferant_id, periode, status, created_at)
            VALUES (:id, :kontrakt_id, :tenant_id, :kontrakt_nr, :artikel_id, :menge_t,
                    :preis_eur_t, :lieferant_id, :periode, 'ENTWURF', NOW())
        """),
        {
            "id": rec_id,
            "kontrakt_id": kontrakt_id,
            "tenant_id": tenant_id,
            "kontrakt_nr": kontrakt_nr,
            "artikel_id": artikel_id,
            "menge_t": menge_t,
            "preis_eur_t": preis_eur_t,
            "lieferant_id": lieferant_id,
            "periode": periode,
        },
    )
    db.commit()
    _log_kontrakt_transition(db, kontrakt_id, "", "ENTWURF", tenant_id, operator, "Anlage")
    db.commit()
    return _fetch_kontrakt_lifecycle(db, kontrakt_id)


def transition_kontrakt(
    db: Session,
    kontrakt_id: str,
    new_status: str,
    tenant_id: str,
    operator: str,
    grund: str = "",
) -> Dict[str, Any]:
    rec = _fetch_kontrakt_lifecycle(db, kontrakt_id)
    if not rec:
        raise KontraktLifecycleError(f"Kontrakt {kontrakt_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_KONTRAKT_TRANSITIONS:
        raise KontraktLifecycleError(
            f"Ungültiger Übergang {old_status} → {new_status}"
        )
    db.execute(
        text("""
            UPDATE domain_kontrakte.kontrakt_lifecycle
            SET status = :new_status, updated_at = NOW()
            WHERE kontrakt_id = :kontrakt_id AND tenant_id = :tenant_id
        """),
        {"new_status": new_status, "kontrakt_id": kontrakt_id, "tenant_id": tenant_id},
    )
    _log_kontrakt_transition(db, kontrakt_id, old_status, new_status, tenant_id, operator, grund)
    db.commit()
    return _fetch_kontrakt_lifecycle(db, kontrakt_id)
