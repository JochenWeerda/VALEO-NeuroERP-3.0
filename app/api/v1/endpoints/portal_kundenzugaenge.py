"""Kundenzugaenge des Portals: welche Anmeldung welche Kundenkonten mit welcher Portalrolle sieht (TENANT-DOC-001,
PORTAL-CONTEXT-001).

Die Zuordnung pflegt die Leitung von Vertrieb oder Verkauf — oder der Betriebsinhaber fuer seinen eigenen Betrieb
(Benutzerverwaltung des Betriebs). Rollen, die das Haus vergibt (Aussendienst, Lohndienstleister), vergibt der Inhaber
nicht. Ein Mitarbeiter kann auf zugewiesene Schlaege beschraenkt werden. Zuordnungen werden widerrufen, nicht
geloescht. Die Anmeldung sieht ihre eigenen Konten, um das aktive zu waehlen (``X-Kundenkonto``).
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.beleg_roles import rollen_von
from app.auth.deps import get_current_user
from app.auth.portal_kunde import NUR_DURCH_DAS_HAUS, PORTAL_RECHTE, ZUGAENGE_VERWALTEN, Betriebsrolle, zugeordnete_kunden
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/portal", tags=["portal", "kundenzugang"])

# Zuordnungen pflegen: die Leitung von Vertrieb und Verkauf (dieselben Rollen wie in app/auth/beleg_roles.py).
LEITUNG_DES_HAUSES = frozenset({"CRM_ADMIN", "SALES_ADMIN", "admin"})


class Kundenkonto(BaseModel):
    customer_id: str
    rolle: str
    customer_number: Optional[str] = None
    name: Optional[str] = None
    rechte: list[str] = Field(default_factory=list)


class KundenzugangIn(BaseModel):
    subject: str = Field(..., min_length=1, description="Kennung der Anmeldung (OIDC sub)")
    customer_id: str = Field(..., min_length=1, description="CRM-Kunde dieses Mandanten")
    rolle: Betriebsrolle = Field(..., description="Portalrolle der Person")
    gueltig_bis: Optional[datetime] = None
    schlag_ids: Optional[list[str]] = Field(None, description="Nur Mitarbeiter: zugewiesene Schlaege; leer = alle")


class Kundenzugang(BaseModel):
    id: str
    subject: str
    customer_id: str
    rolle: str
    gueltig_bis: Optional[datetime] = None
    schlag_ids: Optional[list[str]] = None
    angelegt_von: str
    angelegt_am: datetime
    widerrufen_von: Optional[str] = None
    widerrufen_am: Optional[datetime] = None


def _akteur(nutzer) -> str:
    return str((nutzer or {}).get("sub") or "").strip() if isinstance(nutzer, dict) else ""


def _leitung(nutzer) -> bool:
    return bool(rollen_von(nutzer) & LEITUNG_DES_HAUSES)


def _inhaber_von(db: Session, tenant_id: str, nutzer) -> set[str]:
    """Kundenkonten, deren Benutzer diese Anmeldung verwalten darf (Portalrecht ``zugaenge_verwalten``)."""
    konten = zugeordnete_kunden(db, tenant_id, _akteur(nutzer), rollen_von(nutzer))
    return {k for k, rolle in konten.items() if ZUGAENGE_VERWALTEN in PORTAL_RECHTE.get(rolle, frozenset())}


def _darf_verwalten(db: Session, tenant_id: str, nutzer, customer_id: str) -> bool:
    return _leitung(nutzer) or customer_id in _inhaber_von(db, tenant_id, nutzer)


@router.get("/kundenkonten", response_model=list[Kundenkonto], summary="Eigene Kundenkonten der Anmeldung")
def meine_kundenkonten(
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    konten = zugeordnete_kunden(db, tenant_id, _akteur(nutzer), rollen_von(nutzer))
    if not konten:
        return []
    zeilen = db.execute(text(
        "SELECT id, customer_number, company_name FROM domain_crm.customers "
        "WHERE tenant_id = :t AND id = ANY(:ids) ORDER BY company_name LIMIT 500"),
        {"t": tenant_id, "ids": list(konten)})
    return [{"customer_id": z[0], "rolle": konten[z[0]], "customer_number": z[1], "name": z[2],
             "rechte": sorted(PORTAL_RECHTE.get(konten[z[0]], frozenset()))} for z in zeilen]


@router.get("/kundenzugaenge", response_model=list[Kundenzugang], summary="Kundenzugaenge auflisten")
def kundenzugaenge(
    customer_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    eigene: list[str] | None = None
    if not _leitung(nutzer):
        eigene = sorted(_inhaber_von(db, tenant_id, nutzer))
        if not eigene or (customer_id and customer_id not in eigene):
            raise HTTPException(status_code=403, detail="Keine Berechtigung: Kundenzugaenge verwalten")
    zeilen = db.execute(text("""
        SELECT id, subject, customer_id, rolle, gueltig_bis, schlag_ids, angelegt_von, angelegt_am, widerrufen_von,
               widerrufen_am
        FROM domain_portal.kundenzugaenge
        WHERE tenant_id = :t
          AND (CAST(:eigene AS text[]) IS NULL OR customer_id = ANY(CAST(:eigene AS text[])))
          AND (CAST(:c AS text) IS NULL OR customer_id = CAST(:c AS text))
        ORDER BY angelegt_am DESC, id
        LIMIT 1000
    """), {"t": tenant_id, "eigene": eigene, "c": customer_id or None})
    return [dict(z._mapping) for z in zeilen]


@router.post("/kundenzugaenge", response_model=Kundenzugang, status_code=201, summary="Kundenzugang anlegen")
def kundenzugang_anlegen(
    eingabe: KundenzugangIn,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if not _darf_verwalten(db, tenant_id, nutzer, eingabe.customer_id):
        raise HTTPException(status_code=403, detail="Keine Berechtigung: Kundenzugaenge verwalten")
    if eingabe.rolle in NUR_DURCH_DAS_HAUS and not _leitung(nutzer):
        raise HTTPException(status_code=403, detail=f"Die Rolle {eingabe.rolle} vergibt die Leitung des Hauses")
    kunde = db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": eingabe.customer_id, "t": tenant_id}).first()
    if kunde is None:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    schlaege = None
    if eingabe.schlag_ids:
        if eingabe.rolle != "mitarbeiter":
            raise HTTPException(status_code=422, detail="Zugewiesene Schlaege gibt es nur fuer Mitarbeiter")
        schlaege = sorted(set(eingabe.schlag_ids))
        vorhanden = {z[0] for z in db.execute(text(
            "SELECT id FROM domain_agrar.feldbuch_schlaege WHERE tenant_id = :t AND customer_id = :c "
            "AND id = ANY(:ids)"), {"t": tenant_id, "c": eingabe.customer_id, "ids": schlaege})}
        if set(schlaege) - vorhanden:
            raise HTTPException(status_code=422, detail="Schlaege gehoeren nicht zum Kundenkonto")
    try:
        zeile = db.execute(text("""
            INSERT INTO domain_portal.kundenzugaenge (id, tenant_id, subject, customer_id, rolle, gueltig_bis,
              schlag_ids, angelegt_von)
            VALUES (:id, :t, :s, :c, :r, :g, CAST(:sch AS jsonb), :v)
            RETURNING id, subject, customer_id, rolle, gueltig_bis, schlag_ids, angelegt_von, angelegt_am,
              widerrufen_von, widerrufen_am
        """), {"id": str(uuid.uuid4()), "t": tenant_id, "s": eingabe.subject.strip(), "c": eingabe.customer_id,
               "r": eingabe.rolle, "g": eingabe.gueltig_bis, "sch": json.dumps(schlaege) if schlaege else None,
               "v": _akteur(nutzer)}).one()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Diese Zuordnung besteht bereits") from exc
    return dict(zeile._mapping)


@router.post("/kundenzugaenge/{zugang_id}/widerrufen", response_model=Kundenzugang, summary="Kundenzugang widerrufen")
def kundenzugang_widerrufen(
    zugang_id: str,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    ziel = db.execute(text(
        "SELECT customer_id, rolle FROM domain_portal.kundenzugaenge WHERE id = :id AND tenant_id = :t"),
        {"id": zugang_id, "t": tenant_id}).first()
    if ziel is None:
        raise HTTPException(status_code=404, detail="Kundenzugang nicht gefunden oder bereits widerrufen")
    if not _darf_verwalten(db, tenant_id, nutzer, ziel.customer_id):
        raise HTTPException(status_code=403, detail="Keine Berechtigung: Kundenzugaenge verwalten")
    if ziel.rolle in NUR_DURCH_DAS_HAUS and not _leitung(nutzer):
        raise HTTPException(status_code=403, detail=f"Die Rolle {ziel.rolle} verwaltet die Leitung des Hauses")
    zeile = db.execute(text("""
        UPDATE domain_portal.kundenzugaenge SET widerrufen_von = :v, widerrufen_am = now()
        WHERE id = :id AND tenant_id = :t AND widerrufen_am IS NULL
        RETURNING id, subject, customer_id, rolle, gueltig_bis, schlag_ids, angelegt_von, angelegt_am,
          widerrufen_von, widerrufen_am
    """), {"id": zugang_id, "t": tenant_id, "v": _akteur(nutzer)}).first()
    if zeile is None:
        db.rollback()
        raise HTTPException(status_code=404, detail="Kundenzugang nicht gefunden oder bereits widerrufen")
    db.commit()
    return dict(zeile._mapping)
