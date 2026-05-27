"""
Operational Governance API — Wave 4 AP4

Delegation Reviews, Export Reviews und Governance Audit-Trail.
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ....core.tenant import get_tenant_id
from ....core.operational_governance import (
    GovernanceAuditEntry,
    DelegationReviewEntry,
    ExportReviewEntry,
    OperationalGovernanceStore,
)

router = APIRouter(prefix="/governance", tags=["governance", "audit"])

_STORE: OperationalGovernanceStore = OperationalGovernanceStore()


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------

@router.get("/audit-trail", response_model=list[dict], summary="Audit trail abrufen")
async def get_audit_trail(
    governance_type: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle Governance-Audit-Einträge, optional nach Typ gefiltert."""
    entries = _STORE.get_audit_entries(tenant_id, governance_type)
    return [e.model_dump(mode="json") for e in entries]


@router.post("/audit-trail", response_model=dict, status_code=201, summary="Audit entry anlegen")
async def create_audit_entry(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt einen neuen Governance-Audit-Eintrag."""
    entry = GovernanceAuditEntry(
        entry_id=body.get("entry_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        governance_type=body.get("governance_type", ""),
        aggregate_type=body.get("aggregate_type", ""),
        aggregate_id=body.get("aggregate_id", ""),
        action=body.get("action", ""),
        actor_id=body.get("actor_id", ""),
        decision=body.get("decision", ""),
        reason=body.get("reason"),
        policy_ref=body.get("policy_ref"),
    )
    _STORE.audit_entries.append(entry)
    return entry.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Delegation Reviews
# ---------------------------------------------------------------------------

@router.get("/delegation-reviews", response_model=list[dict], summary="Delegation reviews auflisten")
async def list_delegation_reviews(
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle offenen Delegation-Reviews."""
    reviews = _STORE.get_pending_delegation_reviews(tenant_id)
    return [r.model_dump(mode="json") for r in reviews]


@router.post("/delegation-reviews", response_model=dict, status_code=201, summary="Delegation review anlegen")
async def create_delegation_review(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Legt eine neue Delegation-Prüfung an."""
    review = DelegationReviewEntry(
        review_id=body.get("review_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        agent_id=body.get("agent_id", ""),
        delegation_scope=body.get("delegation_scope", ""),
        requested_by=body.get("requested_by", ""),
        expires_at=body.get("expires_at"),
    )
    _STORE.delegation_reviews.append(review)
    return review.model_dump(mode="json")


@router.post("/delegation-reviews/{review_id}/approve", response_model=dict, summary="Delegation review genehmigen")
async def approve_delegation_review(
    review_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Genehmigt eine Delegation-Prüfung."""
    review = next(
        (r for r in _STORE.delegation_reviews
         if r.review_id == review_id and r.tenant_id == tenant_id),
        None,
    )
    if not review:
        raise HTTPException(status_code=404, detail=f"Delegation review {review_id} not found")
    reviewer_id = body.get("reviewer_id", "")
    review.approve(reviewer_id)
    return review.model_dump(mode="json")


@router.post("/delegation-reviews/{review_id}/reject", response_model=dict, summary="Delegation review ablehnen")
async def reject_delegation_review(
    review_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Lehnt eine Delegation-Prüfung ab."""
    review = next(
        (r for r in _STORE.delegation_reviews
         if r.review_id == review_id and r.tenant_id == tenant_id),
        None,
    )
    if not review:
        raise HTTPException(status_code=404, detail=f"Delegation review {review_id} not found")
    reviewer_id = body.get("reviewer_id", "")
    reason = body.get("reason", "")
    review.reject(reviewer_id, reason)
    return review.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Export Reviews
# ---------------------------------------------------------------------------

@router.get("/export-reviews", response_model=list[dict], summary="Export reviews auflisten")
async def list_export_reviews(
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle offenen Export-Reviews."""
    reviews = _STORE.get_pending_export_reviews(tenant_id)
    return [r.model_dump(mode="json") for r in reviews]


@router.post("/export-reviews", response_model=dict, status_code=201, summary="Export review anlegen")
async def create_export_review(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Legt eine neue Export-Prüfung an."""
    review = ExportReviewEntry(
        review_id=body.get("review_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        export_type=body.get("export_type", ""),
        target_zone=body.get("target_zone", "EU"),
        classification=body.get("classification", ""),
        requested_by=body.get("requested_by", ""),
        policy_violations=body.get("policy_violations", []),
    )
    _STORE.export_reviews.append(review)
    return review.model_dump(mode="json")
