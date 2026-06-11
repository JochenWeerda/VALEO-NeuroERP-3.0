"""Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2).

Schreib-/Lese-Endpunkte für die Teilfixierung MATIF-bepreister Kontrakte und die
Mark-to-Market-Bewertung gegen die jüngste Marktnotierung.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.contract_fixing_service import ContractFixingService, FixingActionError

router = APIRouter(prefix="/contracts", tags=["contracts", "kontrakte", "agrar"])


@router.get("/fixing/workspace", summary="Fixierungs-Arbeitsraum je Kontrakt (fixiert/offen + Bewertung)")
def workspace(
    kontrakt: str = Query(..., description="Kontraktnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ContractFixingService(db, tenant_id).workspace(kontrakt)


@router.get("/fixing/list", summary="Fixierungen eines Kontrakts")
def list_fixings(
    kontrakt: str = Query(..., description="Kontraktnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ContractFixingService(db, tenant_id).list_fixings(kontrakt)}


class FixingIn(BaseModel):
    kontrakt: str
    position: Optional[str] = None          # Position-Nr oder line_id (bei mehreren Positionen Pflicht)
    menge: float
    matifPreis: float
    praemie: Optional[float] = None         # Default = Kontrakt-Prämie
    matifReferenz: Optional[str] = None
    notiz: Optional[str] = None
    bediener: Optional[str] = None


@router.post("/fixing", summary="Teilfixierung anlegen (Menge zu MATIF-Preis + Prämie)")
def create_fixing(
    body: FixingIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return ContractFixingService(db, tenant_id).create_fixing(
            contract_ref=body.kontrakt, line_ref=body.position, quantity=body.menge,
            matif_price=body.matifPreis, premium=body.praemie,
            matif_reference=body.matifReferenz, note=body.notiz, bediener=body.bediener or "KIM",
        )
    except FixingActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class QuoteIn(BaseModel):
    symbol: str
    preis: float
    datum: Optional[str] = None             # ISO-Datum; Default heute
    einheit: Optional[str] = None
    quelle: Optional[str] = None


@router.post("/matif-quote", summary="MATIF-Notierung erfassen/aktualisieren (Bewertungsbasis)")
def upsert_quote(
    body: QuoteIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    from datetime import date

    qd = None
    if body.datum:
        try:
            qd = date.fromisoformat(body.datum[:10])
        except ValueError:
            raise HTTPException(status_code=422, detail="Ungültiges Datum (erwartet ISO YYYY-MM-DD).")
    try:
        return ContractFixingService(db, tenant_id).upsert_quote(
            symbol=body.symbol, quote_date=qd, price=body.preis,
            unit=body.einheit, source=body.quelle or "manual",
        )
    except FixingActionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
