"""Evaluation systems, requirement profiles and optimization runs API (FEED-CORE-020)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_requirements_service import FeedingRequirementsService

router = APIRouter(prefix="/feeding", tags=["feeding-requirements"])

RunStatus = Literal["optimal", "infeasible", "unbounded", "error", "timeout"]


class FeedingRequirementsOut(BaseModel):
    """Stable public contract while allowing additive database fields."""

    model_config = ConfigDict(extra="ignore")


class EvaluationSystemVersionOut(FeedingRequirementsOut):
    id: str
    system_id: str
    version_label: str
    module_ref: str
    is_current: bool
    valid_from: datetime


class EvaluationSystemOut(FeedingRequirementsOut):
    id: str
    name: str
    description: str | None = None
    versions: list[EvaluationSystemVersionOut]


class RequirementProfileIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    inputs: dict[str, Any] = Field(default_factory=dict)


class RequirementProfileOut(FeedingRequirementsOut):
    id: str
    tenant_id: str
    group_id: str
    system_version_id: str
    inputs: dict[str, Any]
    estimated_inputs: list[str]
    requirements: dict[str, Any]
    created_by: str
    created_at: datetime


class OptimizationRunIn(BaseModel):
    ration_version_id: str = Field(min_length=1, max_length=80)
    solver_version: str = Field(min_length=1, max_length=80)
    objective: str = Field(min_length=1, max_length=60)
    status: RunStatus
    duration_ms: int | None = Field(default=None, ge=0)
    parameters: dict[str, Any] = Field(default_factory=dict)


class OptimizationRunOut(FeedingRequirementsOut):
    id: str
    tenant_id: str
    ration_id: str
    ration_version_id: str
    solver_version: str
    objective: str
    status: RunStatus
    duration_ms: int | None = None
    parameters: dict[str, Any]
    created_by: str
    created_at: datetime


def _service(db: Session, tenant_id: str, user: User) -> FeedingRequirementsService:
    return FeedingRequirementsService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.get("/evaluation-systems", response_model=list[EvaluationSystemOut],
            summary="Registrierte Bedarfs-/Bewertungssysteme mit Versionen")
async def list_evaluation_systems(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                  user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Bewertungssysteme.")
    return _service(db, tenant_id, user).list_systems()


@router.post("/requirement-profiles", response_model=RequirementProfileOut, status_code=201,
             summary="Bedarfsprofil regelversioniert berechnen und persistieren")
async def create_requirement_profile(body: RequirementProfileIn, db: Session = Depends(get_db),
                                     tenant_id: str = Depends(get_tenant_id),
                                     user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Bedarfsprofile.")
    try:
        return _service(db, tenant_id, user).create_requirement_profile(body.group_id, body.inputs)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/requirement-profiles", response_model=list[RequirementProfileOut],
            summary="Bedarfsprofile einer Fuetterungsgruppe (neueste zuerst)")
async def list_requirement_profiles(group_id: str, db: Session = Depends(get_db),
                                    tenant_id: str = Depends(get_tenant_id),
                                    user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Bedarfsprofile.")
    return _service(db, tenant_id, user).list_requirement_profiles(group_id)


@router.post("/optimization-runs", response_model=OptimizationRunOut, status_code=201,
             summary="Solverlauf reproduzierbar zu einer Rationsversion dokumentieren")
async def record_optimization_run(body: OptimizationRunIn, db: Session = Depends(get_db),
                                  tenant_id: str = Depends(get_tenant_id),
                                  user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Solverlauf-Dokumentation.")
    try:
        return _service(db, tenant_id, user).record_optimization_run(
            body.ration_version_id, body.model_dump(exclude={"ration_version_id"}))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/optimization-runs", response_model=list[OptimizationRunOut],
            summary="Dokumentierte Solverlaeufe einer Ration (neueste zuerst)")
async def list_optimization_runs(ration_id: str, db: Session = Depends(get_db),
                                 tenant_id: str = Depends(get_tenant_id),
                                 user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Solverlauf-Dokumentation.")
    return _service(db, tenant_id, user).list_optimization_runs(ration_id=ration_id)
