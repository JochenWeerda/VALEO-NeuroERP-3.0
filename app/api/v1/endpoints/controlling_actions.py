"""DOM-CONTROLLING-004 — Budget-Lifecycle, Abweichungsanalyse, KST-Abschluss."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter(prefix="/controlling", tags=["controlling"])
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BudgetCreateRequest(BaseModel):
    kostenstelle_id: str
    periode: str
    plan_eur: float
    bezeichnung: str = ""
    operator: str = "system"


class BudgetTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"


class IstWertRequest(BaseModel):
    kostenstelle_id: str
    periode: str
    ist_eur: float
    buchungsref: str
    operator: str = "system"


class KSTAbschlussRequest(BaseModel):
    periode: str
    new_status: str
    operator: str = "system"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/budgets", response_model=dict[str, Any], status_code=201)
def create_budget(
    body: BudgetCreateRequest,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_budget_lifecycle_service import create_budget as svc, BudgetLifecycleError
    tenant_id = x_tenant_id or "default"
    try:
        return svc(db, tenant_id, body.kostenstelle_id, body.periode, body.plan_eur, body.bezeichnung, body.operator)
    except BudgetLifecycleError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/budgets/{budget_id}/transition", response_model=dict[str, Any])
def transition_budget(
    budget_id: str,
    body: BudgetTransitionRequest,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_budget_lifecycle_service import transition_budget_status, BudgetLifecycleError
    tenant_id = x_tenant_id or "default"
    try:
        return transition_budget_status(db, budget_id, tenant_id, body.new_status, body.operator)
    except BudgetLifecycleError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/abweichung", response_model=dict[str, Any])
def get_abweichung(
    kostenstelle_id: str,
    periode: str,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_abweichung_service import get_abweichung as svc
    tenant_id = x_tenant_id or "default"
    return svc(db, tenant_id, kostenstelle_id, periode)


@router.post("/ist-werte", response_model=dict[str, Any], status_code=201)
def buche_ist_wert(
    body: IstWertRequest,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_abweichung_service import buche_ist_wert as svc
    tenant_id = x_tenant_id or "default"
    try:
        return svc(db, tenant_id, body.kostenstelle_id, body.periode, body.ist_eur, body.buchungsref, body.operator)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/abweichung/drill-down", response_model=dict[str, Any])
def drill_down(
    periode: str,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
):
    from app.services.controlling_abweichung_service import list_abweichungen_drill_down
    tenant_id = x_tenant_id or "default"
    return list_abweichungen_drill_down(db, tenant_id, periode)


@router.post("/kostenstellen/{kostenstelle_id}/abschluss", response_model=dict[str, Any])
def advance_abschluss(
    kostenstelle_id: str,
    body: KSTAbschlussRequest,
    x_tenant_id: Optional[str] = Header(None),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss, KSTAbschlussError
    tenant_id = x_tenant_id or "default"
    try:
        return advance_kst_abschluss(db, kostenstelle_id, body.periode, tenant_id, body.new_status, body.operator)
    except KSTAbschlussError as e:
        raise HTTPException(status_code=422, detail=str(e))
