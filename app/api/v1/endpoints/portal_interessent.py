"""PORTAL-INTERESSENT-001 — Interessenten-Onboarding-API."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.services.portal_interessent_service import (
    BetriebsTyp,
    InteressentNichtGefundenFehler,
    InteressentStatus,
    UngueltigerUebergangFehler,
    get_interessent_service,
)

router = APIRouter(prefix="/portal/interessenten", tags=["portal", "interessent"])


def _tid(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


class RegistrierenBody(BaseModel):
    vorname: str
    nachname: str
    email: str
    telefon: str | None = None
    betrieb_name: str | None = None
    betrieb_typ: str | None = None
    flaeche_ha: float | None = None
    hauptkulturen: list[str] = []
    tiere_anzahl: int | None = None
    tierart: str | None = None
    plz: str | None = None
    ort: str | None = None
    interesse_themen: list[str] = []
    anmerkung: str | None = None


class StatusWechselBody(BaseModel):
    neuer_status: str
    zugewiesen_an: str | None = None
    kunden_nr: str | None = None


@router.post("", response_model=dict[str, Any], status_code=201,
             summary="Interessent selbst registrieren (public)")
def registrieren(body: RegistrierenBody, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    tid = _tid(x_tenant_id)
    svc = get_interessent_service(tid)
    try:
        i = svc.registrieren(
            vorname=body.vorname,
            nachname=body.nachname,
            email=body.email,
            telefon=body.telefon,
            betrieb_name=body.betrieb_name,
            betrieb_typ=BetriebsTyp(body.betrieb_typ) if body.betrieb_typ else None,
            flaeche_ha=body.flaeche_ha,
            hauptkulturen=body.hauptkulturen,
            tiere_anzahl=body.tiere_anzahl,
            tierart=body.tierart,
            plz=body.plz,
            ort=body.ort,
            interesse_themen=body.interesse_themen,
            anmerkung=body.anmerkung,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return i.to_dict()


@router.get("", response_model=dict[str, Any], summary="Interessenten-Liste (Innendienst)")
def list_interessenten(
    status: str | None = Query(None),
    betrieb_typ: str | None = Query(None),
    zugewiesen_an: str | None = Query(None),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    svc = get_interessent_service(_tid(x_tenant_id))
    items = svc.list_interessenten(
        status=InteressentStatus(status) if status else None,
        betrieb_typ=BetriebsTyp(betrieb_typ) if betrieb_typ else None,
        zugewiesen_an=zugewiesen_an,
    )
    return {"items": items, "count": len(items)}


@router.get("/{interessent_id}", response_model=dict[str, Any])
def get_interessent(interessent_id: str, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    try:
        return get_interessent_service(_tid(x_tenant_id)).get(interessent_id)
    except InteressentNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{interessent_id}/status", response_model=dict[str, Any])
def status_wechsel(
    interessent_id: str,
    body: StatusWechselBody,
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    svc = get_interessent_service(_tid(x_tenant_id))
    try:
        i = svc.status_wechsel(
            interessent_id=interessent_id,
            neuer_status=InteressentStatus(body.neuer_status),
            zugewiesen_an=body.zugewiesen_an,
            kunden_nr=body.kunden_nr,
        )
    except InteressentNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (UngueltigerUebergangFehler, ValueError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return i.to_dict()
