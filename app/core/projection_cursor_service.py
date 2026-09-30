"""
Projection Cursor Service — shared core utility for persisting projection cursors.

Extracted from app/api/v1/endpoints/finance_read_models.py to avoid cross-endpoint
imports (Schichtverletzung). Both finance_read_models and runtime_operations
import from here.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

REPLAY_PROJECTION_CONSUMER_ID = "finance-projections-01/replay"


def persist_projection_cursor(
    db: Any,
    tenant_id: str,
    consumer_id: str,
    projection_key: str,
    *,
    cursor_token: str | None = None,
    last_event_id: str | None = None,
    source_rebuilt_at: str | None = None,
    replay_from_event_id: str | None = None,
    replay_to_event_id: str | None = None,
    status: str = "active",
) -> None:
    if db is None:
        return
    now = datetime.now(tz=timezone.utc).isoformat()
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.process_projection_cursors (
                    tenant_id,
                    consumer_id,
                    projection_key,
                    schema_version,
                    cursor_token,
                    last_event_id,
                    source_rebuilt_at,
                    replay_from_event_id,
                    replay_to_event_id,
                    status,
                    updated_at
                ) VALUES (
                    :tenant_id,
                    :consumer_id,
                    :projection_key,
                    :schema_version,
                    :cursor_token,
                    :last_event_id,
                    :source_rebuilt_at,
                    :replay_from_event_id,
                    :replay_to_event_id,
                    :status,
                    :updated_at
                )
                ON CONFLICT (tenant_id, consumer_id, projection_key) DO UPDATE SET
                    schema_version = EXCLUDED.schema_version,
                    cursor_token = EXCLUDED.cursor_token,
                    last_event_id = EXCLUDED.last_event_id,
                    source_rebuilt_at = EXCLUDED.source_rebuilt_at,
                    replay_from_event_id = EXCLUDED.replay_from_event_id,
                    replay_to_event_id = EXCLUDED.replay_to_event_id,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "tenant_id": tenant_id,
                "consumer_id": consumer_id,
                "projection_key": projection_key,
                "schema_version": 1,
                "cursor_token": cursor_token,
                "last_event_id": last_event_id,
                "source_rebuilt_at": source_rebuilt_at,
                "replay_from_event_id": replay_from_event_id,
                "replay_to_event_id": replay_to_event_id,
                "status": status,
                "updated_at": now,
            },
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:  # noqa: BLE001 — Rollback-Fehler ignorieren (Verbindung bereits geschlossen)
            pass
