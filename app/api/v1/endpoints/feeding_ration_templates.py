"""Ration templates and grant-safe feeding-business file API (FEED-EDITOR-025)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.authz import APPROVE_ROLES, READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.ration_templates import RationTemplateValidationError
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_business_service import FeedingBusinessService
from app.services.feeding_ration_template_service import (
    FeedingRationTemplateService,
    RationTemplateConflict,
    RationTemplateNotFound,
)
from app.services.rations_lifecycle_service import (
    RationLifecycleConflict,
    RationLifecycleNotFound,
    RationLifecycleService,
)

router = APIRouter(prefix="/feeding", tags=["feeding-ration-templates"])


class TemplateCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=2_000)
    source_ration_version_id: str = Field(min_length=1, max_length=80)


class TemplateApplyIn(BaseModel):
    target_ration_id: str = Field(min_length=1, max_length=80)
    expected_latest_version_no: int = Field(ge=1)
    reason: str = Field(min_length=10, max_length=2_000)


class TemplateOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    tenant_id: str
    business_id: str
    group_id: str
    name: str
    description: str | None = None
    source_ration_version_id: str
    source_ration_name: str
    source_version_no: int
    snapshot_checksum: str
    created_by: str
    created_at: datetime


class VersionCopyOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    ration_id: str
    version_no: int
    source: str
    based_on_version_id: str
    status: str


class BusinessOverviewOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    name: str
    advisory_status: str
    group_count: int
    ration_count: int
    template_count: int
    active_ration_count: int
    readiness_unknown_count: int
    readiness_blocked_count: int
    data_status: str


def _unrestricted(user: User) -> bool:
    return bool(set(user.get("roles") or []).intersection(APPROVE_ROLES))


def _actor(user: User) -> str:
    return str(user.get("sub") or "unknown")


def _template_service(db: Session, tenant_id: str, user: User) -> FeedingRationTemplateService:
    return FeedingRationTemplateService(db, tenant_id, _actor(user))


def _require_business(db: Session, tenant_id: str, user: User, business_id: str, scope: str) -> None:
    if _unrestricted(user):
        return
    service = FeedingBusinessService(db, tenant_id, _actor(user))
    if not service.has_business_access(business_id, _actor(user), scope):
        raise HTTPException(status_code=404, detail="Fuetterungsbetrieb nicht gefunden.")


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, (RationTemplateNotFound, RationLifecycleNotFound)):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, (RationTemplateConflict, RationLifecycleConflict, RationTemplateValidationError)):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=500, detail="Rationsvorlage konnte nicht verarbeitet werden.")


@router.post("/ration-templates", response_model=TemplateOut, status_code=201)
async def create_template(body: TemplateCreateIn, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        source = db.execute(text("""
          SELECT g.business_id FROM domain_agrar.ration_versions rv
          JOIN domain_agrar.rations r ON r.tenant_id=rv.tenant_id AND r.id=rv.ration_id
          JOIN domain_agrar.feeding_groups g ON g.tenant_id=r.tenant_id AND g.id=r.group_id
          WHERE rv.tenant_id=:tenant_id AND rv.id=:version_id
        """), {"tenant_id": tenant_id, "version_id": body.source_ration_version_id}).mappings().first()
        if not source or not source["business_id"]:
            raise RationTemplateNotFound("Quellversion mit Fuetterungsbetrieb nicht gefunden.")
        _require_business(db, tenant_id, user, source["business_id"], "write")
        return _template_service(db, tenant_id, user).create(
            name=body.name, description=body.description,
            source_version_id=body.source_ration_version_id,
        )
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("/businesses/{business_id}/ration-templates", response_model=list[TemplateOut])
async def list_templates(business_id: str, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    _require_business(db, tenant_id, user, business_id, "read")
    return _template_service(db, tenant_id, user).list_for_business(business_id)


@router.post("/ration-templates/{template_id}/apply", response_model=VersionCopyOut, status_code=201)
async def apply_template(template_id: str, body: TemplateApplyIn, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        service = _template_service(db, tenant_id, user)
        template = service.get(template_id)
        _require_business(db, tenant_id, user, template["business_id"], "write")
        lifecycle = RationLifecycleService(db, tenant_id, _actor(user))
        target = lifecycle.get_ration(body.target_ration_id, include_audit=False)
        if not _unrestricted(user) and not lifecycle.has_group_access(target["group_id"], _actor(user), "write"):
            raise HTTPException(status_code=404, detail="Zielration nicht gefunden.")
        return service.apply(template_id=template_id, target_ration_id=body.target_ration_id,
                             expected_latest_version_no=body.expected_latest_version_no, reason=body.reason)
    except Exception as exc:
        db.rollback()
        raise _translate(exc) from exc


@router.get("/businesses/{business_id}/overview", response_model=BusinessOverviewOut)
async def business_overview(business_id: str, db: Session = Depends(get_db),
                            tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES)
    _require_business(db, tenant_id, user, business_id, "read")
    try:
        return _template_service(db, tenant_id, user).business_overview(business_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/businesses/{business_id}/groups")
async def business_groups(business_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                          user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES); _require_business(db, tenant_id, user, business_id, "read")
    return _template_service(db, tenant_id, user).list_business_groups(business_id)


@router.get("/businesses/{business_id}/rations")
async def business_rations(business_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES); _require_business(db, tenant_id, user, business_id, "read")
    return _template_service(db, tenant_id, user).list_business_rations(business_id)


@router.get("/businesses/{business_id}/findings")
async def business_findings(business_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                            user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES); _require_business(db, tenant_id, user, business_id, "read")
    return _template_service(db, tenant_id, user).list_business_findings(business_id)
