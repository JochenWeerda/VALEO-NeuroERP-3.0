"""Daueraufträge [DAU] — Wiederkehrende Aufträge/Rechnungen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 02 Warenwirtschaft):
  Daueraufträge sind eine spezielle Form des Auftrages mit Turnus-Steuerung.
  Der Vorgangskopf enthält:
  - DA-Anfang: Startdatum
  - DA-Nächster Termin: nächste Fälligkeit
  - DA-Periode: Periodizität (1–12 Monate, wöchentlich, alle 2/3/4 Wochen,
    mehrfach im Monat/Woche)
  - DA-Ende: letztes wirksames Datum

  Funktion "Dauerauftrag starten" (SF9) erstellt eine Rechnung aus dem
  Dauerauftrag und setzt die nächste Fälligkeit neu.

  Perioden-Typen: monatlich (1..12), woechentlich, alle_2_wochen,
  alle_3_wochen, alle_4_wochen, mehrfach_monat, mehrfach_woche
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.dauerauftraege_schemas import (
    AusfuehrungOut,
    DauerauftragCreate,
    DauerauftragOut,
    DauerauftragPositionCreate,
    DauerauftragPositionOut,
)


router = APIRouter(prefix="/dauerauftraege", tags=["Warenwirtschaft - Daueraufträge"])

GUELTIGE_PERIODEN_TYPEN = (
    "monatlich", "woechentlich", "alle_2_wochen",
    "alle_3_wochen", "alle_4_wochen", "mehrfach_monat", "mehrfach_woche",
)


# ── Schemas ───────────────────────────────────────────────────────────────────

# ── Helpers ───────────────────────────────────────────────────────────────────

def _naechster_termin(aktuell: date, perioden_typ: str, perioden_wert: int) -> date:
    """Berechnet den nächsten Fälligkeitstermin."""
    from calendar import monthrange
    if perioden_typ == "monatlich":
        monat = aktuell.month + perioden_wert
        jahr = aktuell.year + (monat - 1) // 12
        monat = ((monat - 1) % 12) + 1
        tag = min(aktuell.day, monthrange(jahr, monat)[1])
        return date(jahr, monat, tag)
    if perioden_typ == "woechentlich":
        return aktuell + timedelta(weeks=1)
    if perioden_typ == "alle_2_wochen":
        return aktuell + timedelta(weeks=2)
    if perioden_typ == "alle_3_wochen":
        return aktuell + timedelta(weeks=3)
    if perioden_typ == "alle_4_wochen":
        return aktuell + timedelta(weeks=4)
    return aktuell + timedelta(days=30)


def _load_positionen(db, tenant_id: str, dauerauftrag_id: str) -> list:
    rows = db.execute(text("""
        SELECT * FROM domain_shared.dauerauftrag_positionen
        WHERE tenant_id = :tid AND dauerauftrag_id = :did
        ORDER BY pos_nr
    """), {"tid": tenant_id, "did": dauerauftrag_id}).fetchall()
    return [DauerauftragPositionOut(**dict(r._mapping)) for r in rows]


def _row_to_out(db, tenant_id: str, row) -> DauerauftragOut:
    d = dict(row._mapping)
    d["positionen"] = _load_positionen(db, tenant_id, d["id"])
    return DauerauftragOut(**d)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[DauerauftragOut], summary="Dauerauftraege auflisten")
def list_dauerauftraege(
    kunden_nr: Optional[str] = Query(None),
    nur_aktive: bool = Query(True),
    faellig_bis: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.dauerauftraege WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if kunden_nr:
        sql += " AND kunden_nr = :kdnr"
        params["kdnr"] = kunden_nr
    if nur_aktive:
        sql += " AND aktiv = true"
    if faellig_bis:
        sql += " AND da_naechster <= :fdatum"
        params["fdatum"] = faellig_bis
    sql += " ORDER BY da_naechster"
    rows = db.execute(text(sql), params).fetchall()
    return [_row_to_out(db, tenant_id, r) for r in rows]


@router.get("/{da_nr}", response_model=DauerauftragOut, summary="Dauerauftrag abrufen")
def get_dauerauftrag(
    da_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.dauerauftraege
        WHERE tenant_id = :tid AND da_nr = :nr
    """), {"tid": tenant_id, "nr": da_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Dauerauftrag nicht gefunden.")
    return _row_to_out(db, tenant_id, row)


@router.post("", response_model=DauerauftragOut, status_code=201, summary="Dauerauftrag anlegen")
def create_dauerauftrag(
    payload: DauerauftragCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.perioden_typ not in GUELTIGE_PERIODEN_TYPEN:
        raise HTTPException(422, f"Ungültiger Perioden-Typ: {payload.perioden_typ}")

    new_id = uuid7()
    da_nr = payload.da_nr or f"DA-{new_id[:8].upper()}"

    existing = db.execute(text("""
        SELECT id FROM domain_shared.dauerauftraege
        WHERE tenant_id = :tid AND da_nr = :nr
    """), {"tid": tenant_id, "nr": da_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Dauerauftrag {da_nr} bereits vorhanden.")

    db.execute(text("""
        INSERT INTO domain_shared.dauerauftraege
            (id, tenant_id, da_nr, kunden_nr, bezeichnung,
             da_anfang, da_naechster, da_ende, perioden_typ, perioden_wert, aktiv)
        VALUES (:id, :tid, :nr, :kdnr, :bez,
                :anfang, :naechster, :ende, :ptyp, :pwert, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": da_nr,
        "kdnr": payload.kunden_nr, "bez": payload.bezeichnung,
        "anfang": payload.da_anfang, "naechster": payload.da_naechster,
        "ende": payload.da_ende, "ptyp": payload.perioden_typ,
        "pwert": payload.perioden_wert,
    })

    for pos in payload.positionen:
        db.execute(text("""
            INSERT INTO domain_shared.dauerauftrag_positionen
                (id, tenant_id, dauerauftrag_id, pos_nr, artikel_nr, menge, mengeneinheit, preis_eur)
            VALUES (:id, :tid, :did, :pnr, :anr, :menge, :me, :preis)
        """), {
            "id": uuid7(), "tid": tenant_id, "did": new_id,
            "pnr": pos.pos_nr, "anr": pos.artikel_nr,
            "menge": pos.menge, "me": pos.mengeneinheit, "preis": pos.preis_eur,
        })

    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.dauerauftraege WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return _row_to_out(db, tenant_id, row)


@router.post("/{da_nr}/starten", response_model=AusfuehrungOut, summary="Starten dauerauftrag")
def dauerauftrag_starten(
    da_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt eine Rechnung aus dem Dauerauftrag und setzt nächste Fälligkeit."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.dauerauftraege
        WHERE tenant_id = :tid AND da_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": da_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Dauerauftrag nicht gefunden oder inaktiv.")

    d = dict(row._mapping)
    if d["da_ende"] and date.today() > d["da_ende"]:
        raise HTTPException(409, "Dauerauftrag ist abgelaufen (DA-Ende überschritten).")

    ausfuehrungs_id = uuid7()
    belegnummer = f"RE-DA-{ausfuehrungs_id[:8].upper()}"

    db.execute(text("""
        INSERT INTO domain_shared.dauerauftrag_ausfuehrungen
            (id, tenant_id, dauerauftrag_id, ausfuehrungs_datum, belegnummer, status)
        VALUES (:id, :tid, :did, :datum, :beleg, 'erstellt')
    """), {
        "id": ausfuehrungs_id, "tid": tenant_id, "did": d["id"],
        "datum": date.today(), "beleg": belegnummer,
    })

    naechster = _naechster_termin(d["da_naechster"], d["perioden_typ"], d["perioden_wert"])
    db.execute(text("""
        UPDATE domain_shared.dauerauftraege
        SET da_naechster = :naechster, letzter_lauf = now()
        WHERE id = :id
    """), {"naechster": naechster, "id": d["id"]})
    db.commit()

    aus_row = db.execute(text(
        "SELECT * FROM domain_shared.dauerauftrag_ausfuehrungen WHERE id = :id"
    ), {"id": ausfuehrungs_id}).fetchone()
    return AusfuehrungOut(**dict(aus_row._mapping))


@router.get("/{da_nr}/ausfuehrungen", response_model=list[AusfuehrungOut], summary="Ausfuehrungen auflisten")
def list_ausfuehrungen(
    da_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    da_row = db.execute(text("""
        SELECT id FROM domain_shared.dauerauftraege
        WHERE tenant_id = :tid AND da_nr = :nr
    """), {"tid": tenant_id, "nr": da_nr}).fetchone()
    if not da_row:
        raise HTTPException(404, "Dauerauftrag nicht gefunden.")

    rows = db.execute(text("""
        SELECT * FROM domain_shared.dauerauftrag_ausfuehrungen
        WHERE tenant_id = :tid AND dauerauftrag_id = :did
        ORDER BY ausfuehrungs_datum DESC
    """), {"tid": tenant_id, "did": da_row.id}).fetchall()
    return [AusfuehrungOut(**dict(r._mapping)) for r in rows]


@router.patch("/{da_nr}/deaktivieren", summary="Deaktivieren",
    response_model=None
)
def deaktivieren(
    da_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.dauerauftraege SET aktiv = false
        WHERE tenant_id = :tid AND da_nr = :nr
    """), {"tid": tenant_id, "nr": da_nr})
    db.commit()
    return Response(status_code=204)
