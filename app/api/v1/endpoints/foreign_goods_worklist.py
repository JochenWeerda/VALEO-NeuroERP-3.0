"""Foreign-goods operator worklist API."""

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.foreign_goods_worklist_service import (
    ForeignGoodsError,
    ForeignGoodsWorklistService,
)

router = APIRouter(prefix="/foreign-goods", tags=["inventory", "foreign-goods"])


class TransferIn(BaseModel):
    warehouse_id: str = Field(min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=100)
    reason: str = Field(min_length=5, max_length=500)


class CompleteIn(BaseModel):
    remaining_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "foreign-goods-operator"


@router.get("", response_model=dict)
def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    owner_id: str | None = None,
    warehouse_id: str | None = None,
    status: str | None = None,
    query: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ForeignGoodsWorklistService(db, tenant_id).list_page(
        page=page,
        page_size=page_size,
        owner_id=owner_id,
        warehouse_id=warehouse_id,
        status=status,
        query=query,
    )


@router.get("/summary", response_model=dict)
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return ForeignGoodsWorklistService(db, tenant_id).summary()


def _handle(action) -> dict[str, Any]:  # noqa: ANN001
    try:
        return action()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ForeignGoodsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{foreign_goods_id}/transfer", response_model=dict)
def transfer(
    foreign_goods_id: str,
    body: TransferIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ForeignGoodsWorklistService(db, tenant_id)
    return _handle(
        lambda: service.transfer(
            foreign_goods_id,
            warehouse_id=body.warehouse_id,
            location=body.location,
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post("/{foreign_goods_id}/complete", response_model=dict)
def complete(
    foreign_goods_id: str,
    body: CompleteIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ForeignGoodsWorklistService(db, tenant_id)
    return _handle(
        lambda: service.complete(
            foreign_goods_id,
            remaining_quantity=body.remaining_quantity,
            actor=actor(request),
            reason=body.reason,
        )
    )
