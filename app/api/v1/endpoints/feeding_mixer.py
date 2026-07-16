"""Mixer export and feedback API (FEED-INT-035)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_mixer_service import (
    FeedingMixerService,
    StalePlanVersionError,
    UnknownFeedbackFeedError,
)
from app.services.feeding_plan_service import FeedingPlanNotFound

router = APIRouter(prefix="/feeding", tags=["feeding-mixer"])


class MixerLoadOut(BaseModel):
    sequence: int
    feed_id: str
    feed_name: str
    kg_fm_per_animal: float | None = None
    target_batch_kg: float | None = None


class MixerExportOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    format: str
    reference: str
    plan_id: str
    version_no: int
    group_id: str
    group_name: str
    animal_count: int
    valid_from: str
    valid_until: str | None = None
    loads: list[MixerLoadOut]


class MixerLoadIn(BaseModel):
    feed_id: str = Field(min_length=1, max_length=80)
    kg_loaded: float = Field(ge=0)


class MixerFeedbackIn(BaseModel):
    plan_version_id: str = Field(min_length=1, max_length=80)
    client_ref: str = Field(min_length=1, max_length=120)
    loaded: list[MixerLoadIn] = Field(min_length=1)
    residual_kg: float | None = Field(default=None, ge=0)


class MixerFeedbackLineOut(BaseModel):
    feed_id: str
    feed_name: str
    kg_loaded: float
    target_batch_kg: float | None = None
    delta_kg: float | None = None


class MixerFeedbackOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    plan_version_id: str
    client_ref: str
    lines: list[MixerFeedbackLineOut]
    residual_kg: float | None = None
    accuracy_pct: float | None = None
    duplicate: bool
    quarantined: bool
    created_by: str
    created_at: datetime


class MixerFeedbackQuarantinedOut(BaseModel):
    quarantined: bool
    import_job_id: str


def _service(db: Session, tenant_id: str, user: User) -> FeedingMixerService:
    return FeedingMixerService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.get("/plans/versions/{plan_version_id}/mixer-export", response_model=MixerExportOut,
            summary="Planversion als Mischwagen-/Roboter-Dokument exportieren")
async def mixer_export(plan_version_id: str, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer den Mischwagen-Export.")
    try:
        return _service(db, tenant_id, user).build_export(plan_version_id)
    except StalePlanVersionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except FeedingPlanNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/mixer-feedback", response_model=MixerFeedbackOut | MixerFeedbackQuarantinedOut,
             status_code=201,
             summary="Geladene Mengen idempotent auf die Planversion zurueckmelden",
             responses={202: {"model": MixerFeedbackQuarantinedOut,
                              "description": "Veraltete Planversion — Rueckmeldung in Quarantaene"}})
async def mixer_feedback(body: MixerFeedbackIn, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)):
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Mischwagen-Rueckmeldungen.")
    from fastapi.responses import JSONResponse
    service = _service(db, tenant_id, user)
    try:
        result = service.record_feedback(
            plan_version_id=body.plan_version_id, client_ref=body.client_ref,
            loaded=[entry.model_dump() for entry in body.loaded],
            residual_kg=body.residual_kg)
    except UnknownFeedbackFeedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FeedingPlanNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if result.get("quarantined"):
        return JSONResponse(status_code=202, content={
            "quarantined": True, "import_job_id": result["import_job_id"]})
    return result
