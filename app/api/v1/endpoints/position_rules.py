"""
Commodity Position Rules API (No-Speculation Guard Regeln).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rbac import Permission, require_permission
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.domains.operations.models import PosPositionRule

router = APIRouter(prefix="/positions/rules", tags=["positions", "commodity", "rules"])


class PositionRuleIn(BaseModel):
    scope_type: str = Field(..., description="ARTICLE or GROUP")
    scope_id: str = Field(..., max_length=64)
    neg_tolerance_qty: float = Field(..., description="Negative Toleranz z.B. -50")
    max_short_days: int = Field(0, ge=0)
    yellow_threshold: Optional[float] = None
    red_threshold: Optional[float] = None
    approval_required: bool = False
    approval_role: Optional[str] = Field(None, max_length=30)
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None


class PositionRuleOut(BaseModel):
    rule_id: str
    scope_type: str
    scope_id: str
    neg_tolerance_qty: float
    max_short_days: int
    yellow_threshold: Optional[float] = None
    red_threshold: Optional[float] = None
    approval_required: bool
    approval_role: Optional[str] = None
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@router.get("", response_model=list[PositionRuleOut])
def list_rules(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
    scope_type: Optional[str] = None,
    scope_id: Optional[str] = None,
) -> list[PositionRuleOut]:
    q = db.query(PosPositionRule).filter(PosPositionRule.tenant_id == tenant_id)
    if scope_type:
        q = q.filter(PosPositionRule.scope_type == scope_type)
    if scope_id:
        q = q.filter(PosPositionRule.scope_id == scope_id)
    rows = q.order_by(PosPositionRule.scope_type, PosPositionRule.scope_id).all()
    return [
        PositionRuleOut(
            rule_id=r.rule_id,
            scope_type=r.scope_type,
            scope_id=r.scope_id,
            neg_tolerance_qty=float(r.neg_tolerance_qty or 0),
            max_short_days=int(r.max_short_days or 0),
            yellow_threshold=float(r.yellow_threshold) if r.yellow_threshold is not None else None,
            red_threshold=float(r.red_threshold) if r.red_threshold is not None else None,
            approval_required=bool(r.approval_required),
            approval_role=r.approval_role,
            active_from=r.active_from,
            active_to=r.active_to,
            tenant_id=r.tenant_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("", response_model=PositionRuleOut, status_code=201)
def create_rule(
    payload: PositionRuleIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_EDIT_RULES)),
) -> PositionRuleOut:
    if payload.scope_type not in ("ARTICLE", "GROUP"):
        raise HTTPException(status_code=400, detail="scope_type must be ARTICLE or GROUP")
    if payload.neg_tolerance_qty > 0:
        raise HTTPException(status_code=400, detail="neg_tolerance_qty must be <= 0")
    row = PosPositionRule(
        rule_id=uuid7(),
        tenant_id=tenant_id,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        neg_tolerance_qty=Decimal(str(payload.neg_tolerance_qty)),
        max_short_days=payload.max_short_days,
        yellow_threshold=Decimal(str(payload.yellow_threshold)) if payload.yellow_threshold is not None else None,
        red_threshold=Decimal(str(payload.red_threshold)) if payload.red_threshold is not None else None,
        approval_required=payload.approval_required,
        approval_role=payload.approval_role,
        active_from=payload.active_from,
        active_to=payload.active_to,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return PositionRuleOut(
        rule_id=row.rule_id,
        scope_type=row.scope_type,
        scope_id=row.scope_id,
        neg_tolerance_qty=float(row.neg_tolerance_qty or 0),
        max_short_days=int(row.max_short_days or 0),
        yellow_threshold=float(row.yellow_threshold) if row.yellow_threshold is not None else None,
        red_threshold=float(row.red_threshold) if row.red_threshold is not None else None,
        approval_required=bool(row.approval_required),
        approval_role=row.approval_role,
        active_from=row.active_from,
        active_to=row.active_to,
        tenant_id=row.tenant_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{rule_id}", response_model=PositionRuleOut)
def get_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_READ)),
) -> PositionRuleOut:
    row = (
        db.query(PosPositionRule)
        .filter(PosPositionRule.rule_id == rule_id, PosPositionRule.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Regel nicht gefunden")
    return PositionRuleOut(
        rule_id=row.rule_id,
        scope_type=row.scope_type,
        scope_id=row.scope_id,
        neg_tolerance_qty=float(row.neg_tolerance_qty or 0),
        max_short_days=int(row.max_short_days or 0),
        yellow_threshold=float(row.yellow_threshold) if row.yellow_threshold is not None else None,
        red_threshold=float(row.red_threshold) if row.red_threshold is not None else None,
        approval_required=bool(row.approval_required),
        approval_role=row.approval_role,
        active_from=row.active_from,
        active_to=row.active_to,
        tenant_id=row.tenant_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.put("/{rule_id}", response_model=PositionRuleOut)
def update_rule(
    rule_id: str,
    payload: PositionRuleIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_EDIT_RULES)),
) -> PositionRuleOut:
    row = (
        db.query(PosPositionRule)
        .filter(PosPositionRule.rule_id == rule_id, PosPositionRule.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Regel nicht gefunden")
    if payload.neg_tolerance_qty > 0:
        raise HTTPException(status_code=400, detail="neg_tolerance_qty must be <= 0")
    row.scope_type = payload.scope_type
    row.scope_id = payload.scope_id
    row.neg_tolerance_qty = Decimal(str(payload.neg_tolerance_qty))
    row.max_short_days = payload.max_short_days
    row.yellow_threshold = Decimal(str(payload.yellow_threshold)) if payload.yellow_threshold is not None else None
    row.red_threshold = Decimal(str(payload.red_threshold)) if payload.red_threshold is not None else None
    row.approval_required = payload.approval_required
    row.approval_role = payload.approval_role
    row.active_from = payload.active_from
    row.active_to = payload.active_to
    db.commit()
    db.refresh(row)
    return PositionRuleOut(
        rule_id=row.rule_id,
        scope_type=row.scope_type,
        scope_id=row.scope_id,
        neg_tolerance_qty=float(row.neg_tolerance_qty or 0),
        max_short_days=int(row.max_short_days or 0),
        yellow_threshold=float(row.yellow_threshold) if row.yellow_threshold is not None else None,
        red_threshold=float(row.red_threshold) if row.red_threshold is not None else None,
        approval_required=bool(row.approval_required),
        approval_role=row.approval_role,
        active_from=row.active_from,
        active_to=row.active_to,
        tenant_id=row.tenant_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.delete("/{rule_id}", status_code=200)
def delete_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission(Permission.POS_EDIT_RULES)),
) -> None:
    row = (
        db.query(PosPositionRule)
        .filter(PosPositionRule.rule_id == rule_id, PosPositionRule.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Regel nicht gefunden")
    db.delete(row)
    db.commit()
