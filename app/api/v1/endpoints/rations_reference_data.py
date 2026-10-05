"""Feeding nutrient, unit and matter-basis reference API (FEED-CORE-017)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, require_roles
from app.agrar.rations.reference_data import BasisValueKind, MatterBasis, RoundingMode
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.rations_reference_data_service import RationsReferenceDataService

router = APIRouter(prefix="/reference-data", tags=["rations-reference-data"])


class ReferenceOut(BaseModel):
    model_config = ConfigDict(extra="ignore")


class NutrientDefinitionOut(ReferenceOut):
    id: str
    tenant_id: str | None = None
    code: str
    display_name: str
    canonical_unit_code: str
    default_basis: MatterBasis
    value_kind: BasisValueKind
    minimum_value: Decimal | None = None
    maximum_value: Decimal | None = None
    sort_order: int
    revision: int
    source: str
    active: bool
    updated_at: datetime


class UnitDefinitionOut(ReferenceOut):
    id: str
    tenant_id: str | None = None
    code: str
    display_name: str
    dimension: str
    factor_to_base: Decimal
    precision: int
    revision: int
    source: str
    active: bool
    updated_at: datetime


class BasisConversionIn(BaseModel):
    value: Decimal
    from_basis: MatterBasis
    to_basis: MatterBasis
    dry_matter_pct: Decimal = Field(gt=0, le=100)
    kind: BasisValueKind = BasisValueKind.QUANTITY
    precision: int = Field(default=3, ge=0, le=12)
    rounding_mode: RoundingMode = RoundingMode.HALF_UP


class BasisConversionOut(BaseModel):
    value: Decimal
    unrounded_value: Decimal
    from_basis: MatterBasis
    to_basis: MatterBasis
    dry_matter_pct: Decimal
    kind: BasisValueKind
    precision: int
    rounding_mode: RoundingMode


def _service(db: Session, tenant_id: str) -> RationsReferenceDataService:
    return RationsReferenceDataService(db, tenant_id)


@router.get("/nutrients", response_model=list[NutrientDefinitionOut], summary="Naehrstoffdefinitionen auflisten")
async def list_nutrients(include_inactive: bool = False, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Fuetterungs-Referenzdaten.")
    return _service(db, tenant_id).list_nutrients(include_inactive=include_inactive)


@router.get("/units", response_model=list[UnitDefinitionOut], summary="Einheitendefinitionen auflisten")
async def list_units(include_inactive: bool = False, db: Session = Depends(get_db),
                     tenant_id: str = Depends(get_tenant_id),
                     user: User = Depends(get_current_user)) -> list[dict]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Fuetterungs-Referenzdaten.")
    return _service(db, tenant_id).list_units(include_inactive=include_inactive)


@router.post("/convert-basis", response_model=BasisConversionOut, summary="Frischmasse/Trockenmasse konvertieren")
async def convert_matter_basis(body: BasisConversionIn, db: Session = Depends(get_db),
                               tenant_id: str = Depends(get_tenant_id),
                               user: User = Depends(get_current_user)) -> dict:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Fuetterungs-Referenzdaten.")
    try:
        return _service(db, tenant_id).convert_matter_basis(**body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
