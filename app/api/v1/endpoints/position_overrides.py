"""
Commodity Position Override API (Freigabe anfordern / genehmigen / ablehnen).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import Permission, require_permission
from app.core.tenant import get_tenant_id
from app.domains.operations.models import PosPositionOverride
from app.services.position_guard_service import PositionGuardService

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/positions/overrides", tags=["positions", "commodity", "overrides"])


class OverrideRequestIn(BaseModel):
    branch_id: Optional[str] = None
    article_id: str = Field(..., max_length=64)
    period_key: str = Field(..., max_length=20)
    reason: str = Field(..., min_length=1)
    related_doc_type: Optional[str] = None
    related_doc_id: Optional[str] = None


class OverrideApproveIn(BaseModel):
    comment: str = Field(..., min_length=1)
    valid_days: int = Field(14, ge=1, le=365)


class OverrideRejectIn(BaseModel):
    comment: str = Field(..., min_length=1)


class OverrideOut(BaseModel):
    override_id: str
    branch_id: Optional[str] = None
    article_id: str
    period_key: str
    requested_by: Optional[str] = None
    requested_at: Optional[datetime] = None
    reason: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    comment: Optional[str] = None
    related_doc_type: Optional[str] = None
    related_doc_id: Optional[str] = None
    tenant_id: str
    created_at: Optional[datetime] = None


def _override_to_out(r: PosPositionOverride) -> OverrideOut:
    return OverrideOut(
        override_id=r.override_id,
        branch_id=r.branch_id,
        article_id=r.article_id,
        period_key=r.period_key,
        requested_by=r.requested_by,
        requested_at=r.requested_at,
        reason=r.reason,
        status=r.status,
        approved_by=r.approved_by,
        approved_at=r.approved_at,
        valid_until=r.valid_until,
        comment=r.comment,
        related_doc_type=r.related_doc_type,
        related_doc_id=r.related_doc_id,
        tenant_id=r.tenant_id,
        created_at=r.created_at,
    )


@router.get("", response_model=list[OverrideOut], summary="Overrides auflisten")
def list_overrides(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    status_filter: Optional[str] = Query(None, description="REQUESTED, APPROVED, REJECTED"),
    article_id: Optional[str] = None,
    period_key: Optional[str] = None,
) -> list[OverrideOut]:
    q = db.query(PosPositionOverride).filter(PosPositionOverride.tenant_id == tenant_id)
    if status_filter:
        q = q.filter(PosPositionOverride.status == status_filter)
    if article_id:
        q = q.filter(PosPositionOverride.article_id == article_id)
    if period_key:
        q = q.filter(PosPositionOverride.period_key == period_key)
    rows = q.order_by(PosPositionOverride.requested_at.desc()).limit(200).all()
    return [_override_to_out(r) for r in rows]


@router.post("", response_model=OverrideOut, status_code=201, summary="Override request")
def request_override(
    payload: OverrideRequestIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    requested_by: str = Body(None, embed=True),
    _: bool = Depends(require_permission(Permission.POS_REQUEST_OVERRIDE)),
) -> OverrideOut:
    guard = PositionGuardService(db)
    row = guard.request_override(
        tenant_id=tenant_id,
        branch_id=payload.branch_id,
        article_id=payload.article_id,
        period_key=payload.period_key,
        requested_by=requested_by or "api",
        reason=payload.reason,
        related_doc_type=payload.related_doc_type,
        related_doc_id=payload.related_doc_id,
    )
    db.commit()
    db.refresh(row)
    return _override_to_out(row)


@router.post("/{override_id}/approve", response_model=OverrideOut, summary="Override genehmigen")
def approve_override(
    override_id: str,
    payload: OverrideApproveIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    approved_by: str = Body(None, embed=True),
    _: bool = Depends(require_permission(Permission.POS_APPROVE_OVERRIDE)),
) -> OverrideOut:
    guard = PositionGuardService(db)
    row = guard.approve_override(
        override_id=override_id,
        tenant_id=tenant_id,
        approved_by=approved_by or "api",
        comment=payload.comment,
        valid_days=payload.valid_days,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Override nicht gefunden oder nicht im Status REQUESTED")
    db.commit()
    db.refresh(row)
    return _override_to_out(row)


@router.post("/{override_id}/reject", response_model=OverrideOut, summary="Override ablehnen")
def reject_override(
    override_id: str,
    payload: OverrideRejectIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    rejected_by: str = Body(None, embed=True),
    _: bool = Depends(require_permission(Permission.POS_APPROVE_OVERRIDE)),
) -> OverrideOut:
    guard = PositionGuardService(db)
    row = guard.reject_override(
        override_id=override_id,
        tenant_id=tenant_id,
        rejected_by=rejected_by or "api",
        comment=payload.comment,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Override nicht gefunden oder nicht im Status REQUESTED")
    db.commit()
    db.refresh(row)
    return _override_to_out(row)


@router.get("/{override_id}", response_model=OverrideOut, summary="Override abrufen")
def get_override(
    override_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
) -> OverrideOut:
    row = (
        db.query(PosPositionOverride)
        .filter(PosPositionOverride.override_id == override_id, PosPositionOverride.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Override nicht gefunden")
    return _override_to_out(row)
