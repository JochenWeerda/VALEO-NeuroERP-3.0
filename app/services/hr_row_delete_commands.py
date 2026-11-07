"""Versioned, transaction-bound deletion for HR rows; no transport registration.

The caller owns commit/rollback and must provide the verified identity. Agent writes
remain disabled until a capability and role have been explicitly approved.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import PERSONAL
from app.auth.deps import effective_roles
from app.services.mask_action_runtime_service import _write_audit, _write_outbox
from app.services.mcp_execution_service import _advisory_lock, _store_execution, _tenant_from_claims


class HrDeleteCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["onboarding", "qualification", "assignment"]
    entity_id: str = Field(min_length=1, max_length=120)
    expected_updated_at: datetime
    idempotency_key: str = Field(min_length=1, max_length=120)

    @field_validator("entity_id", "idempotency_key")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip() or value != value.strip():
            raise ValueError("non-empty canonical value required")
        return value

    @field_validator("expected_updated_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone required")
        return value.astimezone(timezone.utc)


_SELECT = {
    "onboarding": text("SELECT updated_at FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
    "qualification": text("SELECT updated_at FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
    "assignment": text("SELECT updated_at FROM domain_hr.training_assignments WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
}
_DELETE = {
    "onboarding": text("DELETE FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant AND id=:id AND updated_at=:version"),
    "qualification": text("DELETE FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id AND updated_at=:version"),
    "assignment": text("DELETE FROM domain_hr.training_assignments WHERE tenant_id=:tenant AND id=:id AND updated_at=:version"),
}



def _replay_or_none(db: Session, tenant: str, name: str, key: str, actor: str, fingerprint: str) -> dict | None:
    # Do not roll back the caller's transaction merely to read a replay.
    row = db.execute(text("""
        SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions
        WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key
    """), {"tenant": tenant, "tool": name, "key": key}).mappings().first()
    if row is None:
        return None
    if row["actor_id"] != actor or row["payload_hash"] != fingerprint:
        raise HTTPException(409, "Idempotency key is already bound to another request")
    result = json.loads(row["result"]) if isinstance(row["result"], str) else row["result"]
    return {**result, "replayed": True}

def delete_hr_row(db: Session, command: HrDeleteCommand, *, user: dict, tenant: str) -> dict:
    """Delete only the reviewed version; caller commits the entire transaction.

    Authorization is checked before even replay lookup. Identity and tenant must
    be verified by the caller's authentication middleware; no request body may
    choose them. Human-only until a per-capability agent policy is approved.
    """
    actor = user.get("sub")
    raw = user.get("raw")
    verified_tenant = _tenant_from_claims(raw)
    roles = user.get("roles") or []
    if not isinstance(roles, (list, tuple, set)):
        roles = []
    if (not isinstance(actor, str) or not actor.strip() or not tenant or verified_tenant != tenant
            or not effective_roles(roles) & set(PERSONAL)):
        raise HTTPException(403, "Verified subject, tenant and personnel write role required")
    if (not isinstance(raw, dict) or raw.get("identity_type") != "human"
            or raw.get("act") or raw.get("agent_id")):
        raise HTTPException(403, "HR deletion capability is not enabled for agents")

    name = f"hr.{command.kind}.delete.v1"
    payload = {"kind": command.kind, "entity_id": command.entity_id,
               "expected_updated_at": command.expected_updated_at.isoformat()}
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    _advisory_lock(db, tenant, name, command.idempotency_key)
    replay = _replay_or_none(db, tenant, name, command.idempotency_key, actor, fingerprint)
    if replay is not None:
        return replay

    params = {"tenant": tenant, "id": command.entity_id}
    row = db.execute(_SELECT[command.kind], params).mappings().first()
    if row is None:
        raise HTTPException(404, "HR record not found")
    current = row["updated_at"]
    if not isinstance(current, datetime) or current.tzinfo is None or current != command.expected_updated_at:
        raise HTTPException(409, "HR record changed; reload before deleting")
    deleted = db.execute(_DELETE[command.kind], {**params, "version": command.expected_updated_at})
    if deleted.rowcount != 1:
        raise HTTPException(409, "HR record changed; reload before deleting")
    audit_id = _write_audit(db, tenant_id=tenant, action_key=name, entity_type=f"hr_{command.kind}",
                            entity_id=command.entity_id, audit_reason=None, idempotency_key=command.idempotency_key,
                            summary=f"HR {command.kind} deleted", performed_by=actor)
    outbox_id = _write_outbox(db, tenant_id=tenant, event_type=name, aggregate_id=command.entity_id,
                               payload={"id": command.entity_id, "tenant_id": tenant})
    result = {"success": True, "replayed": False, "entity_id": command.entity_id,
              "auditEntryId": audit_id, "outboxEventId": outbox_id}
    _store_execution(db, tenant=tenant, tool=name, key=command.idempotency_key, actor=actor,
                     fingerprint=fingerprint, result=result)
    return result
