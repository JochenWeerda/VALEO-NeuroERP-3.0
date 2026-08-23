"""Feeding groups and immutable ration-version lifecycle API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.groups import GroupProfile, GroupRiskLevel, PregnancyStatus, validate_group_parameters
from app.agrar.rations.lifecycle import RationStatus, TransitionError
from app.auth.deps import User, get_current_user
from app.api.v1.schemas.rations_lifecycle_schemas import (
    ActiveRationOut,
    RationAuditEventOut,
    RationDetailOut,
    RationTransitionOut,
    RationVersionOut,
    RationWorklistItemOut,
)
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
    business_id: str | None = Field(default=None, max_length=80)
    herd_id: str | None = Field(default=None, max_length=80)
    profile_code: GroupProfile = GroupProfile.CUSTOM
    pregnancy_status: PregnancyStatus = PregnancyStatus.UNKNOWN
    gestation_day: int | None = Field(default=None, ge=0, le=305)
    milk_fat_pct: float | None = Field(default=None, ge=0, le=15)
    milk_protein_pct: float | None = Field(default=None, ge=0, le=10)
    milk_urea_mg_dl: float | None = Field(default=None, ge=0, le=100)
    risk_level: GroupRiskLevel = GroupRiskLevel.LOW
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None
    active: bool = True

    @model_validator(mode="after")
    def validate_parameters(self) -> "FeedingGroupIn":
        validate_group_parameters(
            profile=self.profile_code,
            pregnancy_status=self.pregnancy_status,
            gestation_day=self.gestation_day,
            milk_fat_pct=self.milk_fat_pct,
            milk_protein_pct=self.milk_protein_pct,
            valid_from=self.valid_from,
            valid_until=self.valid_until,
        )
        return self


class FeedingGroupUpdateIn(BaseModel):
    expected_revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)
    external_ref: str | None = Field(default=None, max_length=160)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    animal_type: str | None = Field(default=None, min_length=1, max_length=40)
    animal_count: int | None = Field(default=None, ge=0, le=100_000)
    body_mass_kg: float | None = Field(default=None, gt=0, le=3_000)
    days_in_milk: int | None = Field(default=None, ge=0, le=1_500)
    lactation_number: float | None = Field(default=None, ge=0, le=30)
    target_milk_kg: float | None = Field(default=None, ge=0, le=150)
    feeding_system: Literal["TMR", "PMR", "PMR+Weide"] | None = None
    location: str | None = Field(default=None, max_length=200)
    herd_id: str | None = Field(default=None, max_length=80)
    profile_code: GroupProfile | None = None
    pregnancy_status: PregnancyStatus | None = None
    gestation_day: int | None = Field(default=None, ge=0, le=305)
    milk_fat_pct: float | None = Field(default=None, ge=0, le=15)
    milk_protein_pct: float | None = Field(default=None, ge=0, le=10)
    milk_urea_mg_dl: float | None = Field(default=None, ge=0, le=100)
    risk_level: GroupRiskLevel | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    active: bool | None = None

    @model_validator(mode="after")
    def validate_partial_parameters(self) -> "FeedingGroupUpdateIn":
        if self.gestation_day is not None and self.pregnancy_status not in (None, PregnancyStatus.PREGNANT):
            raise ValueError("Traechtigkeitstag ist nur fuer traechtige Gruppen zulaessig.")
        if self.valid_from is not None and self.valid_until is not None and self.valid_until < self.valid_from:
            raise ValueError("Gueltigkeitsende darf nicht vor dem Gueltigkeitsbeginn liegen.")
        return self


class FeedingGroupOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    tenant_id: str
    external_ref: str | None = None
    business_id: str | None = None
    herd_id: str | None = None
    name: str
    animal_type: str
    animal_count: int
    body_mass_kg: float | None = None
    days_in_milk: int | None = None
    lactation_number: float | None = None
    target_milk_kg: float | None = None
    feeding_system: str
    location: str | None = None
    profile_code: GroupProfile
    pregnancy_status: PregnancyStatus
    gestation_day: int | None = None
    milk_fat_pct: float | None = None
    milk_protein_pct: float | None = None
    milk_urea_mg_dl: float | None = None
    risk_level: GroupRiskLevel
    valid_from: date
    valid_until: date | None = None
    active: bool
    revision: int
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    ration_count: int | None = None
    active_ration_count: int | None = None


class FeedingGroupRevisionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    tenant_id: str
    group_id: str
    revision: int
    snapshot: dict[str, Any]
    reason: str
    changed_by: str
    changed_at: datetime


class RationCreateIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4_000)
    snapshot: dict[str, Any] = Field(min_length=1)
    source: Literal["solver", "manual", "import", "editor"] = "solver"
    comment: str | None = Field(default=None, max_length=2_000)


class RationVersionCreateIn(BaseModel):
    snapshot: dict[str, Any] = Field(min_length=1)
    source: Literal["solver", "manual", "import", "editor", "template", "optimizer"] = "solver"
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


def _unrestricted(user: User) -> bool:
    return bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))


def _require_group_scope(service: RationLifecycleService, group_id: str, user: User,
                         scope: Literal["read", "write"]) -> None:
    if _unrestricted(user):
        return
    if not service.has_group_access(group_id, str(user.get("sub") or ""), scope):
        raise HTTPException(status_code=404, detail="Fuetterungsgruppe nicht gefunden.")


def _require_business_scope(service: RationLifecycleService, business_id: str | None,
                            user: User, scope: Literal["read", "write"]) -> None:
    if _unrestricted(user):
        return
    if not business_id or not service.has_business_access(
        business_id, str(user.get("sub") or ""), scope
    ):
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Fuetterungsbetrieb.")


def _translate_error(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, RationLifecycleNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (RationLifecycleConflict, TransitionError)):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Rations-Lifecycle konnte nicht verarbeitet werden.")


@router.post("/groups", response_model=FeedingGroupOut, status_code=201, summary="Fuetterungsgruppe anlegen")
async def create_feeding_group(
    body: FeedingGroupIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, WRITE_ROLES)
    try:
        service = _service(db, tenant_id, user)
        _require_business_scope(service, body.business_id, user, "write")
        return service.create_group(body.model_dump())
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.get("/groups", response_model=list[FeedingGroupOut], summary="Fuetterungsgruppen auflisten")
async def list_feeding_groups(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_groups(
        active_only=active_only,
        subject=str(user.get("sub") or ""),
        unrestricted=_unrestricted(user),
    )


@router.get("/groups/{group_id}", response_model=FeedingGroupOut, summary="Fuetterungsgruppe lesen")
async def get_feeding_group(
    group_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, READ_ROLES)
    try:
        service = _service(db, tenant_id, user)
        _require_group_scope(service, group_id, user, "read")
        return service.get_group(group_id)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.patch("/groups/{group_id}", response_model=FeedingGroupOut, summary="Fuetterungsgruppe versioniert aktualisieren")
async def update_feeding_group(
    group_id: str,
    body: FeedingGroupUpdateIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    _require(user, WRITE_ROLES)
    try:
        service = _service(db, tenant_id, user)
        _require_group_scope(service, group_id, user, "write")
        return service.update_group(
            group_id,
            body.model_dump(exclude_unset=True),
        )
    except Exception as exc:
        db.rollback()
        raise _translate_error(exc) from exc


@router.get("/groups/{group_id}/history", response_model=list[FeedingGroupRevisionOut], summary="Parameterhistorie der Fuetterungsgruppe")
async def list_feeding_group_history(
    group_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    try:
        service = _service(db, tenant_id, user)
        _require_group_scope(service, group_id, user, "read")
        return service.list_group_history(group_id)
    except Exception as exc:
        raise _translate_error(exc) from exc


@router.post("/rations", response_model=RationDetailOut, status_code=201, summary="Ration mit Version 1 anlegen")
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


@router.get("/rations", response_model=list[RationWorklistItemOut], summary="Rationen als Worklist auflisten")
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


@router.get("/active-rations", response_model=list[ActiveRationOut], summary="Aktive Rationen fuer die Stallausfuehrung")
async def list_active_rations(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_active_rations()


@router.get("/rations/{ration_id}", response_model=RationDetailOut, summary="Ration mit Versionen und Audit lesen")
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


@router.post("/rations/{ration_id}/versions", response_model=RationVersionOut, status_code=201, summary="Neue unveraenderliche Rationsversion anlegen")
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


@router.get("/rations/{ration_id}/versions", response_model=list[RationVersionOut], summary="Rationsversionen auflisten")
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


@router.post("/versions/{version_id}/transitions", response_model=RationTransitionOut, summary="Rationsstatus kontrolliert wechseln")
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


@router.get("/rations/{ration_id}/audit", response_model=list[RationAuditEventOut], summary="Rations-Audit lesen")
async def list_ration_audit(
    ration_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    _require(user, READ_ROLES)
    return _service(db, tenant_id, user).list_audit(ration_id)
