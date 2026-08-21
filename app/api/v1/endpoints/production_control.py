"""General production control worklist API."""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.production_control_service import ProductionControlError, ProductionControlService

router = APIRouter(prefix="/production-control", tags=["production-control", "agrar", "inventory"])


class OperationIn(BaseModel):
    operation_type: Literal["production_order", "mill_run", "stock_transfer", "batch_posting", "rework"]
    source_type: str = Field(min_length=1, max_length=80)
    source_ref: str = Field(min_length=1, max_length=120)
    source_number: str = Field(min_length=1, max_length=120)
    source_route: str | None = None
    work_center: str | None = None
    article_ref: str | None = None
    article_name: str | None = None
    batch_ref: str | None = None
    quantity: float | None = None
    unit: str | None = None
    assigned_user: str | None = None
    planned_at: datetime | None = None
    notes: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class TransitionIn(ReasonIn):
    target: Literal["queued", "released", "running", "paused", "completed", "cancelled", "rework"]


def _actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "production-operator"


@router.post("/operations", response_model=dict, status_code=201)
def register(body: OperationIn, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return ProductionControlService(db, tenant_id).register(body.model_dump(), actor=_actor(request))
    except ProductionControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/operations", response_model=dict)
def list_operations(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
                    operation_type: str | None = None, status: str | None = None,
                    work_center: str | None = None, assigned_user: str | None = None,
                    q: str | None = None, sort: str = "planned_at", sort_dir: Literal["asc", "desc"] = "asc",
                    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return ProductionControlService(db, tenant_id).list_page(page=page, page_size=page_size,
        operation_type=operation_type, status=status, work_center=work_center, assigned_user=assigned_user,
        q=q, sort=sort, sort_dir=sort_dir)


@router.get("/summary", response_model=dict)
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return ProductionControlService(db, tenant_id).summary()


@router.post("/sync", response_model=dict)
def sync(body: ReasonIn, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return ProductionControlService(db, tenant_id).sync_production_orders(actor=_actor(request), reason=body.reason)


@router.post("/operations/{operation_id}/transition", response_model=dict)
def transition(operation_id: str, body: TransitionIn, request: Request,
               db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, str]:
    try:
        return ProductionControlService(db, tenant_id).transition(operation_id, target=body.target,
            actor=_actor(request), reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductionControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/operations/{operation_id}/audit", response_model=list[dict])
def audit(operation_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, Any]]:
    return ProductionControlService(db, tenant_id).audit(operation_id)
