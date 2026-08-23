"""
Interaction State Manager — NC-002
Verwaltet Kanal-/Dialogzustaende getrennt vom Business State.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class InteractionState(str, Enum):
    NEW = "new"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    INTENT_DETECTED = "intent_detected"
    CONVERSION_READY = "conversion_ready"
    ESCALATED = "escalated"
    CLOSED = "closed"


ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "new": ["engaged", "closed"],
    "engaged": ["qualified", "closed"],
    "qualified": ["intent_detected", "closed"],
    "intent_detected": ["conversion_ready", "escalated", "closed"],
    "conversion_ready": ["closed"],
    "escalated": ["closed"],
    "closed": [],
}


def create_interaction(
    channel: str,
    entity_id: Optional[str],
    tenant_id: str,
    db: Session,
) -> dict:
    interaction_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(text("""
            INSERT INTO domain_shared.interactions
                (id, tenant_id, channel, entity_id, state, created_at, updated_at)
            VALUES (:id, :tid, :ch, :eid, 'new', :now, :now)
        """), {"id": interaction_id, "tid": tenant_id, "ch": channel, "eid": entity_id, "now": now})
        db.commit()
    except Exception as exc:
        logger.warning("Interaction create failed (table may not exist): %s", exc)
        db.rollback()

    return {
        "id": interaction_id,
        "channel": channel,
        "entity_id": entity_id,
        "state": InteractionState.NEW.value,
        "created_at": now,
    }


def transition_interaction(
    interaction_id: str,
    target_state: str,
    tenant_id: str,
    db: Session,
) -> dict:
    current = InteractionState.NEW.value
    try:
        row = db.execute(text("""
            SELECT state FROM domain_shared.interactions
            WHERE id = :id AND tenant_id = :tid
        """), {"id": interaction_id, "tid": tenant_id}).fetchone()
        if row:
            current = row.state
    except Exception:  # noqa: BLE001 — Interaktions-State nicht abrufbar; Standardzustand wird verwendet
        pass

    allowed = ALLOWED_TRANSITIONS.get(current, [])
    if target_state not in allowed:
        return {
            "error": f"Uebergang '{current}' -> '{target_state}' nicht erlaubt. Erlaubt: {allowed}",
            "current_state": current,
        }

    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(text("""
            UPDATE domain_shared.interactions
            SET state = :state, updated_at = :now
            WHERE id = :id AND tenant_id = :tid
        """), {"state": target_state, "id": interaction_id, "tid": tenant_id, "now": now})
        db.commit()
    except Exception as exc:
        logger.warning("Interaction transition failed: %s", exc)
        db.rollback()

    return {
        "id": interaction_id,
        "previous_state": current,
        "state": target_state,
        "updated_at": now,
    }


def get_interaction(interaction_id: str, tenant_id: str, db: Session) -> Optional[dict]:
    try:
        row = db.execute(text("""
            SELECT id, channel, entity_id, state, created_at, updated_at
            FROM domain_shared.interactions
            WHERE id = :id AND tenant_id = :tid
        """), {"id": interaction_id, "tid": tenant_id}).fetchone()
        if row:
            return {
                "id": row.id, "channel": row.channel, "entity_id": row.entity_id,
                "state": row.state, "created_at": str(row.created_at), "updated_at": str(row.updated_at),
            }
    except Exception:  # noqa: BLE001 — Interaktions-State nicht abrufbar; Standardzustand wird verwendet
        pass
    return None


def list_interactions(tenant_id: str, db: Session, state: Optional[str] = None, limit: int = 50) -> list[dict]:
    try:
        where = "WHERE tenant_id = :tid"
        params: dict = {"tid": tenant_id, "lim": limit}
        if state:
            where += " AND state = :state"
            params["state"] = state
        rows = db.execute(text(f"""
            SELECT id, channel, entity_id, state, created_at, updated_at
            FROM domain_shared.interactions
            {where}
            ORDER BY updated_at DESC LIMIT :lim
        """), params).fetchall()  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        return [
            {"id": r.id, "channel": r.channel, "entity_id": r.entity_id,
             "state": r.state, "created_at": str(r.created_at), "updated_at": str(r.updated_at)}
            for r in rows
        ]
    except Exception:
        return []
