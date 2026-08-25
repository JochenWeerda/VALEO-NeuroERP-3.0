"""Inventory auxiliary batch API."""

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.inventory_bundle_schemas import (
    AuxiliaryBatchCreatedOut,
    AuxiliaryBatchPageOut,
    AuxiliarySummaryOut,
    AuxiliaryTransitionOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.inventory_auxiliary_service import InventoryAuxiliaryError, InventoryAuxiliaryService

router = APIRouter(prefix="/inventory/auxiliary", tags=["inventory", "inventory-auxiliary"])


class BatchIn(BaseModel):
    inventory_count_id: str = Field(min_length=1)
    batch_type: Literal["count_sheet", "count_import", "control_run", "preliminary_valuation", "opening_balance"]
    reason: str = Field(min_length=5, max_length=500)
    import_rows: list[dict[str, Any]] | None = None
    declared_hash: str | None = Field(default=None, min_length=64, max_length=64)


class TransitionIn(BaseModel):
    target: Literal["reviewed", "approved", "applied", "rejected"]
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "inventory-operator"


@router.post("/batches", response_model=AuxiliaryBatchCreatedOut, status_code=201)
def create_batch(body: BatchIn, request: Request, db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return InventoryAuxiliaryService(db, tenant_id).create(count_id=body.inventory_count_id,
            batch_type=body.batch_type, actor=actor(request), reason=body.reason,
            import_rows=body.import_rows, declared_hash=body.declared_hash)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InventoryAuxiliaryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/batches", response_model=AuxiliaryBatchPageOut)
def list_batches(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
                 batch_type: str | None = None, status: str | None = None,
                 inventory_count_id: str | None = None, db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return InventoryAuxiliaryService(db, tenant_id).list_page(page=page, page_size=page_size,
        batch_type=batch_type, status=status, count_id=inventory_count_id)


@router.get("/summary", response_model=AuxiliarySummaryOut)
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return InventoryAuxiliaryService(db, tenant_id).summary()


@router.post("/batches/{batch_id}/transition", response_model=AuxiliaryTransitionOut)
def transition(batch_id: str, body: TransitionIn, request: Request, db: Session = Depends(get_db),
               tenant_id: str = Depends(get_tenant_id)) -> dict[str, str]:
    try:
        return InventoryAuxiliaryService(db, tenant_id).transition(batch_id, target=body.target,
            actor=actor(request), reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InventoryAuxiliaryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
