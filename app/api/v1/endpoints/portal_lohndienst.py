"""PORTAL-LOHNDIENST-001 — Lohndienstleistungs-Auftrags-API."""
from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.portal_bundle_schemas import (
    PortalLohndienstAuftragOut,
    PortalLohndienstListOut,
)
from app.auth.beleg_roles import verlange
from app.auth.deps import get_current_user
from app.auth.portal_kunde import PortalKunde, kundennummer, portal_kunde
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_lohndienst_service import (
    AuftragNichtGefundenFehler,
    LohndienstStatus,
    LohndienstTyp,
    UngueltigerStatusFehler,
    get_lohndienst_service,
)

router = APIRouter(prefix="/portal/lohndienste", tags=["portal", "lohndienste"])


# Mandant und Kunde nur aus Anmeldung und gepruefter Zuordnung (TENANT-DOC-001, ``app/auth/portal_kunde.py``).
# Bis 14.10.2026 nahm dieser Router den Mandanten aus dem rohen Kopf ``X-Tenant-ID`` und den Kunden aus ``kunden_nr``
# in Body oder Query; den Status setzte jede Anmeldung. Ein mitgeschicktes ``kunden_nr`` bleibt wirkungslos.


def _innendienst_bearbeiten(nutzer: dict = Depends(get_current_user)) -> None:
    """Auftraege disponieren (Status, Termin, Preis) ist Innendienst: Rechte wie fuer Auftraege."""
    verlange(nutzer, "bearbeiten", "sales_order")


class AuftragCreateBody(BaseModel):
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


@router.post("", response_model=PortalLohndienstAuftragOut, status_code=201, summary="Lohndienst-Auftrag anlegen")
def auftrag_anlegen(
    body: AuftragCreateBody,
    kunde: PortalKunde = Depends(portal_kunde),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if kunde.intern:
        verlange(nutzer, "bearbeiten", "sales_order")
    svc = get_lohndienst_service(kunde.tenant_id)
    try:
        a = svc.auftrag_anlegen(
            kunden_nr=kundennummer(db, kunde),
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


@router.get("", response_model=PortalLohndienstListOut, summary="Lohndienst-Auftraege auflisten")
def list_auftraege(
    typ: str | None = Query(None),
    status: str | None = Query(None),
    kunde: PortalKunde = Depends(portal_kunde),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = get_lohndienst_service(kunde.tenant_id)
    items = svc.list_auftraege(
        kunden_nr=kundennummer(db, kunde),
        typ=LohndienstTyp(typ) if typ else None,
        status=LohndienstStatus(status) if status else None,
    )
    return {"items": items, "count": len(items)}


@router.get("/{auftrag_id}", response_model=PortalLohndienstAuftragOut, summary="Lohndienst-Auftrag abrufen")
def get_auftrag(
    auftrag_id: str,
    kunde: PortalKunde = Depends(portal_kunde),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        auftrag = get_lohndienst_service(kunde.tenant_id).get_auftrag(auftrag_id)
    except AuftragNichtGefundenFehler as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if auftrag.get("kunden_nr") != kundennummer(db, kunde):
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    return auftrag


@router.post("/{auftrag_id}/status", response_model=PortalLohndienstAuftragOut, summary="Lohndienst-Auftragsstatus wechseln",
             dependencies=[Depends(_innendienst_bearbeiten)])
def status_wechsel(
    auftrag_id: str,
    body: StatusWechselBody,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = get_lohndienst_service(tenant_id)
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
