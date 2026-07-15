"""Feeding groups and immutable ration-version lifecycle API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.lifecycle import RationStatus, TransitionError
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rations_lifecycle_service import (
    RationLifecycleConflict,
    RationLifecycleNotFound,
    RationLifecycleService,
)

router = APIRouter(prefix="/lifecycle", tags=["rations-lifecycle"])


class FeedingGroupIn(BaseModel):
    external_ref: str | None = Field(default=None, max_length=160)
    name: str = Field(min_length=1, max_length=200)
    animal_type: str = Field(default="dairy_cow", min_length=1, max_length=40)
    animal_count: int = Field(ge=0, le=100_000)
    body_mass_kg: float | None = Field(default=None, gt=0, le=3_000)
    days_in_milk: int | None = Field(default=None, ge=0, le=1_500)
    lactation_number: float | None = Field(default=None, ge=0, le=30)
    target_milk_kg: float | None = Field(default=None, ge=0, le=150)
    feeding_system: Literal["TMR", "PMR", "PMR+Weide"] = "TMR"
    location: str | None = Field(default=None, max_length=200)
    active: bool = True


class RationCreateIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4_000)
    snapshot: dict[str, Any] = Field(min_length=1)
    source: Literal["solver", "manual", "import"] = "solver"
    comment: str | None = Field(default=None, max_length=2_000)


class RationVersionCreateIn(BaseModel):
    snapshot: dict[str, Any] = Field(min_length=1)
    source: Literal["solver", "manual", "import"] = "solver"
    comment: str | None = Field(default=None, max_length=2_000)
    based_on_version_id: str | None = Field(default=None, max_length=80)
    expected_latest_version_no: int = Field(ge=1)


class RationTransitionIn(BaseModel):
    target_status: RationStatus
    expected_status: RationStatus
    reason: str | None = Field(default=None, max_length=2_000)
    feeding_start: datetime | None = None


def _require(user: User, allowed: set[str]) -> None:
    require_roles(user, allowed, detail="Keine Berechtigung fuer diesen Rations-Lifecycle-Schritt.")


def _service(db: Session, tenant_id: str, user: User) -> RationLifecycleService:
    return RationLifecycleService(db, tenant_id, str(user.get("sub") or "unknown"))


def _translate_error(exc: Exception) -> HTTPException:
    if isinstance(exc, RationLifecycleNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (RationLifecycleConflict, TransitionError)):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Rations-Lifecycle konnte nicht verarbeitet werden.")


@router.post("/groups", response_model=dict, status_code=201, summary="Fuetterungsgruppe anlegen")
async def create_feeding_group(
    body: FeedingGroupIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).create_group(body.model_dump())
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/groups", response_model=list[dict], summary="Fuetterungsgruppen auflisten")
async def list_feeding_groups(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_groups(active_only=active_only)


@router.post("/rations", response_model=dict, status_code=201, summary="Ration mit Version 1 anlegen")
async def create_ration(
    body: RationCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).create_ration(**body.model_dump())
    except Exception as exc:
        db.rollback()
        raise _translate_error(exc) from exc


@router.get("/rations", response_model=list[dict], summary="Rationen als Worklist auflisten")
async def list_rations(
    group_id: str | None = Query(default=None),
    status: RationStatus | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_rations(group_id=group_id, status=status, limit=limit)


@router.get("/active-rations", response_model=list[dict], summary="Aktive Rationen fuer die Stallausfuehrung")
async def list_active_rations(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_active_rations()


@router.get("/rations/{ration_id}", response_model=dict, summary="Ration mit Versionen und Audit lesen")
async def get_ration(
    ration_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).get_ration(ration_id)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/rations/{ration_id}/versions", response_model=dict, status_code=201, summary="Neue unveraenderliche Rationsversion anlegen")
async def create_ration_version(
    ration_id: str,
    body: RationVersionCreateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).create_version(ration_id=ration_id, **body.model_dump())
    except Exception as exc:
        db.rollback()
        raise _translate_error(exc) from exc


@router.get("/rations/{ration_id}/versions", response_model=list[dict], summary="Rationsversionen auflisten")
async def list_ration_versions(
    ration_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).list_versions(ration_id)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/versions/{version_id}/transitions", response_model=dict, summary="Rationsstatus kontrolliert wechseln")
async def transition_ration_version(
    version_id: str,
    body: RationTransitionIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, APPROVE_ROLES if body.target_status in {RationStatus.APPROVED, RationStatus.ACTIVE} else WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).transition(
            version_id=version_id,
            target=body.target_status,
            expected_status=body.expected_status,
            reason=body.reason,
            feeding_start=body.feeding_start,
        )
    except Exception as exc:
        db.rollback()
        raise _translate_error(exc) from exc


@router.get("/rations/{ration_id}/audit", response_model=list[dict], summary="Rations-Audit lesen")
async def list_ration_audit(
    ration_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_audit(ration_id)
