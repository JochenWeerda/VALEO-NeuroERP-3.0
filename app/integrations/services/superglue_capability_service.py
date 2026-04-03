"""Capability bridge from Neuro broker plans to Superglue-backed integrations."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.integrations.services.superglue_execution_service import SuperglueExecutionService


class SuperglueCapabilityService:
    def __init__(self, execution_service: SuperglueExecutionService | None = None) -> None:
        self._execution_service = execution_service or SuperglueExecutionService()

    @staticmethod
    def can_handle(*, capability: str | None, action: str, parameters: dict[str, Any]) -> bool:
        if parameters.get("provider_key") == "superglue":
            return True
        if parameters.get("superglue_tool_id"):
            return True
        if capability and capability.startswith("superglue"):
            return True
        return action.startswith("superglue_")

    def execute_step(
        self,
        *,
        tenant_id: str,
        capability: str | None,
        action: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        tool_id = str(parameters.get("superglue_tool_id") or capability or action)
        target_kind = str(parameters.get("superglue_target_kind") or "external_api")
        execution_mode = str(parameters.get("superglue_execution_mode") or "execute")
        envelope = self._execution_service.execute_tool(
            tenant_id=tenant_id,
            correlation_id=str(parameters.get("correlation_id") or uuid4()),
            tool_id=tool_id,
            execution_mode=execution_mode,
            target_kind=target_kind,
            payload=parameters,
        )
        return envelope.model_dump(mode="json")
