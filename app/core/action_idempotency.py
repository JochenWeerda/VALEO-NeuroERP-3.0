"""
Wave 17: Action-Idempotency-Store fuer den Process Kernel.

In-Memory, contract-first und bewusst ohne DB-Persistenz.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.action_execution import ActionExecutionResult


@dataclass(frozen=True)
class ActionIdempotencyRecord:
    tenant_id: str
    idempotency_key: str
    request_fingerprint: str
    result: ActionExecutionResult


@dataclass(frozen=True)
class ActionIdempotencyAuditEntry:
    """Kompakte Audit-Sicht auf eine idempotente Action-Ausfuehrung."""

    tenant_id: str
    idempotency_key: str
    execution_id: str
    command_name: str
    aggregate_type: str
    aggregate_id: str
    status: str
    result_source: str
    request_fingerprint: str
    requires_human_confirmation: bool
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "idempotency_key": self.idempotency_key,
            "execution_id": self.execution_id,
            "command_name": self.command_name,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": self.aggregate_id,
            "status": self.status,
            "result_source": self.result_source,
            "request_fingerprint": self.request_fingerprint,
            "requires_human_confirmation": self.requires_human_confirmation,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class ActionIdempotencyAuditTrail:
    """Audit-/Monitoring-Read-Model fuer den Idempotenz-Layer."""

    entry_count: int
    tenant_count: int
    command_count: int
    aggregate_count: int
    replay_count: int
    pending_approval_count: int
    status_counts: dict[str, int]
    result_source_counts: dict[str, int]
    entries: list[ActionIdempotencyAuditEntry]
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "entry_count": self.entry_count,
            "tenant_count": self.tenant_count,
            "command_count": self.command_count,
            "aggregate_count": self.aggregate_count,
            "replay_count": self.replay_count,
            "pending_approval_count": self.pending_approval_count,
            "status_counts": self.status_counts,
            "result_source_counts": self.result_source_counts,
            "entries": [entry.as_dict() for entry in self.entries],
            "schema_version": self.schema_version,
        }


class IdempotencyConflictError(ValueError):
    """Ein Idempotency-Key wurde fuer einen anderen Request wiederverwendet."""


class ActionIdempotencyStore:
    """Speichert Action-Execution-Resultate je Tenant und Idempotency-Key."""

    def __init__(self) -> None:
        self._records_by_key: dict[tuple[str, str], ActionIdempotencyRecord] = {}
        self._records_by_execution_id: dict[str, ActionIdempotencyRecord] = {}

    def get_by_key(
        self, tenant_id: str, idempotency_key: str
    ) -> ActionIdempotencyRecord | None:
        return self._records_by_key.get((tenant_id, idempotency_key))

    def get_by_execution_id(self, execution_id: str) -> ActionIdempotencyRecord | None:
        return self._records_by_execution_id.get(execution_id)

    def clear(self) -> None:
        self._records_by_key.clear()
        self._records_by_execution_id.clear()

    def remember(
        self,
        *,
        tenant_id: str,
        idempotency_key: str,
        request_fingerprint: str,
        result: ActionExecutionResult,
    ) -> ActionIdempotencyRecord:
        key = (tenant_id, idempotency_key)
        existing = self._records_by_key.get(key)
        if existing is not None:
            if existing.request_fingerprint != request_fingerprint:
                raise IdempotencyConflictError(
                    "IDEMPOTENCY_KEY_REUSED"
                )
            return existing

        record = ActionIdempotencyRecord(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            result=result,
        )
        self._records_by_key[key] = record
        self._records_by_execution_id[result.execution_id] = record
        return record

    def summary(self) -> dict[str, Any]:
        records = list(self._records_by_key.values())
        tenant_ids = {record.tenant_id for record in records}
        command_names = sorted({record.result.command_name for record in records})
        aggregate_types = sorted({record.result.aggregate_type for record in records})
        status_counts: dict[str, int] = {}
        result_source_counts: dict[str, int] = {}
        replay_count = 0
        pending_approval_count = 0
        for record in records:
            status_key = record.result.status.value
            source_key = record.result.result_source.value
            status_counts[status_key] = status_counts.get(status_key, 0) + 1
            result_source_counts[source_key] = result_source_counts.get(source_key, 0) + 1
            if source_key == "idempotent_replay":
                replay_count += 1
            if status_key == "pending_approval":
                pending_approval_count += 1
        return {
            "total_records": len(records),
            "tenant_count": len(tenant_ids),
            "execution_count": len(self._records_by_execution_id),
            "command_count": len(command_names),
            "aggregate_count": len(aggregate_types),
            "commands": command_names,
            "aggregates": aggregate_types,
            "status_counts": status_counts,
            "result_source_counts": result_source_counts,
            "replay_count": replay_count,
            "pending_approval_count": pending_approval_count,
        }

    def audit_feed(
        self,
        *,
        tenant_id: str | None = None,
        command_name: str | None = None,
        aggregate_type: str | None = None,
        limit: int | None = None,
    ) -> ActionIdempotencyAuditTrail:
        records = list(self._records_by_key.values())
        if tenant_id is not None:
            records = [record for record in records if record.tenant_id == tenant_id]
        if command_name is not None:
            records = [record for record in records if record.result.command_name == command_name]
        if aggregate_type is not None:
            records = [record for record in records if record.result.aggregate_type == aggregate_type]

        entries = [
            ActionIdempotencyAuditEntry(
                tenant_id=record.tenant_id,
                idempotency_key=record.idempotency_key,
                execution_id=record.result.execution_id,
                command_name=record.result.command_name,
                aggregate_type=record.result.aggregate_type,
                aggregate_id=record.result.aggregate_id,
                status=record.result.status.value,
                result_source=record.result.result_source.value,
                request_fingerprint=record.request_fingerprint,
                requires_human_confirmation=record.result.requires_human_confirmation,
            )
            for record in records
        ]
        if limit is not None:
            entries = entries[:limit]

        status_counts: dict[str, int] = {}
        result_source_counts: dict[str, int] = {}
        tenant_ids = {entry.tenant_id for entry in entries}
        command_names = {entry.command_name for entry in entries}
        aggregate_types = {entry.aggregate_type for entry in entries}
        replay_count = 0
        pending_approval_count = 0
        for entry in entries:
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1
            result_source_counts[entry.result_source] = result_source_counts.get(entry.result_source, 0) + 1
            if entry.result_source == "idempotent_replay":
                replay_count += 1
            if entry.status == "pending_approval":
                pending_approval_count += 1

        return ActionIdempotencyAuditTrail(
            entry_count=len(entries),
            tenant_count=len(tenant_ids),
            command_count=len(command_names),
            aggregate_count=len(aggregate_types),
            replay_count=replay_count,
            pending_approval_count=pending_approval_count,
            status_counts=status_counts,
            result_source_counts=result_source_counts,
            entries=entries,
        )


_STORE = ActionIdempotencyStore()


def get_action_idempotency_store() -> ActionIdempotencyStore:
    return _STORE
