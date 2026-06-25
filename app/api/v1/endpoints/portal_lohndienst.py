"""PORTAL-LOHNDIENST-001 — Lohndienstleistungs-Auftrags-API."""
from __future__ import annotations

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.services.portal_lohndienst_service import (
    AuftragNichtGefundenFehler,
    LohndienstStatus,
    LohndienstTyp,
    UngueltigerStatusFehler,
    get_lohndienst_service,
)

router = APIRouter(prefix="/portal/lohndienste", tags=["portal", "lohndienste"])


def _tid(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


class AuftragCreateBody(BaseModel):
    kunden_nr: str
    typ: str
    schlag_ids: list[str] = []
    schlag_beschreibung: str = ""
    flaeche_ha: float | None = None
    wunsch_datum: date | None = None
    getreide_art: str | None = None
    menge_dt: float | None = None
    tierart: str | None = None
    tiere_anzahl: int | None = None
    psm_mittel: list[str] = []
    kultur: str | None = None
    anmerkung: str | None = None


class StatusWechselBody(BaseModel):
    neuer_status: str
    geplant_datum: date | None = None
    innendienst_notiz: str | None = None
    preis_indikativ_eur: float | None = None


@router.post("", response_model=dict[str, Any], status_code=201)
def auftrag_anlegen(body: AuftragCreateBody, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_lohndienst_service(tid)
    try:
        a = svc.auftrag_anlegen(
            kunden_nr=body.kunden_nr,
            typ=LohndienstTyp(body.typ),
            schlag_ids=body.schlag_ids,
            schlag_beschreibung=body.schlag_beschreibung,
            flaeche_ha=body.flaeche_ha,
            wunsch_datum=body.wunsch_datum,
            getreide_art=body.getreide_art,
            menge_dt=body.menge_dt,
            tierart=body.tierart,
            tiere_anzahl=body.tiere_anzahl,
            psm_mittel=body.psm_mittel,
            kultur=body.kultur,
            anmerkung=body.anmerkung,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return a.to_dict()


@router.get("", response_model=dict[str, Any])
def list_auftraege(
    kunden_nr: str | None = Query(None),
    typ: str | None = Query(None),
    status: str | None = Query(None),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_lohndienst_service(tid)
    items = svc.list_auftraege(
        kunden_nr=kunden_nr,
        typ=LohndienstTyp(typ) if typ else None,
        status=LohndienstStatus(status) if status else None,
    )
    return {"items": items, "count": len(items)}


@router.get("/{auftrag_id}", response_model=dict[str, Any])
def get_auftrag(auftrag_id: str, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    try:
        return get_lohndienst_service(_tid(x_tenant_id)).get_auftrag(auftrag_id)
    except AuftragNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{auftrag_id}/status", response_model=dict[str, Any])
def status_wechsel(
    auftrag_id: str,
    body: StatusWechselBody,
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    svc = get_lohndienst_service(_tid(x_tenant_id))
    try:
        a = svc.status_wechsel(
            auftrag_id=auftrag_id,
            neuer_status=LohndienstStatus(body.neuer_status),
            geplant_datum=body.geplant_datum,
            innendienst_notiz=body.innendienst_notiz,
            preis_indikativ_eur=body.preis_indikativ_eur,
        )
    except AuftragNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except UngueltigerStatusFehler as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return a.to_dict()
