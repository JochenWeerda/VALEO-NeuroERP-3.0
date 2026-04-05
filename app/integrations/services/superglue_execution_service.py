"""Execution service that wraps Superglue transport calls in the shared result envelope."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.tool_sync import validate_superglue_execution_request
from app.integrations.contracts import ExternalResultEnvelope, ExternalResultError
from app.integrations.services.superglue_execution_journal import append_execution_journal_entry
from app.integrations.services.superglue_quarantine import append_quarantine_entry
from app.integrations.services.superglue_secret_resolver import resolve_superglue_auth_token
from app.services.security_observability import security_observer


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
        try:
            tool_record = validate_superglue_execution_request(
                tool_id=tool_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
            )
            normalized_tool_id = tool_record.external_tool_id
            if execution_mode == "execute" and not settings.SUPERGLUE_EXECUTION_ENABLED:
                raise ValueError("Superglue execute mode ist aktuell deaktiviert")
            result = client.request(
                "POST",
                f"/v1/tools/{normalized_tool_id}/run",
                mode="rest",
                json={
                    "inputs": payload,
                    "options": {
                        "async": execution_mode == "execute",
                        "traceId": correlation_id,
                    },
                },
            )
            finished_at = datetime.now(UTC)
            upstream_status = str(result.get("status", "success"))
            result_status = "pending" if upstream_status == "running" else "success"
            append_execution_journal_entry(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                tool_id=normalized_tool_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status=result_status,
                started_at=started_at,
                finished_at=finished_at,
                detail={
                    "provider_key": "superglue",
                    "run_id": result.get("runId"),
                    "upstream_status": upstream_status,
                },
            )
            security_observer.record_event(
                category="superglue_execution",
                outcome="accepted" if result_status == "pending" else "executed",
                severity="info",
                message=f"Superglue tool '{normalized_tool_id}' erfolgreich ausgefuehrt",
                tenant_id=tenant_id,
                details={
                    "execution_mode": execution_mode,
                    "target_kind": target_kind,
                    "run_id": result.get("runId"),
                    "upstream_status": upstream_status,
                },
            )
            return ExternalResultEnvelope(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status=result_status,
                started_at=started_at,
                finished_at=finished_at,
                payload={
                    "upstream_run": result,
                    "audit_metadata": {
                        "provider_key": "superglue",
                        "tool_id": normalized_tool_id,
                        "execution_mode": execution_mode,
                        "run_id": result.get("runId"),
                    },
                },
            )
        except Exception as exc:
            finished_at = datetime.now(UTC)
            append_quarantine_entry(
                tenant_id=tenant_id,
                tool_id=tool_id,
                execution_mode=execution_mode,
                outcome="degraded",
                reason=str(exc),
                correlation_id=correlation_id,
                detail={"target_kind": target_kind},
            )
            append_execution_journal_entry(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                tool_id=tool_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status="error",
                started_at=started_at,
                finished_at=finished_at,
                detail={"provider_key": "superglue", "error": str(exc)},
            )
            security_observer.record_event(
                category="superglue_execution",
                outcome="degraded",
                severity="warning",
                message=f"Superglue tool '{tool_id}' ist degradiert",
                tenant_id=tenant_id,
                details={"execution_mode": execution_mode, "target_kind": target_kind, "error": str(exc)},
            )
            return ExternalResultEnvelope(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status="error",
                started_at=started_at,
                finished_at=finished_at,
                payload={
                    "audit_metadata": {
                        "provider_key": "superglue",
                        "tool_id": tool_id,
                        "execution_mode": execution_mode,
                    }
                },
                errors=[ExternalResultError(code="SUPERGLUE_EXECUTION_FAILED", message=str(exc), retryable=True)],
            )
