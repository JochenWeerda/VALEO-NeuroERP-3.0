"""Revision-safe feeding reports API (FEED-REP-039)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_plan_service import FeedingPlanNotFound
from app.services.feeding_reports_service import FeedingReportsService

router = APIRouter(prefix="/feeding", tags=["feeding-reports"])

ReportType = Literal["feeding_plan", "consulting", "target_actual", "trend"]
ReportProfile = Literal["farmer", "advisor", "feeder"]


class ReportCreateIn(BaseModel):
    report_type: ReportType
    profile: ReportProfile
    source_ref: str = Field(min_length=1, max_length=80)


class ReportOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    tenant_id: str
    report_type: ReportType
    profile: ReportProfile
    source_ref: str
    content: dict[str, Any] | None = None
    content_hash: str
    dms_document_ref: str | None = None
    duplicate: bool | None = None
    created_by: str
    created_at: datetime


def _service(db: Session, tenant_id: str, user: User) -> FeedingReportsService:
    return FeedingReportsService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.post("/reports", response_model=ReportOut, status_code=201,
             summary="Bericht reproduzierbar aus unveraenderlicher Quellversion erzeugen")
async def create_report(body: ReportCreateIn, db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id),
                        user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Berichte.")
    try:
        return _service(db, tenant_id, user).create_report(
            report_type=body.report_type, profile=body.profile, source_ref=body.source_ref)
    except FeedingPlanNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/reports", response_model=list[ReportOut],
            summary="Berichte auflisten (neueste zuerst)")
async def list_reports(source_ref: str | None = None, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Berichte.")
    return _service(db, tenant_id, user).list_reports(source_ref=source_ref)


@router.get("/reports/{report_id}", response_model=ReportOut,
            summary="Bericht mit Inhalt lesen")
async def get_report(report_id: str, db: Session = Depends(get_db),
                     tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Berichte.")
    try:
        return _service(db, tenant_id, user).get_report(report_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/reports/{report_id}/csv", response_class=PlainTextResponse,
            summary="Strukturierte Berichtsdaten als CSV exportieren")
async def report_csv(report_id: str, db: Session = Depends(get_db),
                     tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> PlainTextResponse:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Berichte.")
    try:
        csv_text = _service(db, tenant_id, user).report_csv(report_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PlainTextResponse(csv_text, media_type="text/csv; charset=utf-8")
