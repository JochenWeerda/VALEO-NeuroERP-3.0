"""
Nachgelagerte Schreibpfade fuer ActionExecutionService (Wave-17/18).

Der CommandDispatcher validiert nur und liefert ACCEPTED — hier werden optionale
persistente Nebenwirkungen ausgefuehrt:

1) Audit-Zeile in domain_shared.neuro_step_audit_trace (best-effort, Tabelle optional)
2) Registrierte Domain-Mutationen pro command_name (fachliche DB-Updates)

Slice fuer neue Commands: register_domain_mutation(\"CreatePurchaseOrder\", handler) setzen.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.action_execution import (
    ActionExecutionRequest,
    ActionExecutionResult,
    ActionExecutionStatus,
)

logger = logging.getLogger(__name__)

DomainMutationHandler = Callable[[Session, ActionExecutionRequest, ActionExecutionResult], None]

_DOMAIN_MUTATIONS: dict[str, DomainMutationHandler] = {}


def register_domain_mutation(command_name: str, handler: DomainMutationHandler) -> None:
    """Registriert eine fachliche Mutation nach erfolgreichem Dispatch (ACCEPTED)."""
    _DOMAIN_MUTATIONS[command_name] = handler


def apply_accepted_action_mutations(
    db: Session,
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
) -> None:
    """
    Wird nur bei status ACCEPTED aufgerufen.
    Ein gemeinsames commit() schliesst Audit + Domain-Handler ab; Rollback bei Fehler.
    """
    if result.status != ActionExecutionStatus.ACCEPTED:
        return

    _persist_kernel_action_audit_no_commit(db, request, result)

    handler = _DOMAIN_MUTATIONS.get(request.command_name)
    if handler is not None:
        try:
            handler(db, request, result)
        except Exception as exc:
            logger.warning("Domain mutation %s failed: %s", request.command_name, exc)
            try:
                db.rollback()
            except Exception:
                pass
            return

    try:
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise


def _persist_kernel_action_audit_no_commit(
    db: Session,
    request: ActionExecutionRequest,
    result: ActionExecutionResult,
) -> None:
    """Append-only Audit in neuro_step_audit_trace (gleiches Muster wie NeuroToolBroker)."""
    rid = result.execution_id
    now = datetime.now(timezone.utc)
    detail = {
        "kind": "kernel_action_execute",
        "execution_id": rid,
        "command_name": request.command_name,
        "aggregate_type": request.aggregate_type,
        "aggregate_id": request.aggregate_id,
        "tenant_id": request.tenant_id,
        "idempotency_key": request.idempotency_key,
        "recorded_at": now.isoformat(),
    }
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_shared.neuro_step_audit_trace
                    (id, tenant_id, plan_id, step_id, step_order, action,
                     step_type, binding_kind, binding_target, step_status,
                     execution_detail, recorded_at)
                VALUES
                    (:id, :tid, :plan_id, :step_id, :step_order, :action,
                     :step_type, :binding_kind, :binding_target, :step_status,
                     :detail, :recorded_at)
                """
            ),
            {
                "id": str(uuid4()),
                "tid": request.tenant_id,
                "plan_id": f"action-exec:{rid}",
                "step_id": request.command_name,
                "step_order": 0,
                "action": "ActionExecute",
                "step_type": "command",
                "binding_kind": "kernel",
                "binding_target": request.command_name,
                "step_status": "accepted",
                "detail": json.dumps(detail),
                "recorded_at": now,
            },
        )
        try:
            from app.core.metrics import neuro_kernel_audit_inserts_total

            neuro_kernel_audit_inserts_total.inc()
        except Exception:
            pass
    except Exception as exc:
        logger.debug("Kernel action audit skipped: %s", exc)
        try:
            db.rollback()
        except Exception:
            pass
