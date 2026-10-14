"""PORTAL-INTELLIGENCE-001 — Cross-Sell-Empfehlungs-API."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.portal_bundle_schemas import (
    PortalEmpfehlungAckOut,
    PortalEmpfehlungGeneratedOut,
    PortalEmpfehlungListOut,
    PortalEmpfehlungSummaryOut,
)
from app.auth.beleg_roles import verlange
from app.auth.deps import get_current_user
from app.auth.portal_kunde import PortalKunde, kundennummer, kundennummer_des_mandanten, portal_kunde
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_intelligence_service import get_intelligence_service

router = APIRouter(prefix="/portal/empfehlungen", tags=["portal", "intelligence"])


# Mandant und Kunde nur aus Anmeldung und gepruefter Zuordnung (TENANT-DOC-001, ``app/auth/portal_kunde.py``).
# Bis 14.10.2026 nahm dieser Router den Mandanten aus dem rohen Kopf ``X-Tenant-ID``; die Kundennummer im Pfad
# genuegte, um die Empfehlungen jedes Kunden zu lesen. Jetzt muss sie die des angemeldeten Kontos sein, sonst 404.
# Empfehlungen erzeugen ist Innendienst (Angebote an den Kunden): Rechte wie fuer Auftraege.


def _eigene_kundennummer(
    kunden_nr: str,
    kunde: PortalKunde = Depends(portal_kunde),
    db: Session = Depends(get_db),
) -> str:
    if kunden_nr != kundennummer(db, kunde):
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return kunden_nr


def _kunde_fuer_angebot(db: Session, tenant_id: str, nutzer: dict, kunden_nr: str) -> None:
    verlange(nutzer, "bearbeiten", "sales_order")
    if not kundennummer_des_mandanten(db, tenant_id, kunden_nr):
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")


@router.get("/{kunden_nr}", response_model=PortalEmpfehlungListOut, summary="Cross-Sell-Empfehlungen fuer Kunden abrufen")
def empfehlungen_fuer_kunden(
    nur_ungesehen: bool = Query(False),
    kunden_nr: str = Depends(_eigene_kundennummer),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = get_intelligence_service(tenant_id)
    items = svc.empfehlungen_fuer_kunden(kunden_nr, nur_ungesehen=nur_ungesehen)
    return {"items": items, "count": len(items)}


@router.get("/{kunden_nr}/zusammenfassung", response_model=PortalEmpfehlungSummaryOut, summary="Empfehlungs-Zusammenfassung fuer Kunden abrufen")
def zusammenfassung(
    kunden_nr: str = Depends(_eigene_kundennummer),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return get_intelligence_service(tenant_id).zusammenfassung(kunden_nr)


@router.post("/{kunden_nr}/gesehen/{empfehlung_id}", response_model=PortalEmpfehlungAckOut, summary="Empfehlung als gesehen markieren")
def als_gesehen(
    empfehlung_id: str,
    kunden_nr: str = Depends(_eigene_kundennummer),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    svc = get_intelligence_service(tenant_id)
    ok = svc.als_gesehen_markieren(empfehlung_id, kunden_nr)
    if not ok:
        raise HTTPException(status_code=404, detail="Empfehlung nicht gefunden")
    return {"ok": True}


class RationContext(BaseModel):
    kunden_nr: str
    tiere_anzahl: int
    tier_kategorie: str
    benoetigt_rohwaren: list[str] = []


@router.post("/generieren/ration", response_model=PortalEmpfehlungGeneratedOut, status_code=201, summary="Empfehlungen aus Rationskontext generieren")
def generiere_aus_ration(
    body: RationContext,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _kunde_fuer_angebot(db, tenant_id, nutzer, body.kunden_nr)
    svc = get_intelligence_service(tenant_id)
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


@router.post("/generieren/schlagkartei", response_model=PortalEmpfehlungGeneratedOut, status_code=201, summary="Empfehlungen aus Schlagkartei-Kontext generieren")
def generiere_aus_schlagkartei(
    body: SchlagContext,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _kunde_fuer_angebot(db, tenant_id, nutzer, body.kunden_nr)
    svc = get_intelligence_service(tenant_id)
    neue = svc.generiere_aus_schlagkartei(
        kunden_nr=body.kunden_nr,
        kulturen=body.kulturen,
        flaeche_ha=body.flaeche_ha,
        ernte_jahr=body.ernte_jahr,
    )
    return {"neue_empfehlungen": neue, "count": len(neue)}
