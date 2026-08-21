"""Tankanlagen adapter inbox API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.tank_adapter_service import TankAdapterError, TankAdapterService

router = APIRouter(prefix="/tank-adapter", tags=["tankstelle", "integration"])


class IntakeIn(BaseModel):
    adapter_key: str = Field(min_length=1, max_length=80)
    external_id: str = Field(min_length=1, max_length=160)
    payload: dict[str, Any]


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class RetryIn(ReasonIn):
    corrected_payload: dict[str, Any] | None = None


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "tank-operator"


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TankAdapterError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/intake", response_model=dict, status_code=202)
def intake(
    body: IntakeIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).ingest(
            body.adapter_key, body.external_id, body.payload, actor=actor(request)
        )
    )


@router.get("/intake", response_model=dict)
def list_intake(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return TankAdapterService(db, tenant_id).list_page(
        page=page, page_size=page_size, status=status
    )


@router.get("/summary", response_model=dict)
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return TankAdapterService(db, tenant_id).summary()


@router.post("/intake/{intake_id}/validate", response_model=dict)
def validate(
    intake_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).validate(
            intake_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/intake/{intake_id}/process", response_model=dict)
def process(
    intake_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).process(
            intake_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/intake/{intake_id}/retry", response_model=dict)
def retry(
    intake_id: str,
    body: RetryIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).retry(
            intake_id, body.corrected_payload, actor=actor(request), reason=body.reason
        )
    )
