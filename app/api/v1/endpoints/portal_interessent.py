"""PORTAL-INTERESSENT-001 — Interessenten-Onboarding-API.

Mandant aus dem geprueften Token (``get_tenant_id``), nicht aus einem frei setzbaren Kopf. Liste und Abruf zeigen
Personendaten und brauchen eine Innen-/Aussendienstrolle, der Statuswechsel die CRM-Bearbeitung (20.10.2026: vorher
konnte jede angemeldete Person — auch ein Portalkunde — alle Interessenten lesen und umstufen).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.portal_bundle_schemas import (
    PortalInteressentListOut,
    PortalInteressentOut,
)
from app.auth import bereich_roles
from app.auth.deps import require_roles
from app.auth.portal_kunde import AUSSENDIENST_FACHROLLEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_interessent_service import (
    BetriebsTyp,
    InteressentNichtGefundenFehler,
    InteressentStatus,
    UngueltigerUebergangFehler,
    get_interessent_service,
)

router = APIRouter(prefix="/portal/interessenten", tags=["portal", "interessent"])

_innendienst = require_roles(*sorted(AUSSENDIENST_FACHROLLEN))
_crm = require_roles(*bereich_roles.CRM)


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


def _enum(typ: type, wert: str | None, feld: str) -> Any:
    if not wert:
        return None
    try:
        return typ(wert)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Unbekannter Wert fuer {feld}: {wert!r}") from e


@router.post("", response_model=PortalInteressentOut, status_code=201,
             summary="Interessent selbst registrieren (Portal)")
def registrieren(
    body: RegistrierenBody, db: Session = Depends(get_db), tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = get_interessent_service(db, tid)
    try:
        i = svc.registrieren(
            vorname=body.vorname,
            nachname=body.nachname,
            email=body.email,
            telefon=body.telefon,
            betrieb_name=body.betrieb_name,
            betrieb_typ=_enum(BetriebsTyp, body.betrieb_typ, "betrieb_typ"),
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


@router.get("", response_model=PortalInteressentListOut, summary="Interessenten-Liste (Innendienst)",
            dependencies=[Depends(_innendienst)])
def list_interessenten(
    status: str | None = Query(None),
    betrieb_typ: str | None = Query(None),
    zugewiesen_an: str | None = Query(None),
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    items = get_interessent_service(db, tid).list_interessenten(
        status=_enum(InteressentStatus, status, "status"),
        betrieb_typ=_enum(BetriebsTyp, betrieb_typ, "betrieb_typ"),
        zugewiesen_an=zugewiesen_an,
    )
    return {"items": items, "count": len(items)}


@router.get("/{interessent_id}", response_model=PortalInteressentOut, summary="Interessent abrufen",
            dependencies=[Depends(_innendienst)])
def get_interessent(
    interessent_id: str, db: Session = Depends(get_db), tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return get_interessent_service(db, tid).get(interessent_id)
    except InteressentNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/{interessent_id}/status", response_model=PortalInteressentOut, summary="Interessentenstatus wechseln",
             dependencies=[Depends(_crm)])
def status_wechsel(
    interessent_id: str,
    body: StatusWechselBody,
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = get_interessent_service(db, tid)
    try:
        i = svc.status_wechsel(
            interessent_id=interessent_id,
            neuer_status=_enum(InteressentStatus, body.neuer_status, "neuer_status"),
            zugewiesen_an=body.zugewiesen_an,
            kunden_nr=body.kunden_nr,
        )
    except InteressentNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (UngueltigerUebergangFehler, ValueError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return i.to_dict()
