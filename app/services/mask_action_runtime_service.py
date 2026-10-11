"""SPEC-P1-04 — gemeinsame ActionRuntime für Mask-CommandEndpoints.

commandEndpoint → validate/dryRun/propose/execute → Service-Mutation → Outbox → Audit.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Literal

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
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


_FORBIDDEN_MASK_IDENTITY_KEYS = frozenset({"tenant_id", "mandanten_id"})


def parse_action_body(body: dict[str, Any]) -> tuple[ActionMode, str | None, str | None, dict[str, Any]]:
    payload = dict(body)
    mode_raw = payload.pop("_mode", "execute")
    if mode_raw not in ("execute", "dryRun", "validate", "propose"):
        raise ValueError("Unbekannter Aktionsmodus.")
    mode: ActionMode = mode_raw
    audit_reason = payload.pop("_auditReason", None)
    idempotency_key = payload.pop("_idempotencyKey", None)
    # Mandanten-ID nur aus Token/Depends — nie aus Masken-Payload mutieren.
    for key in _FORBIDDEN_MASK_IDENTITY_KEYS:
        payload.pop(key, None)
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
    performed_by: str | None = None,
) -> str:
    """``performed_by``: die Kennung aus dem geprueften Token. Nur wer sie uebergibt, schreibt
    die Spalte (Migration ``audit_urheber_20261011``); alle anderen Wege bleiben, wie sie waren."""
    audit_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    if performed_by is not None:
        db.execute(
            text("""
                INSERT INTO domain_crm.crm_action_audit_log
                  (id, tenant_id, action_key, entity_type, entity_id, idempotency_key,
                   audit_reason, performed_at, result_summary, performed_by)
                VALUES
                  (:id, :tid, :akey, :etype, :eid, :ikey, :areason, :now, :summary, :durch)
            """),
            {"id": audit_id, "tid": tenant_id, "akey": action_key, "etype": entity_type, "eid": entity_id,
             "ikey": idempotency_key, "areason": audit_reason, "now": now, "summary": summary,
             "durch": performed_by},
        )
        return audit_id
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


def frueherer_lauf(
    db: Session, *, tenant_id: str, action_key: str, entity_type: str, idempotency_key: str,
) -> dict[str, Any] | None:
    """Sperrt den Idempotenzschluessel bis zum Ende der Transaktion und liefert den frueheren Lauf.

    Die Sperre legt zwei gleichzeitige Laeufe hintereinander: Der zweite wartet, bis der erste
    abgeschlossen ist, und findet dann dessen Auditeintrag.
    """
    db.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:s, 0))"),
        {"s": f"mask_action:{tenant_id}:{entity_type}:{action_key}:{idempotency_key}"},
    )
    zeile = db.execute(
        text(
            "SELECT id, entity_id FROM domain_crm.crm_action_audit_log "
            "WHERE tenant_id = :t AND action_key = :a AND entity_type = :e AND idempotency_key = :k "
            "ORDER BY performed_at LIMIT 1"
        ),
        {"t": tenant_id, "a": action_key, "e": entity_type, "k": idempotency_key},
    ).mappings().first()
    return dict(zeile) if zeile else None


def wiederholter_auftrag(
    db: Session,
    *,
    tenant_id: str,
    action_key: str,
    entity_type: str,
    idempotency_key: Any,
    mode: str,
    entity_id: str | None = None,
) -> MaskActionResult | None:
    """Die Antwort auf einen Schluessel, der schon gelaufen ist — sonst ``None``.

    Bis zum 11.10.2026 wurde ``_idempotencyKey`` nur ins Audit geschrieben: Wer einen Auftrag
    nach einem Zeitlimit mit demselben Schluessel wiederholte, fuehrte ihn ein zweites Mal aus.
    Jeder Schreibweg ruft das hier am Beginn seiner Transaktion; ohne Schluessel aendert sich
    nichts. ``entity_id`` uebergibt, wer auf einem bestehenden Objekt arbeitet: Derselbe
    Schluessel fuer ein anderes Objekt ist kein Erfolg, sondern ein Fehler des Aufrufers.
    """
    schluessel = str(idempotency_key).strip() if idempotency_key is not None else ""
    if not schluessel:
        return None
    frueher = frueherer_lauf(
        db, tenant_id=tenant_id, action_key=action_key, entity_type=entity_type, idempotency_key=schluessel,
    )
    if frueher is None:
        return None
    db.rollback()
    if entity_id is not None and str(frueher["entity_id"]) != str(entity_id):
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False,
            error="Dieser Idempotenzschluessel gehoert zu einem frueheren Auftrag fuer ein anderes Objekt; "
                  "nichts ausgefuehrt.",
            validationErrors=[{"field": "_idempotencyKey", "message": "Schluessel bereits verwendet",
                               "severity": "blocking"}],
        )
    return MaskActionResult(
        actionKey=action_key, mode=mode, success=True,
        summary="Dieser Auftrag wurde bereits ausgefuehrt — nichts erneut ausgefuehrt.",
        affectedIds=[str(frueher["entity_id"])], auditEntryId=str(frueher["id"]),
    )


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


CheckFn = Callable[[Session, dict[str, Any], str, str], Awaitable[list[dict[str, Any]]]]
DelegateFn = Callable[[Session, dict[str, Any], str, str], Awaitable[str]]


def _fehlertext(exc: Exception) -> str:
    if isinstance(exc, SQLAlchemyError) or (isinstance(exc, HTTPException) and exc.status_code >= 500):
        return "Aktion konnte nicht gespeichert oder geprueft werden. Es wurde kein Erfolg bestaetigt."
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
    * Bei ``execute`` liegen Audit- und Outbox-Zeile in der aeusseren Sitzung.
      Der Fachweg erhaelt eine eigene SAVEPOINT-Session. Sein innerer Commit
      gibt nur den Savepoint frei; erst die Runtime committet die gesamte Einheit.
      Auch bei einer Ablehnung nach innerem Commit wird alles zurueckgerollt.
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

    # Eine fehlende Begruendung ist ein Formfehler der Anfrage — vor jeder Datenbank.
    if mode == "execute" and require_audit_reason and not (audit_reason or "").strip():
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False,
            error="auditReason ist für diese Aktion erforderlich.",
            validationErrors=[{"field": "_auditReason", "message": "Pflichtfeld", "severity": "blocking"}],
        )

    # Eine Wiederholung wird beantwortet, bevor der Zustand geprueft wird: Nach dem ersten Lauf
    # passt er nicht mehr ("schon freigegeben"), und das waere die falsche Antwort.
    if mode == "execute":
        try:
            wiederholt = wiederholter_auftrag(
                db, tenant_id=tenant_id, action_key=action_key, entity_type=entity_type,
                idempotency_key=idempotency_key, mode=mode, entity_id=entity_id,
            )
        except Exception as exc:  # noqa: BLE001 — kein Erfolg ohne gepruefte Wiederholung
            db.rollback()
            return MaskActionResult(actionKey=action_key, mode=mode, success=False, error=_fehlertext(exc))
        if wiederholt is not None:
            return wiederholt

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

    try:
        # Noch einmal in der Schreibtransaktion: Die Sperre von oben endete mit der Pruefung.
        wiederholt = wiederholter_auftrag(
            db, tenant_id=tenant_id, action_key=action_key, entity_type=entity_type,
            idempotency_key=idempotency_key, mode=mode, entity_id=entity_id,
        )
        if wiederholt is not None:
            return wiederholt
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
        # Ein Fachweg darf seinen Savepoint committen, nie die aeussere Einheit.
        # Der produktive get_db-Vertrag liefert eine SQLAlchemy-Session.
        if isinstance(db, Session):
            with Session(bind=db.connection(), join_transaction_mode="create_savepoint") as delegate_db:
                summary = await delegate_fn(delegate_db, payload, entity_id, tenant_id)
                delegate_db.commit()  # Auch Fachwege ohne eigenen Commit geben den Savepoint frei.
        else:
            # Kleine In-Memory-Adapter in den isolierten Vertragspruefungen.
            summary = await delegate_fn(db, payload, entity_id, tenant_id)
        db.commit()
    except Exception as exc:  # noqa: BLE001 — der Grund geht an die Maske
        db.rollback()
        logger.warning("Mask-Aktion %s fuer %s abgelehnt: %s", action_key, entity_id, _fehlertext(exc))
        return MaskActionResult(
            actionKey=action_key, mode=mode, success=False, error=_fehlertext(exc),
        )

    return MaskActionResult(
        actionKey=action_key, mode=mode, success=True, summary=summary,
        affectedIds=[entity_id], auditEntryId=audit_id, outboxEventId=outbox_id,
    )

