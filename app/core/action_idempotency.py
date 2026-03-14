"""
Wave 17: Action-Idempotency-Store fuer den Process Kernel.

In-Memory, contract-first und bewusst ohne DB-Persistenz.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.action_execution import ActionExecutionResult


@dataclass(frozen=True)
class ActionIdempotencyRecord:
    tenant_id: str
    idempotency_key: str
    request_fingerprint: str
    result: ActionExecutionResult


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


_STORE = ActionIdempotencyStore()


def get_action_idempotency_store() -> ActionIdempotencyStore:
    return _STORE
