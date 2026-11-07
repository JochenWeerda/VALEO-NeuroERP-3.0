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
from app.services.command_idempotency import lock_and_replay, store_execution


class DeactivateProfileV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile_id: str = Field(min_length=1, max_length=120)
    expected_active: Literal[True]
    idempotency_key: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=500)


def deactivate_profile(db: Session, tenant: str, command: DeactivateProfileV1) -> dict:
    """Lock, authorize, compare state, audit and replay; caller owns the transaction."""
    principal = current_identity()
    if principal.tenant_id != tenant or not principal.roles.intersection(LOGISTIK):
        raise HTTPException(403, "Versandprofil-Schreibrecht erforderlich")
    identity_type = principal.claims.get("identity_type")
    if principal.claims.get("act") or (identity_type == "human" and principal.claims.get("agent_id")):
        raise HTTPException(403, "Delegierte Identitaet ist nicht freigeschaltet")
    if identity_type != "human":
        if identity_type not in {"agent", "service"}:
            raise HTTPException(403, "Deklarierter Identitaetstyp erforderlich")
        from app.services.mcp_write_capability import authorize_agent
        authorize_agent(principal, "logistik.versandprofil.deactivate.v1",
                        "/api/v1/logistik/versand/profile/{entity_id}/actions/deactivate",
                        "logistik/versandprofile", "loeschen")
    actor = principal.subject
    if not actor or not command.idempotency_key.strip() or not command.reason.strip():
        raise HTTPException(422, "Akteur, Wiederholungsschluessel und Grund sind erforderlich")
    action = "logistik.versandprofil.deactivate.v1"
    fingerprint = hashlib.sha256(json.dumps(command.model_dump(exclude={"idempotency_key"}),
                                            sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    try:
        replayed = lock_and_replay(db, tenant=tenant, command=action, key=command.idempotency_key,
                                   actor=actor, fingerprint=fingerprint)
        if replayed is not None:
            return replayed
        row = db.execute(text("SELECT id, aktiv FROM domain_shared.versandprofile "
                              "WHERE tenant_id=:tenant AND id=:id FOR UPDATE"),
                         {"tenant": tenant, "id": command.profile_id}).mappings().first()
        if not row:
            raise HTTPException(404, "Versandprofil nicht gefunden")
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
        store_execution(db, tenant=tenant, command=action, key=command.idempotency_key,
                        actor=actor, fingerprint=fingerprint, result=result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "Versandprofil konnte nicht sicher deaktiviert werden") from exc
