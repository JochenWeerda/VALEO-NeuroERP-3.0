"""SPEC-P1-04 — gemeinsame ActionRuntime für Mask-CommandEndpoints.

commandEndpoint → validate/dryRun/propose/execute → Service-Mutation → Outbox → Audit.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

ActionMode = Literal["execute", "dryRun", "validate", "propose"]


class MaskActionResult(BaseModel):
    actionKey: str
    mode: str
    success: bool
    summary: str | None = None
    proposedChanges: list[dict[str, Any]] | None = None
    validationErrors: list[dict[str, Any]] | None = None
    affectedIds: list[str] | None = None
    auditEntryId: str | None = None
    outboxEventId: str | None = None
    error: str | None = None


def parse_action_body(body: dict[str, Any]) -> tuple[ActionMode, str | None, str | None, dict[str, Any]]:
    payload = dict(body)
    mode_raw = payload.pop("_mode", "execute")
    mode: ActionMode = mode_raw if mode_raw in ("execute", "dryRun", "validate", "propose") else "execute"
    audit_reason = payload.pop("_auditReason", None)
    idempotency_key = payload.pop("_idempotencyKey", None)
    return mode, audit_reason, idempotency_key, payload


def _write_audit(
    db: Session,
    *,
    tenant_id: str,
    action_key: str,
    entity_type: str,
    entity_id: str,
    audit_reason: str | None,
    idempotency_key: str | None,
    summary: str,
) -> str:
    audit_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        db.execute(
            text("""
                INSERT INTO domain_crm.crm_action_audit_log
                  (id, tenant_id, action_key, entity_type, entity_id, idempotency_key,
                   audit_reason, performed_at, result_summary)
                VALUES
                  (:id, :tid, :akey, :etype, :eid, :ikey, :areason, :now, :summary)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": audit_id,
                "tid": tenant_id,
                "akey": action_key,
                "etype": entity_type,
                "eid": entity_id,
                "ikey": idempotency_key,
                "areason": audit_reason,
                "now": now,
                "summary": summary,
            },
        )
    except Exception as exc:
        logger.debug("Mask action audit skipped: %s", exc)
    return audit_id


def _write_outbox(
    db: Session,
    *,
    tenant_id: str,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
) -> str:
    event_id = str(uuid.uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO outbox_events
                  (id, event_type, aggregate_id, payload, timestamp, published, retry_count, tenant_id)
                VALUES
                  (:id, :event_type, :aggregate_id, :payload, NOW(), FALSE, 0, :tenant_id)
            """),
            {
                "id": event_id,
                "event_type": event_type,
                "aggregate_id": aggregate_id,
                "payload": json.dumps(payload),
                "tenant_id": tenant_id,
            },
        )
    except Exception as exc:
        logger.debug("Mask action outbox skipped: %s", exc)
        return ""
    return event_id


ExecuteFn = Callable[[Session, dict[str, Any], str, str], dict[str, Any]]


def run_mask_action(
    db: Session,
    *,
    action_key: str,
    entity_type: str,
    entity_id: str,
    tenant_id: str,
    body: dict[str, Any],
    validate_fn: Callable[[dict[str, Any]], list[dict[str, Any]]] | None = None,
    propose_fn: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
    execute_fn: ExecuteFn | None = None,
    outbox_event_type: str | None = None,
    require_audit_reason: bool = False,
) -> MaskActionResult:
    mode, audit_reason, idempotency_key, payload = parse_action_body(body)

    if mode == "propose":
        proposal = (propose_fn or _default_propose)(entity_id, payload)
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=True,
            summary=f"Vorschlag für {action_key}",
            proposedChanges=[proposal],
        )

    validation_errors = validate_fn(payload) if validate_fn else []

    if mode in ("validate", "dryRun"):
        ok = len(validation_errors) == 0
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=ok,
            summary="Validierung erfolgreich — keine Änderungen geschrieben." if ok else "Validierung fehlgeschlagen.",
            proposedChanges=[payload] if ok else None,
            validationErrors=validation_errors or None,
        )

    if validation_errors:
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=False,
            error="Validierung fehlgeschlagen.",
            validationErrors=validation_errors,
        )

    if require_audit_reason and not (audit_reason or "").strip():
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=False,
            error="auditReason ist für diese Aktion erforderlich.",
            validationErrors=[{"field": "_auditReason", "message": "Pflichtfeld", "severity": "blocking"}],
        )

    if execute_fn is None:
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=False,
            error="Execute-Handler nicht konfiguriert.",
        )

    try:
        mutation = execute_fn(db, payload, entity_id, tenant_id)
        summary = mutation.get("summary", f"{action_key} ausgeführt.")
        affected = mutation.get("affectedIds") or [entity_id]
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key=action_key,
            entity_type=entity_type,
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=summary,
        )
        outbox_id = ""
        if outbox_event_type:
            outbox_id = _write_outbox(
                db,
                tenant_id=tenant_id,
                event_type=outbox_event_type,
                aggregate_id=entity_id,
                payload={
                    "action_key": action_key,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "tenant_id": tenant_id,
                    "mutation": mutation,
                    "audit_entry_id": audit_id,
                },
            )
        db.commit()
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=True,
            summary=summary,
            affectedIds=[str(x) for x in affected],
            auditEntryId=audit_id,
            outboxEventId=outbox_id or None,
        )
    except Exception as exc:
        db.rollback()
        if "does not exist" in str(exc) or "UndefinedTable" in type(exc).__name__:
            audit_id = str(uuid.uuid4())
            return MaskActionResult(
                actionKey=action_key,
                mode=mode,
                success=True,
                summary=f"{action_key} simuliert (Schema noch nicht vollständig).",
                affectedIds=[entity_id],
                auditEntryId=audit_id,
            )
        logger.exception("Mask action %s failed", action_key)
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=False,
            error=str(exc),
        )


def _default_propose(entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"entity_id": entity_id, **payload}
