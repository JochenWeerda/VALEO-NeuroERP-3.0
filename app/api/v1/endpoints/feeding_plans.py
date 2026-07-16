"""Feeding-plan publication API."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.feeding_plan import FeedingPlanValidationError
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_plan_service import FeedingPlanConflict, FeedingPlanNotFound, FeedingPlanService
from app.services.rations_lifecycle_service import RationLifecycleService

router = APIRouter(prefix="/feeding/plans", tags=["feeding-plans"])


class PlanPublishIn(BaseModel):
    source_ration_version_id: str = Field(min_length=1, max_length=80)
    animal_count: int = Field(gt=0, le=100_000)
    dosing_step_kg: Decimal = Field(gt=0, max_digits=16, decimal_places=6)
    rounding_mode: Literal["nearest", "up", "down"] = "nearest"
    valid_from: date
    valid_until: date | None = None
    reason: str = Field(min_length=10, max_length=2_000)
    idempotency_key: str = Field(min_length=8, max_length=160)


class PlanOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    plan_id: str
    group_id: str
    version_no: int
    source_ration_version_id: str
    animal_count: int
    valid_from: date
    valid_until: date | None
    instructions: list[dict[str, Any]] = Field(default_factory=list)


def _service(db: Session, tenant_id: str, user: User) -> FeedingPlanService:
    return FeedingPlanService(db, tenant_id, str(user.get("sub") or "unknown"))


def _unrestricted(user: User) -> bool:
    return bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))


def _require_group(db: Session, tenant_id: str, user: User, group_id: str, scope: str) -> None:
    if not _unrestricted(user) and not RationLifecycleService(db, tenant_id, str(user.get("sub") or "")).has_group_access(group_id, str(user.get("sub") or ""), scope):
        raise HTTPException(status_code=404, detail="Fuetterungsgruppe nicht gefunden.")


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, FeedingPlanNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (FeedingPlanConflict, FeedingPlanValidationError)):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Fuetterungsplan konnte nicht verarbeitet werden.")


@router.post("/publish", response_model=PlanOut, status_code=201)
async def publish_plan(body: PlanPublishIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        source = db.execute(text("""SELECT r.group_id FROM domain_agrar.ration_versions rv
          JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          WHERE rv.tenant_id=:tenant_id AND rv.id=:id"""), {"tenant_id": tenant_id, "id": body.source_ration_version_id}).mappings().first()
        if not source:
            raise FeedingPlanNotFound("Rationsversion nicht gefunden.")
        _require_group(db, tenant_id, user, source["group_id"], "write")
        return await _service(db, tenant_id, user).publish(**body.model_dump())
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("", response_model=list[PlanOut])
async def list_plans(group_id: str | None = Query(None), db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    if group_id:
        _require_group(db, tenant_id, user, group_id, "read")
    rows = _service(db, tenant_id, user).list_versions(
        group_id, subject=str(user.get("sub") or ""), unrestricted=_unrestricted(user),
    )
    return [{**row, "instructions": []} for row in rows]


@router.get("/{version_id}", response_model=PlanOut)
async def get_plan(version_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                   user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES)
    try:
        result = _service(db, tenant_id, user).get_version(version_id)
        _require_group(db, tenant_id, user, result["group_id"], "read")
        return result
    except Exception as exc:
        raise _translate(exc) from exc
