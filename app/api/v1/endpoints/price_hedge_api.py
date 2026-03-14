from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid
from app.core.price_hedge import HedgeReference, HedgeStore, TerminmarktProdukt, HedgeTyp, berechne_hedge_quote

router = APIRouter(prefix="/price-hedge", tags=["price-hedge"])
_store = HedgeStore()

class HedgeCreateRequest(BaseModel):
    tenant_id: str
    produkt: str
    typ: str
    menge_t: float
    basis_preis_eur_t: float
    verfall_datum: str
    kontrakt_id: Optional[str] = None
    broker_referenz: Optional[str] = None

@router.post("/hedges", status_code=201)
def create_hedge(req: HedgeCreateRequest):
    hedge = HedgeReference(
        hedge_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        kontrakt_id=req.kontrakt_id,
        produkt=TerminmarktProdukt(req.produkt),
        typ=HedgeTyp(req.typ),
        menge_t=req.menge_t,
        basis_preis_eur_t=req.basis_preis_eur_t,
        verfall_datum=date.fromisoformat(req.verfall_datum),
        broker_referenz=req.broker_referenz,
    )
    _store.add_hedge(hedge)
    return hedge

@router.get("/quote")
def get_hedge_quote(kontrakt_menge_t: float, hedge_menge_t: float):
    quote = berechne_hedge_quote(kontrakt_menge_t, hedge_menge_t)
    return {"kontrakt_menge_t": kontrakt_menge_t, "hedge_menge_t": hedge_menge_t, "hedge_quote_pct": quote, "schema_version": 1}
