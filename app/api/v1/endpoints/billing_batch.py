"""Billing batch orchestration API."""

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.billing_batch_schemas import (
    BatchActionOut,
    BatchCreatedOut,
    BatchLineOut,
    BatchPageOut,
    BatchSummaryOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.billing_batch_service import BillingBatchError, BillingBatchService

router = APIRouter(
    prefix="/billing-batches", tags=["finance", "billing-batches", "self-billing"]
)


class LineIn(BaseModel):
    source_type: str = Field(min_length=1, max_length=80)
    source_ref: str = Field(min_length=1, max_length=120)
    source_number: str | None = None
    source_route: str | None = None
    evidence_route: str | None = None
    amount: float = 0
    validation_error: str | None = None
    idempotency_key: str | None = None


class BatchIn(BaseModel):
    batch_type: Literal[
        "sales_invoice",
        "purchase_invoice",
        "self_billing_sales",
        "self_billing_purchase",
    ]
    batch_number: str | None = None
    description: str | None = None
    currency: str = "EUR"
    reason: str = Field(min_length=5, max_length=500)
    lines: list[LineIn] = Field(min_length=1)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "billing-operator"


@router.post("", response_model=BatchCreatedOut, status_code=201)
def create(
    body: BatchIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return BillingBatchService(db, tenant_id).create(
            body.model_dump(), actor=actor(request)
        )
    except BillingBatchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=BatchPageOut)
def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    batch_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return BillingBatchService(db, tenant_id).list_page(
        page=page, page_size=page_size, batch_type=batch_type, status=status
    )


@router.get("/summary", response_model=BatchSummaryOut)
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return BillingBatchService(db, tenant_id).summary()


@router.get("/lines", response_model=list[BatchLineOut])
def lines(
    status: str | None = None,
    batch_id: str | None = None,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return BillingBatchService(db, tenant_id).list_lines(
        status=status, batch_id=batch_id, limit=limit
    )


def _batch_action(
    action: str,
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session,
    tenant_id: str,
) -> dict[str, Any]:
    service = BillingBatchService(db, tenant_id)
    try:
        return getattr(service, action)(
            batch_id, actor=actor(request), reason=body.reason
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BillingBatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{batch_id}/validate", response_model=BatchActionOut)
def validate(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("validate", batch_id, body, request, db, tenant_id)


@router.post("/{batch_id}/release", response_model=BatchActionOut)
def release(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("release", batch_id, body, request, db, tenant_id)


@router.post("/{batch_id}/execute", response_model=BatchActionOut)
def execute(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("execute", batch_id, body, request, db, tenant_id)


@router.post("/lines/{line_id}/retry", response_model=BatchActionOut)
def retry(
    line_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return _batch_action("retry", line_id, body, request, db, tenant_id)
