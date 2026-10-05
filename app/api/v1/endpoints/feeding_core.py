"""Feeding businesses, farm sites, herds and business grants API (FEED-CORE-015)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_business_service import (
    FeedingBusinessConflict,
    FeedingBusinessNotFound,
    FeedingBusinessService,
)

router = APIRouter(prefix="/feeding", tags=["feeding-core"])

GrantScope = Literal["read", "write", "approve", "admin"]


class FeedingCoreOut(BaseModel):
    """Stable public contract while allowing additive database fields."""

    model_config = ConfigDict(extra="ignore")


class FeedingBusinessOut(FeedingCoreOut):
    id: str
    tenant_id: str
    business_partner_id: str | None = None
    name: str
    production_type: str | None = None
    husbandry_form: str | None = None
    feeding_system: str | None = None
    milking_system: str | None = None
    advisory_status: str
    last_consultation_at: datetime | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    active: bool
    created_by: str
    created_at: datetime
    updated_by: str
    updated_at: datetime
    herd_count: int | None = None
    group_count: int | None = None


class FarmSiteOut(FeedingCoreOut):
    id: str
    tenant_id: str
    business_id: str
    name: str
    address: str | None = None
    active: bool
    created_at: datetime
    updated_at: datetime


class HerdOut(FeedingCoreOut):
    id: str
    tenant_id: str
    business_id: str
    site_id: str | None = None
    name: str
    animal_type: str
    active: bool
    created_at: datetime
    updated_at: datetime


class FeedingGroupSummaryOut(FeedingCoreOut):
    id: str
    name: str
    animal_count: int | None = None
    herd_id: str | None = None


class BusinessStructureOut(FeedingCoreOut):
    business: FeedingBusinessOut
    sites: list[FarmSiteOut]
    herds: list[HerdOut]
    groups: list[FeedingGroupSummaryOut]


class GroupAssignmentOut(FeedingCoreOut):
    id: str
    name: str
    business_id: str
    herd_id: str | None = None


class BackfillOut(FeedingCoreOut):
    business_id: str
    assigned_groups: int


class BusinessGrantOut(FeedingCoreOut):
    id: str
    tenant_id: str
    business_id: str
    subject: str
    scope: GrantScope
    valid_from: datetime
    valid_until: datetime | None = None
    granted_by: str
    revoked_by: str | None = None
    revoked_at: datetime | None = None
    revoke_reason: str | None = None
    created_at: datetime


class RevokeResultOut(FeedingCoreOut):
    removed: int


class FeedingBusinessIn(BaseModel):
    id: str | None = Field(default=None, max_length=80)
    business_partner_id: str | None = Field(default=None, max_length=64)
    name: str = Field(min_length=1, max_length=240)
    production_type: str | None = Field(default=None, max_length=80)
    husbandry_form: str | None = Field(default=None, max_length=80)
    feeding_system: str | None = Field(default=None, max_length=40)
    milking_system: str | None = Field(default=None, max_length=80)
    advisory_status: str | None = Field(default=None, max_length=40)
    preferences: dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class PartnerActivationIn(BaseModel):
    business_partner_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=240)


class FarmSiteIn(BaseModel):
    id: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=240)
    address: str | None = Field(default=None, max_length=400)
    active: bool = True


class HerdIn(BaseModel):
    id: str | None = Field(default=None, max_length=80)
    name: str = Field(min_length=1, max_length=240)
    site_id: str | None = Field(default=None, max_length=80)
    animal_type: str = Field(default="dairy_cow", max_length=40)
    active: bool = True


class GroupAssignmentIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    herd_id: str | None = Field(default=None, max_length=80)


class GrantIn(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    scope: GrantScope
    valid_until: datetime | None = None


def _service(db: Session, tenant_id: str, user: User) -> FeedingBusinessService:
    return FeedingBusinessService(db, tenant_id, str(user.get("sub") or "unknown"))


def _not_found(exc: FeedingBusinessNotFound) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))


def _require_business_scope(service: FeedingBusinessService, business_id: str,
                            user: User, scope: GrantScope) -> None:
    if set(user.get("roles") or []).intersection(APPROVE_ROLES):
        return
    subject = str(user.get("sub") or "")
    if not subject or not service.has_business_access(business_id, subject, scope):
        raise HTTPException(status_code=403, detail="Kein Zugriff auf diesen Fuetterungsbetrieb.")


@router.post("/businesses", response_model=FeedingBusinessOut, status_code=201, summary="Fuetterungsbetrieb anlegen/aktualisieren")
async def upsert_business(body: FeedingBusinessIn, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Fuetterungsbetriebe.")
    try:
        return _service(db, tenant_id, user).upsert_business(body.model_dump())
    except FeedingBusinessConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/businesses/activate-from-partner", response_model=FeedingBusinessOut, status_code=201,
             summary="CRM-Geschaeftspartner ohne Doppelerfassung als Fuetterungsbetrieb aktivieren")
async def activate_from_partner(body: PartnerActivationIn, db: Session = Depends(get_db),
                                tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Fuetterungsbetriebe.")
    return _service(db, tenant_id, user).activate_from_partner(body.business_partner_id, body.name)


@router.get("/businesses", response_model=list[FeedingBusinessOut], summary="Fuetterungsbetriebe auflisten")
async def list_businesses(include_inactive: bool = False, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Fuetterungsbetriebe.")
    unrestricted = bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))
    return _service(db, tenant_id, user).list_businesses(
        include_inactive=include_inactive,
        subject=str(user.get("sub") or ""),
        unrestricted=unrestricted,
    )


@router.get("/businesses/{business_id}", response_model=BusinessStructureOut, summary="Betriebsstruktur (Standorte, Herden, Gruppen)")
async def get_business_structure(business_id: str, db: Session = Depends(get_db),
                                 tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Fuetterungsbetriebe.")
    service = _service(db, tenant_id, user)
    try:
        _require_business_scope(service, business_id, user, "read")
        return service.list_structure(business_id)
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/businesses/{business_id}/sites", response_model=FarmSiteOut, status_code=201, summary="Betriebsstaette anlegen/aktualisieren")
async def upsert_site(business_id: str, body: FarmSiteIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Betriebsstaetten.")
    service = _service(db, tenant_id, user)
    try:
        _require_business_scope(service, business_id, user, "write")
        return service.upsert_site(business_id, body.model_dump())
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/businesses/{business_id}/herds", response_model=HerdOut, status_code=201, summary="Herde anlegen/aktualisieren")
async def upsert_herd(business_id: str, body: HerdIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Herden.")
    service = _service(db, tenant_id, user)
    try:
        _require_business_scope(service, business_id, user, "write")
        return service.upsert_herd(business_id, body.model_dump())
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/businesses/{business_id}/groups", response_model=GroupAssignmentOut, summary="Fuetterungsgruppe dem Betrieb/der Herde zuordnen")
async def assign_group(business_id: str, body: GroupAssignmentIn, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Gruppenzuordnung.")
    service = _service(db, tenant_id, user)
    try:
        _require_business_scope(service, business_id, user, "write")
        return service.assign_group(business_id, body.group_id, body.herd_id)
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc


@router.post("/businesses/backfill-default", response_model=BackfillOut,
             summary="Bestehende Tiergruppen dem Default-Betrieb des Mandanten zuordnen")
async def backfill_default(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, APPROVE_ROLES, detail="Backfill erfordert Futtermittel-Administration.")
    return _service(db, tenant_id, user).backfill_default_business()


@router.post("/businesses/{business_id}/grants", response_model=BusinessGrantOut, status_code=201,
             summary="Betriebszugriff gewaehren (auch zeitlich begrenzt)")
async def grant_access(business_id: str, body: GrantIn, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, APPROVE_ROLES, detail="Grant-Verwaltung erfordert Futtermittel-Administration.")
    try:
        return _service(db, tenant_id, user).grant_access(business_id, body.subject, body.scope, body.valid_until)
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc


@router.delete("/businesses/{business_id}/grants", response_model=RevokeResultOut,
               summary="Betriebszugriff entziehen")
async def revoke_access(business_id: str, subject: str, scope: GrantScope, db: Session = Depends(get_db),
                        reason: str | None = None, tenant_id: str = Depends(get_tenant_id),
                        user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, APPROVE_ROLES, detail="Grant-Verwaltung erfordert Futtermittel-Administration.")
    removed = _service(db, tenant_id, user).revoke_access(business_id, subject, scope, reason)
    return {"removed": removed}


@router.get("/businesses/{business_id}/grants", response_model=list[BusinessGrantOut], summary="Betriebszugriffe auflisten")
async def list_grants(business_id: str, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, APPROVE_ROLES, detail="Grant-Verwaltung erfordert Futtermittel-Administration.")
    try:
        _service(db, tenant_id, user).get_business(business_id)
    except FeedingBusinessNotFound as exc:
        raise _not_found(exc) from exc
    return _service(db, tenant_id, user).list_grants(business_id)
