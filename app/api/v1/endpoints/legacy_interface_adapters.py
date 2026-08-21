"""Governed L3 Standard and Unimet adapter API."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.legacy_interface_adapter_service import (
    LegacyAdapterError,
    LegacyInterfaceAdapterService,
)

router = APIRouter(
    prefix="/legacy-interface-adapters",
    tags=["integration", "l3-parity"],
    dependencies=[
        Depends(require_roles("admin", "manager", "FINANCE_ADMIN", "LAGER_ADMIN"))
    ],
)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ProfileIn(ReasonIn):
    format_version: str = Field(min_length=1, max_length=40)
    mapping_version: str = Field(min_length=1, max_length=40)
    status: str = "ready"
    format_contract: dict[str, Any]
    field_mapping: dict[str, str]


class IntakeIn(BaseModel):
    external_id: str = Field(min_length=1, max_length=200)
    payload: dict[str, Any]


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "interface-operator"


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LegacyAdapterError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/profiles", response_model=dict)
def profiles(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = LegacyInterfaceAdapterService(db, tenant_id).catalog()
    return {"items": items, "total": len(items), "execution_enabled": False}


@router.put("/profiles/{profile_key}", response_model=dict)
def configure(
    profile_key: str,
    body: ProfileIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).configure(
            profile_key,
            body.model_dump(exclude={"reason"}),
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post(
    "/{profile_key}/intake", response_model=dict, status_code=status.HTTP_202_ACCEPTED
)
def intake(
    profile_key: str,
    body: IntakeIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).intake(
            profile_key, body.external_id, body.payload, actor=actor(request)
        )
    )


@router.get("/batches", response_model=dict)
def monitor(
    batch_status: str | None = Query(default=None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).monitor(
            status=batch_status, page=page, page_size=page_size
        )
    )


@router.post("/batches/{batch_id}/stage", response_model=dict)
def stage(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).stage(
            batch_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/batches/{batch_id}/reconcile", response_model=dict)
def reconcile(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).reconcile(
            batch_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/batches/{batch_id}/approve", response_model=dict)
def approve(
    batch_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: LegacyInterfaceAdapterService(db, tenant_id).approve(
            batch_id, actor=actor(request), reason=body.reason
        )
    )
