"""Vertreterstamm — Außendienstmitarbeiter und Vertretergruppen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 06 CRM):
  Im Vertreterstamm werden Außendienstmitarbeiter/Provisionsvertreter gepflegt.
  Jedem Kunden kann eine Vertretergruppe zugeordnet werden, die bei der
  Vorgangserfassung automatisch vorbelegt wird (SPA 611).
  Vertretergruppen-Information wird auch in Warenbewegungen gespeichert und
  bildet die Basis für die Provisionsabrechnung.

  Jedem Artikel kann über "Weitere Kennzeichen" eine Provisionsgruppe zugeordnet
  werden, die bei der Warenpositionserfassung automatisch ermittelt wird.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/crm/vertreter", tags=["CRM - Vertreterstamm"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class VertreterCreate(BaseModel):
    vertreter_nr: str = Field(..., max_length=20)
    name: str
    vorname: Optional[str] = None
    kuerzel: Optional[str] = Field(None, max_length=10)
    telefon: Optional[str] = None
    email: Optional[str] = None
    vertretergruppe_nr: Optional[str] = None
    provisionsgruppe_nr: Optional[str] = None
    gebiet: Optional[str] = None


class VertreterOut(BaseModel):
    id: str
    vertreter_nr: str
    name: str
    vorname: Optional[str]
    kuerzel: Optional[str]
    telefon: Optional[str]
    email: Optional[str]
    vertretergruppe_nr: Optional[str]
    provisionsgruppe_nr: Optional[str]
    gebiet: Optional[str]
    aktiv: bool
    created_at: datetime
    updated_at: datetime


class VertretergruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str


class VertretergruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    aktiv: bool
    created_at: datetime


# ── Vertretergruppen ──────────────────────────────────────────────────────────

@router.get("/gruppen", response_model=list[VertretergruppeOut], summary="Vertretergruppen auflisten")
def list_vertretergruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.crm_vertretergruppen
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [VertretergruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/gruppen", response_model=VertretergruppeOut, status_code=201, summary="Vertretergruppe anlegen")
def create_vertretergruppe(
    payload: VertretergruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.crm_vertretergruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Vertretergruppe {payload.gruppe_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.crm_vertretergruppen
            (id, tenant_id, gruppe_nr, bezeichnung, aktiv)
        VALUES (:id, :tid, :nr, :bez, true)
    """), {"id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung})
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.crm_vertretergruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return VertretergruppeOut(**dict(row._mapping))


@router.delete("/gruppen/{gruppe_nr}", summary="Vertretergruppe löschen",
    response_model=None
)
def delete_vertretergruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.crm_vertretergruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)


# ── Vertreter ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[VertreterOut], summary="Vertreter auflisten")
def list_vertreter(
    vertretergruppe_nr: Optional[str] = Query(None),
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.crm_vertreter WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    if vertretergruppe_nr:
        sql += " AND vertretergruppe_nr = :vg"
        params["vg"] = vertretergruppe_nr
    sql += " ORDER BY vertreter_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [VertreterOut(**dict(r._mapping)) for r in rows]


@router.get("/{vertreter_nr}", response_model=VertreterOut, summary="Vertreter abrufen")
def get_vertreter(
    vertreter_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.crm_vertreter
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {"tid": tenant_id, "nr": vertreter_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Vertreter nicht gefunden.")
    return VertreterOut(**dict(row._mapping))


@router.post("", response_model=VertreterOut, status_code=201, summary="Vertreter anlegen")
def create_vertreter(
    payload: VertreterCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.crm_vertreter
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {"tid": tenant_id, "nr": payload.vertreter_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Vertreter {payload.vertreter_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.crm_vertreter
            (id, tenant_id, vertreter_nr, name, vorname, kuerzel,
             telefon, email, vertretergruppe_nr, provisionsgruppe_nr, gebiet, aktiv)
        VALUES (:id, :tid, :nr, :name, :vname, :kz, :tel, :email, :vg, :pg, :geb, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.vertreter_nr,
        "name": payload.name, "vname": payload.vorname, "kz": payload.kuerzel,
        "tel": payload.telefon, "email": payload.email,
        "vg": payload.vertretergruppe_nr, "pg": payload.provisionsgruppe_nr,
        "geb": payload.gebiet,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.crm_vertreter WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return VertreterOut(**dict(row._mapping))


@router.put("/{vertreter_nr}", response_model=VertreterOut, summary="Vertreter aktualisieren")
def update_vertreter(
    vertreter_nr: str,
    payload: VertreterCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.crm_vertreter
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {"tid": tenant_id, "nr": vertreter_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Vertreter nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.crm_vertreter
        SET name = :name, vorname = :vname, kuerzel = :kz,
            telefon = :tel, email = :email,
            vertretergruppe_nr = :vg, provisionsgruppe_nr = :pg,
            gebiet = :geb, updated_at = now()
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {
        "tid": tenant_id, "nr": vertreter_nr, "name": payload.name,
        "vname": payload.vorname, "kz": payload.kuerzel, "tel": payload.telefon,
        "email": payload.email, "vg": payload.vertretergruppe_nr,
        "pg": payload.provisionsgruppe_nr, "geb": payload.gebiet,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.crm_vertreter
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {"tid": tenant_id, "nr": vertreter_nr}).fetchone()
    return VertreterOut(**dict(updated._mapping))


@router.delete("/{vertreter_nr}", summary="Vertreter löschen",
    response_model=None
)
def delete_vertreter(
    vertreter_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.crm_vertreter SET aktiv = false
        WHERE tenant_id = :tid AND vertreter_nr = :nr
    """), {"tid": tenant_id, "nr": vertreter_nr})
    db.commit()
    return Response(status_code=204)
