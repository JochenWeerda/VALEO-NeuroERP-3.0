"""Zuweisungsbestätigung für LKW-Disposition.

Ablauf: Prüfung (rein) → Tabelle domain_logistics.tours/tour_stops → Outbox
``logistik.tour.created`` (Ist-Publisher, Soll-Annotation assignment_confirmed).
Kontraktmengenbuchung geschieht nicht auf diesem Weg.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.services.disposition_assignment_repository import (
    AssignmentPersistError,
    persist_assignment,
)
from app.services.disposition_assignment_validation import (
    ASSIGNMENT_CONFIRMED_EVENT,
    AssignmentContext,
    AssignmentDecision,
    validate_assignment,
)

logger = logging.getLogger(__name__)


def confirm_assignment(
    ctx: AssignmentContext,
    *,
    db: Session | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Validiert vor jeder Persistenz. Drop bucht keine Menge."""
    decision: AssignmentDecision = validate_assignment(ctx)
    payload: dict[str, Any] = {
        "ok": decision.ok,
        "issues": [
            {"code": issue.code, "message": issue.message, "severity": issue.severity}
            for issue in decision.issues
        ],
        "event": decision.event,
        "persist_allowed": decision.persist_allowed,
        "quantity_posted": False,
        "dry_run": dry_run,
        "order_id": ctx.order_id,
        "resource_id": ctx.resource_id,
        "tenant_id": ctx.tenant_id,
        "abruf_id": ctx.abruf_id,
        "tour_id": None,
        "stop_id": None,
    }
    if not decision.ok or dry_run or db is None:
        payload["outbox_event_id"] = None
        payload["persisted"] = False
        return payload

    try:
        stored = persist_assignment(db, ctx)
        from app.services.mask_action_runtime_service import _write_outbox

        event_id = _write_outbox(
            db,
            tenant_id=ctx.tenant_id,
            event_type=ASSIGNMENT_CONFIRMED_EVENT,
            aggregate_id=stored.tour_id,
            payload={
                "id": stored.tour_id,
                "tenant_id": ctx.tenant_id,
                "order_id": ctx.order_id,
                "stop_id": stored.stop_id,
                "quantity_posted": False,
                "abruf_id": ctx.abruf_id,
            },
        )
        db.commit()
    except AssignmentPersistError as exc:
        db.rollback()
        payload["ok"] = False
        payload["persist_allowed"] = False
        payload["event"] = None
        payload["persisted"] = False
        payload["outbox_event_id"] = None
        payload["issues"] = [{"code": exc.code, "message": exc.message, "severity": "blocking"}]
        return payload
    except Exception:
        db.rollback()
        raise

    payload["outbox_event_id"] = event_id
    payload["persisted"] = True
    payload["tour_id"] = stored.tour_id
    payload["stop_id"] = stored.stop_id
    logger.info(
        "disposition assignment persisted tour=%s stop=%s order=%s event=%s",
        stored.tour_id,
        stored.stop_id,
        ctx.order_id,
        event_id,
    )
    return payload
