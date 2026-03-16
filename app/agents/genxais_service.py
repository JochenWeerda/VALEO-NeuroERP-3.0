"""Application service for productive GENXAIS business workflows and assistants."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from .genxais import (
    GenxaisCapability,
    get_genxais_capabilities,
    get_productive_genxais_capabilities,
)
from .langgraph_server import get_bestellvorschlag_workflow, invoke_bestellvorschlag, resume_bestellvorschlag
from .workflows.compliance_copilot import check_compliance
from .workflows.skonto_optimizer import optimize_skonto


class GENXAISService:
    """Facade for productive GENXAIS capabilities inside the application core."""

    def list_capabilities(self, *, productive_only: bool = False) -> tuple[GenxaisCapability, ...]:
        if productive_only:
            return get_productive_genxais_capabilities()
        return get_genxais_capabilities()

    async def trigger_bestellvorschlag(self, tenant_id: str) -> dict[str, Any]:
        correlation_id = str(uuid4())
        result = await invoke_bestellvorschlag(tenant_id, correlation_id)
        status = "completed" if result.get("order_id") else "pending_approval"
        return {
            "workflow_id": correlation_id,
            "correlation_id": correlation_id,
            "status": status,
            "started_at": datetime.utcnow().isoformat(),
            "capability_key": "bestellvorschlag_assistant",
        }

    async def approve_bestellvorschlag(
        self,
        workflow_id: str,
        approved: bool,
        rejection_reason: str | None = None,
    ) -> dict[str, Any]:
        result = await resume_bestellvorschlag(workflow_id, approved, rejection_reason)
        return {
            "workflow_id": workflow_id,
            "approved": approved,
            "order_id": result.get("order_id"),
            "status": "completed" if result.get("order_id") else "rejected",
            "capability_key": "bestellvorschlag_assistant",
        }

    async def get_bestellvorschlag_status(self, workflow_id: str) -> dict[str, Any]:
        workflow = get_bestellvorschlag_workflow()
        config = {"configurable": {"thread_id": workflow_id}}
        state = await workflow.aget_state(config)
        if state is None:
            raise ValueError(f"Workflow {workflow_id} not found")
        approval_record = state.values.get("approval_record") or {}
        if state.values.get("order_id"):
            status = "completed"
        elif approval_record.get("decision") == "ABGELEHNT":
            status = "rejected"
        elif (state.values.get("approval_requirement") or {}).get("requires_human_approval"):
            status = "pending_approval"
        else:
            status = "running"
        return {
            "workflow_id": workflow_id,
            "status": status,
            "proposal": state.values.get("proposal"),
            "approval_requirement": state.values.get("approval_requirement"),
            "approval_record": state.values.get("approval_record"),
            "command_result": state.values.get("command_result"),
            "order_id": state.values.get("order_id"),
            "created_at": state.values.get("created_at"),
            "capability_key": "bestellvorschlag_assistant",
        }

    async def run_skonto_assistant(
        self,
        *,
        available_cash: Decimal,
        payment_date: datetime | None = None,
    ) -> dict[str, Any]:
        result = await optimize_skonto(available_cash=available_cash, payment_date=payment_date)
        result["capability_key"] = "finance_skonto_assistant"
        return result

    async def run_compliance_copilot(
        self,
        *,
        entity_type: str,
        entity_id: str,
        entity_data: dict[str, Any],
    ) -> dict[str, Any]:
        result = await check_compliance(entity_type=entity_type, entity_id=entity_id, entity_data=entity_data)
        result["capability_key"] = "compliance_copilot"
        return result


_genxais_service: GENXAISService | None = None


def get_genxais_service() -> GENXAISService:
    global _genxais_service
    if _genxais_service is None:
        _genxais_service = GENXAISService()
    return _genxais_service
