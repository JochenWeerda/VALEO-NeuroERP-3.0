"""Schema-stable Feeding domain events persisted through the transactional outbox."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Final

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7


FEEDING_EVENT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "feeding.analysis.released",
        "feeding.ration.version.activated",
        "feeding.plan.published",
        "feeding.actual.recorded",
        "feeding.deviation.exceeded",
        "feeding.measure.created",
        "feeding.measure.completed",
        "feeding.measure.overdue",
        "feeding.import.quarantined",
        "feeding.supply.procurement_handoff.created",
    }
)


def build_feeding_event(
    event_type: str,
    *,
    aggregate_id: str,
    payload: dict[str, Any],
    event_id: str | None = None,
    occurred_at: datetime | None = None,
) -> dict[str, Any]:
    """Build the canonical 1.0 envelope and reject contract drift early."""
    if event_type not in FEEDING_EVENT_TYPES:
        raise ValueError(f"Unbekannter Feeding-Eventtyp: {event_type}")
    if not str(aggregate_id).strip():
        raise ValueError("aggregate_id darf nicht leer sein.")
    if not isinstance(payload, dict):
        raise ValueError("payload muss ein Objekt sein.")
    timestamp = occurred_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return {
        "schema_version": "1.0",
        "event_id": event_id or str(uuid7()),
        "event_type": event_type,
        "aggregate_id": str(aggregate_id),
        "timestamp": timestamp.astimezone(timezone.utc).isoformat(),
        "payload": payload,
    }


def emit_feeding_event(
    db: Session,
    *,
    tenant_id: str,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    event_id: str | None = None,
    occurred_at: datetime | None = None,
) -> dict[str, Any]:
    """Insert one event without committing; the caller owns the transaction."""
    event = build_feeding_event(
        event_type,
        aggregate_id=aggregate_id,
        payload=payload,
        event_id=event_id,
        occurred_at=occurred_at,
    )
    db.execute(
        text(
            """INSERT INTO public.outbox_events
          (id,event_type,aggregate_id,payload,"timestamp",published,retry_count,tenant_id)
          VALUES (:id,:event_type,:aggregate_id,CAST(:payload AS jsonb),:timestamp,FALSE,0,:tenant_id)"""
        ),
        {
            "id": event["event_id"],
            "event_type": event_type,
            "aggregate_id": aggregate_id,
            "payload": json.dumps(event, default=str, ensure_ascii=False),
            "timestamp": datetime.fromisoformat(event["timestamp"]),
            "tenant_id": tenant_id,
        },
    )
    return event


__all__ = ["FEEDING_EVENT_TYPES", "build_feeding_event", "emit_feeding_event"]
