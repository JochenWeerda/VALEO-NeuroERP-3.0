"""Stücklisten / Rezepturen [ARTSTLI] — Artikelkomponenten-Stammdaten.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 11 Produktion):
  Stücklisten (Rezepturen) definieren die Zusammensetzung eines Produktes aus
  Komponenten. Zentral für Mischfutter-Produktion, aber auch für allgemeine
  Fertigung:
  - Basis-Menge: Menge des Fertigprodukts (z.B. 1000 kg Fertigfutter)
  - Positionen: Komponenten mit Menge oder %-Anteil
  - Variable Komponenten (SPA): Komponenten können in der Produktion geändert werden
  - Mengenkontrolle: Summe Komponenten ≈ Produktmenge

  EPA ARTSTLI = Rezepturverwaltung
  SPA 28 = Stücklistenverwaltung angeschlossen
  SPA 309 = Rezeptur-Definition aus Vorgangsbearbeitung
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/produktion/stuecklisten",
                   tags=["Produktion - Stücklisten & Rezepturen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class StuecklistenPositionCreate(BaseModel):
    pos_nr: int
    komponente_nr: str
    komponente_bez: Optional[str] = None
    menge: Decimal = Field(..., gt=0)
    einheit: Optional[str] = None
    anteil_prozent: Optional[Decimal] = Field(None, ge=0, le=100)
    optional: bool = False


class StuecklisteCreate(BaseModel):
    stueckliste_nr: str = Field(..., max_length=30)
    artikel_nr: str
    bezeichnung: Optional[str] = None
    menge_basis: Decimal = Field(default=Decimal("1"), gt=0)
    einheit: str = Field(default="Stk", max_length=10)
    variable_komp: bool = False
    positionen: list[StuecklistenPositionCreate] = []

    @model_validator(mode="after")
    def check_pos_nummern(self) -> "StuecklisteCreate":
        nummern = [p.pos_nr for p in self.positionen]
        if len(nummern) != len(set(nummern)):
            raise ValueError("Positionsnummern müssen eindeutig sein.")
        return self


class StuecklistenPositionOut(BaseModel):
    id: str
    pos_nr: int
    komponente_nr: str
    komponente_bez: Optional[str]
    menge: Decimal
    einheit: Optional[str]
    anteil_prozent: Optional[Decimal]
    optional: bool


class StuecklisteOut(BaseModel):
    id: str
    stueckliste_nr: str
    artikel_nr: str
    bezeichnung: Optional[str]
    menge_basis: Decimal
    einheit: str
    variable_komp: bool
    aktiv: bool
    created_at: datetime
    positionen: list[StuecklistenPositionOut] = []


class MengenbedarfResult(BaseModel):
    stueckliste_nr: str
    produktionsmenge: Decimal
    einheit: str
    positionen: list[dict]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_positionen(db, stueckliste_id: str) -> list:
    rows = db.execute(text("""
        SELECT * FROM domain_shared.stuecklisten_positionen
        WHERE stueckliste_id = :sid ORDER BY pos_nr
    """), {"sid": stueckliste_id}).fetchall()
    return [StuecklistenPositionOut(**dict(r._mapping)) for r in rows]


def _row_to_out(db, row) -> StuecklisteOut:
    d = dict(row._mapping)
    d["positionen"] = _load_positionen(db, d["id"])
    return StuecklisteOut(**d)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[StuecklisteOut], summary="Stuecklisten auflisten")
def list_stuecklisten(
    artikel_nr: Optional[str] = Query(None),
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.stuecklisten WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if artikel_nr:
        sql += " AND artikel_nr = :anr"
        params["anr"] = artikel_nr
    if nur_aktive:
        sql += " AND aktiv = true"
    sql += " ORDER BY stueckliste_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [_row_to_out(db, r) for r in rows]


@router.get("/{stueckliste_nr}", response_model=StuecklisteOut, summary="Stueckliste abrufen")
def get_stueckliste(
    stueckliste_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.stuecklisten
        WHERE tenant_id = :tid AND stueckliste_nr = :nr
    """), {"tid": tenant_id, "nr": stueckliste_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Stückliste nicht gefunden.")
    return _row_to_out(db, row)


@router.post("", response_model=StuecklisteOut, status_code=201, summary="Stueckliste anlegen")
def create_stueckliste(
    payload: StuecklisteCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.stuecklisten
        WHERE tenant_id = :tid AND stueckliste_nr = :nr
    """), {"tid": tenant_id, "nr": payload.stueckliste_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Stückliste {payload.stueckliste_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.stuecklisten
            (id, tenant_id, stueckliste_nr, artikel_nr, bezeichnung,
             menge_basis, einheit, variable_komp, aktiv)
        VALUES (:id, :tid, :nr, :anr, :bez, :mb, :ein, :vk, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.stueckliste_nr,
        "anr": payload.artikel_nr, "bez": payload.bezeichnung,
        "mb": payload.menge_basis, "ein": payload.einheit,
        "vk": payload.variable_komp,
    })

    for pos in payload.positionen:
        db.execute(text("""
            INSERT INTO domain_shared.stuecklisten_positionen
                (id, tenant_id, stueckliste_id, pos_nr, komponente_nr,
                 komponente_bez, menge, einheit, anteil_prozent, optional)
            VALUES (:id, :tid, :sid, :pnr, :knr, :kbez, :menge, :ein, :ap, :opt)
        """), {
            "id": uuid7(), "tid": tenant_id, "sid": new_id,
            "pnr": pos.pos_nr, "knr": pos.komponente_nr,
            "kbez": pos.komponente_bez, "menge": pos.menge,
            "ein": pos.einheit, "ap": pos.anteil_prozent, "opt": pos.optional,
        })

    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.stuecklisten WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return _row_to_out(db, row)


@router.put("/{stueckliste_nr}", response_model=StuecklisteOut, summary="Stueckliste aktualisieren")
def update_stueckliste(
    stueckliste_nr: str,
    payload: StuecklisteCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.stuecklisten
        WHERE tenant_id = :tid AND stueckliste_nr = :nr
    """), {"tid": tenant_id, "nr": stueckliste_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Stückliste nicht gefunden.")

    sid = row.id
    db.execute(text("""
        UPDATE domain_shared.stuecklisten
        SET bezeichnung = :bez, menge_basis = :mb, einheit = :ein, variable_komp = :vk
        WHERE id = :id
    """), {"bez": payload.bezeichnung, "mb": payload.menge_basis,
           "ein": payload.einheit, "vk": payload.variable_komp, "id": sid})

    db.execute(text(
        "DELETE FROM domain_shared.stuecklisten_positionen WHERE stueckliste_id = :sid"
    ), {"sid": sid})

    for pos in payload.positionen:
        db.execute(text("""
            INSERT INTO domain_shared.stuecklisten_positionen
                (id, tenant_id, stueckliste_id, pos_nr, komponente_nr,
                 komponente_bez, menge, einheit, anteil_prozent, optional)
            VALUES (:id, :tid, :sid, :pnr, :knr, :kbez, :menge, :ein, :ap, :opt)
        """), {
            "id": uuid7(), "tid": tenant_id, "sid": sid,
            "pnr": pos.pos_nr, "knr": pos.komponente_nr,
            "kbez": pos.komponente_bez, "menge": pos.menge,
            "ein": pos.einheit, "ap": pos.anteil_prozent, "opt": pos.optional,
        })

    db.commit()
    updated = db.execute(text(
        "SELECT * FROM domain_shared.stuecklisten WHERE id = :id"
    ), {"id": sid}).fetchone()
    return _row_to_out(db, updated)


@router.delete("/{stueckliste_nr}", summary="Stueckliste löschen",
    response_model=CompatFlexOut
)
def delete_stueckliste(
    stueckliste_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Setzt Löschkennzeichen — keine physische Löschung."""
    db.execute(text("""
        UPDATE domain_shared.stuecklisten SET aktiv = false
        WHERE tenant_id = :tid AND stueckliste_nr = :nr
    """), {"tid": tenant_id, "nr": stueckliste_nr})
    db.commit()
    return Response(status_code=204)


@router.get("/{stueckliste_nr}/mengenbedarf", response_model=MengenbedarfResult, summary="Mengenbedarf")
def mengenbedarf(
    stueckliste_nr: str,
    produktionsmenge: Decimal = Query(..., gt=0),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Berechnet Komponentenbedarf für eine gegebene Produktionsmenge."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.stuecklisten
        WHERE tenant_id = :tid AND stueckliste_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": stueckliste_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Stückliste nicht gefunden.")

    d = dict(row._mapping)
    faktor = produktionsmenge / Decimal(str(d["menge_basis"]))
    positionen = _load_positionen(db, d["id"])

    result_pos = []
    for pos in positionen:
        bedarf = (pos.menge * faktor).quantize(Decimal("0.000001"))
        result_pos.append({
            "pos_nr": pos.pos_nr,
            "komponente_nr": pos.komponente_nr,
            "komponente_bez": pos.komponente_bez,
            "bedarf_menge": float(bedarf),
            "einheit": pos.einheit,
            "optional": pos.optional,
        })

    return MengenbedarfResult(
        stueckliste_nr=stueckliste_nr,
        produktionsmenge=produktionsmenge,
        einheit=d["einheit"],
        positionen=result_pos,
    )
