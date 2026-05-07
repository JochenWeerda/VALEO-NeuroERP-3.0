"""Abstraktion Privacy-Erasure-Persistenz (Memory / DB)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from app.schemas.privacy_erasure import DecisionSnapshot


@dataclass
class IdempotentExecution:
    """Ergebnis einer erfolgreichen Execute-Operation."""

    request_id: UUID
    tenant_id: str
    subject_id: UUID
    decision_id: UUID
    action: str
    anonymize_only: bool
    erasure_log: dict | None
    correlation_id: str
    completed_at: datetime


@dataclass
class AuditEntryDTO:
    """Transportobjekt für Audit-Zeilen."""

    audit_id: UUID
    request_id: UUID
    decision_id: UUID | None
    tenant_id: str
    subject_ref: str
    actor_id: str | None
    policy_version: str
    decision: str | None
    reason_codes: list[str]
    allowed_actions: list[str]
    blocked_actions: list[str]
    executed_action: str | None
    result: str
    correlation_id: str
    timestamp: datetime
    extra: dict[str, Any] = field(default_factory=dict)


class PrivacyErasurePersistence(Protocol):
    async def persist_evaluate(self, snap: DecisionSnapshot, audit: AuditEntryDTO) -> None: ...

    async def remove_decision(self, decision_id: UUID) -> None: ...

    async def get_decision(self, decision_id: UUID) -> DecisionSnapshot | None: ...

    async def append_audit(self, entry: AuditEntryDTO) -> None: ...

    async def get_execution(self, key: str) -> IdempotentExecution | None: ...

    async def save_execution(self, key: str, exe: IdempotentExecution) -> None: ...

    async def has_successful_execute_for_request(
        self,
        *,
        tenant_id: str,
        request_id: UUID,
        subject_id: UUID,
        anonymize_only: bool,
        action: str = "",
    ) -> bool: ...
