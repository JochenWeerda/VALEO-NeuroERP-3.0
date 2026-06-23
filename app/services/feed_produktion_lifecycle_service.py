"""DOM-FEED-PROD-004.2 — Mischfutter Produktions-Lifecycle (Rezeptur→Charge→Freigabe)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_PRODUKTION_TRANSITIONS = {
    ("GEPLANT", "IN_PRODUKTION"),
    ("GEPLANT", "STORNIERT"),
    ("IN_PRODUKTION", "FERTIG"),
    ("IN_PRODUKTION", "STORNIERT"),
    ("FERTIG", "QS_FREIGEGEBEN"),
    ("FERTIG", "QS_GESPERRT"),
    ("QS_GESPERRT", "QS_FREIGEGEBEN"),
    ("QS_GESPERRT", "VERNICHTET"),
    ("QS_FREIGEGEBEN", "AUSGELAGERT"),
}


class FeedProduktionError(Exception):
    pass


def create_produktionsauftrag(
    db: Session,
    tenant_id: str,
    rezeptur_id: str,
    soll_menge_kg: float,
    geplant_datum: str,
    charge_nr: str,
    operator: str = "system",
) -> Dict[str, Any]:
    existing = db.execute(
        text("""
            SELECT * FROM domain_futtermittel.feed_produktionsauftraege
            WHERE charge_nr = :cnr AND tenant_id = :tid
        """),
        {"cnr": charge_nr, "tid": tenant_id},
    ).mappings().first()
    if existing:
        return dict(existing)

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_futtermittel.feed_produktionsauftraege
                (id, tenant_id, rezeptur_id, soll_menge_kg, geplant_datum,
                 charge_nr, status, operator, created_at)
            VALUES (:id, :tenant_id, :rezeptur_id, :soll_menge_kg, :geplant_datum,
                    :charge_nr, 'GEPLANT', :operator, NOW())
        """),
        {
            "id": rec_id,
            "tenant_id": tenant_id,
            "rezeptur_id": rezeptur_id,
            "soll_menge_kg": soll_menge_kg,
            "geplant_datum": geplant_datum,
            "charge_nr": charge_nr,
            "operator": operator,
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_futtermittel.feed_produktionsauftraege WHERE id = :id"),
        {"id": rec_id},
    ).mappings().first()
    return dict(row)


def transition_produktionsauftrag(
    db: Session,
    auftrag_id: str,
    new_status: str,
    tenant_id: str,
    ist_menge_kg: Optional[float],
    operator: str,
    qs_befund: str = "",
) -> Dict[str, Any]:
    rec = db.execute(
        text("""
            SELECT * FROM domain_futtermittel.feed_produktionsauftraege
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": auftrag_id, "tid": tenant_id},
    ).mappings().first()
    if not rec:
        raise FeedProduktionError(f"Produktionsauftrag {auftrag_id} nicht gefunden")
    old_status = rec["status"]
    if (old_status, new_status) not in VALID_PRODUKTION_TRANSITIONS:
        raise FeedProduktionError(f"Ungültiger Übergang {old_status} → {new_status}")

    update_fields = "status = :new_status, updated_at = NOW()"
    params: Dict[str, Any] = {
        "new_status": new_status,
        "id": auftrag_id,
        "tid": tenant_id,
    }
    if ist_menge_kg is not None:
        update_fields += ", ist_menge_kg = :ist_menge_kg"
        params["ist_menge_kg"] = ist_menge_kg
    if qs_befund:
        update_fields += ", qs_befund = :qs_befund"
        params["qs_befund"] = qs_befund

    db.execute(
        text(f"""
            UPDATE domain_futtermittel.feed_produktionsauftraege
            SET {update_fields}
            WHERE id = :id AND tenant_id = :tid
        """),
        params,
    )
    _log_produktion_event(db, auftrag_id, tenant_id, old_status, new_status, operator, qs_befund)
    db.commit()
    updated = db.execute(
        text("SELECT * FROM domain_futtermittel.feed_produktionsauftraege WHERE id = :id"),
        {"id": auftrag_id},
    ).mappings().first()
    return dict(updated)


def _log_produktion_event(
    db: Session,
    auftrag_id: str,
    tenant_id: str,
    old_status: str,
    new_status: str,
    operator: str,
    qs_befund: str = "",
) -> None:
    db.execute(
        text("""
            INSERT INTO domain_futtermittel.feed_produktion_log
                (id, auftrag_id, tenant_id, old_status, new_status, operator, qs_befund, created_at)
            VALUES (:id, :auftrag_id, :tenant_id, :old_status, :new_status, :operator, :qs_befund, NOW())
        """),
        {
            "id": str(uuid.uuid4()),
            "auftrag_id": auftrag_id,
            "tenant_id": tenant_id,
            "old_status": old_status,
            "new_status": new_status,
            "operator": operator,
            "qs_befund": qs_befund,
        },
    )
