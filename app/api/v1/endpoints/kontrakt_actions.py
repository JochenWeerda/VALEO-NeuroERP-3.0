"""DOM-CON-004 — Kontrakt Lifecycle, Fixing, Settlement."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter(prefix="/kontrakte", tags=["kontrakte-lifecycle"])
logger = logging.getLogger(__name__)


class KontraktCreateRequest(BaseModel):
    kontrakt_id: str
    kontrakt_nr: str
    artikel_id: str
    menge_t: float
    preis_eur_t: float
    lieferant_id: str
    periode: str
    operator: str = "system"


class KontraktTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    grund: str = ""


class FixingCreateRequest(BaseModel):
    kontrakt_id: str
    fixing_datum: str
    fixing_preis_eur_t: float
    menge_t: float
    markt: str = "KASSA"
    referenz: str
    operator: str = "system"


class SettlementCreateRequest(BaseModel):
    kontrakt_id: str
    lieferung_datum: str
    gelieferte_menge_t: float
    abrechnungspreis_eur_t: float
    referenz: str
    operator: str = "system"


class SettlementTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    storno_grund: str = ""


@router.post("/lifecycle", response_model=Dict[str, Any], summary="Kontrakt-Lifecycle anlegen")
def create_kontrakt_lifecycle(
    req: KontraktCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_lifecycle_service import (
        create_kontrakt_lifecycle as svc_create,
        KontraktLifecycleError,
    )
    try:
        result = svc_create(
            db=db,
            kontrakt_id=req.kontrakt_id,
            tenant_id=x_tenant_id,
            kontrakt_nr=req.kontrakt_nr,
            artikel_id=req.artikel_id,
            menge_t=req.menge_t,
            preis_eur_t=req.preis_eur_t,
            lieferant_id=req.lieferant_id,
            periode=req.periode,
            operator=req.operator,
        )
        return result
    except KontraktLifecycleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/lifecycle/{kontrakt_id}/transition",
    response_model=Dict[str, Any],
    summary="Kontraktstatus wechseln",
)
def transition_kontrakt(
    kontrakt_id: str,
    req: KontraktTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_lifecycle_service import (
        transition_kontrakt as svc_transition,
        KontraktLifecycleError,
    )
    try:
        return svc_transition(
            db=db,
            kontrakt_id=kontrakt_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            grund=req.grund,
        )
    except KontraktLifecycleError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lifecycle/{kontrakt_id}", response_model=Dict[str, Any], summary="Kontrakt-Lifecycle abrufen")
def get_kontrakt_lifecycle(
    kontrakt_id: str,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_lifecycle_service import _fetch_kontrakt_lifecycle
    rec = _fetch_kontrakt_lifecycle(db, kontrakt_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Kontrakt nicht gefunden")
    return rec


@router.post("/fixing", response_model=Dict[str, Any], summary="Kontrakt-Fixing anlegen")
def create_fixing(
    req: FixingCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_fixing_service import create_fixing as svc, KontraktFixingError
    try:
        return svc(
            db=db,
            kontrakt_id=req.kontrakt_id,
            tenant_id=x_tenant_id,
            fixing_datum=req.fixing_datum,
            fixing_preis_eur_t=req.fixing_preis_eur_t,
            menge_t=req.menge_t,
            markt=req.markt,
            referenz=req.referenz,
            operator=req.operator,
        )
    except KontraktFixingError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/fixing/{kontrakt_id}/summary",
    response_model=Dict[str, Any],
    summary="Kontrakt-Fixing-Zusammenfassung abrufen",
)
def get_fixing_summary(
    kontrakt_id: str,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_fixing_service import get_fixing_summary as svc
    return svc(db=db, kontrakt_id=kontrakt_id, tenant_id=x_tenant_id)


@router.post("/settlement", response_model=Dict[str, Any], summary="Kontrakt-Settlement anlegen")
def create_settlement(
    req: SettlementCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_settlement_service import (
        create_settlement as svc,
        KontraktSettlementError,
    )
    try:
        return svc(
            db=db,
            kontrakt_id=req.kontrakt_id,
            tenant_id=x_tenant_id,
            lieferung_datum=req.lieferung_datum,
            gelieferte_menge_t=req.gelieferte_menge_t,
            abrechnungspreis_eur_t=req.abrechnungspreis_eur_t,
            referenz=req.referenz,
            operator=req.operator,
        )
    except KontraktSettlementError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/settlement/{settlement_id}/transition",
    response_model=Dict[str, Any],
    summary="Kontrakt-Settlement-Status wechseln",
)
def transition_settlement(
    settlement_id: str,
    req: SettlementTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.kontrakt_settlement_service import (
        transition_settlement as svc,
        KontraktSettlementError,
    )
    try:
        return svc(
            db=db,
            settlement_id=settlement_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            storno_grund=req.storno_grund,
        )
    except KontraktSettlementError as e:
        raise HTTPException(status_code=400, detail=str(e))
