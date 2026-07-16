"""Plan-bound supply projection and procurement-proposal API."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.supply import FeedingSupplyValidationError
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_supply_service import (
    FeedingSupplyConflict,
    FeedingSupplyNotFound,
    FeedingSupplyService,
)
from app.services.rations_lifecycle_service import RationLifecycleService

router = APIRouter(prefix="/feeding/supply", tags=["feeding-supply"])


class ProcurementHandoffIn(BaseModel):
    plan_version_id: str = Field(min_length=1, max_length=80)
    feed_id: str = Field(min_length=1, max_length=160)
    horizon_days: int = Field(default=30, ge=1, le=365)
    safety_pct: float = Field(default=10, ge=0, le=100)
    idempotency_key: str = Field(min_length=8, max_length=160)
    reason: str = Field(min_length=10, max_length=2_000)


def _actor(user: User) -> str:
    return str(user.get("sub") or "unknown")


def _unrestricted(user: User) -> bool:
    return bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))


def _service(db: Session, tenant_id: str, user: User) -> FeedingSupplyService:
    return FeedingSupplyService(db, tenant_id, _actor(user))


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, FeedingSupplyNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (FeedingSupplyConflict, FeedingSupplyValidationError)):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Versorgungsbedarf konnte nicht verarbeitet werden.")


@router.get("", response_model=list[dict[str, Any]])
async def project_supply(
    horizon_days: int = Query(default=30, ge=1, le=365),
    safety_pct: float = Query(default=10, ge=0, le=100),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).project(
            horizon_days=horizon_days,
            safety_pct=safety_pct,
            subject=_actor(user),
            unrestricted=_unrestricted(user),
        )
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/procurement-handoffs", response_model=list[dict[str, Any]])
async def list_procurement_handoffs(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).list_handoffs(
        subject=_actor(user), unrestricted=_unrestricted(user),
    )


@router.post("/procurement-handoffs", response_model=dict[str, Any], status_code=201)
async def create_procurement_handoff(
    body: ProcurementHandoffIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        projection = next((row for row in _service(db, tenant_id, user).project(
            horizon_days=body.horizon_days,
            safety_pct=body.safety_pct,
            subject=_actor(user),
            unrestricted=_unrestricted(user),
        ) if row["plan_version_id"] == body.plan_version_id and row["feed_id"] == body.feed_id), None)
        if not projection:
            raise FeedingSupplyNotFound("Aktueller Planbedarf nicht gefunden.")
        if not _unrestricted(user) and not RationLifecycleService(
            db, tenant_id, _actor(user),
        ).has_group_access(projection["group_id"], _actor(user), "write"):
            raise FeedingSupplyNotFound("Aktueller Planbedarf nicht gefunden.")
        return _service(db, tenant_id, user).create_handoff(
            **body.model_dump(), subject=_actor(user), unrestricted=_unrestricted(user),
        )
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc
