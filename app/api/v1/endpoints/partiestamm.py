"""Partiestamm [PAR] & Partiegruppen [PGR] — Lot-/Charge-Verwaltung.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 08 Lager/Bestand):
  Partien ermöglichen die chargenweise Verfolgung von Rohwaren durch den
  Warenfluss. Typischer Einsatz: Getreidepartien mit Erntejahr, Anbauland,
  Qualitätsdaten.

  Struktur:
  - Partiegruppen [PGR]: Ordnungsrahmen mit eigenem Nummernkreis
  - Partiestamm [PAR]: Einzelpartie mit Typ (artikelstamm|artikel_lager),
    Artikel, Lager, Partiegruppe, Erntejahr, Herkunftsland
  - Partieumbuchung: Transfer einer Partie auf anderes Lager/Artikel

  Direktsprung: [PAR] = Partie-Stammdaten, [PGR] = Partiegruppen.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/lager/partien", tags=["Lager - Partiestamm & Partiegruppen"])

GUELTIGE_TYP = {"artikelstamm", "artikel_lager"}
GUELTIGE_STATUS = {"aktiv", "gesperrt", "abgeschlossen"}


# ── Schemas ───────────────────────────────────────────────────────────────────

class PartiegruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str


class PartiegruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime


class PartiestammCreate(BaseModel):
    partie_nr: Optional[str] = Field(None, max_length=30)
    bezeichnung: Optional[str] = None
    artikel_nr: str
    lager_nr: Optional[str] = None
    partie_typ: str = "artikelstamm"
    gruppe_id: Optional[str] = None
    erntejahr: Optional[int] = Field(None, ge=1900, le=2100)
    herkunftsland: Optional[str] = Field(None, max_length=3)

    @model_validator(mode="after")
    def check_typ(self):
        if self.partie_typ not in GUELTIGE_TYP:
            raise ValueError(f"Ungültiger partie_typ: {self.partie_typ}. Erlaubt: {GUELTIGE_TYP}")
        if self.partie_typ == "artikel_lager" and not self.lager_nr:
            raise ValueError("lager_nr erforderlich bei partie_typ='artikel_lager'.")
        return self


class PartiestammOut(BaseModel):
    id: str
    partie_nr: str
    bezeichnung: Optional[str]
    artikel_nr: str
    lager_nr: Optional[str]
    partie_typ: str
    gruppe_id: Optional[str]
    erntejahr: Optional[int]
    herkunftsland: Optional[str]
    status: str
    aktiv: bool
    created_at: datetime


class PartieUmbuchungCreate(BaseModel):
    ziel_lager_nr: str
    menge: Optional[float] = None
    bemerkung: Optional[str] = None


# ── Partiegruppen CRUD ────────────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[PartiegruppeOut], summary="Partiegruppen auflisten")
def list_partiegruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.partiegruppen
        WHERE tenant_id = :tid AND aktiv = true ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [PartiegruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/gruppen", response_model=PartiegruppeOut, status_code=201, summary="Partiegruppe anlegen")
def create_partiegruppe(
    payload: PartiegruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.partiegruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Partiegruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.partiegruppen (id, tenant_id, gruppe_nr, bezeichnung)
        VALUES (:id, :tid, :nr, :bez)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.partiegruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return PartiegruppeOut(**dict(row._mapping))


@router.delete("/gruppen/{gruppe_nr}", summary="Partiegruppe löschen",
    response_model=dict
)
def delete_partiegruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.partiegruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Partiestamm CRUD ──────────────────────────────────────────────────────────

@router.get("", response_model=list[PartiestammOut], summary="Partien auflisten")
def list_partien(
    artikel_nr: Optional[str] = Query(None),
    lager_nr: Optional[str] = Query(None),
    gruppe_id: Optional[str] = Query(None),
    erntejahr: Optional[int] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.partiestamm WHERE tenant_id = :tid AND aktiv = true"
    params: dict = {"tid": tenant_id}
    if artikel_nr:
        sql += " AND artikel_nr = :anr"
        params["anr"] = artikel_nr
    if lager_nr:
        sql += " AND lager_nr = :lnr"
        params["lnr"] = lager_nr
    if gruppe_id:
        sql += " AND gruppe_id = :gid"
        params["gid"] = gruppe_id
    if erntejahr:
        sql += " AND erntejahr = :ej"
        params["ej"] = erntejahr
    sql += " ORDER BY partie_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [PartiestammOut(**dict(r._mapping)) for r in rows]


@router.get("/{partie_nr}", response_model=PartiestammOut, summary="Partie abrufen")
def get_partie(
    partie_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.partiestamm
        WHERE tenant_id = :tid AND partie_nr = :nr
    """), {"tid": tenant_id, "nr": partie_nr}).fetchone()
    if not row:
        raise HTTPException(404, f"Partie {partie_nr} nicht gefunden.")
    return PartiestammOut(**dict(row._mapping))


@router.post("", response_model=PartiestammOut, status_code=201, summary="Partie anlegen")
def create_partie(
    payload: PartiestammCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if payload.partie_nr and db.execute(text("""
        SELECT id FROM domain_shared.partiestamm
        WHERE tenant_id = :tid AND partie_nr = :nr
    """), {"tid": tenant_id, "nr": payload.partie_nr}).fetchone():
        raise HTTPException(409, f"Partie {payload.partie_nr} bereits vorhanden.")

    # Automatische Nummer wenn nicht angegeben
    partie_nr = payload.partie_nr
    if not partie_nr:
        count = db.execute(text(
            "SELECT COUNT(*) FROM domain_shared.partiestamm WHERE tenant_id = :tid"
        ), {"tid": tenant_id}).scalar()
        partie_nr = f"PAR-{(count or 0) + 1:06d}"

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.partiestamm
            (id, tenant_id, partie_nr, bezeichnung, artikel_nr, lager_nr,
             partie_typ, gruppe_id, erntejahr, herkunftsland)
        VALUES (:id, :tid, :nr, :bez, :anr, :lnr, :typ, :gid, :ej, :hl)
    """), {
        "id": new_id, "tid": tenant_id, "nr": partie_nr, "bez": payload.bezeichnung,
        "anr": payload.artikel_nr, "lnr": payload.lager_nr, "typ": payload.partie_typ,
        "gid": payload.gruppe_id, "ej": payload.erntejahr, "hl": payload.herkunftsland,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.partiestamm WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return PartiestammOut(**dict(row._mapping))


@router.patch("/{partie_nr}/status", summary="Partie status setzen",
    response_model=None
)
def set_partie_status(
    partie_nr: str,
    status: str = Query(...),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if status not in GUELTIGE_STATUS:
        raise HTTPException(400, f"Ungültiger Status: {status}. Erlaubt: {GUELTIGE_STATUS}")
    result = db.execute(text("""
        UPDATE domain_shared.partiestamm SET status = :status
        WHERE tenant_id = :tid AND partie_nr = :nr AND aktiv = true
    """), {"status": status, "tid": tenant_id, "nr": partie_nr})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Partie {partie_nr} nicht gefunden.")
    return {"partie_nr": partie_nr, "status": status}


@router.post("/{partie_nr}/umbuchung", summary="Umbuchung partie",
    response_model=dict
)
def partie_umbuchung(
    partie_nr: str,
    payload: PartieUmbuchungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Umbucht eine Partie auf ein anderes Lager."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.partiestamm
        WHERE tenant_id = :tid AND partie_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": partie_nr}).fetchone()
    if not row:
        raise HTTPException(404, f"Partie {partie_nr} nicht gefunden.")
    if dict(row._mapping).get("status") == "gesperrt":
        raise HTTPException(409, "Partie ist gesperrt — Umbuchung nicht möglich.")

    db.execute(text("""
        UPDATE domain_shared.partiestamm SET lager_nr = :lnr
        WHERE tenant_id = :tid AND partie_nr = :nr
    """), {"lnr": payload.ziel_lager_nr, "tid": tenant_id, "nr": partie_nr})
    db.commit()
    return {"partie_nr": partie_nr, "neues_lager": payload.ziel_lager_nr}


@router.delete("/{partie_nr}", summary="Partie löschen",
    response_model=dict
)
def delete_partie(
    partie_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.partiestamm SET aktiv = false
        WHERE tenant_id = :tid AND partie_nr = :nr
    """), {"tid": tenant_id, "nr": partie_nr})
    db.commit()
    return Response(status_code=204)
