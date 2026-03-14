from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid
from app.core.reklamation import (
    Reklamation, ReklamationStore, ReklamationZustandsmaschine,
    ReklamationsTyp, ReklamationsStatus, ReklamationsPosition
)

router = APIRouter(prefix="/reklamationen", tags=["reklamationen"])
_store = ReklamationStore()

class ReklamationCreateRequest(BaseModel):
    tenant_id: str
    lieferant_id: str
    typ: str
    positionen: list[dict]
    zustaendiger: str
    frist_datum: str
    kontrakt_id: Optional[str] = None

@router.post("", status_code=201)
def create_reklamation(req: ReklamationCreateRequest):
    positionen = [ReklamationsPosition(**p) for p in req.positionen]
    rek = Reklamation(
        reklamation_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        lieferant_id=req.lieferant_id,
        typ=ReklamationsTyp(req.typ),
        positionen=positionen,
        zustaendiger=req.zustaendiger,
        frist_datum=date.fromisoformat(req.frist_datum),
        erstellt_am=datetime.utcnow(),
        kontrakt_id=req.kontrakt_id,
    )
    _store.add(rek)
    return rek

@router.post("/{reklamation_id}/transition")
def transition_status(reklamation_id: str, neuer_status: str):
    rek = _store.get(reklamation_id)
    if rek is None:
        raise HTTPException(status_code=404, detail="Reklamation nicht gefunden")
    try:
        ReklamationZustandsmaschine.transition(rek, ReklamationsStatus(neuer_status))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return rek

@router.get("/offene/{tenant_id}")
def get_offene(tenant_id: str):
    return _store.offene(tenant_id)
