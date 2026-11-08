"""PORTAL-INTELLIGENCE-001 — Cross-Sell-Empfehlungs-API (persistent, PORTAL-CONTEXT-001).

Mandant und Kunde nur aus Anmeldung und gepruefter Zuordnung (``app/auth/portal_kunde.py``); lesen und als gesehen
markieren mit dem Portalrecht ``empfehlungen``. Bis 14.10.2026 genuegte die Kundennummer im Pfad, um die Empfehlungen
jedes Kunden zu lesen; die Pfade mit ``{kunden_nr}`` bleiben, die Nummer muss aber die des angemeldeten Kontos sein
(sonst 404). Empfehlungen erzeugen ist Innendienst (Angebote an den Kunden): Rechte wie fuer Auftraege.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.portal_bundle_schemas import (
    PortalEmpfehlungAckOut,
    PortalEmpfehlungGeneratedOut,
    PortalEmpfehlungListOut,
    PortalEmpfehlungSummaryOut,
)
from app.auth.beleg_roles import verlange
from app.auth.deps import get_current_user
from app.auth.portal_kunde import EMPFEHLUNGEN, PortalKunde, kunde_zur_nummer, kundennummer, portal_recht
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_intelligence_service import PortalIntelligenceService

router = APIRouter(prefix="/portal/empfehlungen", tags=["portal", "intelligence"])


def _eigenes_konto(
    kunden_nr: str,
    kunde: PortalKunde = Depends(portal_recht(EMPFEHLUNGEN)),
    db: Session = Depends(get_db),
) -> PortalKunde:
    if kunden_nr != kundennummer(db, kunde):
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return kunde


def _kunde_fuer_angebot(db: Session, tenant_id: str, nutzer: dict, kunden_nr: str) -> str:
    verlange(nutzer, "bearbeiten", "sales_order")
    customer_id = kunde_zur_nummer(db, tenant_id, kunden_nr)
    if customer_id is None:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return customer_id


@router.get("", response_model=PortalEmpfehlungListOut, summary="Cross-Sell-Empfehlungen des Kundenkontos")
def empfehlungen_des_kontos(
    nur_ungesehen: bool = Query(False),
    kunde: PortalKunde = Depends(portal_recht(EMPFEHLUNGEN)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items = PortalIntelligenceService(db, kunde.tenant_id).empfehlungen_fuer_kunden(
        kunde.customer_id, nur_ungesehen=nur_ungesehen)
    return {"items": items, "count": len(items)}


@router.get("/{kunden_nr}", response_model=PortalEmpfehlungListOut, summary="Cross-Sell-Empfehlungen fuer Kunden abrufen")
def empfehlungen_fuer_kunden(
    nur_ungesehen: bool = Query(False),
    kunde: PortalKunde = Depends(_eigenes_konto),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items = PortalIntelligenceService(db, kunde.tenant_id).empfehlungen_fuer_kunden(
        kunde.customer_id, nur_ungesehen=nur_ungesehen)
    return {"items": items, "count": len(items)}


@router.get("/{kunden_nr}/zusammenfassung", response_model=PortalEmpfehlungSummaryOut, summary="Empfehlungs-Zusammenfassung fuer Kunden abrufen")
def zusammenfassung(
    kunden_nr: str,
    kunde: PortalKunde = Depends(_eigenes_konto),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return PortalIntelligenceService(db, kunde.tenant_id).zusammenfassung(kunde.customer_id, kunden_nr)


@router.post("/{kunden_nr}/gesehen/{empfehlung_id}", response_model=PortalEmpfehlungAckOut, summary="Empfehlung als gesehen markieren")
def als_gesehen(
    empfehlung_id: str,
    kunde: PortalKunde = Depends(_eigenes_konto),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    ok = PortalIntelligenceService(db, kunde.tenant_id).als_gesehen_markieren(
        empfehlung_id, kunde.customer_id, kunde.subject)
    if not ok:
        raise HTTPException(status_code=404, detail="Empfehlung nicht gefunden")
    return {"ok": True}


class RationContext(BaseModel):
    kunden_nr: str = Field(..., min_length=1)
    tiere_anzahl: int = Field(..., ge=0)
    tier_kategorie: str = Field(..., min_length=1, max_length=200)
    benoetigt_rohwaren: list[str] = Field(default_factory=list, max_length=100)


@router.post("/generieren/ration", response_model=PortalEmpfehlungGeneratedOut, status_code=201, summary="Empfehlungen aus Rationskontext generieren")
def generiere_aus_ration(
    body: RationContext,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    customer_id = _kunde_fuer_angebot(db, tenant_id, nutzer, body.kunden_nr)
    neue = PortalIntelligenceService(db, tenant_id).generiere_aus_ration(
        customer_id=customer_id, akteur=str(nutzer.get("sub") or ""), tiere_anzahl=body.tiere_anzahl,
        tier_kategorie=body.tier_kategorie, benoetigt_rohwaren=body.benoetigt_rohwaren)
    return {"neue_empfehlungen": neue, "count": len(neue)}


class SchlagContext(BaseModel):
    kunden_nr: str = Field(..., min_length=1)
    kulturen: list[str] = Field(..., max_length=100)
    flaeche_ha: float = Field(..., ge=0)
    ernte_jahr: int = Field(..., ge=2000, le=2100)


@router.post("/generieren/schlagkartei", response_model=PortalEmpfehlungGeneratedOut, status_code=201, summary="Empfehlungen aus Schlagkartei-Kontext generieren")
def generiere_aus_schlagkartei(
    body: SchlagContext,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    customer_id = _kunde_fuer_angebot(db, tenant_id, nutzer, body.kunden_nr)
    neue = PortalIntelligenceService(db, tenant_id).generiere_aus_schlagkartei(
        customer_id=customer_id, akteur=str(nutzer.get("sub") or ""), kulturen=body.kulturen,
        flaeche_ha=body.flaeche_ha, ernte_jahr=body.ernte_jahr)
    return {"neue_empfehlungen": neue, "count": len(neue)}
