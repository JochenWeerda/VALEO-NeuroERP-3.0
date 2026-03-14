from __future__ import annotations

import asyncio
import importlib
import logging
from datetime import datetime
from typing import Protocol, runtime_checkable

from app.domains.shared.process_events import (
    APInvoiceApprovalGranted,
    APInvoiceApprovalRequested,
    APInvoiceApproved,
    APInvoiceRejected,
)


logger = logging.getLogger(__name__)


def _resolve_outbox_publisher():
    return importlib.import_module("app.infrastructure.eventbus.outbox").OutboxPublisher


def _resolve_event_publisher():
    return importlib.import_module("app.domains.shared.events").get_event_publisher()


@runtime_checkable
class ApprovalOverrideResolutionLike(Protocol):
    rule_id: str | None


@runtime_checkable
class ApprovalStatusResponseLike(Protocol):
    status: str
    required_approvals: int
    current_approvals: int
    override_resolution: ApprovalOverrideResolutionLike


def build_ap_approval_outbox_event(
    *,
    action: str,
    invoice_id: str,
    tenant_id: str,
    actor: str,
    response: ApprovalStatusResponseLike,
):
    """Build the process event for AP approval workflow transitions."""
    rule_id = response.override_resolution.rule_id or "ap.approval.default"
    common = {
        "aggregate_id": invoice_id,
        "timestamp": datetime.utcnow(),
        "tenant_id": tenant_id,
        "workflow_instance_id": f"wf-ap-{invoice_id}",
    }

    if action == "approval_requested":
        return APInvoiceApprovalRequested(
            **common,
            invoice_id=invoice_id,
            requested_by=actor,
            required_approvals=response.required_approvals,
            rule_id=rule_id,
        )
    if action == "approval_approve":
        if response.status == "approved":
            return APInvoiceApproved(
                **common,
                invoice_id=invoice_id,
                approved_by=actor,
                rule_id=rule_id,
            )
        return APInvoiceApprovalGranted(
            **common,
            invoice_id=invoice_id,
            approved_by=actor,
            current_approvals=response.current_approvals,
            required_approvals=response.required_approvals,
            rule_id=rule_id,
        )
    if action == "approval_reject":
        return APInvoiceRejected(
            **common,
            invoice_id=invoice_id,
            rejected_by=actor,
            rule_id=rule_id,
        )
    return None


def store_ap_approval_event_in_outbox(
    db,
    *,
    action: str,
    invoice_id: str,
    tenant_id: str,
    actor: str,
    response: ApprovalStatusResponseLike,
) -> None:
    """Best-effort outbox write for AP approval events."""
    event = build_ap_approval_outbox_event(
        action=action,
        invoice_id=invoice_id,
        tenant_id=tenant_id,
        actor=actor,
        response=response,
    )
    if event is None:
        return

    async def _store() -> None:
        outbox = _resolve_outbox_publisher()(db, _resolve_event_publisher())
        await outbox.store_event(event, tenant_id=tenant_id)

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    try:
        if running_loop is None:
            asyncio.run(_store())
            return

        task = running_loop.create_task(_store())

        def _log_task_failure(completed_task: asyncio.Task[None]) -> None:
            try:
                completed_task.result()
            except Exception as exc:
                logger.warning("Outbox write failed in scheduled task (best-effort, continuing): %s", exc)

        task.add_done_callback(_log_task_failure)
    except Exception as exc:
        logger.warning("Outbox write failed (best-effort, continuing): %s", exc)
