"""SPEC-P1-04 — gemeinsame ActionRuntime für Mask-CommandEndpoints.

commandEndpoint → validate/dryRun/propose/execute → Service-Mutation → Outbox → Audit.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Literal

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
    if mode_raw not in ("execute", "dryRun", "validate", "propose"):
        raise ValueError("Unbekannter Aktionsmodus.")
    mode: ActionMode = mode_raw
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
    db.execute(
        text("""
            INSERT INTO domain_crm.crm_action_audit_log
              (id, tenant_id, action_key, entity_type, entity_id, idempotency_key,
               audit_reason, performed_at, result_summary)
            VALUES
              (:id, :tid, :akey, :etype, :eid, :ikey, :areason, :now, :summary)
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
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey=action_key, mode="invalid", success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[{"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}],
        )

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
        logger.exception("Mask action %s failed", action_key)
        return MaskActionResult(
            actionKey=action_key,
            mode=mode,
            success=False,
            error="Aktion konnte nicht gespeichert werden. Es wurde kein Erfolg bestaetigt.",
        )


CheckFn = Callable[[Session, dict[str, Any], str, str], Awaitable[list[dict[str, Any]]]]
DelegateFn = Callable[[Session, dict[str, Any], str, str], Awaitable[str]]


def _fehlertext(exc: Exception) -> str:
    detail = getattr(exc, "detail", None)
    if isinstance(detail, dict):
        return str(detail.get("error") or detail.get("detail") or detail)
    return str(detail if detail is not None else exc)


async def run_delegated_mask_action(
    db: Session,
    *,
    action_key: str,
    entity_type: str,
    entity_id: str,
    tenant_id: str,
    body: dict[str, Any],
    check_fn: CheckFn,
    delegate_fn: DelegateFn,
    outbox_event_type: str,
    require_audit_reason: bool = False,
) -> MaskActionResult:
    """Eine Mask-Aktion, die an den **echten Fachweg** delegiert.

    Bis zum 07.10.2026 bauten die Mask-Aktionen nur ein Ergebnis-Dict und meldeten
    Erfolg — Audit und Ereignis bestaetigten Freigaben, die nie stattfanden. Hier
    gilt:

    * ``check_fn`` liest die Datenbank (Objekt da, Zustand passt) und laeuft in
      **jedem** Modus. Ein Trockenlauf meldet so, was der Fachweg ablehnen wuerde,
      und schreibt nichts.
    * Bei ``execute`` liegen Audit- und Outbox-Zeile schon in der Sitzung, wenn der
      Fachweg laeuft; dessen eigener Commit schreibt Mutation, Audit und Ereignis
      **zusammen**. Scheitert er, wird alles zurueckgerollt, und die Antwort nennt
      den fachlichen Grund.
    * ``delegate_fn`` liefert die Zusammenfassung des Geschehenen.
    """
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey=action_key, mode="invalid", success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[{"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}],
        )

    try:
        fehler = await check_fn(db, payload, entity_id, tenant_id)
    except Exception as exc:  # noqa: BLE001 — Pruefung als Antwort, nicht als 500
        db.rollback()
        fehler = [{"field": "_entity", "message": _fehlertext(exc), "severity": "blocking"}]
    # Lesen ist erledigt; die Sitzung beginnt fuer den Fachweg neu.
    db.rollback()

    if mode != "execute":
        ok = not fehler
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=ok,
            summary="Pruefung erfolgreich — keine Aenderungen geschrieben." if ok else "Pruefung fehlgeschlagen.",
            proposedChanges=[payload] if ok else None,
            validationErrors=fehler or None,
            error=None if ok else fehler[0]["message"],
        )

    if fehler:
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False,
            error=fehler[0]["message"], validationErrors=fehler,
        )

    if require_audit_reason and not (audit_reason or "").strip():
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False,
            error="auditReason ist für diese Aktion erforderlich.",
            validationErrors=[{"field": "_auditReason", "message": "Pflichtfeld", "severity": "blocking"}],
        )

    try:
        audit_id = _write_audit(
            db, tenant_id=tenant_id, action_key=action_key, entity_type=entity_type,
            entity_id=entity_id, audit_reason=audit_reason, idempotency_key=idempotency_key,
            summary=f"{action_key} angestossen",
        )
        outbox_id = _write_outbox(
            db, tenant_id=tenant_id, event_type=outbox_event_type, aggregate_id=entity_id,
            payload={
                "action_key": action_key, "entity_type": entity_type, "entity_id": entity_id,
                "tenant_id": tenant_id, "audit_entry_id": audit_id, "payload": payload,
            },
        )
        summary = await delegate_fn(db, payload, entity_id, tenant_id)
        # Fachwege, die selbst committen, haben Audit und Ereignis schon mitgenommen;
        # fuer die anderen schliesst dieser Commit die Einheit.
        db.commit()
    except Exception as exc:  # noqa: BLE001 — der Grund geht an die Maske
        db.rollback()
        logger.warning("Mask-Aktion %s fuer %s abgelehnt: %s", action_key, entity_id, exc)
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False, error=_fehlertext(exc),
        )

    return MaskActionResult(
        actionKey=action_key, mode=mode, success=True, summary=summary,
        affectedIds=[entity_id], auditEntryId=audit_id, outboxEventId=outbox_id,
    )


def _default_propose(entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"entity_id": entity_id, **payload}
