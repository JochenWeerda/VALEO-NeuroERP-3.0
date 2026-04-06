"""Execution service that wraps Superglue transport calls in the shared result envelope."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.adapters.superglue.tool_sync import validate_superglue_execution_request
from app.integrations.contracts import ExternalArtifactReference, ExternalResultEnvelope, ExternalResultError
from app.integrations.services.superglue_execution_journal import (
    append_execution_journal_entry,
    find_latest_execution_by_idempotency_key,
)
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
            if execution_mode == "execute" and not bool(
                payload.get("human_confirmation") or payload.get("approval_granted")
            ):
                raise ValueError("Superglue execute mode erfordert human_confirmation oder approval_granted")
            idempotency_key = str(payload.get("idempotency_key") or correlation_id)
            replay_entry = (
                find_latest_execution_by_idempotency_key(
                    tenant_id=tenant_id,
                    tool_id=normalized_tool_id,
                    idempotency_key=idempotency_key,
                )
                if execution_mode == "execute"
                else None
            )
            if replay_entry and replay_entry.get("result_status") in {"success", "pending"}:
                replay_finished_at = datetime.now(UTC)
                return ExternalResultEnvelope(
                    tenant_id=tenant_id,
                    correlation_id=correlation_id,
                    execution_mode=execution_mode,
                    target_kind=target_kind,
                    result_status=str(replay_entry.get("result_status")),
                    idempotency_key=idempotency_key,
                    replayed_from_correlation_id=str(replay_entry.get("correlation_id") or ""),
                    started_at=started_at,
                    finished_at=replay_finished_at,
                    artifacts=[
                        ExternalArtifactReference.model_validate(item)
                        for item in replay_entry.get("artifacts") or []
                        if isinstance(item, dict)
                    ],
                    metrics={"replayed": True},
                    payload={
                        "audit_metadata": {
                            "provider_key": "superglue",
                            "tool_id": normalized_tool_id,
                            "execution_mode": execution_mode,
                            "replayed_from_correlation_id": replay_entry.get("correlation_id"),
                        },
                        "replay": replay_entry,
                    },
                )
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
            normalized_run = normalize_superglue_run_result(result)
            upstream_status = str(normalized_run["upstream_status"])
            result_status = "pending" if upstream_status == "running" else "success"
            artifact_refs = extract_superglue_artifacts(normalized_run["result"])
            cost_cents = int(result.get("costCents") or payload.get("cost_cents") or 0)
            append_execution_journal_entry(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                tool_id=normalized_tool_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status=result_status,
                started_at=started_at,
                finished_at=finished_at,
                idempotency_key=idempotency_key,
                cost_cents=cost_cents,
                artifacts=[artifact.model_dump() for artifact in artifact_refs],
                detail={
                    "provider_key": "superglue",
                    "run_id": normalized_run["run_id"],
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
                    "run_id": normalized_run["run_id"],
                    "upstream_status": upstream_status,
                    "artifact_count": len(artifact_refs),
                },
            )
            return ExternalResultEnvelope(
                tenant_id=tenant_id,
                correlation_id=correlation_id,
                execution_mode=execution_mode,
                target_kind=target_kind,
                result_status=result_status,
                cost_cents=cost_cents,
                idempotency_key=idempotency_key,
                started_at=started_at,
                finished_at=finished_at,
                artifacts=artifact_refs,
                metrics={
                    "artifact_count": len(artifact_refs),
                    "upstream_status": upstream_status,
                },
                payload={
                    "upstream_run": result,
                    "result": normalized_run["result"],
                    "audit_metadata": {
                        "provider_key": "superglue",
                        "tool_id": normalized_tool_id,
                        "execution_mode": execution_mode,
                        "run_id": normalized_run["run_id"],
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
                detail={"target_kind": target_kind, "payload_keys": sorted(payload.keys())},
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
                idempotency_key=str(payload.get("idempotency_key") or correlation_id),
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
                idempotency_key=str(payload.get("idempotency_key") or correlation_id),
                started_at=started_at,
                finished_at=finished_at,
                metrics={"replayed": False},
                payload={
                    "audit_metadata": {
                        "provider_key": "superglue",
                        "tool_id": tool_id,
                        "execution_mode": execution_mode,
                    }
                },
                errors=[ExternalResultError(code="SUPERGLUE_EXECUTION_FAILED", message=str(exc), retryable=True)],
            )


def normalize_superglue_run_result(result: dict[str, Any]) -> dict[str, Any]:
    run_id = result.get("runId") or result.get("id")
    upstream_status = str(result.get("status", "success"))
    run_data = result.get("data")
    if not isinstance(run_data, dict):
        run_data = {}
    normalized_result = run_data.get("data")
    if normalized_result is None:
        normalized_result = run_data
    return {
        "run_id": run_id,
        "upstream_status": upstream_status,
        "result": normalized_result,
        "raw_data": run_data,
        "raw_result": result,
    }


def extract_superglue_artifacts(result: Any) -> list[ExternalArtifactReference]:
    if not isinstance(result, dict):
        return []
    artifact_candidates: list[dict[str, Any]] = []
    for key in ("artifacts", "files", "fileReferences"):
        value = result.get(key)
        if isinstance(value, list):
            artifact_candidates.extend(item for item in value if isinstance(item, dict))
    if not artifact_candidates:
        for value in result.values():
            if isinstance(value, dict):
                for key in ("artifacts", "files", "fileReferences"):
                    nested = value.get(key)
                    if isinstance(nested, list):
                        artifact_candidates.extend(item for item in nested if isinstance(item, dict))
    normalized: list[ExternalArtifactReference] = []
    for index, item in enumerate(artifact_candidates, start=1):
        uri = str(item.get("uri") or item.get("url") or "").strip()
        if not uri:
            continue
        normalized.append(
            ExternalArtifactReference(
                artifact_id=str(item.get("artifact_id") or item.get("id") or f"artifact-{index}"),
                label=str(item.get("label") or item.get("name") or f"artifact-{index}"),
                storage_backend=str(item.get("storage_backend") or item.get("backend") or "superglue"),
                uri=uri,
                content_type=str(item.get("content_type") or item.get("mime_type") or "application/octet-stream"),
                size_bytes=int(item.get("size_bytes") or item.get("size") or 0) or None,
                metadata={k: v for k, v in item.items() if k not in {"artifact_id", "id", "label", "name", "storage_backend", "backend", "uri", "url", "content_type", "mime_type", "size_bytes", "size"}},
            )
        )
    return normalized
