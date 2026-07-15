"""Canonical feeding feed catalog API (FEED-CORE-018)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.agrar.rations.feed_catalog import FeedApprovalStatus, FeedKind
from app.agrar.rations.reference_data import MatterBasis
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_feed_catalog_service import (
    FeedCatalogConflict,
    FeedCatalogNotFound,
    FeedingFeedCatalogService,
)

router = APIRouter(prefix="/feed-catalog", tags=["feeding-feed-catalog"])


class FeedCatalogOut(BaseModel):
    model_config = ConfigDict(extra="ignore")


class FeedProductOut(FeedCatalogOut):
    id: str
    feed_id: str
    supplier_partner_id: str | None = None
    sku: str
    display_name: str
    packaging_unit: str
    package_size: Decimal
    minimum_order_qty: Decimal | None = None
    price_eur_t: Decimal | None = None
    freight_eur_t: Decimal = Decimal("0")
    valid_from: date
    valid_until: date | None = None
    active: bool
    revision: int


class FeedReferenceValueOut(FeedCatalogOut):
    id: str
    feed_id: str
    nutrient_code: str
    nutrient_name: str | None = None
    value: Decimal
    unit_code: str
    basis: MatterBasis
    value_status: str
    source_type: str
    source_ref: str | None = None
    valid_from: date
    valid_until: date | None = None
    priority: int
    revision: int


class FeedSummaryOut(FeedCatalogOut):
    id: str
    tenant_id: str
    artikel_nummer: str
    name: str
    art: str
    feed_kind: FeedKind
    species_scope: str | None = None
    approval_status: FeedApprovalStatus
    valid_from: date
    valid_until: date | None = None
    revision: int
    trockensubstanz: Decimal | None = None
    preis_pro_t: Decimal | None = None
    aktiv: bool
    updated_at: datetime | None = None


class FeedDetailOut(FeedSummaryOut):
    herkunft: str | None = None
    lieferant: str | None = None
    conservation_method: str | None = None
    protein: Decimal | None = None
    energie: Decimal | None = None
    faser: Decimal | None = None
    fett: Decimal | None = None
    asche: Decimal | None = None
    gvo_status: str | None = None
    qs_milch: bool = False
    gmp_plus: bool = False
    bio_zertifiziert: bool = False
    verfuegbar_t: Decimal = Decimal("0")
    einheit: str = "t"
    min_bestand_t: Decimal | None = None
    inventory_article_id: str | None = None
    reference_values: list[FeedReferenceValueOut] = Field(default_factory=list)
    products: list[FeedProductOut] = Field(default_factory=list)
    solver_feed: dict[str, Any] = Field(default_factory=dict)


class FeedRevisionOut(FeedCatalogOut):
    id: str
    feed_id: str
    revision: int
    snapshot: dict[str, Any]
    reason: str
    changed_by: str
    changed_at: datetime


class FeedCreateIn(BaseModel):
    id: str | None = None
    artikel_nummer: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    art: str = Field(min_length=1, max_length=100)
    feed_kind: FeedKind
    species_scope: str | None = None
    conservation_method: str | None = None
    approval_status: FeedApprovalStatus = FeedApprovalStatus.DRAFT
    valid_from: date | None = None
    valid_until: date | None = None
    herkunft: str | None = None
    lieferant: str | None = None
    protein: Decimal | None = Field(default=None, ge=0, le=100)
    energie: Decimal | None = Field(default=None, ge=0)
    faser: Decimal | None = Field(default=None, ge=0, le=100)
    fett: Decimal | None = Field(default=None, ge=0, le=100)
    asche: Decimal | None = Field(default=None, ge=0, le=100)
    trockensubstanz: Decimal | None = Field(default=None, gt=0, le=100)
    gvo_status: str | None = None
    qs_milch: bool = False
    gmp_plus: bool = False
    bio_zertifiziert: bool = False
    verfuegbar_t: Decimal = Field(default=Decimal("0"), ge=0)
    einheit: str = "t"
    min_bestand_t: Decimal | None = Field(default=None, ge=0)
    preis_pro_t: Decimal | None = Field(default=None, ge=0)
    aktiv: bool = True


class FeedUpdateIn(BaseModel):
    expected_revision: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    art: str | None = Field(default=None, min_length=1, max_length=100)
    feed_kind: FeedKind | None = None
    species_scope: str | None = None
    conservation_method: str | None = None
    approval_status: FeedApprovalStatus | None = None
    valid_from: date | None = None
    valid_until: date | None = None
    trockensubstanz: Decimal | None = Field(default=None, gt=0, le=100)
    protein: Decimal | None = Field(default=None, ge=0, le=100)
    energie: Decimal | None = Field(default=None, ge=0)
    preis_pro_t: Decimal | None = Field(default=None, ge=0)
    aktiv: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "FeedUpdateIn":
        if not self.model_fields_set.difference({"expected_revision", "reason"}):
            raise ValueError("Mindestens ein Futtermittelfeld muss geaendert werden.")
        return self


class FeedReferenceValueIn(BaseModel):
    id: str | None = None
    nutrient_code: str = Field(min_length=1, max_length=60)
    value: Decimal
    unit_code: str = Field(min_length=1, max_length=40)
    basis: MatterBasis
    value_status: str = Field(default="reference", pattern="^(reference|estimated|analyzed)$")
    source_type: str = Field(min_length=1, max_length=40)
    source_ref: str | None = None
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None
    priority: int = 0
    revision: int = 1


class FeedProductIn(BaseModel):
    id: str | None = None
    supplier_partner_id: str | None = None
    sku: str = Field(min_length=1, max_length=80)
    display_name: str = Field(min_length=1, max_length=240)
    packaging_unit: str = "t"
    package_size: Decimal = Field(default=Decimal("1"), gt=0)
    minimum_order_qty: Decimal | None = Field(default=None, ge=0)
    price_eur_t: Decimal | None = Field(default=None, ge=0)
    freight_eur_t: Decimal = Field(default=Decimal("0"), ge=0)
    valid_from: date = Field(default_factory=date.today)
    valid_until: date | None = None
    active: bool = True


def _service(db: Session, tenant_id: str, user: User) -> FeedingFeedCatalogService:
    return FeedingFeedCatalogService(db, tenant_id, str(user.get("sub") or "unknown"))


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, FeedCatalogNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, FeedCatalogConflict):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.get("/feeds", response_model=list[FeedSummaryOut])
async def list_feeds(search: str | None = None, include_inactive: bool = False,
                     db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return _service(db, tenant_id, user).list_feeds(search=search, include_inactive=include_inactive)


@router.post("/feeds", response_model=FeedDetailOut, status_code=201)
async def create_feed(body: FeedCreateIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).create_feed(body.model_dump())
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/feeds/{feed_id}", response_model=FeedDetailOut)
async def get_feed(feed_id: str, db: Session = Depends(get_db),
                   tenant_id: str = Depends(get_tenant_id),
                   user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).get_feed(feed_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.patch("/feeds/{feed_id}", response_model=FeedDetailOut)
async def update_feed(feed_id: str, body: FeedUpdateIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).update_feed(feed_id, body.model_dump(exclude_unset=True))
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/feeds/{feed_id}/history", response_model=list[FeedRevisionOut])
async def feed_history(feed_id: str, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).history(feed_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/feeds/{feed_id}/reference-values", response_model=list[FeedReferenceValueOut])
async def list_values(feed_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).list_reference_values(feed_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/feeds/{feed_id}/reference-values", response_model=FeedReferenceValueOut, status_code=201)
async def add_value(feed_id: str, body: FeedReferenceValueIn, db: Session = Depends(get_db),
                    tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).add_reference_value(feed_id, body.model_dump())
    except Exception as exc:
        raise _translate(exc) from exc


@router.get("/feeds/{feed_id}/products", response_model=list[FeedProductOut])
async def list_products(feed_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                        user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    try:
        return _service(db, tenant_id, user).list_products(feed_id)
    except Exception as exc:
        raise _translate(exc) from exc


@router.post("/feeds/{feed_id}/products", response_model=FeedProductOut, status_code=201)
async def add_product(feed_id: str, body: FeedProductIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id), user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES)
    try:
        return _service(db, tenant_id, user).add_product(feed_id, body.model_dump())
    except Exception as exc:
        raise _translate(exc) from exc
