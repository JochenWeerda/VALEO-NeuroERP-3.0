"""Vereinheitlichtes Stammdaten-Audit (FEED-RBAC-048).

Fachlich lesbare AuditEvents fuer Stammdaten-Mutationen (Betriebe, Futter,
Analysen, Grants) nach dem Lifecycle-Muster: Der Aufrufer schreibt das Event
IN DERSELBEN Transaktion wie die Mutation (kein Commit hier) — Audit und
Fachdaten sind atomar.
"""
from __future__ import annotations

import json
from typing import Any, Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7

MasterDataEntity = Literal["business", "feed", "analysis", "grant"]


def record_master_data_audit(db: Session, *, tenant_id: str, actor: str,
                             entity_type: MasterDataEntity, entity_id: str,
                             event_type: str, delta: dict[str, Any],
                             reason: str | None = None) -> None:
    db.execute(text("""
      INSERT INTO domain_agrar.feeding_master_data_audit_events
        (id,tenant_id,entity_type,entity_id,event_type,actor,reason,delta)
      VALUES (:id,:tenant_id,:entity_type,:entity_id,:event_type,:actor,:reason,
              CAST(:delta AS jsonb))
    """), {"id": str(uuid7()), "tenant_id": tenant_id, "entity_type": entity_type,
           "entity_id": entity_id, "event_type": event_type, "actor": actor,
           "reason": reason, "delta": json.dumps(delta, ensure_ascii=False, default=str)})
