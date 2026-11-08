"""Versioned, transaction-bound deletion for HR rows; no transport registration.

The caller owns commit/rollback and must provide the verified identity. Agent writes
remain disabled until a capability and role have been explicitly approved.
"""
from __future__ import annotations

import hashlib
import json
from typing import Literal
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import PERSONAL
from app.services.mask_action_runtime_service import _write_audit, _write_outbox
from app.core.identity_context import current_identity
from app.services.command_idempotency import lock_and_replay, store_execution


class HrDeleteCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["onboarding", "qualification", "assignment"]
    entity_id: str = Field(min_length=1, max_length=120)
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")
    idempotency_key: str = Field(min_length=1, max_length=120)

    @field_validator("entity_id", "idempotency_key")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip() or value != value.strip():
            raise ValueError("non-empty canonical value required")
        return value



_SELECT = {
    "onboarding": text("SELECT encode(sha256(convert_to(to_jsonb(r)::text, 'UTF8')), 'hex') AS revision FROM domain_hr.onboarding_runs r WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
    "qualification": text("SELECT encode(sha256(convert_to(to_jsonb(r)::text, 'UTF8')), 'hex') AS revision FROM domain_hr.qualification_profiles r WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
    "assignment": text("SELECT encode(sha256(convert_to(to_jsonb(r)::text, 'UTF8')), 'hex') AS revision FROM domain_hr.training_assignments r WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
}
_DELETE = {
    "onboarding": text("DELETE FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant AND id=:id"),
    "qualification": text("DELETE FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id"),
    "assignment": text("DELETE FROM domain_hr.training_assignments WHERE tenant_id=:tenant AND id=:id"),
}


_SCREENS = {"onboarding": "personal/onboarding", "qualification": "personal/qualifikationen",
            "assignment": "personal/schulungen"}
_ENDPOINTS = {
    "onboarding": "/api/v1/training/onboarding/runs/{entity_id}/actions/loeschen",
    "qualification": "/api/v1/training/qualifications/{entity_id}/actions/loeschen",
    "assignment": "/api/v1/training/assignments/{entity_id}/actions/loeschen",
}


def delete_hr_row(db: Session, command: HrDeleteCommand, *, tenant: str) -> dict:
    """Use the verified request principal; caller commits or rolls back atomically."""
    principal = current_identity()
    if principal.tenant_id != tenant or not principal.roles.intersection(PERSONAL) or not principal.subject:
        raise HTTPException(403, "Verified subject, tenant and personnel write role required")
    name = f"hr.{command.kind}.delete.v1"
    identity_type = principal.claims.get("identity_type")
    if principal.claims.get("act") or (identity_type == "human" and principal.claims.get("agent_id")):
        raise HTTPException(403, "Delegated identity is not enabled for HR deletion")
    if identity_type != "human":
        if identity_type not in {"agent", "service"}:
            raise HTTPException(403, "Declared execution identity required")
        from app.services.mcp_write_capability import authorize_agent
        authorize_agent(principal, name, _ENDPOINTS[command.kind], _SCREENS[command.kind], "loeschen")
    actor = principal.subject
    payload = {"kind": command.kind, "entity_id": command.entity_id,
               "expected_revision": command.expected_revision}
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    replay = lock_and_replay(db, tenant=tenant, command=name, key=command.idempotency_key,
                             actor=actor, fingerprint=fingerprint)
    if replay is not None:
        return replay

    # Canonicalize timestamptz serialization in to_jsonb for every database session.
    db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
    params = {"tenant": tenant, "id": command.entity_id}
    row = db.execute(_SELECT[command.kind], params).mappings().first()
    if row is None:
        raise HTTPException(404, "HR record not found")
    if row["revision"] != command.expected_revision:
        raise HTTPException(409, "HR record changed; reload before deleting")
    deleted = db.execute(_DELETE[command.kind], params)
    if deleted.rowcount != 1:
        raise HTTPException(409, "HR record changed; reload before deleting")
    audit_id = _write_audit(db, tenant_id=tenant, action_key=name, entity_type=f"hr_{command.kind}",
                            entity_id=command.entity_id, audit_reason=None, idempotency_key=command.idempotency_key,
                            summary=f"HR {command.kind} deleted", performed_by=actor)
    outbox_id = _write_outbox(db, tenant_id=tenant, event_type=name, aggregate_id=command.entity_id,
                               payload={"id": command.entity_id, "tenant_id": tenant, "actor_id": actor,
                                        "audit_id": audit_id, "correlation_id": str(uuid4())})
    result = {"success": True, "replayed": False, "entity_id": command.entity_id,
              "auditEntryId": audit_id, "outboxEventId": outbox_id}
    store_execution(db, tenant=tenant, command=name, key=command.idempotency_key,
                    actor=actor, fingerprint=fingerprint, result=result)
    return result
