"""DOM-MEL-004 — Meldewesen Lifecycle: Intrastat, ELSTER, ATLAS."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.schemas.base import TypedObjectOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.akteur import gepruefter_akteur_aus_request  # Bearbeiter aus dem Token

router = APIRouter(prefix="/meldewesen/lifecycle", tags=["meldewesen-lifecycle"])
logger = logging.getLogger(__name__)


class MeldungCreateRequest(BaseModel):
    meldung_typ: str
    periode: str
    betrag_eur: float
    waehrung: str = "EUR"
    referenz_ids: List[str] = []


class MeldungTransitionRequest(BaseModel):
    new_status: str
    fehler_grund: str = ""
    externe_referenz: str = ""


@router.post("", response_model=TypedObjectOut, summary="Meldewesen-Meldung anlegen", dependencies=SCHREIBEN["FINANZ"])
def create_meldung(
    req: MeldungCreateRequest,
    request: Request,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.meldewesen_lifecycle_service import create_meldung as svc, MeldungError
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            meldung_typ=req.meldung_typ,
            periode=req.periode,
            betrag_eur=req.betrag_eur,
            waehrung=req.waehrung,
            referenz_ids=req.referenz_ids,
            operator=gepruefter_akteur_aus_request(request),
        )
    except MeldungError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{meldung_id}/transition",
    response_model=TypedObjectOut,
    summary="Meldewesen-Meldungsstatus wechseln", dependencies=SCHREIBEN["FINANZ"])
def transition_meldung(
    meldung_id: str,
    req: MeldungTransitionRequest,
    request: Request,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.meldewesen_lifecycle_service import (
        transition_meldung as svc,
        MeldungError,
    )
    try:
        return svc(
            db=db,
            meldung_id=meldung_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=gepruefter_akteur_aus_request(request),
            fehler_grund=req.fehler_grund,
            externe_referenz=req.externe_referenz,
        )
    except MeldungError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/simulate-uebermittlung",
    response_model=TypedObjectOut,
    summary="Meldewesen-Uebermittlung simulieren", dependencies=SCHREIBEN["FINANZ"])
def simulate_uebermittlung(
    meldung_typ: str,
    periode: str,
    betrag_eur: float,
    x_tenant_id: str = Header(...),
):
    """Simulierte Übermittlung für Tests — kein echtes ELSTER/ATLAS."""
    from app.services.meldewesen_lifecycle_service import simulate_uebermittlung as svc
    return svc(meldung_typ=meldung_typ, periode=periode, betrag_eur=betrag_eur)
