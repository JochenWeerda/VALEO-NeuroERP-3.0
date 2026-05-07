"""Schemas für Evaluate/Execute nach ADR + Policy (Erasure Decision API)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# Erlaubte Decision-Werte (kanonisch mit Policy §6 / ADR §7)
ErasureDecision = Literal[
    "delete_allowed",
    "anonymize_allowed",
    "pseudonymize_allowed",
    "restrict_processing",
    "deny_due_to_retention",
    "deny_due_to_legal_hold",
    "deny_due_to_open_business_process",
    "deny_due_to_legal_claims",
    "manual_legal_review_required",
    "insufficient_information",
]


class ErasureReasonItem(BaseModel):
    """Normierter Grund (policy-konform, ohne Klartext-PII)."""

    code: str
    entity: str | None = None
    retention_until: str | None = None


class ErasureEvaluateRequest(BaseModel):
    """POST evaluate — zusätzlicher Kontext."""

    tenant_id: str = Field(..., description="Tenant (Pflicht)")
    anonymize_only: bool = Field(default=False, description="Nur anonymisieren, kein Kontakt-Hard-Delete")
    scope: Literal["crm_slice", "full_subject"] = Field(
        default="crm_slice",
        description="full_subject bleibt bis ERP-Discovery konservativ blockiert",
    )


class ErasureEvaluateResponse(BaseModel):
    """Mindestfelder entsprechend Policy §7."""

    request_id: UUID
    tenant_id: str
    subject_id: UUID
    decision_id: UUID
    decision: ErasureDecision
    allowed_actions: list[str]
    blocked_actions: list[str]
    reasons: list[ErasureReasonItem] = Field(default_factory=list)
    policy_version: str
    requires_manual_review: bool
    correlation_id: str


class ErasureExecuteRequest(BaseModel):
    """POST execute."""

    tenant_id: str
    decision_id: UUID
    action: str = Field(..., description="Muss in der gespeicherten Decision in allowed_actions stehen")
    anonymize_only: bool = Field(
        ...,
        description="Muss exakt zur Decision passen (Verteidigung gegen später geänderten Intent)",
    )
    actor_id: str | None = Field(default=None, description="Handelndes Subjekt (Pflicht sobald IAM angebunden)")


class ErasureExecuteResponse(BaseModel):
    """Antwort nach Execute-Versuch."""

    request_id: UUID
    tenant_id: str
    decision_id: UUID
    action: str
    result: Literal["completed", "failed", "blocked", "duplicate_idempotent_retry"]
    policy_version: str
    correlation_id: str
    erasure_log: dict | None = None
    message: str | None = None


class DecisionSnapshot(BaseModel):
    """Persistierbare Decision für Execute + Audit."""

    decision_id: UUID
    request_id: UUID
    tenant_id: str
    subject_id: UUID
    decision: ErasureDecision
    allowed_actions: list[str]
    blocked_actions: list[str]
    reasons: list[ErasureReasonItem]
    policy_version: str
    requires_manual_review: bool
    anonymize_only: bool
    correlation_id_evaluate: str
    created_at: datetime
    expires_at: datetime
