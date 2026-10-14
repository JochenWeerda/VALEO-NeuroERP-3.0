"""PORTAL-LOHNDIENST-001 — Lohndienstleistungs-Auftrags-API (persistent, PORTAL-CONTEXT-001).

Mandant und Kunde nur aus Anmeldung und gepruefter Zuordnung (``app/auth/portal_kunde.py``); was eine Anmeldung darf,
bestimmt ihre Portalrolle (``PORTAL_RECHTE``) bzw. beim Innendienst die Fachrolle fuer Auftraege
(``app/auth/beleg_roles.py``, ``sales_order``). Jede Aenderung braucht den Kopf ``X-Idempotency-Key``; ein
Statuswechsel nennt die gesehene ``erwartete_version``.

* Anlegen: Portalrolle mit ``lohndienst_beauftragen``; Innendienst zusaetzlich ``sales_order`` bearbeiten.
* Lesen: ``lohndienst_lesen``; ein Lohndienstleister sieht nur die ihm zugewiesenen Auftraege.
* Bestaetigen (Freigabe), Einplanen: nur Innendienst. Abschliessen: Innendienst oder der zugewiesene
  Lohndienstleister. Stornieren: Innendienst; im Portal nur, solange der Auftrag angefragt ist.
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.portal_bundle_schemas import (
    PortalLohndienstAuftragOut,
    PortalLohndienstEreignisOut,
    PortalLohndienstListOut,
)
from app.auth.beleg_roles import darf, verlange
from app.auth.deps import get_current_user
from app.auth.portal_kunde import (
    KOPF,
    LOHNDIENST_AUSFUEHREN,
    LOHNDIENST_BEAUFTRAGEN,
    LOHNDIENST_LESEN,
    PortalKunde,
    portal_kunde,
    portal_recht,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_lohndienst_service import (
    Aktion,
    AuftragNichtGefundenFehler,
    IdempotenzKonflikt,
    LohndienstService,
    LohndienstStatus,
    LohndienstTyp,
    UngueltigerStatusFehler,
    VersionsKonflikt,
)

router = APIRouter(prefix="/portal/lohndienste", tags=["portal", "lohndienste"])

IDEMPOTENZ_KOPF = "X-Idempotency-Key"


def _schluessel(schluessel: str = Header(..., alias=IDEMPOTENZ_KOPF, min_length=8, max_length=100)) -> str:
    return schluessel.strip()


def _innendienst(recht: str):
    def _pruefen(nutzer: dict = Depends(get_current_user)) -> dict:
        verlange(nutzer, recht, "sales_order")
        return nutzer

    return _pruefen


class AuftragCreateBody(BaseModel):
    typ: LohndienstTyp
    schlag_ids: list[str] = Field(default_factory=list, max_length=500)
    schlag_beschreibung: str = Field("", max_length=2000)
    flaeche_ha: float | None = Field(None, ge=0)
    wunsch_datum: date | None = None
    getreide_art: str | None = Field(None, max_length=200)
    menge_dt: float | None = Field(None, ge=0)
    tierart: str | None = Field(None, max_length=200)
    tiere_anzahl: int | None = Field(None, ge=0)
    psm_mittel: list[str] = Field(default_factory=list, max_length=100)
    kultur: str | None = Field(None, max_length=200)
    anmerkung: str | None = Field(None, max_length=4000)


class StatusWechselBody(BaseModel):
    aktion: Aktion
    erwartete_version: int = Field(..., ge=1)
    geplant_datum: date | None = None
    innendienst_notiz: str | None = Field(None, max_length=4000)
    preis_indikativ_eur: float | None = None
    dienstleister_subject: str | None = Field(None, max_length=200, description="Anmeldung des Lohndienstleisters")


def _ausgabe(auftrag: dict[str, Any], intern: bool) -> dict[str, Any]:
    a = dict(auftrag)
    a["dienstleister_zugewiesen"] = bool(a.get("dienstleister_subject"))
    if not intern:
        a["dienstleister_subject"] = None  # Datenminimierung: die Anmeldung des Dienstleisters bleibt intern
    return a


def _fehler(e: Exception) -> HTTPException:
    if isinstance(e, AuftragNichtGefundenFehler):
        return HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    if isinstance(e, VersionsKonflikt):
        return HTTPException(status_code=409, detail={"meldung": str(e), "aktuelle_version": e.aktuelle_version})
    if isinstance(e, (UngueltigerStatusFehler, IdempotenzKonflikt)):
        return HTTPException(status_code=409, detail=str(e))
    return HTTPException(status_code=422, detail=str(e))


def _dienstleister(kunde: PortalKunde) -> Optional[str]:
    return kunde.subject if kunde.rolle == "lohndienstleister" else None


@router.post("", response_model=PortalLohndienstAuftragOut, status_code=201, summary="Lohndienst-Auftrag anlegen")
def auftrag_anlegen(
    body: AuftragCreateBody,
    kunde: PortalKunde = Depends(portal_recht(LOHNDIENST_BEAUFTRAGEN)),
    nutzer: dict = Depends(get_current_user),
    schluessel: str = Depends(_schluessel),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    if kunde.intern:
        verlange(nutzer, "bearbeiten", "sales_order")
    felder = body.model_dump(exclude={"typ"})
    try:
        auftrag = LohndienstService(db, kunde.tenant_id).auftrag_anlegen(
            customer_id=kunde.customer_id, typ=body.typ, akteur=kunde.subject,
            kanal="intern" if kunde.intern else "portal", idempotenz_schluessel=schluessel, **felder)
    except (ValueError, IdempotenzKonflikt) as e:
        raise _fehler(e) from e
    return _ausgabe(auftrag, kunde.intern)


@router.get("", response_model=PortalLohndienstListOut, summary="Lohndienst-Auftraege des Kundenkontos")
def list_auftraege(
    typ: LohndienstTyp | None = Query(None),
    status: LohndienstStatus | None = Query(None),
    kunde: PortalKunde = Depends(portal_recht(LOHNDIENST_LESEN)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items = LohndienstService(db, kunde.tenant_id).list_auftraege(
        customer_id=kunde.customer_id, dienstleister=_dienstleister(kunde), typ=typ, status=status)
    return {"items": [_ausgabe(a, kunde.intern) for a in items], "count": len(items)}


@router.get("/disposition", response_model=PortalLohndienstListOut, summary="Lohndienst-Disposition (Innendienst)",
            dependencies=[Depends(_innendienst("lesen"))])
def disposition(
    typ: LohndienstTyp | None = Query(None),
    status: LohndienstStatus | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Alle Auftraege des Mandanten fuer die Disposition — ueber alle Kunden, nur mit Fachrolle des Hauses."""
    items = LohndienstService(db, tenant_id).list_auftraege(typ=typ, status=status)
    return {"items": [_ausgabe(a, True) for a in items], "count": len(items)}


