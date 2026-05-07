"""Orchestrierung Evaluate / Execute mit persistierbarem Audit."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.config.settings import settings
from app.schemas.privacy_erasure import (
    ErasureEvaluateRequest,
    ErasureEvaluateResponse,
    ErasureExecuteRequest,
    ErasureExecuteResponse,
)
from app.services.deletion_flow import orchestrate_erasure
from app.services.privacy_erasure.constants import (
    ACTION_LEGACY_HTTP_CRM_ERASURE,
    erasure_idempotency_key,
)
from app.services.privacy_erasure.policy_engine import build_decision_snapshot
from app.services.privacy_erasure.protocol import AuditEntryDTO, IdempotentExecution, PrivacyErasurePersistence

logger = logging.getLogger(__name__)


class PrivacyErasureError(Exception):
    """Fachlicher Fehler — Router mappt zu HTTP."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PrivacyErasureService:
    """Pro Request: frische `PrivacyErasureService`-Instanz mit passendem Repository."""

    def __init__(self, repo: PrivacyErasurePersistence) -> None:
        self._repo = repo

    async def has_successful_execute_for_request(
        self,
        *,
        tenant_id: str,
        request_id: UUID,
        subject_id: UUID,
        anonymize_only: bool,
    ) -> bool:
        """Für GDPR-Delete-Gate."""
        return await self._repo.has_successful_execute_for_request(
            tenant_id=tenant_id,
            request_id=request_id,
            subject_id=subject_id,
            anonymize_only=anonymize_only,
            action=ACTION_LEGACY_HTTP_CRM_ERASURE,
        )

    async def evaluate(
        self,
        *,
        request_id: UUID,
        subject_id: UUID,
        body: ErasureEvaluateRequest,
        correlation_id: str,
        actor_id: str | None,
    ) -> ErasureEvaluateResponse:
        snap = build_decision_snapshot(
            request_id=request_id,
            subject_id=subject_id,
            body=body,
            correlation_id=correlation_id,
        )
        dto = AuditEntryDTO(
            audit_id=uuid4(),
            request_id=snap.request_id,
            decision_id=snap.decision_id,
            tenant_id=snap.tenant_id,
            subject_ref=f"subject_hash:{snap.subject_id}",
            actor_id=actor_id,
            policy_version=snap.policy_version,
            decision=snap.decision,
            reason_codes=[r.code for r in snap.reasons],
            allowed_actions=list(snap.allowed_actions),
            blocked_actions=list(snap.blocked_actions),
            executed_action=None,
            result="evaluate_decision_persisted",
            correlation_id=correlation_id,
            timestamp=_utcnow(),
        )
        try:
            await self._repo.persist_evaluate(snap, dto)
        except Exception:
            logger.exception("persist_evaluate failed — Audit/Decision nicht atomar (ADR P5)")
            raise PrivacyErasureError(
                "Audit-Persistenz fehlgeschlagen; Decision nicht gültig (ADR P5)",
                status_code=503,
            ) from None

        return ErasureEvaluateResponse(
            request_id=request_id,
            tenant_id=snap.tenant_id,
            subject_id=subject_id,
            decision_id=snap.decision_id,
            decision=snap.decision,
            allowed_actions=snap.allowed_actions,
            blocked_actions=snap.blocked_actions,
            reasons=snap.reasons,
            policy_version=snap.policy_version,
            requires_manual_review=snap.requires_manual_review,
            correlation_id=correlation_id,
        )

    async def execute(
        self,
        *,
        request_id: UUID,
        subject_id: UUID,
        body: ErasureExecuteRequest,
        correlation_id: str,
    ) -> ErasureExecuteResponse:
        if settings.PRIVACY_EXECUTE_REQUIRE_ACTOR_ID and not (
            body.actor_id and body.actor_id.strip()
        ):
            raise PrivacyErasureError("actor_id ist für execute Pflicht", status_code=400)

        snap = await self._repo.get_decision(body.decision_id)
        if snap is None:
            raise PrivacyErasureError("decision_id unbekannt", status_code=404)
        if snap.tenant_id != body.tenant_id:
            raise PrivacyErasureError("tenant passt nicht zur Decision", status_code=403)
        if snap.request_id != request_id:
            raise PrivacyErasureError("request_id passt nicht zur Decision", status_code=400)
        if snap.subject_id != subject_id:
            raise PrivacyErasureError("subject_id passt nicht zur Decision", status_code=400)
        if _utcnow() > snap.expires_at:
            raise PrivacyErasureError("Decision abgelaufen — erneut evaluate aufrufen", status_code=409)
        if body.anonymize_only != snap.anonymize_only:
            raise PrivacyErasureError(
                "anonymize_only weicht von der Decision ab",
                status_code=400,
            )

        action = body.action.strip()
        if action not in snap.allowed_actions:
            await self._repo.append_audit(
                AuditEntryDTO(
                    audit_id=uuid4(),
                    request_id=request_id,
                    decision_id=body.decision_id,
                    tenant_id=body.tenant_id,
                    subject_ref=f"subject_hash:{subject_id}",
                    actor_id=body.actor_id,
                    policy_version=snap.policy_version,
                    decision=snap.decision,
                    reason_codes=["ACTION_NOT_ALLOWED"],
                    allowed_actions=list(snap.allowed_actions),
                    blocked_actions=list(snap.blocked_actions),
                    executed_action=action,
                    result="blocked",
                    correlation_id=correlation_id,
                    timestamp=_utcnow(),
                )
            )
            return ErasureExecuteResponse(
                request_id=request_id,
                tenant_id=body.tenant_id,
                decision_id=body.decision_id,
                action=action,
                result="blocked",
                policy_version=snap.policy_version,
                correlation_id=correlation_id,
                message="Aktion nicht in allowed_actions",
            )

        idem_key = erasure_idempotency_key(
            body.tenant_id,
            request_id,
            body.decision_id,
            action,
        )
        existing = await self._repo.get_execution(idem_key)
        if existing:
            return ErasureExecuteResponse(
                request_id=request_id,
                tenant_id=body.tenant_id,
                decision_id=body.decision_id,
                action=action,
                result="duplicate_idempotent_retry",
                policy_version=snap.policy_version,
                correlation_id=correlation_id,
                erasure_log=existing.erasure_log,
                message="Idempotenter Wiederholungsaufruf",
            )

        await self._repo.append_audit(
            AuditEntryDTO(
                audit_id=uuid4(),
                request_id=request_id,
                decision_id=body.decision_id,
                tenant_id=body.tenant_id,
                subject_ref=f"subject_hash:{subject_id}",
                actor_id=body.actor_id,
                policy_version=snap.policy_version,
                decision=snap.decision,
                reason_codes=[r.code for r in snap.reasons],
                allowed_actions=list(snap.allowed_actions),
                blocked_actions=list(snap.blocked_actions),
                executed_action=action,
                result="audit_pre_write_ok",
                correlation_id=correlation_id,
                timestamp=_utcnow(),
            )
        )

        if action != ACTION_LEGACY_HTTP_CRM_ERASURE:
            await self._repo.append_audit(
                AuditEntryDTO(
                    audit_id=uuid4(),
                    request_id=request_id,
                    decision_id=body.decision_id,
                    tenant_id=body.tenant_id,
                    subject_ref=f"subject_hash:{subject_id}",
                    actor_id=body.actor_id,
                    policy_version=snap.policy_version,
                    decision=snap.decision,
                    reason_codes=["ACTION_NOT_EXECUTABLE_IN_GATEWAY"],
                    allowed_actions=list(snap.allowed_actions),
                    blocked_actions=list(snap.blocked_actions),
                    executed_action=action,
                    result="failed",
                    correlation_id=correlation_id,
                    timestamp=_utcnow(),
                )
            )
            raise PrivacyErasureError(
                f"Aktion {action} ist in diesem Gateway noch nicht implementiert",
                status_code=501,
            )

        try:
            erasure_log = await orchestrate_erasure(
                tenant_id=body.tenant_id,
                contact_id=subject_id,
                anonymize_only=snap.anonymize_only,
            )
        except Exception:
            logger.exception("orchestrate_erasure failed during execute")
            await self._repo.append_audit(
                AuditEntryDTO(
                    audit_id=uuid4(),
                    request_id=request_id,
                    decision_id=body.decision_id,
                    tenant_id=body.tenant_id,
                    subject_ref=f"subject_hash:{subject_id}",
                    actor_id=body.actor_id,
                    policy_version=snap.policy_version,
                    decision=snap.decision,
                    reason_codes=["ORCHESTRATION_EXCEPTION"],
                    allowed_actions=list(snap.allowed_actions),
                    blocked_actions=list(snap.blocked_actions),
                    executed_action=action,
                    result="failed",
                    correlation_id=correlation_id,
                    timestamp=_utcnow(),
                )
            )
            raise PrivacyErasureError(
                "Execute fehlgeschlagen (Orchestrierung)",
                status_code=502,
            ) from None

        steps = erasure_log.get("steps") or []
        await self._repo.append_audit(
            AuditEntryDTO(
                audit_id=uuid4(),
                request_id=request_id,
                decision_id=body.decision_id,
                tenant_id=body.tenant_id,
                subject_ref=f"subject_hash:{subject_id}",
                actor_id=body.actor_id,
                policy_version=snap.policy_version,
                decision=snap.decision,
                reason_codes=[r.code for r in snap.reasons],
                allowed_actions=list(snap.allowed_actions),
                blocked_actions=list(snap.blocked_actions),
                executed_action=action,
                result="completed",
                correlation_id=correlation_id,
                timestamp=_utcnow(),
                extra={"http_steps_count": len(steps)},
            )
        )

        await self._repo.save_execution(
            idem_key,
            IdempotentExecution(
                request_id=request_id,
                tenant_id=body.tenant_id,
                subject_id=subject_id,
                decision_id=body.decision_id,
                action=action,
                anonymize_only=snap.anonymize_only,
                erasure_log=erasure_log,
                correlation_id=correlation_id,
                completed_at=_utcnow(),
            ),
        )

        return ErasureExecuteResponse(
            request_id=request_id,
            tenant_id=body.tenant_id,
            decision_id=body.decision_id,
            action=action,
            result="completed",
            policy_version=snap.policy_version,
            correlation_id=correlation_id,
            erasure_log=erasure_log,
        )


def clear_erasure_store_for_tests() -> None:
    """Leert den Memory-Persistenz-Singleton (nach Tests)."""
    reset_privacy_erasure_memory_repository()
