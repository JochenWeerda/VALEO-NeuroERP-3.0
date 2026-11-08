"""DOM-CONTROLLING-004 — Budget-Lifecycle, Abweichungsanalyse, KST-Abschluss."""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.api.v1.schemas.finance_controlling_bundle_schemas import (
    ControllingAbweichungOut,
    ControllingBudgetCreatedOut,
    ControllingBudgetTransitionOut,
    ControllingIstWertOut,
    ControllingKstAbschlussOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.akteur import gepruefter_akteur_aus_request  # Bearbeiter aus dem Token

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

@router.post("/budgets", response_model=ControllingBudgetCreatedOut, status_code=201, summary="Controlling-Budget anlegen", dependencies=SCHREIBEN["CONTROLLING"])
def create_budget(
    body: BudgetCreateRequest,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_budget_lifecycle_service import create_budget as svc, BudgetLifecycleError
    try:
        return svc(db, tenant_id, body.kostenstelle_id, body.periode, body.plan_eur, body.bezeichnung, gepruefter_akteur_aus_request(request))
    except BudgetLifecycleError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/budgets/{budget_id}/transition",
    response_model=ControllingBudgetTransitionOut,
    summary="Controlling-Budgetstatus wechseln", dependencies=SCHREIBEN["CONTROLLING"])
def transition_budget(
    budget_id: str,
    body: BudgetTransitionRequest,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_budget_lifecycle_service import transition_budget_status, BudgetLifecycleError
    try:
        return transition_budget_status(db, budget_id, tenant_id, body.new_status, gepruefter_akteur_aus_request(request))
    except BudgetLifecycleError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/abweichung", response_model=ControllingAbweichungOut, summary="Plan-Ist-Abweichung abrufen")
def get_abweichung(
    kostenstelle_id: str,
    periode: str,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_abweichung_service import get_abweichung as svc
    return svc(db, tenant_id, kostenstelle_id, periode)


@router.post("/ist-werte", response_model=ControllingIstWertOut, status_code=201, summary="Ist-Wert buchen", dependencies=SCHREIBEN["CONTROLLING"])
def buche_ist_wert(
    body: IstWertRequest,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_abweichung_service import buche_ist_wert as svc
    try:
        return svc(db, tenant_id, body.kostenstelle_id, body.periode, body.ist_eur, body.buchungsref, gepruefter_akteur_aus_request(request))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/abweichung/drill-down",
    response_model=list[ControllingAbweichungOut],
    summary="Plan-Ist-Abweichungs-Drilldown abrufen",
)
def drill_down(
    periode: str,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
):
    from app.services.controlling_abweichung_service import list_abweichungen_drill_down
    return list_abweichungen_drill_down(db, tenant_id, periode)


@router.post(
    "/kostenstellen/{kostenstelle_id}/abschluss",
    response_model=ControllingKstAbschlussOut,
    summary="Kostenstellenabschluss fortschreiben", dependencies=SCHREIBEN["CONTROLLING"])
def advance_abschluss(
    kostenstelle_id: str,
    body: KSTAbschlussRequest,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db=Depends(get_db),
) -> Dict[str, Any]:
    from app.services.controlling_kostenstellen_abschluss_service import advance_kst_abschluss, KSTAbschlussError
    try:
        return advance_kst_abschluss(db, kostenstelle_id, body.periode, tenant_id, body.new_status, gepruefter_akteur_aus_request(request))
    except KSTAbschlussError as e:
        raise HTTPException(status_code=422, detail=str(e))
