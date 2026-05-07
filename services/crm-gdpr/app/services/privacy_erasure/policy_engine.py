"""Policy-Auswertung für Erasure-Evaluate (verteilbar / später austauschbar)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.config.settings import settings
from app.schemas.privacy_erasure import DecisionSnapshot, ErasureDecision, ErasureEvaluateRequest, ErasureReasonItem
from app.services.privacy_erasure.constants import ACTION_LEGACY_HTTP_CRM_ERASURE


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _blocked_financial_and_audit() -> list[str]:
    return [
        "hard_delete",
        "delete_audit_event",
        "delete_financial_trace",
    ]


def build_decision_snapshot(
    *,
    request_id: UUID,
    subject_id: UUID,
    body: ErasureEvaluateRequest,
    correlation_id: str,
) -> DecisionSnapshot:
    """Erzeugt eine neue Decision (jedes evaluate liefert neue decision_id)."""
    decision_id = uuid4()
    ttl = settings.PRIVACY_DECISION_TTL_SECONDS
    expires_at = _utcnow() + timedelta(seconds=ttl)
    pv = settings.PRIVACY_POLICY_VERSION

    scope = body.scope
    legacy = settings.PRIVACY_ERASURE_LEGACY_CRM_EVALUATE

    if scope == "full_subject" or not legacy:
        reasons = [
            ErasureReasonItem(
                code="ERP_FIBU_SUBJECT_DISCOVERY_NOT_IMPLEMENTED",
                entity=None,
                retention_until=None,
            )
        ]
        if scope == "full_subject":
            reasons.insert(
                0,
                ErasureReasonItem(code="FULL_SUBJECT_SCOPE_REQUIRES_CROSS_DOMAIN_DISCOVERY"),
            )
        return DecisionSnapshot(
            decision_id=decision_id,
            request_id=request_id,
            tenant_id=body.tenant_id,
            subject_id=subject_id,
            decision="insufficient_information",
            allowed_actions=[],
            blocked_actions=_blocked_financial_and_audit()
            + [
                ACTION_LEGACY_HTTP_CRM_ERASURE,
            ],
            reasons=reasons,
            policy_version=pv,
            requires_manual_review=True,
            anonymize_only=body.anonymize_only,
            correlation_id_evaluate=correlation_id,
            created_at=_utcnow(),
            expires_at=expires_at,
        )

    # Übergang: nur crm_slice + Flag — explizit keine Retention/Legal-Hold-Prüfung
    blocked = ["delete_audit_event", "delete_financial_trace"]
    allowed = [
        ACTION_LEGACY_HTTP_CRM_ERASURE,
        "unlink_crm_profile",
        "anonymize_non_required_contact_fields",
    ]
    decision_lit: ErasureDecision = "anonymize_allowed" if body.anonymize_only else "delete_allowed"
    reasons = [
        ErasureReasonItem(
            code="LEGACY_CRM_SLICE_DEV_BYPASS",
            entity="contact",
        )
    ]

    return DecisionSnapshot(
        decision_id=decision_id,
        request_id=request_id,
        tenant_id=body.tenant_id,
        subject_id=subject_id,
        decision=decision_lit,
        allowed_actions=allowed,
        blocked_actions=blocked,
        reasons=reasons,
        policy_version=pv,
        requires_manual_review=False,
        anonymize_only=body.anonymize_only,
        correlation_id_evaluate=correlation_id,
        created_at=_utcnow(),
        expires_at=expires_at,
    )
