"""
Operative Governance — Wave 4 AP4

Delegation Reviews, Export Reviews und Governance Audit-Trail.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class GovernanceReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class GovernanceAuditEntry(BaseModel):
    """Audit-Eintrag für eine Governance-Entscheidung (Delegation, Export, Evidence)."""
    entry_id: str
    tenant_id: str
    governance_type: str    # "delegation" | "export" | "evidence"
    aggregate_type: str
    aggregate_id: str
    action: str             # z.B. "delegation_granted", "export_approved", "evidence_verified"
    actor_id: str
    decision: str           # "approved" | "rejected" | "overridden"
    reason: Optional[str] = None
    policy_ref: Optional[str] = None   # z.B. "ExportGovernancePolicy.rule_id"
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1


class DelegationReviewEntry(BaseModel):
    """Offene oder abgeschlossene Prüfung einer Agenten-Delegation."""
    review_id: str
    tenant_id: str
    agent_id: str
    delegation_scope: str   # z.B. "APPROVE_INVOICE"
    requested_by: str
    status: GovernanceReviewStatus = GovernanceReviewStatus.PENDING
    reviewer_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    schema_version: int = 1

    def approve(self, reviewer_id: str) -> None:
        self.status = GovernanceReviewStatus.APPROVED
        self.reviewer_id = reviewer_id
        self.reviewed_at = datetime.now(timezone.utc)

    def reject(self, reviewer_id: str, reason: str = "") -> None:
        self.status = GovernanceReviewStatus.REJECTED
        self.reviewer_id = reviewer_id
        self.reviewed_at = datetime.now(timezone.utc)


class ExportReviewEntry(BaseModel):
    """Prüfung eines geplanten Datenexports gegen Governance-Regeln."""
    review_id: str
    tenant_id: str
    export_type: str        # z.B. "financial_report", "customer_data"
    target_zone: str        # z.B. "EU", "non_EU"
    classification: str     # z.B. "gobd_relevant", "gdpr_personal"
    status: GovernanceReviewStatus = GovernanceReviewStatus.PENDING
    requested_by: str
    policy_violations: list[str] = Field(default_factory=list)
    schema_version: int = 1


class OperationalGovernanceStore(BaseModel):
    """In-Memory-Store für operative Governance-Einträge."""
    audit_entries: list[GovernanceAuditEntry] = Field(default_factory=list)
    delegation_reviews: list[DelegationReviewEntry] = Field(default_factory=list)
    export_reviews: list[ExportReviewEntry] = Field(default_factory=list)
    schema_version: int = 1

    def get_audit_entries(
        self, tenant_id: str, governance_type: Optional[str] = None
    ) -> list[GovernanceAuditEntry]:
        entries = [e for e in self.audit_entries if e.tenant_id == tenant_id]
        if governance_type:
            entries = [e for e in entries if e.governance_type == governance_type]
        return entries

    def get_pending_delegation_reviews(self, tenant_id: str) -> list[DelegationReviewEntry]:
        return [
            r for r in self.delegation_reviews
            if r.tenant_id == tenant_id and r.status == GovernanceReviewStatus.PENDING
        ]

    def get_pending_export_reviews(self, tenant_id: str) -> list[ExportReviewEntry]:
        return [
            r for r in self.export_reviews
            if r.tenant_id == tenant_id and r.status == GovernanceReviewStatus.PENDING
        ]
