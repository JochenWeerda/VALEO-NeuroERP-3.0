"""
Agrar Drying Rule Sets, Lookup Rows, and Factor Ranges — CRUD endpoints.

Routes are mounted at /agrar/settlements to preserve API paths:
  GET/POST /agrar/settlements/drying-rules
  GET/PUT/DELETE /agrar/settlements/drying-rules/{rule_id}
  GET /agrar/settlements/drying-rules/{rule_id}/download
  CRUD /agrar/settlements/drying-rules/lookup-rows/...
  CRUD /agrar/settlements/drying-rules/factor-ranges/...
"""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.domains.inventory.api.inventory_auth import require_inventory_admin
from app.infrastructure.models import DryingRuleFactorRange, DryingRuleLookupRow, DryingRuleSet
from app.services.agrar_drying_rule_service import DryingRuleService

router = APIRouter()


def _drying_svc(db: Session, tenant_id: str) -> DryingRuleService:
    return DryingRuleService(db, tenant_id)


def _get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request state (token claims)."""
    claims = getattr(request.state, "token_claims", {})
    return claims.get("sub") or claims.get("user_id")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class DryingRuleSetCreate(BaseModel):
    crop_code: str = Field(..., min_length=1, max_length=40)
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"] = Field(...)
    base_moisture_pct: float = Field(..., ge=0, le=100)
    rounding_mode: Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"] = Field(default="ROUND_NEAREST")
    clamp_mode: Literal["CLAMP_TO_MAX", "HARD_ERROR"] = Field(default="HARD_ERROR")
    min_moisture_pct: float = Field(default=0, ge=0, le=100)
    max_moisture_pct: float = Field(default=60, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Literal["INVOICE_WEIGHT", "NET_WEIGHT"] = Field(default="INVOICE_WEIGHT")
    contract_id: Optional[str] = Field(None, description="Verknüpfung zu Ankaufskontrakt (optional)")
    customer_id: Optional[str] = Field(None, description="Kunde für Sonderregelung (optional)")
    is_customer_specific: bool = Field(default=False)
    justification: Optional[str] = Field(None, description="Begründung für kundenspezifische Sonderregelungen (erforderlich wenn is_customer_specific=True)")
    document_id: Optional[str] = Field(None, max_length=64, description="DMS-Referenz für Tabelle/Formel-Dokument")

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetUpdate(BaseModel):
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Optional[Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"]] = None
    base_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    rounding_mode: Optional[Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"]] = None
    clamp_mode: Optional[Literal["CLAMP_TO_MAX", "HARD_ERROR"]] = None
    min_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    max_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Optional[Literal["INVOICE_WEIGHT", "NET_WEIGHT"]] = None
    contract_id: Optional[str] = None
    customer_id: Optional[str] = None
    is_customer_specific: Optional[bool] = None
    justification: Optional[str] = None
    document_id: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific is True and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific is True and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetOut(BaseModel):
    id: str
    crop_code: str
    site_id: Optional[str]
    valid_from: Optional[str]
    valid_to: Optional[str]
    version: int
    is_active: bool
    method: str
    base_moisture_pct: float
    rounding_mode: str
    clamp_mode: str
    min_moisture_pct: float
    max_moisture_pct: float
    start_threshold_moisture_pct: Optional[float]
    fee_basis: str
    created_at: str
    created_by: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]
    contract_id: Optional[str]
    customer_id: Optional[str]
    is_customer_specific: bool
    justification: Optional[str]
    document_id: Optional[str]


class DryingLookupRowCreate(BaseModel):
    rule_set_id: str
    moisture_pct: float = Field(..., ge=0, le=100, description="Feuchte in % (0.1-Schritte)")
    entzug_pct_points: float = Field(..., ge=0, description="Entzug in %-Punkten")
    loss_pct: float = Field(..., ge=0, le=100, description="Schwund in %")
    fee_value: Optional[float] = Field(None, ge=0, description="Trocknungskosten (optional)")
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = Field(None, description="Einheit der Trocknungskosten")


class DryingLookupRowUpdate(BaseModel):
    moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    entzug_pct_points: Optional[float] = Field(None, ge=0)
    loss_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_value: Optional[float] = Field(None, ge=0)
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = None


class DryingLookupRowOut(BaseModel):
    id: str
    rule_set_id: str
    moisture_pct: float
    entzug_pct_points: float
    loss_pct: float
    fee_value: Optional[float]
    fee_unit: Optional[str]
    created_at: str


class DryingFactorRangeCreate(BaseModel):
    rule_set_id: str
    from_moisture_incl: float = Field(..., ge=0, le=100, description="Von Feuchte in % (inklusive, 0.1-Schritte)")
    to_moisture_incl: float = Field(..., ge=0, le=100, description="Bis Feuchte in % (inklusive, 0.1-Schritte)")
    factor: float = Field(..., gt=0, description="Faktor für Schwundberechnung")

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl > self.to_moisture_incl:
            raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeUpdate(BaseModel):
    from_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    to_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    factor: Optional[float] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl is not None and self.to_moisture_incl is not None:
            if self.from_moisture_incl > self.to_moisture_incl:
                raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeOut(BaseModel):
    id: str
    rule_set_id: str
    from_moisture_incl: float
    to_moisture_incl: float
    factor: float
    created_at: str


# ── Serialization helpers ─────────────────────────────────────────────────────

def _to_drying_rule_out(r: DryingRuleSet) -> DryingRuleSetOut:
    return DryingRuleSetOut(
        id=r.id,
        crop_code=r.crop_code,
        site_id=r.site_id,
        valid_from=r.valid_from.isoformat() if r.valid_from else None,
        valid_to=r.valid_to.isoformat() if r.valid_to else None,
        version=int(r.version),
        is_active=r.is_active,
        method=r.method,
        base_moisture_pct=float(r.base_moisture_pct),
        rounding_mode=r.rounding_mode,
        clamp_mode=r.clamp_mode,
        min_moisture_pct=float(r.min_moisture_pct),
        max_moisture_pct=float(r.max_moisture_pct),
        start_threshold_moisture_pct=float(r.start_threshold_moisture_pct) if r.start_threshold_moisture_pct else None,
        fee_basis=r.fee_basis,
        created_at=r.created_at.isoformat() if r.created_at else "",
        created_by=r.created_by,
        updated_at=r.updated_at.isoformat() if r.updated_at else None,
        updated_by=r.updated_by,
        contract_id=r.contract_id,
        customer_id=r.customer_id,
        is_customer_specific=r.is_customer_specific,
        justification=r.justification,
        document_id=r.document_id,
    )


def _to_lookup_row_out(r: DryingRuleLookupRow) -> DryingLookupRowOut:
    return DryingLookupRowOut(
        id=r.id,
        rule_set_id=r.rule_set_id,
        moisture_pct=float(r.moisture_pct),
        entzug_pct_points=float(r.entzug_pct_points),
        loss_pct=float(r.loss_pct),
        fee_value=float(r.fee_value) if r.fee_value is not None else None,
        fee_unit=r.fee_unit,
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


def _to_factor_range_out(r: DryingRuleFactorRange) -> DryingFactorRangeOut:
    return DryingFactorRangeOut(
        id=r.id,
        rule_set_id=r.rule_set_id,
        from_moisture_incl=float(r.from_moisture_incl),
        to_moisture_incl=float(r.to_moisture_incl),
        factor=float(r.factor),
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


# ── DryingRuleSet routes ──────────────────────────────────────────────────────

@router.get("/drying-rules", response_model=list[DryingRuleSetOut])
async def list_drying_rules(
    crop_code: Optional[str] = Query(None),
    contract_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    is_customer_specific: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Trocknungs-/Schwundtabellen (Leserechte für alle)."""
    rules = _drying_svc(db, tenant_id).list_rules(
        crop_code=crop_code, contract_id=contract_id,
        customer_id=customer_id, is_customer_specific=is_customer_specific,
    )
    return [_to_drying_rule_out(r) for r in rules]


