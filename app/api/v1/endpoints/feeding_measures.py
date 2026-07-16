"""Versioned measure lifecycle and recipient-scoped notification API."""

from datetime import date
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.authz import (
    APPROVE_ROLES,
    READ_ROLES,
    WRITE_ROLES,
    require_roles,
)
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_measure_lifecycle_service import (
    FeedingMeasureConflict,
    FeedingMeasureLifecycleService,
    FeedingMeasureNotFound,
)

router = APIRouter(prefix="/feeding", tags=["feeding-measures"])


class MeasureTransitionIn(BaseModel):
    expected_version: int = Field(ge=1)
    target_status: Literal["in_progress", "review_due", "completed", "cancelled"]
    reason: str = Field(min_length=10, max_length=2000)
    owner_subject: str | None = Field(default=None, min_length=1, max_length=160)
    due_date: date | None = None
    reminder_date: date | None = None
    escalation_status: Literal["none", "attention", "escalated"] | None = None
    effectiveness: Literal["effective", "partial", "ineffective"] | None = None
    effectiveness_result: str | None = Field(default=None, max_length=4000)


class OverdueRunIn(BaseModel):
    as_of: date


def _groups(db: Session, tenant_id: str, user: User, scope: str) -> list[str]:
    roles = set(user.get("roles") or [])
    if roles.intersection({"admin", "ADMIN", "FUTTERMITTEL_ADMIN"}):
        return list(
            db.execute(
                text("SELECT id FROM domain_agrar.feeding_groups WHERE tenant_id=:t"),
                {"t": tenant_id},
            ).scalars()
        )
    subject = str(user.get("sub") or "")
    scopes = (
        ["read", "write", "approve", "admin"]
        if scope == "read"
        else ["write", "approve", "admin"]
    )
    return list(
        db.execute(
            text("""SELECT g.id FROM domain_agrar.feeding_groups g
      LEFT JOIN domain_agrar.feeding_businesses b ON b.tenant_id=g.tenant_id AND b.id=g.business_id
      WHERE g.tenant_id=:tenant_id AND (g.created_by=:subject OR b.created_by=:subject OR EXISTS (
        SELECT 1 FROM domain_agrar.feeding_business_grants x WHERE x.tenant_id=g.tenant_id
          AND x.business_id=g.business_id AND x.subject=:subject AND x.scope=ANY(:scopes)
          AND x.revoked_at IS NULL))"""),
            {
                "tenant_id": tenant_id,
                "subject": subject,
                "scopes": scopes,
            },
        ).scalars()
    )


def _service(db: Session, tenant_id: str, user: User) -> FeedingMeasureLifecycleService:
    return FeedingMeasureLifecycleService(
        db, tenant_id, str(user.get("sub") or "unknown")
    )


@router.post("/measures/{measure_id}/transitions", response_model=dict[str, Any])
async def transition_measure(
    measure_id: str,
    body: MeasureTransitionIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).transition(
            measure_id,
            body.model_dump(),
            group_ids=_groups(db, tenant_id, user, "write"),
        )
    except FeedingMeasureNotFound as exc:
        raise HTTPException(404, str(exc)) from exc
    except FeedingMeasureConflict as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/measures/{measure_id}/history", response_model=list[dict[str, Any]])
async def measure_history(
    measure_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).history(
            measure_id, group_ids=_groups(db, tenant_id, user, "read")
        )
    except FeedingMeasureNotFound as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/measures/process-overdue", response_model=dict[str, int])
async def process_overdue(
    body: OverdueRunIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, int]:
    require_roles(user, APPROVE_ROLES)
    return _service(db, tenant_id, user).process_overdue(
        as_of=body.as_of, group_ids=_groups(db, tenant_id, user, "write")
    )


@router.get("/notifications", response_model=list[dict[str, Any]])
async def notifications(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).notifications()
