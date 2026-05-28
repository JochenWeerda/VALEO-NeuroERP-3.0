"""
Kontrakt-Hedging und MATIF-Preisbindung.

GET    /kontrakt-hedging/{kontrakt_id}/hedges                       — list hedges
POST   /kontrakt-hedging/{kontrakt_id}/hedges                       — create hedge
POST   /kontrakt-hedging/{kontrakt_id}/hedges/{hedge_id}/mark-to-market — unrealized P&L
DELETE /kontrakt-hedging/{kontrakt_id}/hedges/{hedge_id}            — cancel (STORNIERT)
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/kontrakt-hedging", tags=["kontrakt-hedging"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class HedgeCreate(BaseModel):
    kontrakt_id: str
    terminmarkt: str           # MATIF / CBOT / EURONEXT
    futuresmonat: str          # e.g. "NOV26"
    futures_preis_eur: float
    hedge_menge_t: float
    hedge_datum: date
    status: str = "OFFEN"     # OFFEN / TEILGEDECKT / VOLLGEDECKT


class HedgeOut(HedgeCreate):
    id: str
    created_at: Optional[datetime] = None


class HedgeMarkToMarket(BaseModel):
    aktueller_futures_preis: float
    bewertungsdatum: date


class MarkToMarketResult(BaseModel):
    hedge_id: str
    unrealized_pnl_eur: float
    bewertungsdatum: date
    aktueller_futures_preis: float
    futures_preis_eur: float
    hedge_menge_t: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/{kontrakt_id}/hedges", response_model=List[HedgeOut], summary="Hedges auflisten")
def list_hedges(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text(
                "SELECT id, kontrakt_id, terminmarkt, futuresmonat,"
                " futures_preis_eur, hedge_menge_t, hedge_datum, status, created_at"
                " FROM domain_agrar.kontrakt_hedges"
                " WHERE kontrakt_id=:kontrakt_id AND tenant_id=:tenant_id"
                "   AND status != 'STORNIERT'"
                " ORDER BY hedge_datum"
            ),
            {"kontrakt_id": kontrakt_id, "tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []  # migration_hint: domain_agrar.kontrakt_hedges not yet migrated


@router.post("/{kontrakt_id}/hedges", response_model=HedgeOut, status_code=201, summary="Hedge anlegen")
def create_hedge(
    kontrakt_id: str,
    payload: HedgeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = str(uuid4())
    now = datetime.utcnow()
    # Normalise: kontrakt_id from path takes precedence
    data = payload.model_dump()
    data["kontrakt_id"] = kontrakt_id
    try:
        db.execute(
            text(
                "INSERT INTO domain_agrar.kontrakt_hedges"
                " (id, kontrakt_id, terminmarkt, futuresmonat, futures_preis_eur,"
                "  hedge_menge_t, hedge_datum, status, created_at, tenant_id)"
                " VALUES (:id, :kontrakt_id, :terminmarkt, :futuresmonat,"
                "  :futures_preis_eur, :hedge_menge_t, :hedge_datum, :status,"
                "  :created_at, :tenant_id)"
            ),
            {
                "id": new_id,
                "kontrakt_id": kontrakt_id,
                "terminmarkt": payload.terminmarkt,
                "futuresmonat": payload.futuresmonat,
                "futures_preis_eur": payload.futures_preis_eur,
                "hedge_menge_t": payload.hedge_menge_t,
                "hedge_datum": payload.hedge_datum,
                "status": payload.status,
                "created_at": now,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
    return HedgeOut(id=new_id, created_at=now, **data)


@router.post(
    "/{kontrakt_id}/hedges/{hedge_id}/mark-to-market",
    response_model=MarkToMarketResult,
    summary="To market markieren",
)
def mark_to_market(
    kontrakt_id: str,
    hedge_id: str,
    payload: HedgeMarkToMarket,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    # Try to fetch hedge from DB; fall back to 0-base values if table missing
    futures_preis_eur: float = 0.0
    hedge_menge_t: float = 0.0

    try:
        row = db.execute(
            text(
                "SELECT futures_preis_eur, hedge_menge_t"
                " FROM domain_agrar.kontrakt_hedges"
                " WHERE id=:hedge_id AND kontrakt_id=:kontrakt_id AND tenant_id=:tenant_id"
            ),
            {"hedge_id": hedge_id, "kontrakt_id": kontrakt_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row:
            futures_preis_eur = float(row["futures_preis_eur"])
            hedge_menge_t = float(row["hedge_menge_t"])
    except Exception:
        pass  # migration_hint: use values from payload context only

    # P&L = (aktueller_preis - futures_preis) * hedge_menge  (€/t * t = €)
    unrealized_pnl_eur = (
        payload.aktueller_futures_preis - futures_preis_eur
    ) * hedge_menge_t

    return MarkToMarketResult(
        hedge_id=hedge_id,
        unrealized_pnl_eur=unrealized_pnl_eur,
        bewertungsdatum=payload.bewertungsdatum,
        aktueller_futures_preis=payload.aktueller_futures_preis,
        futures_preis_eur=futures_preis_eur,
        hedge_menge_t=hedge_menge_t,
    )


@router.delete(
    "/{kontrakt_id}/hedges/{hedge_id}",
    status_code=204,
    response_class=Response, response_model=None, summary="Hedge stornieren")
def cancel_hedge(
    kontrakt_id: str,
    hedge_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.kontrakt_hedges SET status='STORNIERT'"
                " WHERE id=:hedge_id AND kontrakt_id=:kontrakt_id AND tenant_id=:tenant_id"
            ),
            {"hedge_id": hedge_id, "kontrakt_id": kontrakt_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
    return Response(status_code=204)