@router.get("/{auftrag_id}", response_model=PortalLohndienstAuftragOut, summary="Lohndienst-Auftrag abrufen")
def get_auftrag(
    auftrag_id: str,
    kunde: PortalKunde = Depends(portal_recht(LOHNDIENST_LESEN)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = LohndienstService(db, kunde.tenant_id)
    try:
        auftrag = svc.get_auftrag(auftrag_id, customer_id=kunde.customer_id, dienstleister=_dienstleister(kunde))
    except AuftragNichtGefundenFehler as e:
        raise _fehler(e) from e
    return {**_ausgabe(auftrag, kunde.intern), "schlaege": svc.schlaege(auftrag)}


@router.get("/{auftrag_id}/historie", response_model=list[PortalLohndienstEreignisOut],
            summary="Statushistorie eines Lohndienst-Auftrags")
def historie(
    auftrag_id: str,
    kunde: PortalKunde = Depends(portal_recht(LOHNDIENST_LESEN)),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    svc = LohndienstService(db, kunde.tenant_id)
    try:
        svc.get_auftrag(auftrag_id, customer_id=kunde.customer_id, dienstleister=_dienstleister(kunde))
    except AuftragNichtGefundenFehler as e:
        raise _fehler(e) from e
    eintraege = svc.historie(auftrag_id)
    if not kunde.intern:  # Datenminimierung: Portalnutzer sehen den Kanal, nicht die Anmeldung des Innendiensts
        eintraege = [{**e, "akteur": e["akteur"] if e["kanal"] == "portal" else "Innendienst"} for e in eintraege]
    return eintraege


def _dienstleister_des_kunden(db: Session, tenant_id: str, customer_id: str, subject: str) -> bool:
    return db.execute(text(
        "SELECT 1 FROM domain_portal.kundenzugaenge WHERE tenant_id = :t AND customer_id = :c AND subject = :s "
        "AND rolle = 'lohndienstleister' AND widerrufen_am IS NULL AND (gueltig_bis IS NULL OR gueltig_bis > now())"),
        {"t": tenant_id, "c": customer_id, "s": subject}).first() is not None


@router.post("/{auftrag_id}/status", response_model=PortalLohndienstAuftragOut,
             summary="Lohndienst-Auftrag fortschreiben (bestaetigen, einplanen, abschliessen, stornieren)")
def status_wechsel(
    auftrag_id: str,
    body: StatusWechselBody,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    schluessel: str = Depends(_schluessel),
    kundenkonto: Optional[str] = Header(None, alias=KOPF),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = LohndienstService(db, tenant_id)
    kwargs: dict[str, Any] = dict(
        auftrag_id=auftrag_id, aktion=body.aktion, erwartete_version=body.erwartete_version,
        idempotenz_schluessel=schluessel)
    try:
        if darf(nutzer, "bearbeiten", "sales_order"):
            # Innendienst: Disposition ueber alle Kunden des Mandanten.
            if body.dienstleister_subject:
                if body.aktion is not Aktion.EINPLANEN:
                    raise HTTPException(status_code=422, detail="Ein Lohndienstleister wird beim Einplanen zugewiesen")
                kunde_id = svc.get_auftrag(auftrag_id)["customer_id"]
                if not _dienstleister_des_kunden(db, tenant_id, kunde_id, body.dienstleister_subject):
                    raise HTTPException(status_code=422, detail="Kein Lohndienstleister dieses Kundenkontos")
            auftrag = svc.status_wechsel(
                **kwargs, akteur=str(nutzer.get("sub") or ""), kanal="intern", geplant_datum=body.geplant_datum,
                innendienst_notiz=body.innendienst_notiz, preis_indikativ_eur=body.preis_indikativ_eur,
                dienstleister_subject=body.dienstleister_subject)
            return _ausgabe(auftrag, True)

        kunde = portal_kunde(tenant_id=tenant_id, nutzer=nutzer, db=db, kundenkonto=kundenkonto)
        if any(v is not None for v in (body.geplant_datum, body.innendienst_notiz, body.preis_indikativ_eur,
                                         body.dienstleister_subject)):
            raise HTTPException(status_code=403, detail="Termin, Notiz, Preis und Zuweisung setzt der Innendienst")
        if body.aktion is Aktion.STORNIEREN and kunde.darf(LOHNDIENST_BEAUFTRAGEN) and not kunde.intern:
            vorher = svc.get_auftrag(auftrag_id, customer_id=kunde.customer_id)
            if vorher["status"] != LohndienstStatus.ANGEFRAGT.value and vorher["version"] == body.erwartete_version:
                raise HTTPException(status_code=409, detail="Im Portal nur stornierbar, solange der Auftrag angefragt ist")
            auftrag = svc.status_wechsel(**kwargs, akteur=kunde.subject, kanal="portal",
                                         customer_id=kunde.customer_id)
        elif body.aktion is Aktion.ABSCHLIESSEN and kunde.darf(LOHNDIENST_AUSFUEHREN):
            auftrag = svc.status_wechsel(**kwargs, akteur=kunde.subject, kanal="portal",
                                         customer_id=kunde.customer_id, dienstleister=kunde.subject)
        else:
            raise HTTPException(status_code=403, detail=f"Keine Berechtigung: Lohndienst {body.aktion.value}")
        return _ausgabe(auftrag, False)
    except (AuftragNichtGefundenFehler, VersionsKonflikt, UngueltigerStatusFehler, IdempotenzKonflikt,
            ValueError) as e:
        raise _fehler(e) from e
