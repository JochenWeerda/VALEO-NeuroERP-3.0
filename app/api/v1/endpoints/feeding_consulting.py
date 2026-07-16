"""Consulting cases and observations API (FEED-CONS-031)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_consulting_service import (
    ConsultingCaseClosedError,
    FeedingConsultingService,
)
from app.services.feeding_consulting_report_service import (
    ConsultingReportConflict,
    FeedingConsultingReportService,
)

router = APIRouter(prefix="/feeding", tags=["feeding-consulting"])

CaseType = Literal["visit", "remote"]
CaseStatus = Literal["open", "closed"]


class ConsultingCaseIn(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    case_type: CaseType
    business_id: str | None = Field(default=None, max_length=80)
    group_id: str | None = Field(default=None, max_length=80)
    initial_situation: str | None = Field(default=None, max_length=4000)


class ObservationIn(BaseModel):
    category: str = Field(min_length=1, max_length=60)
    text: str = Field(min_length=1, max_length=8000)
    client_ref: str = Field(
        min_length=1,
        max_length=120,
        description="Idempotenzschluessel des (mobilen) Clients",
    )
    photo_document_refs: list[str] = Field(default_factory=list, max_length=20)
    ration_id: str | None = Field(default=None, max_length=80)
    analysis_ref: str | None = Field(default=None, max_length=80)
    observation_date: date | None = None


class CaseCloseIn(BaseModel):
    summary: str = Field(min_length=1, max_length=4000)


class CaseMeasureIn(BaseModel):
    measure_id: str = Field(min_length=1, max_length=80)


class ReportDraftIn(BaseModel):
    reason: str = Field(min_length=10, max_length=2000)


class ConsultingCaseOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    tenant_id: str
    business_id: str | None = None
    group_id: str | None = None
    case_type: CaseType
    title: str
    initial_situation: str | None = None
    status: CaseStatus
    closing_summary: str | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    observation_count: int | None = None


class ObservationOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    case_id: str
    category: str
    text: str
    photo_document_refs: list[str]
    ration_id: str | None = None
    analysis_ref: str | None = None
    observation_date: date | None = None
    client_ref: str
    created_by: str
    created_at: datetime
    duplicate: bool | None = None


class ConsultingCaseDetailOut(ConsultingCaseOut):
    observations: list[ObservationOut]


def _service(db: Session, tenant_id: str, user: User) -> FeedingConsultingService:
    return FeedingConsultingService(db, tenant_id, str(user.get("sub") or "unknown"))


def _report_service(
    db: Session, tenant_id: str, user: User
) -> FeedingConsultingReportService:
    roles = set(user.get("roles") or [])
    return FeedingConsultingReportService(
        db,
        tenant_id,
        str(user.get("sub") or "unknown"),
        unrestricted=bool(roles.intersection({"admin", "ADMIN", "FUTTERMITTEL_ADMIN"})),
    )


@router.post(
    "/consulting-cases",
    response_model=ConsultingCaseOut,
    status_code=201,
    summary="Beratungsfall anlegen (Besuch oder Remote)",
)
async def create_case(
    body: ConsultingCaseIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Beratungsfaelle.")
    try:
        return _service(db, tenant_id, user).create_case(body.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/consulting-cases",
    response_model=list[ConsultingCaseOut],
    summary="Beratungsfaelle auflisten (Worklist)",
)
async def list_cases(
    status: CaseStatus | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Beratungsfaelle.")
    return _service(db, tenant_id, user).list_cases(status=status)


@router.get(
    "/consulting-cases/{case_id}",
    response_model=ConsultingCaseDetailOut,
    summary="Beratungsfall mit chronologischen Beobachtungen",
)
async def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Beratungsfaelle.")
    try:
        return _service(db, tenant_id, user).get_case(case_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/consulting-cases/{case_id}/observations",
    response_model=ObservationOut,
    status_code=201,
    summary="Beobachtung idempotent anfuegen (mobiler Erfassungspfad via client_ref)",
)
async def add_observation(
    case_id: str,
    body: ObservationIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Beobachtungen.")
    try:
        return _service(db, tenant_id, user).add_observation(case_id, body.model_dump())
    except ConsultingCaseClosedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/consulting-cases/{case_id}/close",
    response_model=ConsultingCaseOut,
    summary="Beratungsfall mit Abschlussbewertung schliessen",
)
async def close_case(
    case_id: str,
    body: CaseCloseIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Beratungsfaelle.")
    try:
        return _service(db, tenant_id, user).close_case(case_id, body.summary)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/consulting-cases/{case_id}/measures",
    response_model=dict[str, Any],
    status_code=201,
)
async def link_measure(
    case_id: str,
    body: CaseMeasureIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(
        user, WRITE_ROLES, detail="Keine Berechtigung fuer Beratungsmassnahmen."
    )
    service = _report_service(db, tenant_id, user)
    try:
        return service.link_measure(case_id, body.measure_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ConsultingReportConflict as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post(
    "/consulting-cases/{case_id}/report-drafts",
    response_model=dict[str, Any],
    status_code=201,
)
async def create_report_draft(
    case_id: str,
    body: ReportDraftIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Berichtentwuerfe.")
    try:
        return _report_service(db, tenant_id, user).create_draft(case_id, body.reason)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/consulting-cases/{case_id}/measures", response_model=list[dict[str, Any]])
async def list_case_measures(
    case_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(
        user, READ_ROLES, detail="Keine Berechtigung fuer Beratungsmassnahmen."
    )
    try:
        return _report_service(db, tenant_id, user).list_measures(case_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get(
    "/consulting-cases/{case_id}/report-drafts", response_model=list[dict[str, Any]]
)
async def list_report_drafts(
    case_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Berichtentwuerfe.")
    try:
        return _report_service(db, tenant_id, user).list_drafts(case_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
