"""Zahlungsmeldungen [KASSZAME] — Eingehende Zahlungsanzeigen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Zahlungsmeldungen (EPA KASSZAME) sind eingehende Zahlungsanzeigen, die
  Offene Posten (OP) ausziffern. Parameter:
  - Gewährung zusätzlicher Skonto erlaubt: Einzel-Skonto über Zahlungsvereinbarung
  - Teilzahlungen zugelassen: OP bleibt offen für den Restbetrag
  - Auch Ausgangsrechnungen aus FIBU verwenden: Statt nur WaWi-Rechnungen

  Typischer Prozess: Zahlungseingang (z.B. CAMT.053 Kontoauszug) →
  Zahlungsmeldung anlegen → Auszifferung → OP schließen

  Integration mit OP Skonto-Auszifferung: Zahlungsmeldungen mit Skonto können
  direkt zur Skonto-Auszifferung weiterverarbeitet werden.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/fibu/zahlungsmeldungen",
                   tags=["FIBU - Zahlungsmeldungen"])

GUELTIGE_STATUS = ("eingegangen", "verarbeitet", "abgewiesen")


# ── Schemas ───────────────────────────────────────────────────────────────────

class ZahlungsmeldungCreate(BaseModel):
    meldungs_nr: Optional[str] = None
    kunden_nr: str
    rechnungs_nr: Optional[str] = None
    zahlungsdatum: date
    zahlungsbetrag_eur: Decimal = Field(..., gt=0)
    skonto_betrag_eur: Decimal = Field(default=Decimal("0"), ge=0)
    skonto_erlaubt: bool = False
    teilzahlung: bool = False
    aus_fibu: bool = False


class ZahlungsmeldungOut(BaseModel):
    id: str
    meldungs_nr: Optional[str]
    kunden_nr: str
    rechnungs_nr: Optional[str]
    zahlungsdatum: date
    zahlungsbetrag_eur: Decimal
    skonto_betrag_eur: Decimal
    skonto_erlaubt: bool
    teilzahlung: bool
    aus_fibu: bool
    status: str
    verarbeitet_am: Optional[datetime]
    created_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ZahlungsmeldungOut], summary="Zahlungsmeldungen auflisten")
def list_zahlungsmeldungen(
    kunden_nr: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von_datum: Optional[date] = Query(None),
    bis_datum: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.fibu_zahlungsmeldungen WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if kunden_nr:
        sql += " AND kunden_nr = :kdnr"
        params["kdnr"] = kunden_nr
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if von_datum:
        sql += " AND zahlungsdatum >= :von"
        params["von"] = von_datum
    if bis_datum:
        sql += " AND zahlungsdatum <= :bis"
        params["bis"] = bis_datum
    sql += " ORDER BY zahlungsdatum DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [ZahlungsmeldungOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=ZahlungsmeldungOut, status_code=201, summary="Zahlungsmeldung anlegen")
def create_zahlungsmeldung(
    payload: ZahlungsmeldungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.fibu_zahlungsmeldungen
            (id, tenant_id, meldungs_nr, kunden_nr, rechnungs_nr,
             zahlungsdatum, zahlungsbetrag_eur, skonto_betrag_eur,
             skonto_erlaubt, teilzahlung, aus_fibu, status)
        VALUES (:id, :tid, :mnr, :kdnr, :rnr, :zdatum, :zbetrag, :skonto,
                :sk_erl, :teil, :fibu, 'eingegangen')
    """), {
        "id": new_id, "tid": tenant_id, "mnr": payload.meldungs_nr,
        "kdnr": payload.kunden_nr, "rnr": payload.rechnungs_nr,
        "zdatum": payload.zahlungsdatum, "zbetrag": payload.zahlungsbetrag_eur,
        "skonto": payload.skonto_betrag_eur, "sk_erl": payload.skonto_erlaubt,
        "teil": payload.teilzahlung, "fibu": payload.aus_fibu,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.fibu_zahlungsmeldungen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZahlungsmeldungOut(**dict(row._mapping))


@router.post("/{meldung_id}/verarbeiten", response_model=ZahlungsmeldungOut, summary="Verarbeiten meldung")
def meldung_verarbeiten(
    meldung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zahlungsmeldung als verarbeitet markieren (OP wurde ausgeziffert)."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.fibu_zahlungsmeldungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": meldung_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Zahlungsmeldung nicht gefunden.")
    if row.status != "eingegangen":
        raise HTTPException(409, f"Zahlungsmeldung hat Status '{row.status}', nicht 'eingegangen'.")

    db.execute(text("""
        UPDATE domain_shared.fibu_zahlungsmeldungen
        SET status = 'verarbeitet', verarbeitet_am = now()
        WHERE id = :id
    """), {"id": meldung_id})
    db.commit()
    updated = db.execute(text(
        "SELECT * FROM domain_shared.fibu_zahlungsmeldungen WHERE id = :id"
    ), {"id": meldung_id}).fetchone()
    return ZahlungsmeldungOut(**dict(updated._mapping))


@router.post("/{meldung_id}/abweisen", response_model=ZahlungsmeldungOut, summary="Abweisen meldung")
def meldung_abweisen(
    meldung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zahlungsmeldung abweisen (z.B. Betrag stimmt nicht überein)."""
    row = db.execute(text("""
        SELECT status FROM domain_shared.fibu_zahlungsmeldungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": meldung_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Zahlungsmeldung nicht gefunden.")
    if row.status == "verarbeitet":
        raise HTTPException(409, "Bereits verarbeitete Meldungen können nicht abgewiesen werden.")

    db.execute(text("""
        UPDATE domain_shared.fibu_zahlungsmeldungen
        SET status = 'abgewiesen', verarbeitet_am = now()
        WHERE id = :id
    """), {"id": meldung_id})
    db.commit()
    updated = db.execute(text(
        "SELECT * FROM domain_shared.fibu_zahlungsmeldungen WHERE id = :id"
    ), {"id": meldung_id}).fetchone()
    return ZahlungsmeldungOut(**dict(updated._mapping))


@router.get("/offen/zusammenfassung", summary="Meldungen zusammenfassung offene",
    response_model=list
)
def offene_meldungen_zusammenfassung(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zusammenfassung der offenen Zahlungsmeldungen nach Kunden."""
    rows = db.execute(text("""
        SELECT kunden_nr,
               COUNT(*) as anzahl,
               SUM(zahlungsbetrag_eur) as gesamt_betrag_eur,
               SUM(skonto_betrag_eur) as gesamt_skonto_eur,
               MIN(zahlungsdatum) as aelteste_meldung
        FROM domain_shared.fibu_zahlungsmeldungen
        WHERE tenant_id = :tid AND status = 'eingegangen'
        GROUP BY kunden_nr
        ORDER BY gesamt_betrag_eur DESC
    """), {"tid": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]
