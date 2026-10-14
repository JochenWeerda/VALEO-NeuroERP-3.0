"""Kundenzugaenge des Portals: welche Anmeldung welche Kundenkonten sehen darf (TENANT-DOC-001).

Die Zuordnung pflegt die Leitung von Vertrieb oder Verkauf. Sie wird widerrufen, nicht geloescht. Der Portalkunde
sieht seine eigenen Konten, um das aktive zu waehlen (``X-Kundenkonto``).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.auth.portal_kunde import Betriebsrolle, zugeordnete_kunden
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/portal", tags=["portal", "kundenzugang"])

# Zuordnungen pflegen: die Leitung von Vertrieb und Verkauf (dieselben Rollen wie in app/auth/beleg_roles.py).
kundenzugang_verwalten = require_roles("CRM_ADMIN", "SALES_ADMIN", "admin")


class Kundenkonto(BaseModel):
    customer_id: str
    rolle: str
    customer_number: Optional[str] = None
    name: Optional[str] = None


class KundenzugangIn(BaseModel):
    subject: str = Field(..., min_length=1, description="Kennung der Anmeldung (OIDC sub)")
    customer_id: str = Field(..., min_length=1, description="CRM-Kunde dieses Mandanten")
    rolle: Betriebsrolle = Field(..., description="Rolle der Person im Betrieb")
    gueltig_bis: Optional[datetime] = None


class Kundenzugang(BaseModel):
    id: str
    subject: str
    customer_id: str
    rolle: str
    gueltig_bis: Optional[datetime] = None
    angelegt_von: str
    angelegt_am: datetime
    widerrufen_von: Optional[str] = None
    widerrufen_am: Optional[datetime] = None


def _akteur(nutzer) -> str:
    return str((nutzer or {}).get("sub") or "").strip() if isinstance(nutzer, dict) else ""


@router.get("/kundenkonten", response_model=list[Kundenkonto], summary="Eigene Kundenkonten der Anmeldung")
def meine_kundenkonten(
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    konten = zugeordnete_kunden(db, tenant_id, _akteur(nutzer))
    if not konten:
        return []
    zeilen = db.execute(text(
        "SELECT id, customer_number, company_name FROM domain_crm.customers "
        "WHERE tenant_id = :t AND id = ANY(:ids) ORDER BY company_name"), {"t": tenant_id, "ids": list(konten)}).all()
    return [{"customer_id": z[0], "rolle": konten[z[0]], "customer_number": z[1], "name": z[2]} for z in zeilen]


@router.get("/kundenzugaenge", response_model=list[Kundenzugang], summary="Kundenzugaenge auflisten",
            dependencies=[Depends(kundenzugang_verwalten)])
def kundenzugaenge(
    customer_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    sql = ("SELECT id, subject, customer_id, rolle, gueltig_bis, angelegt_von, angelegt_am, widerrufen_von, widerrufen_am "
           "FROM domain_portal.kundenzugaenge WHERE tenant_id = :t")
    werte: dict = {"t": tenant_id}
    if customer_id:
        sql += " AND customer_id = :c"
        werte["c"] = customer_id
    return [dict(z._mapping) for z in db.execute(text(sql + " ORDER BY angelegt_am DESC, id"), werte)]


@router.post("/kundenzugaenge", response_model=Kundenzugang, status_code=201, summary="Kundenzugang anlegen")
def kundenzugang_anlegen(
    eingabe: KundenzugangIn,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(kundenzugang_verwalten),
    db: Session = Depends(get_db),
) -> dict:
    kunde = db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": eingabe.customer_id, "t": tenant_id}).first()
    if kunde is None:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    try:
        zeile = db.execute(text("""
            INSERT INTO domain_portal.kundenzugaenge (id, tenant_id, subject, customer_id, rolle, gueltig_bis, angelegt_von)
            VALUES (:id, :t, :s, :c, :r, :g, :v)
            RETURNING id, subject, customer_id, rolle, gueltig_bis, angelegt_von, angelegt_am, widerrufen_von, widerrufen_am
        """), {"id": str(uuid.uuid4()), "t": tenant_id, "s": eingabe.subject.strip(), "c": eingabe.customer_id,
               "r": eingabe.rolle, "g": eingabe.gueltig_bis, "v": _akteur(nutzer)}).one()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Diese Zuordnung besteht bereits") from exc
    return dict(zeile._mapping)


@router.post("/kundenzugaenge/{zugang_id}/widerrufen", response_model=Kundenzugang, summary="Kundenzugang widerrufen")
def kundenzugang_widerrufen(
    zugang_id: str,
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(kundenzugang_verwalten),
    db: Session = Depends(get_db),
) -> dict:
    zeile = db.execute(text("""
        UPDATE domain_portal.kundenzugaenge SET widerrufen_von = :v, widerrufen_am = now()
        WHERE id = :id AND tenant_id = :t AND widerrufen_am IS NULL
        RETURNING id, subject, customer_id, rolle, gueltig_bis, angelegt_von, angelegt_am, widerrufen_von, widerrufen_am
    """), {"id": zugang_id, "t": tenant_id, "v": _akteur(nutzer)}).first()
    if zeile is None:
        db.rollback()
        raise HTTPException(status_code=404, detail="Kundenzugang nicht gefunden oder bereits widerrufen")
    db.commit()
    return dict(zeile._mapping)
