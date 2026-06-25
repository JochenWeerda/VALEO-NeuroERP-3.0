"""PORTAL-INTELLIGENCE-001 — Cross-Sell-Empfehlungs-API."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.services.portal_intelligence_service import get_intelligence_service

router = APIRouter(prefix="/portal/empfehlungen", tags=["portal", "intelligence"])


def _tid(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


@router.get("/{kunden_nr}", response_model=dict[str, Any])
def empfehlungen_fuer_kunden(
    kunden_nr: str,
    nur_ungesehen: bool = Query(False),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_intelligence_service(tid)
    items = svc.empfehlungen_fuer_kunden(kunden_nr, nur_ungesehen=nur_ungesehen)
    return {"items": items, "count": len(items)}


@router.get("/{kunden_nr}/zusammenfassung", response_model=dict[str, Any])
def zusammenfassung(kunden_nr: str, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    return get_intelligence_service(_tid(x_tenant_id)).zusammenfassung(kunden_nr)


@router.post("/{kunden_nr}/gesehen/{empfehlung_id}", response_model=dict[str, Any])
def als_gesehen(
    kunden_nr: str,
    empfehlung_id: str,
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    svc = get_intelligence_service(_tid(x_tenant_id))
    ok = svc.als_gesehen_markieren(empfehlung_id, kunden_nr)
    if not ok:
        raise HTTPException(status_code=404, detail="Empfehlung nicht gefunden")
    return {"ok": True}


class RationContext(BaseModel):
    kunden_nr: str
    tiere_anzahl: int
    tier_kategorie: str
    benoetigt_rohwaren: list[str] = []


@router.post("/generieren/ration", response_model=dict[str, Any], status_code=201)
def generiere_aus_ration(body: RationContext, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    svc = get_intelligence_service(_tid(x_tenant_id))
    neue = svc.generiere_aus_ration(
        kunden_nr=body.kunden_nr,
        tiere_anzahl=body.tiere_anzahl,
        tier_kategorie=body.tier_kategorie,
        benoetigt_rohwaren=body.benoetigt_rohwaren,
    )
    return {"neue_empfehlungen": neue, "count": len(neue)}


class SchlagContext(BaseModel):
    kunden_nr: str
    kulturen: list[str]
    flaeche_ha: float
    ernte_jahr: int


@router.post("/generieren/schlagkartei", response_model=dict[str, Any], status_code=201)
def generiere_aus_schlagkartei(body: SchlagContext, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    svc = get_intelligence_service(_tid(x_tenant_id))
    neue = svc.generiere_aus_schlagkartei(
        kunden_nr=body.kunden_nr,
        kulturen=body.kulturen,
        flaeche_ha=body.flaeche_ha,
        ernte_jahr=body.ernte_jahr,
    )
    return {"neue_empfehlungen": neue, "count": len(neue)}
