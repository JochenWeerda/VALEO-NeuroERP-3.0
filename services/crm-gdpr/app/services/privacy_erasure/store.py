"""In-Memory-Persistenz für Tests / optionale Dev-Mode-Schicht."""

from __future__ import annotations

from uuid import UUID

from app.schemas.privacy_erasure import DecisionSnapshot
from app.services.privacy_erasure.constants import ACTION_LEGACY_HTTP_CRM_ERASURE
from app.services.privacy_erasure.protocol import AuditEntryDTO, IdempotentExecution


class InMemoryPrivacyRepository:
    """Kein SQL — prozesslokal (kein Cross-Process)."""

    def __init__(self) -> None:
        self._decisions: dict[UUID, DecisionSnapshot] = {}
        self._audits: list[AuditEntryDTO] = []
        self._executed: dict[str, IdempotentExecution] = {}

    def clear(self) -> None:
        self._decisions.clear()
        self._audits.clear()
        self._executed.clear()

    async def persist_evaluate(self, snap: DecisionSnapshot, audit: AuditEntryDTO) -> None:
        self._decisions[snap.decision_id] = snap
        self._audits.append(audit)

    async def remove_decision(self, decision_id: UUID) -> None:
        self._decisions.pop(decision_id, None)

    async def get_decision(self, decision_id: UUID) -> DecisionSnapshot | None:
        return self._decisions.get(decision_id)

    async def append_audit(self, entry: AuditEntryDTO) -> None:
        self._audits.append(entry)

    async def get_execution(self, key: str) -> IdempotentExecution | None:
        return self._executed.get(key)

    async def save_execution(self, key: str, exe: IdempotentExecution) -> None:
        self._executed[key] = exe

    async def has_successful_execute_for_request(
        self,
        *,
        tenant_id: str,
        request_id: UUID,
        subject_id: UUID,
        anonymize_only: bool,
        action: str = "",
    ) -> bool:
        use_action = action or ACTION_LEGACY_HTTP_CRM_ERASURE
        for exe in self._executed.values():
            if exe.tenant_id != tenant_id or exe.request_id != request_id:
                continue
            if exe.subject_id != subject_id:
                continue
            if exe.anonymize_only != anonymize_only:
                continue
            if exe.action != use_action:
                continue
            return True
        return False


