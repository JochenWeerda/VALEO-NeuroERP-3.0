"""Execution service that wraps Superglue transport calls in the shared result envelope."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.contracts import ExternalResultEnvelope
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token


class SuperglueExecutionService:
    def __init__(self, client: SuperglueClient | None = None) -> None:
        self._client = client

    def execute_tool(
        self,
        *,
        tenant_id: str,
        correlation_id: str,
        tool_id: str,
        execution_mode: str,
        target_kind: str,
        payload: dict[str, Any],
    ) -> ExternalResultEnvelope:
        client = self._client or SuperglueClient(auth_token=resolve_superglue_auth_token(tenant_id))
        started_at = datetime.now(UTC)
        result = client.request("POST", f"/api/tools/{tool_id}/execute", mode="rest", json=payload)
        finished_at = datetime.now(UTC)
        return ExternalResultEnvelope(
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            execution_mode=execution_mode,
            target_kind=target_kind,
            result_status="success",
            started_at=started_at,
            finished_at=finished_at,
            payload=result,
        )
