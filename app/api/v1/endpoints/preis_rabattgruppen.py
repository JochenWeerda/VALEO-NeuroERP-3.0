"""Rabattgruppen und Rabattklassen — Stammdaten für die Rabattpflege.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 07 Preise/Konditionen):
  Rabattgruppen werden Artikeln zugeordnet (Artikel-Rabattgruppe EK/VK).
  Rabattklassen werden Kunden/Lieferanten zugeordnet (Kunden-Rabattklasse EK/VK).
  Der Schnittpunkt Rabattgruppe x Rabattklasse ergibt den anzuwendenden Rabattsatz —
  einfach oder gestaffelt (ab_menge). Getrennte Pflege für Einkauf (EK) und
  Verkauf (VK). Modul-Einstiegspunkte: [RAG] Rabattgruppe, [RAK] Rabattklasse.
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

router = APIRouter(prefix="/preise/rabatte", tags=["Preise - Rabattgruppen & Rabattklassen"])

RICHTUNGEN = ("EK", "VK")


# ── Schemas ───────────────────────────────────────────────────────────────────

class RabattgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = Field(..., description="EK oder VK")

    def model_post_init(self, __context):
        if self.richtung not in RICHTUNGEN:
            raise ValueError(f"richtung muss EK oder VK sein, nicht '{self.richtung}'")


class RabattgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class RabattklasseCreate(BaseModel):
    klasse_nr: str = Field(..., max_length=20)
    bezeichnung: str
    richtung: str = Field(..., description="EK oder VK")

    def model_post_init(self, __context):
        if self.richtung not in RICHTUNGEN:
            raise ValueError(f"richtung muss EK oder VK sein, nicht '{self.richtung}'")


class RabattklasseOut(BaseModel):
    id: str
    klasse_nr: str
    bezeichnung: str
    richtung: str
    aktiv: bool
    created_at: datetime


class RabattsatzCreate(BaseModel):
    rabattgruppe_nr: str
    rabattklasse_nr: str
    richtung: str = Field(..., description="EK oder VK")
    rabatt_prozent: Decimal = Field(..., ge=0, le=100)
    ab_menge: Optional[Decimal] = Field(None, ge=0, description="Staffelmenge")
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None


class RabattsatzOut(BaseModel):
    id: str
    rabattgruppe_nr: str
    rabattklasse_nr: str
    richtung: str
    rabatt_prozent: Decimal
    ab_menge: Optional[Decimal]
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    created_at: datetime


# ── Rabattgruppen ─────────────────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[RabattgruppeOut], summary="Rabattgruppen auflisten")
def list_rabattgruppen(
    richtung: Optional[str] = Query(None, description="EK oder VK"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.preis_rabattgruppen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if richtung:
        sql += " AND richtung = :richtung"
        params["richtung"] = richtung
    sql += " ORDER BY richtung, gruppe_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [RabattgruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/gruppen", response_model=RabattgruppeOut, status_code=201, summary="Rabattgruppe anlegen")
def create_rabattgruppe(
    payload: RabattgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.preis_rabattgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": payload.gruppe_nr, "r": payload.richtung}).fetchone()
    if existing:
        raise HTTPException(409, f"Rabattgruppe {payload.gruppe_nr}/{payload.richtung} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.preis_rabattgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, richtung, aktiv)
        VALUES (:id, :tid, :nr, :bez, :r, true)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
           "bez": payload.bezeichnung, "r": payload.richtung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.preis_rabattgruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return RabattgruppeOut(**dict(row._mapping))


@router.delete("/gruppen/{gruppe_id}", summary="Rabattgruppe löschen",
    response_model=dict
)
def delete_rabattgruppe(
    gruppe_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.preis_rabattgruppen SET aktiv = false
        WHERE id = :id AND tenant_id = :tid
    """), {"id": gruppe_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


# ── Rabattklassen ─────────────────────────────────────────────────────────────

@router.get("/klassen", response_model=list[RabattklasseOut], summary="Rabattklassen auflisten")
def list_rabattklassen(
    richtung: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.preis_rabattklassen WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if richtung:
        sql += " AND richtung = :richtung"
        params["richtung"] = richtung
    sql += " ORDER BY richtung, klasse_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [RabattklasseOut(**dict(r._mapping)) for r in rows]


@router.post("/klassen", response_model=RabattklasseOut, status_code=201, summary="Rabattklasse anlegen")
def create_rabattklasse(
    payload: RabattklasseCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.preis_rabattklassen
        WHERE tenant_id = :tid AND klasse_nr = :nr AND richtung = :r
    """), {"tid": tenant_id, "nr": payload.klasse_nr, "r": payload.richtung}).fetchone()
    if existing:
        raise HTTPException(409, f"Rabattklasse {payload.klasse_nr}/{payload.richtung} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.preis_rabattklassen
            (id, tenant_id, klasse_nr, bezeichnung, richtung, aktiv)
        VALUES (:id, :tid, :nr, :bez, :r, true)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.klasse_nr,
           "bez": payload.bezeichnung, "r": payload.richtung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.preis_rabattklassen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return RabattklasseOut(**dict(row._mapping))


@router.delete("/klassen/{klasse_id}", summary="Rabattklasse löschen",
    response_model=None
)
def delete_rabattklasse(
    klasse_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.preis_rabattklassen SET aktiv = false
        WHERE id = :id AND tenant_id = :tid
    """), {"id": klasse_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


# ── Rabattsätze ───────────────────────────────────────────────────────────────

@router.get("/saetze", response_model=list[RabattsatzOut], summary="Rabattsaetze auflisten")
def list_rabattsaetze(
    rabattgruppe_nr: Optional[str] = Query(None),
    rabattklasse_nr: Optional[str] = Query(None),
    richtung: Optional[str] = Query(None),
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.preis_rabattsaetze WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if rabattgruppe_nr:
        sql += " AND rabattgruppe_nr = :grp"
        params["grp"] = rabattgruppe_nr
    if rabattklasse_nr:
        sql += " AND rabattklasse_nr = :kl"
        params["kl"] = rabattklasse_nr
    if richtung:
        sql += " AND richtung = :r"
        params["r"] = richtung
    if stichtag:
        sql += " AND (gueltig_ab IS NULL OR gueltig_ab <= :s) AND (gueltig_bis IS NULL OR gueltig_bis >= :s)"
        params["s"] = stichtag
    sql += " ORDER BY richtung, rabattgruppe_nr, rabattklasse_nr, ab_menge"
    rows = db.execute(text(sql), params).fetchall()
    return [RabattsatzOut(**dict(r._mapping)) for r in rows]


@router.post("/saetze", response_model=RabattsatzOut, status_code=201, summary="Rabattsatz anlegen")
def create_rabattsatz(
    payload: RabattsatzCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.richtung not in RICHTUNGEN:
        raise HTTPException(422, "richtung muss EK oder VK sein.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.preis_rabattsaetze
            (id, tenant_id, rabattgruppe_nr, rabattklasse_nr, richtung,
             rabatt_prozent, ab_menge, gueltig_ab, gueltig_bis)
        VALUES (:id, :tid, :grp, :kl, :r, :rprozent, :ab, :von, :bis)
    """), {
        "id": new_id, "tid": tenant_id,
        "grp": payload.rabattgruppe_nr, "kl": payload.rabattklasse_nr,
        "r": payload.richtung, "rprozent": payload.rabatt_prozent,
        "ab": payload.ab_menge, "von": payload.gueltig_ab, "bis": payload.gueltig_bis,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.preis_rabattsaetze WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return RabattsatzOut(**dict(row._mapping))


@router.delete("/saetze/{satz_id}", summary="Rabattsatz löschen",
    response_model=dict
)
def delete_rabattsatz(
    satz_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.preis_rabattsaetze
        WHERE id = :id AND tenant_id = :tid
    """), {"id": satz_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


@router.get("/saetze/lookup", summary="Rabatt lookup",
    response_model=None
)
def lookup_rabatt(
    rabattgruppe_nr: str,
    rabattklasse_nr: str,
    richtung: str,
    menge: Optional[Decimal] = Query(None),
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Gültigen Rabattsatz für Gruppe x Klasse ermitteln (inkl. Staffelung)."""
    check_date = stichtag or date.today()
    params: dict = {
        "tid": tenant_id, "grp": rabattgruppe_nr,
        "kl": rabattklasse_nr, "r": richtung, "s": check_date,
    }
    sql = """
        SELECT * FROM domain_shared.preis_rabattsaetze
        WHERE tenant_id = :tid AND rabattgruppe_nr = :grp
          AND rabattklasse_nr = :kl AND richtung = :r
          AND (gueltig_ab IS NULL OR gueltig_ab <= :s)
          AND (gueltig_bis IS NULL OR gueltig_bis >= :s)
    """
    if menge is not None:
        sql += " AND (ab_menge IS NULL OR ab_menge <= :menge)"
        params["menge"] = menge
    sql += " ORDER BY ab_menge DESC NULLS LAST LIMIT 1"
    row = db.execute(text(sql), params).fetchone()
    if not row:
        return {"rabatt_prozent": 0, "gefunden": False}
    r = dict(row._mapping)
    return {"rabatt_prozent": float(r["rabatt_prozent"]), "gefunden": True,
            "ab_menge": r.get("ab_menge")}
