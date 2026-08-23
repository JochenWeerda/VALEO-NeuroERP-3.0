"""
Audit Hardening Service — NC-D1/D2
Append-Only Audit mit SHA-256 Hash-Chain.
Nutzt das bestehende AuditLog-Modell (domain_shared.audit_logs).
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _compute_hash(prev_hash: str, payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f"{prev_hash}:{canonical}".encode("utf-8")).hexdigest()


def _get_latest_hash(db: Session, tenant_id: str) -> str:
    try:
        row = db.execute(text("""
            SELECT hash FROM domain_shared.audit_logs
            WHERE tenant_id = :tid AND hash IS NOT NULL
            ORDER BY timestamp DESC LIMIT 1
        """), {"tid": tenant_id}).fetchone()
        return row.hash if row else "genesis"
    except Exception:
        return "genesis"


def append_audit_entry(
    db: Session,
    tenant_id: str,
    action: str,
    entity_type: str,
    entity_id: str = "",
    user_id: str = "system",
    user_email: str = "",
    changes: Optional[dict] = None,
    ip_address: str = "",
    user_agent: str = "",
    correlation_id: str = "",
) -> dict:
    entry_id = str(uuid4())
    now = datetime.now(timezone.utc)

    prev_hash = _get_latest_hash(db, tenant_id)

    payload = {
        "id": entry_id,
        "tenant_id": tenant_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user_id": user_id,
        "timestamp": now.isoformat(),
        "changes": changes or {},
    }
    entry_hash = _compute_hash(prev_hash, payload)

    try:
        db.execute(text("""
            INSERT INTO domain_shared.audit_logs
                (id, timestamp, user_id, user_email, tenant_id, action,
                 entity_type, entity_id, changes, ip_address, user_agent,
                 correlation_id, prev_hash, hash)
            VALUES
                (:id, :ts, :uid, :email, :tid, :action,
                 :etype, :eid, :changes, :ip, :ua,
                 :cid, :prev, :hash)
        """), {
            "id": entry_id, "ts": now, "uid": user_id, "email": user_email,
            "tid": tenant_id, "action": action, "etype": entity_type,
            "eid": entity_id, "changes": json.dumps(changes or {}),
            "ip": ip_address, "ua": user_agent, "cid": correlation_id,
            "prev": prev_hash, "hash": entry_hash,
        })
        db.commit()
    except Exception as exc:
        logger.warning("Audit append failed: %s", exc)
        db.rollback()
        return {"error": str(exc)}

    return {
        "id": entry_id, "hash": entry_hash, "prev_hash": prev_hash,
        "action": action, "entity_type": entity_type, "entity_id": entity_id,
        "timestamp": now.isoformat(),
    }


def validate_hash_chain(db: Session, tenant_id: str, limit: int = 1000) -> dict:
    try:
        rows = db.execute(text("""
            SELECT id, action, entity_type, entity_id, user_id, timestamp,
                   changes, prev_hash, hash
            FROM domain_shared.audit_logs
            WHERE tenant_id = :tid AND hash IS NOT NULL
            ORDER BY timestamp ASC LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
    except Exception as exc:
        return {"valid": False, "error": str(exc), "checked": 0}

    if not rows:
        return {"valid": True, "checked": 0, "breaks": []}

    breaks = []
    expected_prev = "genesis"

    for row in rows:
        if row.prev_hash != expected_prev:
            breaks.append({
                "id": row.id,
                "expected_prev": expected_prev,
                "actual_prev": row.prev_hash,
            })

        payload = {
            "id": row.id, "tenant_id": tenant_id,
            "action": row.action, "entity_type": row.entity_type,
            "entity_id": row.entity_id, "user_id": row.user_id,
            "timestamp": row.timestamp.isoformat() if hasattr(row.timestamp, "isoformat") else str(row.timestamp),
            "changes": json.loads(row.changes) if isinstance(row.changes, str) else (row.changes or {}),
        }
        recomputed = _compute_hash(row.prev_hash, payload)
        if recomputed != row.hash:
            breaks.append({
                "id": row.id,
                "expected_hash": recomputed,
                "actual_hash": row.hash,
                "type": "hash_mismatch",
            })

        expected_prev = row.hash

    return {"valid": len(breaks) == 0, "checked": len(rows), "breaks": breaks}


def query_audit_trail(
    db: Session, tenant_id: str,
    aggregate_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    where = "WHERE tenant_id = :tid"
    params: dict[str, Any] = {"tid": tenant_id, "lim": limit}

    if aggregate_id:
        where += " AND entity_id = :eid"
        params["eid"] = aggregate_id
    if from_date:
        where += " AND timestamp >= :from_dt"
        params["from_dt"] = from_date
    if to_date:
        where += " AND timestamp <= :to_dt"
        params["to_dt"] = to_date

    try:
        rows = db.execute(text(f"""
            SELECT id, timestamp, user_id, user_email, action, entity_type,
                   entity_id, changes, prev_hash, hash, correlation_id
            FROM domain_shared.audit_logs
            {where}
            ORDER BY timestamp DESC LIMIT :lim
        """), params).fetchall()  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        return [
            {
                "id": r.id, "timestamp": str(r.timestamp), "user_id": r.user_id,
                "user_email": r.user_email, "action": r.action,
                "entity_type": r.entity_type, "entity_id": r.entity_id,
                "changes": r.changes, "prev_hash": r.prev_hash, "hash": r.hash,
                "correlation_id": r.correlation_id,
            }
            for r in rows
        ]
    except Exception:
        return []