@router.get("/drying-rules/{rule_id}", response_model=DryingRuleSetOut)
async def get_drying_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelne Trocknungs-/Schwundtabelle abrufen (Leserechte für alle)."""
    try:
        rule = _drying_svc(db, tenant_id).get_rule(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return _to_drying_rule_out(rule)


@router.post("/drying-rules", response_model=DryingRuleSetOut, status_code=201)
async def create_drying_rule(
    payload: DryingRuleSetCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Neue Trocknungs-/Schwundtabelle anlegen (nur Admin)."""
    user_id = _get_user_id_from_request(request) or "system"
    rule = _drying_svc(db, tenant_id).create_rule(payload, user_id)
    return _to_drying_rule_out(rule)


@router.put("/drying-rules/{rule_id}", response_model=DryingRuleSetOut)
async def update_drying_rule(
    rule_id: str,
    payload: DryingRuleSetUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Trocknungs-/Schwundtabelle aktualisieren (nur Admin). Erstellt neue Version bei Änderungen."""
    user_id = _get_user_id_from_request(request) or "system"
    try:
        rule = _drying_svc(db, tenant_id).update_rule(rule_id, payload, user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return _to_drying_rule_out(rule)


@router.delete("/drying-rules/{rule_id}", status_code=204, response_class=Response)
async def delete_drying_rule(
    rule_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Trocknungs-/Schwundtabelle löschen (nur Admin). Soft-Delete: is_active=False."""
    user_id = _get_user_id_from_request(request) or "system"
    try:
        _drying_svc(db, tenant_id).delete_rule(rule_id, user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


@router.get("/drying-rules/{rule_id}/download", response_model=dict)
async def download_drying_rule_document(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Portal-Download für Trocknungs-/Schwundtabelle (für Kunden)."""
    try:
        return _drying_svc(db, tenant_id).get_rule_download_data(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ── Lookup Rows ───────────────────────────────────────────────────────────────

@router.get("/drying-rules/{rule_id}/lookup-rows", response_model=list[DryingLookupRowOut])
async def list_drying_lookup_rows(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lookup-Rows einer Regel auflisten (Leserechte für alle)."""
    try:
        rows = _drying_svc(db, tenant_id).list_lookup_rows(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return [_to_lookup_row_out(r) for r in rows]


@router.post("/drying-rules/lookup-rows", response_model=DryingLookupRowOut, status_code=201)
async def create_drying_lookup_row(
    payload: DryingLookupRowCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Lookup-Row anlegen (nur Admin)."""
    try:
        row = _drying_svc(db, tenant_id).create_lookup_row(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_lookup_row_out(row)


@router.put("/drying-rules/lookup-rows/{row_id}", response_model=DryingLookupRowOut)
async def update_drying_lookup_row(
    row_id: str,
    payload: DryingLookupRowUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Lookup-Row aktualisieren (nur Admin)."""
    try:
        row = _drying_svc(db, tenant_id).update_lookup_row(row_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_lookup_row_out(row)


@router.delete("/drying-rules/lookup-rows/{row_id}", status_code=204, response_class=Response)
async def delete_drying_lookup_row(
    row_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Lookup-Row löschen (nur Admin)."""
    try:
        _drying_svc(db, tenant_id).delete_lookup_row(row_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ── Factor Ranges ─────────────────────────────────────────────────────────────

@router.get("/drying-rules/{rule_id}/factor-ranges", response_model=list[DryingFactorRangeOut])
async def list_drying_factor_ranges(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Factor-Ranges einer Regel auflisten (Leserechte für alle)."""
    try:
        ranges = _drying_svc(db, tenant_id).list_factor_ranges(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return [_to_factor_range_out(r) for r in ranges]


@router.post("/drying-rules/factor-ranges", response_model=DryingFactorRangeOut, status_code=201)
async def create_drying_factor_range(
    payload: DryingFactorRangeCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Factor-Range anlegen (nur Admin)."""
    try:
        range_obj = _drying_svc(db, tenant_id).create_factor_range(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_factor_range_out(range_obj)


@router.put("/drying-rules/factor-ranges/{range_id}", response_model=DryingFactorRangeOut)
async def update_drying_factor_range(
    range_id: str,
    payload: DryingFactorRangeUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Factor-Range aktualisieren (nur Admin)."""
    try:
        range_obj = _drying_svc(db, tenant_id).update_factor_range(range_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_factor_range_out(range_obj)


@router.delete("/drying-rules/factor-ranges/{range_id}", status_code=204, response_class=Response)
async def delete_drying_factor_range(
    range_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),
):
    """Factor-Range löschen (nur Admin)."""
    try:
        _drying_svc(db, tenant_id).delete_factor_range(range_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
