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

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.agrar_drying_rules_schemas import AgrarDryingRulesOut


router = APIRouter()


def _drying_svc(db: Session, tenant_id: str) -> DryingRuleService:
    return DryingRuleService(db, tenant_id)


def _get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request state (token claims)."""
    claims = getattr(request.state, "token_claims", {})
    return claims.get("sub") or claims.get("user_id")


# ── Pydantic schemas ──────────────────────────────────────────────────────────

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

@router.get("/drying-rules", response_model=list[DryingRuleSetOut], summary="Drying rules auflisten")
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


@router.get("/drying-rules/{rule_id}", response_model=DryingRuleSetOut, summary="Drying rule abrufen")
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


@router.post("/drying-rules", response_model=DryingRuleSetOut, status_code=201, summary="Drying rule anlegen")
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


@router.put("/drying-rules/{rule_id}", response_model=DryingRuleSetOut, summary="Drying rule aktualisieren")
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


@router.delete("/drying-rules/{rule_id}", status_code=204, response_class=Response, response_model=None, summary="Drying rule löschen")
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


@router.get("/drying-rules/{rule_id}/download", response_model=AgrarDryingRulesOut, summary="Drying rule document herunterladen")
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

@router.get("/drying-rules/{rule_id}/lookup-rows", response_model=list[DryingLookupRowOut], summary="Drying lookup rows auflisten")
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


@router.post("/drying-rules/lookup-rows", response_model=DryingLookupRowOut, status_code=201, summary="Drying lookup row anlegen")
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


@router.put("/drying-rules/lookup-rows/{row_id}", response_model=DryingLookupRowOut, summary="Drying lookup row aktualisieren")
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


@router.delete("/drying-rules/lookup-rows/{row_id}", status_code=204, response_class=Response, response_model=None, summary="Drying lookup row löschen")
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

@router.get("/drying-rules/{rule_id}/factor-ranges", response_model=list[DryingFactorRangeOut], summary="Drying factor ranges auflisten")
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


@router.post("/drying-rules/factor-ranges", response_model=DryingFactorRangeOut, status_code=201, summary="Drying factor range anlegen")
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


@router.put("/drying-rules/factor-ranges/{range_id}", response_model=DryingFactorRangeOut, summary="Drying factor range aktualisieren")
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


@router.delete("/drying-rules/factor-ranges/{range_id}", status_code=204, response_class=Response, response_model=None, summary="Drying factor range löschen")
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
