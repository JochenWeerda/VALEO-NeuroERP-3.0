"""Canonical, tenant-scoped CRM segment data and bounded membership evaluation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable
from fastapi import HTTPException
from sqlalchemy import text
from app.core.business_time import business_now
from app.core.identity_context import current_identity
from app.core.uuid7 import uuid7
from app.domains.shared.events import IntegrationEvent
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services.mask_action_runtime_service import _write_audit

TEXT_FIELDS = frozenset({"country", "postal_code", "city", "status", "name_1"})
BOOL_FIELDS = frozenset({"is_customer", "is_supplier", "bio_certified", "email_opt_in"})


def criteria_rules(criteria: dict[str, Any]) -> list[dict[str, str]]:
    if len(criteria) > 20:
        raise HTTPException(422, "At most 20 segment rules are supported")
    rules = []
    for field, condition in criteria.items():
        if field not in TEXT_FIELDS | BOOL_FIELDS:
            raise HTTPException(422, f"Unsupported segment criterion: {field}")
        if isinstance(condition, dict):
            if set(condition) != {"op", "value"}:
                raise HTTPException(422, "A criterion requires exactly op and value")
            op, value = condition["op"], condition["value"]
        else:
            op, value = "eq", condition
        if op not in {"eq", "contains", "prefix"} or field in BOOL_FIELDS and op != "eq":
            raise HTTPException(422, "Unsupported segment operator")
        if field in BOOL_FIELDS:
            if isinstance(value, str) and value.lower() in {"true", "false"}:
                value = value.lower() == "true"
            if not isinstance(value, bool):
                raise HTTPException(422, "Boolean segment criterion must be true or false")
            value = "true" if value else "false"
        elif not isinstance(value, str) or not value.strip() or len(value) > 255:
            raise HTTPException(422, "Text segment criterion must have 1..255 characters")
        rules.append({"field": field, "op": op, "value": value})
    return rules


def criteria_from_rules(rules: list[dict[str, str]]) -> dict[str, Any]:
    result = {}
    for rule in rules:
        if set(rule) != {"field", "op", "value"} or rule["field"] in result:
            raise HTTPException(422, "Malformed or duplicate segment rule")
        result[rule["field"]] = {"op": rule["op"], "value": rule["value"]}
    criteria_rules(result)
    return result


def version_of(row: dict) -> int:
    stamp = row.get("updated_at") or row.get("created_at")
    if isinstance(stamp, str):
        stamp = datetime.fromisoformat(stamp)
    if stamp is None:
        return 1
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return max(1, int(stamp.timestamp() * 1_000_000))


def find(db, tenant: str, segment_id: str, *, lock: bool = False) -> dict:
    if not tenant or not tenant.strip():
        raise HTTPException(403, "Verified tenant required")
    query = ("SELECT * FROM domain_crm.crm_segments WHERE tenant_id=:tenant AND id=:id FOR UPDATE" if lock
             else "SELECT * FROM domain_crm.crm_segments WHERE tenant_id=:tenant AND id=:id")
    row = db.execute(text(query), {"tenant": tenant, "id": segment_id}).mappings().first()
    if row is None:
        raise HTTPException(404, "Segment not found")
    result = dict(row)
    result["version"] = version_of(result)
    criteria = result.get("criteria") or {}
    if isinstance(criteria, str):
        criteria = json.loads(criteria)
    result["criteria"] = criteria
    try:
        result["criteria_rules"] = criteria_rules(criteria)
        result["criteria_supported"] = True
    except HTTPException:
        # Existing unknown rules are visible, never silently discarded or evaluated.
        result["criteria_rules"] = []
        result["criteria_supported"] = False
    return result


def check_version(row: dict, expected: int | None) -> None:
    if expected is None:
        raise HTTPException(428, "expected_version is required")
    if row["version"] != expected:
        raise HTTPException(409, "Segment changed; reload before retrying")


def evaluate(db, tenant: str, row: dict) -> int:
    if row["segment_type"] == "static":
        return db.execute(text("SELECT count(*) FROM domain_crm.crm_segment_members m JOIN domain_crm.business_partners p ON p.partner_id=m.partner_id AND p.tenant_id=m.tenant_id WHERE m.tenant_id=:tenant AND m.segment_id=:id"), {"tenant": tenant, "id": row["id"]}).scalar_one()
    if row["segment_type"] != "dynamic":
        raise HTTPException(422, "Hybrid criteria require membership provenance and are not supported")
    rules = criteria_rules(row["criteria"])
    if not rules:
        raise HTTPException(422, "A dynamic segment requires explicit criteria")
    clauses, params = ["tenant_id=:tenant"], {"tenant": tenant, "id": row["id"]}
    for index, rule in enumerate(rules):
        field, op, value = rule["field"], rule["op"], rule["value"]
        key = f"criterion_{index}"
        if field in BOOL_FIELDS:
            clauses.append(f"{field}=:{key}")
            params[key] = value == "true"
        elif op == "eq":
            clauses.append(f"{field}=:{key}")
            params[key] = value
        else:
            # Literal substring/prefix; no wildcard interpretation, no client SQL.
            clauses.append(f"strpos(lower(COALESCE({field}, '')), lower(:{key})) " + ("> 0" if op == "contains" else "= 1"))
            params[key] = value
    members = db.execute(text("SELECT partner_id FROM domain_crm.business_partners WHERE " + " AND ".join(clauses) + " ORDER BY partner_id LIMIT 5001 FOR SHARE"), params).scalars().fetchmany(5001)  # nosec B608  # Spalten nur aus TEXT_FIELDS/BOOL_FIELDS (criteria_rules), Werte gebunden
    if len(members) > 5000:
        raise HTTPException(413, "Segment exceeds the 5000-member evaluation limit")
    db.execute(text("DELETE FROM domain_crm.crm_segment_members WHERE tenant_id=:tenant AND segment_id=:id"), params)
    for member in members:
        db.execute(text("INSERT INTO domain_crm.crm_segment_members (id,tenant_id,segment_id,partner_id,added_at) VALUES (:member_id,:tenant,:id,:partner_id,NOW())"), {"member_id": str(uuid7()), "tenant": tenant, "id": row["id"], "partner_id": member})
    return len(members)


def command(db, tenant: str, action: str, key: str, payload: dict, mutate: Callable[[], dict]) -> dict:
    principal = current_identity()
    if principal.tenant_id != tenant or not principal.subject or principal.claims.get("identity_type") != "human" or principal.claims.get("act") or principal.claims.get("agent_id"):
        raise HTTPException(403, "CRM segment mutation requires an authorized human identity")
    tool = "crm.segment." + action + ".v1"
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    lock = int.from_bytes(hashlib.sha256(json.dumps([tenant, tool, key]).encode()).digest()[:8], "big", signed=True)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock})
        previous = db.execute(text("SELECT actor_id,payload_hash,result FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key"), {"tenant": tenant, "tool": tool, "key": key}).mappings().first()
        if previous:
            if previous["actor_id"] != principal.subject or previous["payload_hash"] != fingerprint:
                raise HTTPException(409, "Replay belongs to another actor or payload")
            result = previous["result"]
            db.commit()
            return json.loads(result) if isinstance(result, str) else result
        result = mutate()
        entity_id = result["id"]
        audit_id = _write_audit(db, tenant_id=tenant, action_key=tool, entity_type="crm_segment", entity_id=entity_id, audit_reason=payload.get("audit_reason"), idempotency_key=key, summary=action, performed_by=principal.subject)
        now = business_now()
        event = IntegrationEvent(aggregate_id=entity_id, timestamp=now, event_type=tool, tenant_id=tenant, payload={"actor_id": principal.subject, "audit_id": audit_id, "version": result.get("version")})
        db.add(OutboxEvent(id=event.event_id,event_type=tool,aggregate_id=entity_id,tenant_id=tenant,timestamp=now,payload=json.dumps(asdict(event),default=str),published=False))
        db.execute(text("INSERT INTO public.mcp_tool_executions (tenant_id,tool_name,idempotency_key,actor_id,payload_hash,result) VALUES (:tenant,:tool,:key,:actor,:hash,CAST(:result AS jsonb))"), {"tenant": tenant,"tool": tool,"key": key,"actor": principal.subject,"hash": fingerprint,"result": json.dumps(result,default=str)})
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
