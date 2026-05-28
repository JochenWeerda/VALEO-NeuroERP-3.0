"""Forderungsgruppen [FORG] — Kundensegmentierung für Bestandskontenzuordnung.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Forderungsgruppen ermöglichen die Zuordnung von Kunden/Lieferanten zu
  unterschiedlichen Bestandskonten in der FIBU. Beispiele: "Großkunden",
  "Landwirte", "Baustoffhändler" erhalten je eigene Sammelkonten.

  Die Forderungsgruppe wird im Kunden-/Lieferantenstamm hinterlegt und
  steuert beim FiBu-Übertrag, auf welches Bestandskonto Forderungen/
  Verbindlichkeiten gebucht werden.

  Direktsprung: [FORG] = Forderungsgruppenpflege.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/fibu/forderungsgruppen",
                   tags=["FIBU - Forderungsgruppen"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ForderungsgruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    konto_forderungen: Optional[str] = None
    konto_verbindlichkeiten: Optional[str] = None
    konto_sammel_1: Optional[str] = None
    konto_sammel_2: Optional[str] = None
    konto_sammel_3: Optional[str] = None


class ForderungsgruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    konto_forderungen: Optional[str]
    konto_verbindlichkeiten: Optional[str]
    konto_sammel_1: Optional[str]
    konto_sammel_2: Optional[str]
    konto_sammel_3: Optional[str]
    aktiv: bool
    created_at: datetime


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ForderungsgruppeOut], summary="Forderungsgruppen auflisten")
def list_forderungsgruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.forderungsgruppen
        WHERE tenant_id = :tid AND aktiv = true ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [ForderungsgruppeOut(**dict(r._mapping)) for r in rows]


@router.get("/{gruppe_nr}", response_model=ForderungsgruppeOut, summary="Forderungsgruppe abrufen")
def get_forderungsgruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.forderungsgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    if not row:
        raise HTTPException(404, f"Forderungsgruppe {gruppe_nr} nicht gefunden.")
    return ForderungsgruppeOut(**dict(row._mapping))


@router.post("", response_model=ForderungsgruppeOut, status_code=201, summary="Forderungsgruppe anlegen")
def create_forderungsgruppe(
    payload: ForderungsgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.forderungsgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone():
        raise HTTPException(409, f"Forderungsgruppe {payload.gruppe_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.forderungsgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, konto_forderungen,
             konto_verbindlichkeiten, konto_sammel_1, konto_sammel_2, konto_sammel_3)
        VALUES (:id, :tid, :nr, :bez, :kf, :kv, :ks1, :ks2, :ks3)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr, "bez": payload.bezeichnung,
        "kf": payload.konto_forderungen, "kv": payload.konto_verbindlichkeiten,
        "ks1": payload.konto_sammel_1, "ks2": payload.konto_sammel_2, "ks3": payload.konto_sammel_3,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.forderungsgruppen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ForderungsgruppeOut(**dict(row._mapping))


@router.put("/{gruppe_nr}", response_model=ForderungsgruppeOut, summary="Forderungsgruppe aktualisieren")
def update_forderungsgruppe(
    gruppe_nr: str,
    payload: ForderungsgruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.forderungsgruppen SET
            bezeichnung = :bez,
            konto_forderungen = :kf,
            konto_verbindlichkeiten = :kv,
            konto_sammel_1 = :ks1,
            konto_sammel_2 = :ks2,
            konto_sammel_3 = :ks3
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {
        "bez": payload.bezeichnung, "kf": payload.konto_forderungen,
        "kv": payload.konto_verbindlichkeiten, "ks1": payload.konto_sammel_1,
        "ks2": payload.konto_sammel_2, "ks3": payload.konto_sammel_3,
        "tid": tenant_id, "nr": gruppe_nr,
    })
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, f"Forderungsgruppe {gruppe_nr} nicht gefunden.")
    row = db.execute(text("""
        SELECT * FROM domain_shared.forderungsgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr}).fetchone()
    return ForderungsgruppeOut(**dict(row._mapping))


@router.delete("/{gruppe_nr}", summary="Forderungsgruppe löschen",
    response_model=None
)
def delete_forderungsgruppe(
    gruppe_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.forderungsgruppen SET aktiv = false
        WHERE tenant_id = :tid AND gruppe_nr = :nr
    """), {"tid": tenant_id, "nr": gruppe_nr})
    db.commit()
    return Response(status_code=204)
