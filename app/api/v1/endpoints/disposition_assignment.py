"""LKW-Dispositions-Zuweisung — eigener Router, nicht Tourenplanung-Godfile.

POST validiert vor Persistenz. Mengenbuchung ist hier ausgeschlossen.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.services.disposition_assignment_service import confirm_assignment
from app.services.disposition_assignment_validation import (
    AssignmentContext,
    permissions_from_roles,
)

router = APIRouter(prefix="/logistik/disposition", tags=["logistik", "disposition"])


class AssignmentIn(BaseModel):
    order_id: str
    resource_id: str
    resource_tenant_id: Optional[str] = None
    planned_start: datetime
    planned_end: datetime
    window_start: datetime
    window_end: datetime
    order_weight_kg: Decimal
    assigned_weight_kg: Decimal = Decimal("0")
    resource_capacity_kg: Decimal
    drop_quantity: Decimal
    contract_remaining_qty: Decimal
    allow_overdelivery: bool = False
    expected_version: Optional[int] = None
    current_version: Optional[int] = None
    approval_required: bool = False
    approval_granted: bool = False
    posts_quantity: bool = False
    dry_run: bool = False
    abruf_id: Optional[str] = None


class AssignmentOut(BaseSchema):
    ok: bool
    issues: list[dict[str, Any]]
    event: Optional[str] = None
    persist_allowed: bool = False
    quantity_posted: bool = False
    dry_run: bool = False
    persisted: bool = False
    outbox_event_id: Optional[str] = None
    order_id: str
    resource_id: str
    tenant_id: str
    tour_id: Optional[str] = None
    stop_id: Optional[str] = None
    abruf_id: Optional[str] = None


def _tenant(x_tenant_id: Optional[str] = Header(None)) -> str:
    if not x_tenant_id or not x_tenant_id.strip():
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    return x_tenant_id.strip()


def _actor_permissions(request: Request) -> frozenset[str]:
    claims = getattr(request.state, "token_claims", None)
    if not isinstance(claims, dict):
        return permissions_from_roles(())
    from app.auth.oidc import extract_roles
    roles = [str(role) for role in extract_roles(claims)]
    extra = claims.get("permissions")
    if isinstance(extra, list):
        roles.extend(str(item) for item in extra)
    return permissions_from_roles(roles)


@router.post(
    "/assignments",
    response_model=AssignmentOut,
    summary="Tourzuweisung prüfen und bestätigen (ohne Mengenbuchung)",
)
def create_assignment(
    body: AssignmentIn,
    request: Request,
    tenant_id: str = Depends(_tenant),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    ctx = AssignmentContext(
        tenant_id=tenant_id,
        actor_tenant_id=tenant_id,
        actor_permissions=_actor_permissions(request),
        order_id=body.order_id,
        resource_id=body.resource_id,
        resource_tenant_id=body.resource_tenant_id or tenant_id,
        planned_start=body.planned_start,
        planned_end=body.planned_end,
        window_start=body.window_start,
        window_end=body.window_end,
        order_weight_kg=body.order_weight_kg,
        assigned_weight_kg=body.assigned_weight_kg,
        resource_capacity_kg=body.resource_capacity_kg,
        drop_quantity=body.drop_quantity,
        contract_remaining_qty=body.contract_remaining_qty,
        allow_overdelivery=body.allow_overdelivery,
        expected_version=body.expected_version,
        current_version=body.current_version,
        approval_required=body.approval_required,
        approval_granted=body.approval_granted,
        posts_quantity=body.posts_quantity,
        abruf_id=body.abruf_id,
    )
    result = confirm_assignment(ctx, db=None if body.dry_run else db, dry_run=body.dry_run)
    if not result["ok"]:
        raise HTTPException(status_code=422, detail=result)
    return result
