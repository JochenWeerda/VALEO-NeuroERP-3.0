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


def _variant_fields_from_rules(rules: dict[str, Any]) -> tuple[str | None, float | None]:
    variant_key = rules.get("_variant_key")
    traffic_weight = rules.get("_traffic_weight")
    try:
        traffic_weight = float(traffic_weight) if traffic_weight is not None else None
    except (TypeError, ValueError):
        traffic_weight = None
    return variant_key, traffic_weight


def register_policy(
    policy_id: str,
    name: str,
    rules: dict[str, Any],
    version: str = "1.0",
    tenant_id: str = "system",
    variant_key: str | None = None,
    traffic_weight: float | None = None,
    db: Optional[Session] = None,
) -> dict:
    if variant_key:
        rules = dict(rules)
        rules["_variant_key"] = variant_key
        if traffic_weight is not None:
            rules["_traffic_weight"] = traffic_weight

    entry = {
        "id": str(uuid4()),
        "policy_id": policy_id,
        "name": name,
        "version": version,
        "rules": rules,
        "tenant_id": tenant_id,
        "active": True,
        "variant_key": variant_key,
        "traffic_weight": traffic_weight,
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
    if variant_key:
        for p in _IN_MEMORY_POLICIES[policy_id]:
            if p.get("variant_key") == variant_key and p.get("tenant_id") == tenant_id:
                p["active"] = False
    else:
        for p in _IN_MEMORY_POLICIES[policy_id]:
            if p.get("tenant_id") == tenant_id:
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
                rules = json.loads(row.rules) if isinstance(row.rules, str) else row.rules
                variant_key, traffic_weight = _variant_fields_from_rules(rules)
                return {
                    "id": row.id, "policy_id": row.policy_id, "name": row.name,
                    "version": row.version,
                    "rules": rules,
                    "active": row.active, "created_at": str(row.created_at),
                    "variant_key": variant_key,
                    "traffic_weight": traffic_weight,
                }
        except Exception:  # noqa: BLE001 — Policy-Abfrage fehlgeschlagen; leeres Ergebnis wird zurückgegeben
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
        except Exception:  # noqa: BLE001 — Policy-Abfrage fehlgeschlagen; leeres Ergebnis wird zurückgegeben
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


def list_active_variants(policy_id: str, tenant_id: str = "system", db: Optional[Session] = None) -> list[dict]:
    if db:
        try:
            rows = db.execute(text("""
                SELECT id, policy_id, name, version, rules, active, created_at
                FROM domain_shared.policy_registry
                WHERE policy_id = :pid AND tenant_id = :tid AND active = true
                ORDER BY created_at DESC
            """), {"pid": policy_id, "tid": tenant_id}).fetchall()
            result = []
            for row in rows:
                rules = json.loads(row.rules) if isinstance(row.rules, str) else row.rules
                variant_key, traffic_weight = _variant_fields_from_rules(rules)
                result.append({
                    "id": row.id,
                    "policy_id": row.policy_id,
                    "name": row.name,
                    "version": row.version,
                    "rules": rules,
                    "active": row.active,
                    "created_at": str(row.created_at),
                    "variant_key": variant_key,
                    "traffic_weight": traffic_weight,
                })
            return result
        except Exception:  # noqa: BLE001 — Policy-Abfrage fehlgeschlagen; leeres Ergebnis wird zurückgegeben
            pass

    versions = _IN_MEMORY_POLICIES.get(policy_id, [])
    return [
        v for v in versions
        if v.get("active") and v.get("tenant_id") == tenant_id
    ]


def select_policy_variant(
    policy_id: str,
    tenant_id: str = "system",
    seed: str | None = None,
    db: Optional[Session] = None,
) -> Optional[dict]:
    variants = list_active_variants(policy_id, tenant_id, db)
    if not variants:
        return None

    weighted = []
    for variant in variants:
        weight = variant.get("traffic_weight")
        if weight is None:
            _, weight = _variant_fields_from_rules(variant.get("rules", {}))
        if weight is None:
            weight = 1.0
        weighted.append((variant, max(0.0, float(weight))))

    total = sum(w for _, w in weighted)
    if total <= 0:
        return variants[0]

    if seed:
        import hashlib

        digest = hashlib.sha256(seed.encode()).hexdigest()
        roll = int(digest, 16) / float(2**256)
    else:
        from random import random

        roll = random()

    threshold = roll * total
    running = 0.0
    for variant, weight in weighted:
        running += weight
        if threshold <= running:
            return variant
    return weighted[-1][0]


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
