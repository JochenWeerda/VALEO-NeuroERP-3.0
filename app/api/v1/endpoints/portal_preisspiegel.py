"""PORTAL-PREISSPIEGEL-001 — Getreidekurs-API fuer Kundenportal und Innendienst."""
from __future__ import annotations

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.services.portal_preisspiegel_service import (
    PreisQuelle,
    PreisVariante,
    get_preisspiegel_service,
)

router = APIRouter(prefix="/portal/preisspiegel", tags=["portal", "preisspiegel"])


def _tid(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


@router.get("", response_model=dict[str, Any], summary="Alle aktuellen Preise")
def preise_alle(
    frucht_gruppe: str | None = Query(None),
    variante: str | None = Query(None),
    ernte_jahr: int | None = Query(None),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_preisspiegel_service(tid)
    variante_enum = PreisVariante(variante) if variante else None
    preise = svc.preise_alle(
        frucht_gruppe=frucht_gruppe,
        variante=variante_enum,
        ernte_jahr=ernte_jahr,
    )
    return {"preise": preise, "count": len(preise), "stand": date.today().isoformat()}


@router.get("/kunde", response_model=dict[str, Any], summary="Preisspiegel gefiltert nach Kundenfrüchten")
def preisspiegel_kunde(
    artikel_ids: str = Query(..., description="Kommagetrennte Artikel-IDs"),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_preisspiegel_service(tid)
    ids = [a.strip() for a in artikel_ids.split(",") if a.strip()]
    return svc.preisspiegel_fuer_kunde(ids)


class PreisSetzenBody(BaseModel):
    artikel_id: str
    artikel_name: str
    frucht_gruppe: str
    variante: str
    preis_eur_dt: float
    basis_qualitaet: str
    ernte_jahr: int
    liefermonat: str | None = None
    aufschlag_eur_dt: float = 0.0
    quelle: str = "manuell"
    gueltig_bis: date | None = None
    hinweis: str | None = None


@router.post("", response_model=dict[str, Any], status_code=201, summary="Preis pflegen (Innendienst)")
def preis_setzen(body: PreisSetzenBody, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_preisspiegel_service(tid)
    try:
        return svc.preis_setzen(
            artikel_id=body.artikel_id,
            artikel_name=body.artikel_name,
            frucht_gruppe=body.frucht_gruppe,
            variante=PreisVariante(body.variante),
            preis_eur_dt=body.preis_eur_dt,
            basis_qualitaet=body.basis_qualitaet,
            ernte_jahr=body.ernte_jahr,
            liefermonat=body.liefermonat,
            aufschlag_eur_dt=body.aufschlag_eur_dt,
            quelle=PreisQuelle(body.quelle),
            gueltig_bis=body.gueltig_bis,
            hinweis=body.hinweis,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
