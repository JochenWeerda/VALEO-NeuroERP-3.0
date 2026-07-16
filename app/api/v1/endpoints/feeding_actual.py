"""Component actual-feeding command, projection and CSV API."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agrar.rations.actual_feeding import ActualFeedingValidationError
from app.agrar.rations.actual_measures import DeviationPolicyError
from app.agrar.rations.authz import (
    APPROVE_ROLES,
    READ_ROLES,
    WRITE_ROLES,
    require_roles,
)
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_actual_service import (
    FeedingActualConflict,
    FeedingActualNotFound,
    FeedingActualService,
)
from app.services.feeding_actual_measure_service import (
    ActualMeasureConflict,
    ActualMeasureNotFound,
    FeedingActualMeasureService,
)
from app.services.feeding_plan_service import FeedingPlanNotFound, FeedingPlanService
from app.services.rations_lifecycle_service import RationLifecycleService

router = APIRouter(prefix="/feeding/actuals", tags=["feeding-actuals"])


class ActualComponentIn(BaseModel):
    feed_id: str = Field(min_length=1, max_length=160)
    actual_kg: Decimal = Field(ge=0, max_digits=18, decimal_places=6)


class ActualRecordIn(BaseModel):
    plan_version_id: str = Field(min_length=1, max_length=80)
    feeding_at: datetime
    source: Literal["manual", "mixing_wagon", "import"] = "manual"
    source_ref: str = Field(min_length=1, max_length=200)
    cause_class: Literal[
        "normal",
        "stock_substitution",
        "dosing_error",
        "feed_quality",
        "animal_intake",
        "technical",
        "other",
    ] = "normal"
    comment: str | None = Field(default=None, max_length=2_000)
    context: dict[str, Any] = Field(default_factory=dict)
    supersedes_id: str | None = Field(default=None, max_length=80)
    idempotency_key: str = Field(min_length=8, max_length=160)
    components: list[ActualComponentIn] = Field(min_length=1, max_length=200)


class DeviationPolicyIn(BaseModel):
    feed_class: Literal[
        "forage", "concentrate", "mineral", "additive", "byproduct", "liquid", "other"
    ]
    warning_pct: Decimal = Field(gt=0, le=100)
    critical_pct: Decimal = Field(gt=0, le=100)
    valid_from: date
    reason: str = Field(min_length=10, max_length=1_000)


class ActualMeasureIn(BaseModel):
    actual_component_id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=3, max_length=240)
    owner_subject: str = Field(min_length=1, max_length=160)
    due_date: date
    reason: str = Field(min_length=10, max_length=2_000)
    idempotency_key: str = Field(min_length=8, max_length=160)


def _actor(user: User) -> str:
    return str(user.get("sub") or "unknown")


def _unrestricted(user: User) -> bool:
    return bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))


def _service(db: Session, tenant_id: str, user: User) -> FeedingActualService:
    return FeedingActualService(db, tenant_id, _actor(user))


def _groups(db: Session, tenant_id: str, user: User, scope: str = "read") -> list[str]:
    if _unrestricted(user):
        return [
            row["id"]
            for row in RationLifecycleService(
                db,
                tenant_id,
                _actor(user),
            ).list_groups(active_only=False, subject=_actor(user), unrestricted=True)
        ]
    return [
        row["id"]
        for row in RationLifecycleService(
            db,
            tenant_id,
            _actor(user),
        ).list_groups(active_only=False, subject=_actor(user), unrestricted=False)
        if scope == "read"
        or RationLifecycleService(
            db,
            tenant_id,
            _actor(user),
        ).has_group_access(row["id"], _actor(user), "write")
    ]


def _translate(exc: Exception) -> HTTPException:
    if isinstance(
        exc, (FeedingActualNotFound, FeedingPlanNotFound, ActualMeasureNotFound)
    ):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(
        exc,
        (
            FeedingActualConflict,
            ActualFeedingValidationError,
            ActualMeasureConflict,
            DeviationPolicyError,
        ),
    ):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(
        status_code=500, detail="Ist-Fuetterung konnte nicht verarbeitet werden."
    )


@router.post("", response_model=dict[str, Any], status_code=201)
async def record_actual(
    body: ActualRecordIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        plan = FeedingPlanService(db, tenant_id, _actor(user)).get_version(
            body.plan_version_id
        )
        if not _unrestricted(user) and not RationLifecycleService(
            db,
            tenant_id,
            _actor(user),
        ).has_group_access(plan["group_id"], _actor(user), "write"):
            raise FeedingActualNotFound("Aktuelle Planversion nicht gefunden.")
        return _service(db, tenant_id, user).record(body.model_dump())
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("", response_model=list[dict[str, Any]])
async def list_actuals(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).list(group_ids=_groups(db, tenant_id, user))


@router.get("/components", response_model=list[dict[str, Any]])
async def list_actual_components(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).list_components(
        group_ids=_groups(db, tenant_id, user)
    )


@router.get("/export.csv")
async def export_actuals_csv(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> Response:
    require_roles(user, READ_ROLES)
    rows = _service(db, tenant_id, user).list(group_ids=_groups(db, tenant_id, user))
    content = _service(db, tenant_id, user).to_csv(rows)
    return Response(
        content=f"\ufeff{content}",
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=ist-fuetterung.csv"},
    )


@router.post("/deviation-policies", response_model=dict[str, Any], status_code=201)
async def create_deviation_policy(
    body: DeviationPolicyIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, APPROVE_ROLES)
    try:
        return FeedingActualMeasureService(db, tenant_id, _actor(user)).create_policy(
            body.model_dump()
        )
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("/deviation-policies", response_model=list[dict[str, Any]])
async def list_deviation_policies(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return FeedingActualMeasureService(db, tenant_id, _actor(user)).list_policies()


@router.get("/findings", response_model=list[dict[str, Any]])
async def list_deviation_findings(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return FeedingActualMeasureService(db, tenant_id, _actor(user)).findings(
        group_ids=_groups(db, tenant_id, user),
    )


@router.post("/measures", response_model=dict[str, Any], status_code=201)
async def create_actual_measure(
    body: ActualMeasureIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return FeedingActualMeasureService(db, tenant_id, _actor(user)).create_measure(
            body.model_dump(),
            group_ids=_groups(db, tenant_id, user, "write"),
        )
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("/measures", response_model=list[dict[str, Any]])
async def list_actual_measures(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return FeedingActualMeasureService(db, tenant_id, _actor(user)).list_measures(
        group_ids=_groups(db, tenant_id, user),
    )
