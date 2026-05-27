"""Betriebsstätten/Filialen — Filialsystem-Stammdaten.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 06 CRM/Kunden):
  Das Betriebsstätten/Filialsystem (Direktsprung [FILS]) ermöglicht die
  Verwaltung von Filialen und Betriebsstätten. Felder:
  - Filialnummer: eindeutige Kennung
  - Bezeichnung: Filialname
  - Ist-Zentrale: Kennzeichen ob Hauptstelle
  - Filialnummer Zentrale: Übergeordnete Betriebsstätte
  - Ident-Bereich: Untergrenze/Obergrenze für Ident-Nummernkreis
  - Untergeordnete Betriebsstätten: Liste aller Filialen der Zentrale

  Verwendung: Tenantseitige Filialsteuerung, Replikationsadressen,
  Publikationszuordnung für Multi-Location-Mandanten.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/stammdaten/betriebsstaetten",
                   tags=["Stammdaten - Betriebsstätten & Filialen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class BetriebsstaetteCreate(BaseModel):
    filial_nr: str = Field(..., max_length=20)
    bezeichnung: str
    ist_zentrale: bool = False
    zentrale_filial_nr: Optional[str] = None
    ident_untergrenze: Optional[int] = None
    ident_obergrenze: Optional[int] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None


class BetriebsstaetteOut(BaseModel):
    id: str
    filial_nr: str
    bezeichnung: str
    ist_zentrale: bool
    zentrale_filial_nr: Optional[str]
    ident_untergrenze: Optional[int]
    ident_obergrenze: Optional[int]
    strasse: Optional[str]
    plz: Optional[str]
    ort: Optional[str]
    land: Optional[str]
    telefon: Optional[str]
    email: Optional[str]
    aktiv: bool
    created_at: datetime
    untergeordnete: list[str] = []


# ── Endpoints ─────────────────────────────────────────────────────────────────

def _load_untergeordnete(db, tenant_id: str, filial_nr: str) -> list[str]:
    rows = db.execute(text("""
        SELECT filial_nr FROM domain_shared.betriebsstaetten
        WHERE tenant_id = :tid AND zentrale_filial_nr = :znr AND aktiv = true
        ORDER BY filial_nr
    """), {"tid": tenant_id, "znr": filial_nr}).fetchall()
    return [r.filial_nr for r in rows]


@router.get("", response_model=list[BetriebsstaetteOut], summary="Betriebsstaetten auflisten")
def list_betriebsstaetten(
    nur_zentralen: bool = Query(False),
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.betriebsstaetten WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    if nur_zentralen:
        sql += " AND ist_zentrale = true"
    sql += " ORDER BY filial_nr"
    rows = db.execute(text(sql), params).fetchall()
    result = []
    for r in rows:
        d = dict(r._mapping)
        d["untergeordnete"] = _load_untergeordnete(db, tenant_id, d["filial_nr"])
        result.append(BetriebsstaetteOut(**d))
    return result


@router.get("/{filial_nr}", response_model=BetriebsstaetteOut, summary="Betriebsstaette abrufen")
def get_betriebsstaette(
    filial_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.betriebsstaetten
        WHERE tenant_id = :tid AND filial_nr = :nr
    """), {"tid": tenant_id, "nr": filial_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Betriebsstätte nicht gefunden.")
    d = dict(row._mapping)
    d["untergeordnete"] = _load_untergeordnete(db, tenant_id, filial_nr)
    return BetriebsstaetteOut(**d)


@router.post("", response_model=BetriebsstaetteOut, status_code=201, summary="Betriebsstaette anlegen")
def create_betriebsstaette(
    payload: BetriebsstaetteCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.betriebsstaetten
        WHERE tenant_id = :tid AND filial_nr = :nr
    """), {"tid": tenant_id, "nr": payload.filial_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Betriebsstätte {payload.filial_nr} bereits vorhanden.")

    if payload.zentrale_filial_nr:
        zentrale = db.execute(text("""
            SELECT id FROM domain_shared.betriebsstaetten
            WHERE tenant_id = :tid AND filial_nr = :nr
        """), {"tid": tenant_id, "nr": payload.zentrale_filial_nr}).fetchone()
        if not zentrale:
            raise HTTPException(404, f"Zentrale {payload.zentrale_filial_nr} nicht gefunden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.betriebsstaetten
            (id, tenant_id, filial_nr, bezeichnung, ist_zentrale, zentrale_filial_nr,
             ident_untergrenze, ident_obergrenze, strasse, plz, ort, land, telefon, email)
        VALUES (:id, :tid, :nr, :bez, :iszentrale, :znr, :iu, :io, :str, :plz, :ort, :land, :tel, :email)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.filial_nr,
        "bez": payload.bezeichnung, "iszentrale": payload.ist_zentrale,
        "znr": payload.zentrale_filial_nr, "iu": payload.ident_untergrenze,
        "io": payload.ident_obergrenze, "str": payload.strasse,
        "plz": payload.plz, "ort": payload.ort, "land": payload.land,
        "tel": payload.telefon, "email": payload.email,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.betriebsstaetten WHERE id = :id"
    ), {"id": new_id}).fetchone()
    d = dict(row._mapping)
    d["untergeordnete"] = []
    return BetriebsstaetteOut(**d)


@router.put("/{filial_nr}", response_model=BetriebsstaetteOut, summary="Betriebsstaette aktualisieren")
def update_betriebsstaette(
    filial_nr: str,
    payload: BetriebsstaetteCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.betriebsstaetten
        WHERE tenant_id = :tid AND filial_nr = :nr
    """), {"tid": tenant_id, "nr": filial_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Betriebsstätte nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.betriebsstaetten
        SET bezeichnung = :bez, ist_zentrale = :iszentrale, zentrale_filial_nr = :znr,
            ident_untergrenze = :iu, ident_obergrenze = :io,
            strasse = :str, plz = :plz, ort = :ort, land = :land, telefon = :tel, email = :email
        WHERE tenant_id = :tid AND filial_nr = :nr
    """), {
        "tid": tenant_id, "nr": filial_nr, "bez": payload.bezeichnung,
        "iszentrale": payload.ist_zentrale, "znr": payload.zentrale_filial_nr,
        "iu": payload.ident_untergrenze, "io": payload.ident_obergrenze,
        "str": payload.strasse, "plz": payload.plz, "ort": payload.ort,
        "land": payload.land, "tel": payload.telefon, "email": payload.email,
    })
    db.commit()
    updated = db.execute(text(
        "SELECT * FROM domain_shared.betriebsstaetten WHERE tenant_id = :tid AND filial_nr = :nr"
    ), {"tid": tenant_id, "nr": filial_nr}).fetchone()
    d = dict(updated._mapping)
    d["untergeordnete"] = _load_untergeordnete(db, tenant_id, filial_nr)
    return BetriebsstaetteOut(**d)


@router.delete("/{filial_nr}", summary="Betriebsstaette löschen")
def delete_betriebsstaette(
    filial_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.betriebsstaetten SET aktiv = false
        WHERE tenant_id = :tid AND filial_nr = :nr
    """), {"tid": tenant_id, "nr": filial_nr})
    db.commit()
    return Response(status_code=204)
