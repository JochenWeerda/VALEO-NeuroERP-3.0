"""
Policy Registry — NC-G4
Versionierte Policy-Speicherung mit Rollback-Faehigkeit.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_IN_MEMORY_POLICIES: dict[str, list[dict]] = {}


def register_policy(
    policy_id: str,
    name: str,
    rules: dict[str, Any],
    version: str = "1.0",
    tenant_id: str = "system",
    db: Optional[Session] = None,
) -> dict:
    entry = {
        "id": str(uuid4()),
        "policy_id": policy_id,
        "name": name,
        "version": version,
        "rules": rules,
        "tenant_id": tenant_id,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if db:
        try:
            db.execute(text("""
                UPDATE domain_shared.policy_registry
                SET active = false
                WHERE policy_id = :pid AND tenant_id = :tid AND active = true
            """), {"pid": policy_id, "tid": tenant_id})
            db.execute(text("""
                INSERT INTO domain_shared.policy_registry
                    (id, policy_id, name, version, rules, tenant_id, active, created_at)
                VALUES (:id, :pid, :name, :ver, :rules, :tid, true, :created)
            """), {
                "id": entry["id"], "pid": policy_id, "name": name,
                "ver": version, "rules": json.dumps(rules),
                "tid": tenant_id, "created": entry["created_at"],
            })
            db.commit()
        except Exception as exc:
            logger.warning("Policy registry DB write failed: %s", exc)
            db.rollback()

    if policy_id not in _IN_MEMORY_POLICIES:
        _IN_MEMORY_POLICIES[policy_id] = []
    for p in _IN_MEMORY_POLICIES[policy_id]:
        p["active"] = False
    _IN_MEMORY_POLICIES[policy_id].append(entry)

    return entry


def get_active_policy(policy_id: str, tenant_id: str = "system", db: Optional[Session] = None) -> Optional[dict]:
    if db:
        try:
            row = db.execute(text("""
                SELECT id, policy_id, name, version, rules, active, created_at
                FROM domain_shared.policy_registry
                WHERE policy_id = :pid AND tenant_id = :tid AND active = true
                LIMIT 1
            """), {"pid": policy_id, "tid": tenant_id}).fetchone()
            if row:
                return {
                    "id": row.id, "policy_id": row.policy_id, "name": row.name,
                    "version": row.version,
                    "rules": json.loads(row.rules) if isinstance(row.rules, str) else row.rules,
                    "active": row.active, "created_at": str(row.created_at),
                }
        except Exception:
            pass

    versions = _IN_MEMORY_POLICIES.get(policy_id, [])
    for v in reversed(versions):
        if v.get("active") and v.get("tenant_id") == tenant_id:
            return v
    return None


def list_policies(tenant_id: str = "system", db: Optional[Session] = None) -> list[dict]:
    if db:
        try:
            rows = db.execute(text("""
                SELECT policy_id, name, version, active, created_at
                FROM domain_shared.policy_registry
                WHERE tenant_id = :tid
                ORDER BY created_at DESC
            """), {"tid": tenant_id}).fetchall()
            return [
                {"policy_id": r.policy_id, "name": r.name, "version": r.version,
                 "active": r.active, "created_at": str(r.created_at)}
                for r in rows
            ]
        except Exception:
            pass

    result = []
    for versions in _IN_MEMORY_POLICIES.values():
        for v in versions:
            if v.get("tenant_id") == tenant_id:
                result.append({
                    "policy_id": v["policy_id"], "name": v["name"],
                    "version": v["version"], "active": v["active"],
                    "created_at": v["created_at"],
                })
    return result


def rollback_policy(policy_id: str, tenant_id: str = "system", db: Optional[Session] = None) -> Optional[dict]:
    versions = _IN_MEMORY_POLICIES.get(policy_id, [])
    tenant_versions = [v for v in versions if v.get("tenant_id") == tenant_id]
    if len(tenant_versions) < 2:
        return None

    for v in tenant_versions:
        v["active"] = False
    tenant_versions[-2]["active"] = True

    if db:
        try:
            db.execute(text("""
                UPDATE domain_shared.policy_registry
                SET active = false
                WHERE policy_id = :pid AND tenant_id = :tid
            """), {"pid": policy_id, "tid": tenant_id})
            db.execute(text("""
                UPDATE domain_shared.policy_registry
                SET active = true
                WHERE id = :id
            """), {"id": tenant_versions[-2]["id"]})
            db.commit()
        except Exception as exc:
            logger.warning("Policy rollback failed: %s", exc)
            db.rollback()

    return tenant_versions[-2]
