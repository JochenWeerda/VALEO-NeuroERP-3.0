"""DOM-POS-004 — POS Tagesabschluss: Z-Bon, TSE-Simulation, DSFinV-K."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter(prefix="/pos/tagesabschluss", tags=["pos-tagesabschluss"])
logger = logging.getLogger(__name__)


class TagesabschlussCreateRequest(BaseModel):
    kasse_id: str
    datum: str
    operator: str = "system"


class TagesabschlussTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    z_bon_nr: Optional[str] = None
    tse_signatur: Optional[str] = None
    dsfinvk_export_pfad: Optional[str] = None
    umsatz_brutto_eur: Optional[float] = None
    fehler_grund: Optional[str] = None


@router.post("", response_model=Dict[str, Any])
def create_tagesabschluss(
    req: TagesabschlussCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.pos_tagesabschluss_service import (
        create_tagesabschluss as svc,
        POSTagesabschlussError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            kasse_id=req.kasse_id,
            datum=req.datum,
            operator=req.operator,
        )
    except POSTagesabschlussError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{abschluss_id}/transition", response_model=Dict[str, Any])
def transition_tagesabschluss(
    abschluss_id: str,
    req: TagesabschlussTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.pos_tagesabschluss_service import (
        transition_tagesabschluss as svc,
        POSTagesabschlussError,
    )
    payload = {}
    if req.z_bon_nr:
        payload["z_bon_nr"] = req.z_bon_nr
    if req.tse_signatur:
        payload["tse_signatur"] = req.tse_signatur
    if req.dsfinvk_export_pfad:
        payload["dsfinvk_export_pfad"] = req.dsfinvk_export_pfad
    if req.umsatz_brutto_eur is not None:
        payload["umsatz_brutto_eur"] = req.umsatz_brutto_eur
    if req.fehler_grund:
        payload["fehler_grund"] = req.fehler_grund
    try:
        return svc(
            db=db,
            abschluss_id=abschluss_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            payload=payload or None,
        )
    except POSTagesabschlussError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tse/simulate", response_model=Dict[str, Any])
def simulate_tse(
    kasse_id: str,
    z_bon_nr: str,
    umsatz_brutto_eur: float,
    x_tenant_id: str = Header(...),
):
    """Simulierte TSE-Signatur für Tests und Demo — kein echtes TSE-Gerät."""
    from app.services.pos_tagesabschluss_service import simulate_tse_signatur
    return simulate_tse_signatur(kasse_id, z_bon_nr, umsatz_brutto_eur)
