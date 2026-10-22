"""Hausbankenstamm — Eigene Bankverbindungen des Mandanten.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 04 eRechnung/EDI):
  Im Hausbankenstamm [BNKH] werden die eigenen Bankkonten des Unternehmens
  gepflegt. Seit Version 9.0.2501.5 gibt es einen eRechnung-Bereich je Hausbank,
  der steuert, ob diese Hausbank in eRechnungen als Zahlungskonto ausgewiesen wird.

  SEPA: Die Gläubiger-ID wird für Lastschriftmandate (SEPA-DD) benötigt.
  eClearing: Bei mehreren Hausbanken zur gleichen IBAN muss die Hausbank
  manuell über "Hausbank zuordnen" im eClearing [ECL] zugeordnet werden.
"""
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/stammdaten/hausbanken", tags=["Stammdaten - Hausbankenstamm"])

IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')


# ── Schemas ───────────────────────────────────────────────────────────────────

class HausbankCreate(BaseModel):
    bank_nr: str = Field(..., max_length=20)
    bezeichnung: str
    iban: str = Field(..., min_length=15, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = None
    kontonummer: Optional[str] = None
    blz: Optional[str] = Field(None, max_length=10)
    waehrung: str = Field(default="EUR", max_length=3)
    erechnung_aktiv: bool = False
    sepa_glaeubiger_id: Optional[str] = Field(None, max_length=35)
    standard: bool = False

    @field_validator("iban")
    @classmethod
    def validate_iban(cls, v: str) -> str:
        cleaned = v.replace(" ", "").upper()
        if not IBAN_PATTERN.match(cleaned):
            raise ValueError("Ungültiges IBAN-Format.")
        return cleaned


class HausbankOut(BaseModel):
    id: str
    bank_nr: str
    bezeichnung: str
    iban: str
    bic: Optional[str]
    bank_name: Optional[str]
    kontonummer: Optional[str]
    blz: Optional[str]
    waehrung: str
    erechnung_aktiv: bool
    sepa_glaeubiger_id: Optional[str]
    standard: bool
    aktiv: bool
    created_at: datetime
    updated_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[HausbankOut], summary="Hausbanken auflisten")
def list_hausbanken(
    nur_aktive: bool = Query(True),
    nur_erechnung: bool = Query(False),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.hausbankenstamm WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    if nur_erechnung:
        sql += " AND erechnung_aktiv = true"
    sql += " ORDER BY standard DESC, bank_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [HausbankOut(**dict(r._mapping)) for r in rows]


@router.get("/{bank_nr}", response_model=HausbankOut, summary="Hausbank abrufen")
def get_hausbank(
    bank_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.hausbankenstamm
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {"tid": tenant_id, "nr": bank_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Hausbank nicht gefunden.")
    return HausbankOut(**dict(row._mapping))


@router.post("", response_model=HausbankOut, status_code=201, summary="Hausbank anlegen")
def create_hausbank(
    payload: HausbankCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.hausbankenstamm
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {"tid": tenant_id, "nr": payload.bank_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Hausbank {payload.bank_nr} bereits vorhanden.")

    if payload.standard:
        db.execute(text("""
            UPDATE domain_shared.hausbankenstamm SET standard = false
            WHERE tenant_id = :tid AND aktiv = true
        """), {"tid": tenant_id})

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.hausbankenstamm
            (id, tenant_id, bank_nr, bezeichnung, iban, bic, bank_name,
             kontonummer, blz, waehrung, erechnung_aktiv, sepa_glaeubiger_id,
             standard, aktiv)
        VALUES (:id, :tid, :nr, :bez, :iban, :bic, :bank, :kto, :blz,
                :whr, :erechn, :sepa_id, :std, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.bank_nr,
        "bez": payload.bezeichnung, "iban": payload.iban, "bic": payload.bic,
        "bank": payload.bank_name, "kto": payload.kontonummer, "blz": payload.blz,
        "whr": payload.waehrung, "erechn": payload.erechnung_aktiv,
        "sepa_id": payload.sepa_glaeubiger_id, "std": payload.standard,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.hausbankenstamm WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return HausbankOut(**dict(row._mapping))


@router.put("/{bank_nr}", response_model=HausbankOut, summary="Hausbank aktualisieren")
def update_hausbank(
    bank_nr: str,
    payload: HausbankCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.hausbankenstamm
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {"tid": tenant_id, "nr": bank_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Hausbank nicht gefunden.")

    if payload.standard:
        db.execute(text("""
            UPDATE domain_shared.hausbankenstamm SET standard = false
            WHERE tenant_id = :tid AND aktiv = true AND bank_nr != :nr
        """), {"tid": tenant_id, "nr": bank_nr})

    db.execute(text("""
        UPDATE domain_shared.hausbankenstamm
        SET bezeichnung = :bez, iban = :iban, bic = :bic, bank_name = :bank,
            kontonummer = :kto, blz = :blz, waehrung = :whr,
            erechnung_aktiv = :erechn, sepa_glaeubiger_id = :sepa_id,
            standard = :std, updated_at = now()
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {
        "tid": tenant_id, "nr": bank_nr, "bez": payload.bezeichnung,
        "iban": payload.iban, "bic": payload.bic, "bank": payload.bank_name,
        "kto": payload.kontonummer, "blz": payload.blz, "whr": payload.waehrung,
        "erechn": payload.erechnung_aktiv, "sepa_id": payload.sepa_glaeubiger_id,
        "std": payload.standard,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.hausbankenstamm
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {"tid": tenant_id, "nr": bank_nr}).fetchone()
    return HausbankOut(**dict(updated._mapping))


@router.delete("/{bank_nr}", summary="Hausbank löschen",
    response_model=None
)
def delete_hausbank(
    bank_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.hausbankenstamm SET aktiv = false
        WHERE tenant_id = :tid AND bank_nr = :nr
    """), {"tid": tenant_id, "nr": bank_nr})
    db.commit()
    return Response(status_code=204)
