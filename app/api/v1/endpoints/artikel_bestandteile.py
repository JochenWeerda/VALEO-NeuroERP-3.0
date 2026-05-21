"""Artikel-Bestandteile — Qualitätsmerkmale und Inhaltsstoffe.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 15 Compliance/Qualität):
  Im Bestandteile-Stamm [ABST] werden Inhaltsstoffe (Nähr- und Schadstoffe)
  global definiert. Je Artikel werden über die Zusammensetzungs-Funktion
  die relevanten Bestandteile mit Sollwerten zugeordnet.

  Verwendung: LWK-Qualitätsanalyse (EPA BTQUALITAETSDATEN1), Partieartikelanalyse,
  Ackerschlagkartei, Qualitätsdaten. Der Typ Schad/Nährstoff steuert die
  Darstellung in der LWK-Auswertung.

  Stoffstrom-Integration: Bestandteile mit Stoffstrom-Art werden für die
  Massebilanz-Berechnung (THG RED II) herangezogen.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/artikel/bestandteile", tags=["Artikelstamm - Bestandteile & Qualitätsmerkmale"])

NUTZUNGEN = ("egal", "qualitaetsdaten", "ackerschlagkartei", "partieartikelanalyse")
TYPEN = ("beides", "schadstoff", "naehrstoff", "keins")


# ── Schemas ───────────────────────────────────────────────────────────────────

class BestandteilDefCreate(BaseModel):
    bestandteil_nr: str = Field(..., max_length=20)
    bezeichnung: str
    einheit: Optional[str] = Field(None, max_length=20,
                                   description="z.B. %, mg/kg, g/kg")
    grenzwert_min: Optional[Decimal] = None
    grenzwert_max: Optional[Decimal] = None
    nutzung: Optional[str] = Field(None,
        description="egal, qualitaetsdaten, ackerschlagkartei, partieartikelanalyse")
    typ_schad_naehr: Optional[str] = Field(None,
        description="beides, schadstoff, naehrstoff, keins")
    waage_qualitaet_nr: Optional[int] = Field(None,
        description="Feldnummer für Waagenqualitäts-Übernahme")


class BestandteilDefOut(BaseModel):
    id: str
    bestandteil_nr: str
    bezeichnung: str
    einheit: Optional[str]
    grenzwert_min: Optional[Decimal]
    grenzwert_max: Optional[Decimal]
    nutzung: Optional[str]
    typ_schad_naehr: Optional[str]
    waage_qualitaet_nr: Optional[int]
    aktiv: bool
    created_at: datetime


class BestandteilZuordnungCreate(BaseModel):
    bestandteil_nr: str
    sollwert: Optional[Decimal] = None


class BestandteilZuordnungOut(BaseModel):
    id: str
    artikel_nr: str
    bestandteil_nr: str
    sollwert: Optional[Decimal]
    created_at: datetime


# ── Stammdaten ────────────────────────────────────────────────────────────────

@router.get("/stamm", response_model=list[BestandteilDefOut])
def list_bestandteile_def(
    nutzung: Optional[str] = Query(None),
    typ: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.artikel_bestandteile_def
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if nutzung:
        sql += " AND nutzung = :nutzung"
        params["nutzung"] = nutzung
    if typ:
        sql += " AND typ_schad_naehr = :typ"
        params["typ"] = typ
    sql += " ORDER BY bestandteil_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [BestandteilDefOut(**dict(r._mapping)) for r in rows]


@router.post("/stamm", response_model=BestandteilDefOut, status_code=201)
def create_bestandteil_def(
    payload: BestandteilDefCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_bestandteile_def
        WHERE tenant_id = :tid AND bestandteil_nr = :nr
    """), {"tid": tenant_id, "nr": payload.bestandteil_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Bestandteil {payload.bestandteil_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_bestandteile_def
            (id, tenant_id, bestandteil_nr, bezeichnung, einheit,
             grenzwert_min, grenzwert_max, nutzung, typ_schad_naehr,
             waage_qualitaet_nr, aktiv)
        VALUES (:id, :tid, :nr, :bez, :eh, :gmin, :gmax,
                :nutz, :typ, :waage_nr, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.bestandteil_nr,
        "bez": payload.bezeichnung, "eh": payload.einheit,
        "gmin": payload.grenzwert_min, "gmax": payload.grenzwert_max,
        "nutz": payload.nutzung, "typ": payload.typ_schad_naehr,
        "waage_nr": payload.waage_qualitaet_nr,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.artikel_bestandteile_def WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return BestandteilDefOut(**dict(row._mapping))


@router.put("/stamm/{bestandteil_nr}", response_model=BestandteilDefOut)
def update_bestandteil_def(
    bestandteil_nr: str,
    payload: BestandteilDefCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.artikel_bestandteile_def
        WHERE tenant_id = :tid AND bestandteil_nr = :nr
    """), {"tid": tenant_id, "nr": bestandteil_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Bestandteil nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.artikel_bestandteile_def
        SET bezeichnung = :bez, einheit = :eh,
            grenzwert_min = :gmin, grenzwert_max = :gmax,
            nutzung = :nutz, typ_schad_naehr = :typ,
            waage_qualitaet_nr = :waage_nr
        WHERE tenant_id = :tid AND bestandteil_nr = :nr
    """), {
        "tid": tenant_id, "nr": bestandteil_nr, "bez": payload.bezeichnung,
        "eh": payload.einheit, "gmin": payload.grenzwert_min,
        "gmax": payload.grenzwert_max, "nutz": payload.nutzung,
        "typ": payload.typ_schad_naehr, "waage_nr": payload.waage_qualitaet_nr,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.artikel_bestandteile_def
        WHERE tenant_id = :tid AND bestandteil_nr = :nr
    """), {"tid": tenant_id, "nr": bestandteil_nr}).fetchone()
    return BestandteilDefOut(**dict(updated._mapping))


@router.delete("/stamm/{bestandteil_nr}")
def delete_bestandteil_def(
    bestandteil_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.artikel_bestandteile_def SET aktiv = false
        WHERE tenant_id = :tid AND bestandteil_nr = :nr
    """), {"tid": tenant_id, "nr": bestandteil_nr})
    db.commit()
    return Response(status_code=204)


# ── Artikel-Zuordnungen ───────────────────────────────────────────────────────

@router.get("/{artikel_nr}/zuordnungen", response_model=list[BestandteilZuordnungOut])
def list_zuordnungen(
    artikel_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Alle Bestandteile (Inhaltsstoffe) die einem Artikel zugeordnet sind."""
    rows = db.execute(text("""
        SELECT * FROM domain_shared.artikel_bestandteile_zuordnung
        WHERE tenant_id = :tid AND artikel_nr = :art_nr
        ORDER BY bestandteil_nr
    """), {"tid": tenant_id, "art_nr": artikel_nr}).fetchall()
    return [BestandteilZuordnungOut(**dict(r._mapping)) for r in rows]


@router.post("/{artikel_nr}/zuordnungen",
             response_model=BestandteilZuordnungOut, status_code=201)
def create_zuordnung(
    artikel_nr: str,
    payload: BestandteilZuordnungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_bestandteile_zuordnung
        WHERE tenant_id = :tid AND artikel_nr = :art_nr AND bestandteil_nr = :b_nr
    """), {"tid": tenant_id, "art_nr": artikel_nr, "b_nr": payload.bestandteil_nr}).fetchone()
    if existing:
        raise HTTPException(409, "Bestandteil bereits zugeordnet.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_bestandteile_zuordnung
            (id, tenant_id, artikel_nr, bestandteil_nr, sollwert)
        VALUES (:id, :tid, :art_nr, :b_nr, :sollwert)
    """), {
        "id": new_id, "tid": tenant_id, "art_nr": artikel_nr,
        "b_nr": payload.bestandteil_nr, "sollwert": payload.sollwert,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.artikel_bestandteile_zuordnung WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return BestandteilZuordnungOut(**dict(row._mapping))


@router.delete("/{artikel_nr}/zuordnungen/{zuordnung_id}")
def delete_zuordnung(
    artikel_nr: str,
    zuordnung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.artikel_bestandteile_zuordnung
        WHERE id = :id AND tenant_id = :tid AND artikel_nr = :art_nr
    """), {"id": zuordnung_id, "tid": tenant_id, "art_nr": artikel_nr})
    db.commit()
    return Response(status_code=204)
