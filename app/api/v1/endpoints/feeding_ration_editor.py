"""Ration draft evaluation API for the ration editor (FEED-EDITOR-021)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_ration_editor_service import FeedingRationEditorService

router = APIRouter(prefix="/feeding", tags=["feeding-ration-editor"])


class DraftComponentIn(BaseModel):
    feed_id: str = Field(min_length=1, max_length=80)
    kg_fm: float = Field(gt=0)


class RationDraftEvaluateIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    requirement_profile_id: str | None = Field(default=None, max_length=80)
    components: list[DraftComponentIn] = Field(min_length=1)


class DraftPositionOut(BaseModel):
    model_config = ConfigDict(extra="allow")

    feed_id: str
    name: str
    kg_fm: float
    kg_tm: float
    cost_eur: float


class DraftDeltaOut(BaseModel):
    metric: str
    actual: float
    target: float
    delta: float


class DraftFindingOut(BaseModel):
    code: str
    severity: str
    metric: str
    actual: float
    target: float | None = None
    message: str


class RationDraftEvaluationOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    group_id: str
    requirement_profile_id: str
    positions: list[DraftPositionOut]
    totals: dict[str, float]
    coverage: dict[str, dict[str, Any]]
    deltas: list[DraftDeltaOut]
    findings: list[DraftFindingOut]


@router.post("/ration-drafts/evaluate", response_model=RationDraftEvaluationOut,
             summary="Rationsentwurf deterministisch bewerten (ohne Persistenz, ohne Solverlauf)")
async def evaluate_ration_draft(body: RationDraftEvaluateIn, db: Session = Depends(get_db),
                                tenant_id: str = Depends(get_tenant_id),
                                user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Rationsbewertung.")
    service = FeedingRationEditorService(db, tenant_id, str(user.get("sub") or "unknown"))
    try:
        return service.evaluate(
            group_id=body.group_id,
            requirement_profile_id=body.requirement_profile_id,
            components=[component.model_dump() for component in body.components],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
