"""Privacy Erasure: DB-Repository (PostgreSQL/async)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PrivacyErasureAudit, PrivacyErasureDecision, PrivacyErasureExecution
from app.schemas.privacy_erasure import DecisionSnapshot, ErasureDecision, ErasureReasonItem
from app.services.privacy_erasure.constants import ACTION_LEGACY_HTTP_CRM_ERASURE
from app.services.privacy_erasure.protocol import AuditEntryDTO, IdempotentExecution


def _snapshot_from_row(row: PrivacyErasureDecision) -> DecisionSnapshot:
    reasons_raw = row.reasons or []
    reasons = [ErasureReasonItem.model_validate(r) for r in reasons_raw]
    decision_str: ErasureDecision = row.decision  # type: ignore[assignment]
    return DecisionSnapshot(
        decision_id=row.id,
        request_id=row.gdpr_request_id,
        tenant_id=row.tenant_id,
        subject_id=row.subject_id,
        decision=decision_str,
        allowed_actions=list(row.allowed_actions or []),
        blocked_actions=list(row.blocked_actions or []),
        reasons=reasons,
        policy_version=row.policy_version,
        requires_manual_review=row.requires_manual_review,
        anonymize_only=row.anonymize_only,
        correlation_id_evaluate=row.correlation_id_evaluate,
        created_at=row.created_at,
        expires_at=row.expires_at,
    )


def _audit_row_from_dto(entry: AuditEntryDTO) -> PrivacyErasureAudit:
    return PrivacyErasureAudit(
        id=entry.audit_id,
        gdpr_request_id=entry.request_id,
        decision_id=entry.decision_id,
        tenant_id=entry.tenant_id,
        subject_ref=entry.subject_ref,
        actor_id=entry.actor_id,
        policy_version=entry.policy_version,
        decision=entry.decision,
        reason_codes=list(entry.reason_codes),
        allowed_actions=list(entry.allowed_actions),
        blocked_actions=list(entry.blocked_actions),
        executed_action=entry.executed_action,
        result=entry.result,
        correlation_id=entry.correlation_id,
        extra=entry.extra if entry.extra else None,
        created_at=entry.timestamp,
    )


class DbPrivacyErasureRepository:
    """Persistenz über SQLAlchemy (eine Session pro Request empfohlen)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def persist_evaluate(self, snap: DecisionSnapshot, audit: AuditEntryDTO) -> None:
        decision_row = PrivacyErasureDecision(
            id=snap.decision_id,
            gdpr_request_id=snap.request_id,
            tenant_id=snap.tenant_id,
            subject_id=snap.subject_id,
            decision=str(snap.decision),
            allowed_actions=list(snap.allowed_actions),
            blocked_actions=list(snap.blocked_actions),
            reasons=[r.model_dump(mode="json") for r in snap.reasons],
            policy_version=snap.policy_version,
            requires_manual_review=snap.requires_manual_review,
            anonymize_only=snap.anonymize_only,
            correlation_id_evaluate=snap.correlation_id_evaluate,
            created_at=snap.created_at,
            expires_at=snap.expires_at,
        )
        audit_row = _audit_row_from_dto(audit)
        async with self._session.begin():
            self._session.add(decision_row)
            self._session.add(audit_row)

    async def remove_decision(self, decision_id: UUID) -> None:
        async with self._session.begin():
            row = await self._session.get(PrivacyErasureDecision, decision_id)
            if row is not None:
                await self._session.delete(row)

    async def get_decision(self, decision_id: UUID) -> DecisionSnapshot | None:
        row = await self._session.get(PrivacyErasureDecision, decision_id)
        if row is None:
            return None
        return _snapshot_from_row(row)

    async def append_audit(self, entry: AuditEntryDTO) -> None:
        row = _audit_row_from_dto(entry)
        async with self._session.begin():
            self._session.add(row)

    async def get_execution(self, key: str) -> IdempotentExecution | None:
        row = await self._session.get(PrivacyErasureExecution, key)
        if row is None:
            return None
        return IdempotentExecution(
            request_id=row.gdpr_request_id,
            tenant_id=row.tenant_id,
            subject_id=row.subject_id,
            decision_id=row.decision_id,
            action=row.action,
            anonymize_only=row.anonymize_only,
            erasure_log=row.erasure_log,
            correlation_id=row.correlation_id,
            completed_at=row.completed_at,
        )

    async def save_execution(self, key: str, exe: IdempotentExecution) -> None:
        row = PrivacyErasureExecution(
            idempotency_key=key,
            tenant_id=exe.tenant_id,
            gdpr_request_id=exe.request_id,
            subject_id=exe.subject_id,
            decision_id=exe.decision_id,
            action=exe.action,
            anonymize_only=exe.anonymize_only,
            erasure_log=exe.erasure_log,
            correlation_id=exe.correlation_id,
            completed_at=exe.completed_at,
        )
        async with self._session.begin():
            self._session.merge(row)

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
        stmt = select(PrivacyErasureExecution.idempotency_key).where(
            PrivacyErasureExecution.tenant_id == tenant_id,
            PrivacyErasureExecution.gdpr_request_id == request_id,
            PrivacyErasureExecution.subject_id == subject_id,
            PrivacyErasureExecution.anonymize_only == anonymize_only,
            PrivacyErasureExecution.action == use_action,
        )
        res = await self._session.execute(stmt.limit(1))
        return res.scalar_one_or_none() is not None
