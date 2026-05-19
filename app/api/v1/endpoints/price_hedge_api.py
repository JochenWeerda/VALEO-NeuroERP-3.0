from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.price_hedge import HedgeTyp, TerminmarktProdukt, berechne_hedge_quote
from app.domains.operations.models import HedgeReferenceDB

router = APIRouter(prefix="/price-hedge", tags=["price-hedge"])


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
def create_hedge(req: HedgeCreateRequest, db: Session = Depends(get_db)):
    hid = str(uuid.uuid4())
    row = HedgeReferenceDB(
        hedge_id=hid,
        tenant_id=req.tenant_id,
        kontrakt_id=req.kontrakt_id,
        produkt=req.produkt,
        typ=req.typ,
        menge_t=req.menge_t,
        basis_preis_eur_t=Decimal(str(req.basis_preis_eur_t)),
        verfall_datum=datetime.fromisoformat(req.verfall_datum),
        broker_referenz=req.broker_referenz,
        status="aktiv",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "hedge_id": row.hedge_id,
        "tenant_id": row.tenant_id,
        "produkt": row.produkt,
        "typ": row.typ,
        "menge_t": float(row.menge_t),
        "basis_preis_eur_t": float(row.basis_preis_eur_t),
        "status": row.status,
    }


@router.get("/hedges")
def list_hedges(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.query(HedgeReferenceDB).filter(HedgeReferenceDB.tenant_id == tenant_id).all()
    return [
        {
            "hedge_id": r.hedge_id,
            "produkt": r.produkt,
            "typ": r.typ,
            "menge_t": float(r.menge_t),
            "basis_preis_eur_t": float(r.basis_preis_eur_t),
            "verfall_datum": r.verfall_datum.date().isoformat() if r.verfall_datum else None,
            "status": r.status,
            "kontrakt_id": r.kontrakt_id,
        }
        for r in rows
    ]


@router.patch("/hedges/{hedge_id}/close")
def close_hedge(hedge_id: str, aktueller_preis: float, db: Session = Depends(get_db)):
    row = db.query(HedgeReferenceDB).filter(HedgeReferenceDB.hedge_id == hedge_id).first()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(404, "Hedge nicht gefunden")
    row.aktueller_preis_eur_t = Decimal(str(aktueller_preis))
    row.pnl_eur = Decimal(str((aktueller_preis - float(row.basis_preis_eur_t)) * float(row.menge_t)))
    row.status = "geschlossen"
    db.commit()
    return {"hedge_id": hedge_id, "status": "geschlossen", "pnl_eur": float(row.pnl_eur)}


@router.get("/quote")
def get_hedge_quote(kontrakt_menge_t: float, hedge_menge_t: float):
    quote = berechne_hedge_quote(kontrakt_menge_t, hedge_menge_t)
    return {"kontrakt_menge_t": kontrakt_menge_t, "hedge_menge_t": hedge_menge_t, "hedge_quote_pct": quote, "schema_version": 1}
