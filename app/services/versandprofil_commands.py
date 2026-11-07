"""Versandprofil-Deaktivierung: vorbereiteter transaktionaler Fachcommand v1.

Noch nicht als MCP-Capability freigeschaltet; alle Aufrufer muessen denselben
Vertrag und die bestehende Logistik-Bereichsrolle verwenden.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from uuid import uuid4
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import LOGISTIK
from app.core.identity_context import current_identity
from app.core.business_time import business_now
from app.domains.shared.events import IntegrationEvent
from app.infrastructure.eventbus.outbox import OutboxEvent
from app.services.mask_action_runtime_service import _write_audit


class DeactivateProfileV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: str = Field(min_length=1, max_length=120)
    expected_active: Literal[True]
    idempotency_key: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=500)


def deactivate_profile(db: Session, tenant: str, command: DeactivateProfileV1) -> dict:
    """Lock, authorize, compare identity/state, audit and replay atomically."""
    principal = current_identity()
    if principal.tenant_id != tenant or not principal.roles.intersection(LOGISTIK):
        raise HTTPException(403, "Versandprofil-Schreibrecht erforderlich")
    if principal.claims.get("identity_type") != "human" or principal.claims.get("act") or principal.claims.get("agent_id"):
        raise HTTPException(403, "Agentenfreigabe fuer diesen Command fehlt")
    actor = principal.subject
    if not actor or not command.idempotency_key.strip() or not command.reason.strip():
        raise HTTPException(422, "Akteur, Wiederholungsschluessel und Grund sind erforderlich")
    action = "logistik.versandprofil.deactivate.v1"
    fingerprint = hashlib.sha256(json.dumps(command.model_dump(exclude={"idempotency_key"}),
                                            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    lock = int.from_bytes(hashlib.sha256(json.dumps([tenant, action, command.idempotency_key]).encode()).digest()[:8],
                          "big", signed=True)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock})
        row = db.execute(text("SELECT id, aktiv FROM domain_shared.versandprofile "
                              "WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
                         {"tenant": tenant, "id": command.profile_id}).mappings().first()
        if not row:
            raise HTTPException(404, "Versandprofil nicht gefunden")
        previous = db.execute(text("SELECT actor_id, payload_hash, result FROM public.mcp_tool_executions "
                                   "WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key"),
                              {"tenant": tenant, "tool": action, "key": command.idempotency_key}).mappings().first()
        if previous:
            if previous["actor_id"] != actor or previous["payload_hash"] != fingerprint:
                raise HTTPException(409, "Wiederholungsschluessel gehoert zu einem anderen Auftrag")
            result = previous["result"]
            if isinstance(result, str):
                result = json.loads(result)
            db.commit()
            return {**result, "replayed": True}
        if row["aktiv"] is not True:
            raise HTTPException(409, "Versandprofil wurde bereits geaendert")
        db.execute(text("UPDATE domain_shared.versandprofile SET aktiv=false WHERE tenant_id=:tenant AND id=:id"),
                   {"tenant": tenant, "id": command.profile_id})
        audit_id = _write_audit(db, tenant_id=tenant, action_key=action, entity_type="versandprofil",
                                entity_id=command.profile_id, audit_reason=command.reason,
                                idempotency_key=command.idempotency_key, summary="Versandprofil deaktiviert",
                                performed_by=actor)
        now = business_now()
        event = IntegrationEvent(aggregate_id=command.profile_id, timestamp=now, event_type=action,
                                 tenant_id=tenant, payload={"profile_id": command.profile_id,
                                 "actor_id": actor, "audit_id": audit_id, "correlation_id": str(uuid4())})
        db.add(OutboxEvent(id=event.event_id, event_type=event.event_type, aggregate_id=command.profile_id,
                           tenant_id=tenant, timestamp=now, payload=json.dumps(asdict(event), default=str),
                           published=False))
        result = {"success": True, "profile_id": command.profile_id, "auditEntryId": audit_id, "replayed": False}
        db.execute(text("INSERT INTO public.mcp_tool_executions "
                        "(tenant_id, tool_name, idempotency_key, actor_id, payload_hash, result) "
                        "VALUES (:tenant, :tool, :key, :actor, :fingerprint, CAST(:result AS jsonb))"),
                   {"tenant": tenant, "tool": action, "key": command.idempotency_key, "actor": actor,
                    "fingerprint": fingerprint, "result": json.dumps(result)})
        db.commit()
        return result
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(503, "Versandprofil konnte nicht sicher deaktiviert werden") from exc
