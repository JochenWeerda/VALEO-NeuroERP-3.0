"""DOM-FEED-PROD-004 — Mischfutter Produktion: Rezeptur, Auftrag, QS-Freigabe."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter(prefix="/futtermittel/produktion", tags=["feed-produktion"])
logger = logging.getLogger(__name__)


class ProduktionsauftragCreateRequest(BaseModel):
    rezeptur_id: str
    soll_menge_kg: float
    geplant_datum: str
    charge_nr: str
    operator: str = "system"


class ProduktionsTransitionRequest(BaseModel):
    new_status: str
    ist_menge_kg: Optional[float] = None
    qs_befund: str = ""
    operator: str = "system"


class RezepturPosition(BaseModel):
    rohware_id: str
    anteil_pct: float


class RezepturCreateRequest(BaseModel):
    rezeptur_nr: str
    artikel_id: str
    bezeichnung: str
    positionen: List[RezepturPosition]
    operator: str = "system"


class RezepturTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"


@router.post("/auftraege", response_model=Dict[str, Any])
def create_produktionsauftrag(
    req: ProduktionsauftragCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.feed_produktion_lifecycle_service import (
        create_produktionsauftrag as svc,
        FeedProduktionError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            rezeptur_id=req.rezeptur_id,
            soll_menge_kg=req.soll_menge_kg,
            geplant_datum=req.geplant_datum,
            charge_nr=req.charge_nr,
            operator=req.operator,
        )
    except FeedProduktionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auftraege/{auftrag_id}/transition", response_model=Dict[str, Any])
def transition_auftrag(
    auftrag_id: str,
    req: ProduktionsTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.feed_produktion_lifecycle_service import (
        transition_produktionsauftrag as svc,
        FeedProduktionError,
    )
    try:
        return svc(
            db=db,
            auftrag_id=auftrag_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            ist_menge_kg=req.ist_menge_kg,
            operator=req.operator,
            qs_befund=req.qs_befund,
        )
    except FeedProduktionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rezepturen", response_model=Dict[str, Any])
def create_rezeptur(
    req: RezepturCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.feed_rezeptur_service import create_rezeptur as svc, RezepturError
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            rezeptur_nr=req.rezeptur_nr,
            artikel_id=req.artikel_id,
            bezeichnung=req.bezeichnung,
            positionen=[p.model_dump() for p in req.positionen],
            operator=req.operator,
        )
    except RezepturError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/rezepturen/{rezeptur_id}/transition", response_model=Dict[str, Any])
def transition_rezeptur(
    rezeptur_id: str,
    req: RezepturTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.feed_rezeptur_service import transition_rezeptur as svc, RezepturError
    try:
        return svc(
            db=db,
            rezeptur_id=rezeptur_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
        )
    except RezepturError as e:
        raise HTTPException(status_code=400, detail=str(e))
