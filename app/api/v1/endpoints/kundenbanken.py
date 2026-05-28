"""Kundenbanken — IBAN/BIC-Bankverbindungen pro Kunde.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 06 CRM):
  Kunden können mehrere Bankverbindungen hinterlegen. Für den automatischen
  Zahlungsverkehr (SEPA-Lastschrift) wird die Standard-Bankverbindung mit
  Mandatsreferenz benötigt. Bei SEPA-Auslandsbank-Konstellationen (SPA)
  werden besondere Verarbeitungsregeln angewendet.

  X-Rechnung: Die Bankverbindung fließt in eRechnung-Metadaten ein.
"""
import re
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/kunden", tags=["CRM - Kundenbanken"])

IBAN_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$')


# ── Schemas ───────────────────────────────────────────────────────────────────

class BankverbindungCreate(BaseModel):
    bezeichnung: Optional[str] = None
    iban: str = Field(..., min_length=15, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = None
    kontoinhaber: Optional[str] = None
    sepa_mandat_ref: Optional[str] = None
    sepa_mandat_datum: Optional[date] = None
    standard: bool = False

    @field_validator("iban")
    @classmethod
    def validate_iban_format(cls, v: str) -> str:
        cleaned = v.replace(" ", "").upper()
        if not IBAN_PATTERN.match(cleaned):
            raise ValueError("Ungültiges IBAN-Format.")
        return cleaned


class BankverbindungOut(BaseModel):
    id: str
    kunden_nr: str
    bezeichnung: Optional[str]
    iban: str
    iban_masked: str
    bic: Optional[str]
    bank_name: Optional[str]
    kontoinhaber: Optional[str]
    sepa_mandat_ref: Optional[str]
    sepa_mandat_datum: Optional[date]
    standard: bool
    aktiv: bool
    created_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "BankverbindungOut":
        iban = row.get("iban", "")
        row["iban_masked"] = iban[:4] + "****" + iban[-4:] if len(iban) >= 8 else iban
        return cls(**row)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/{kunden_nr}/bankverbindungen", response_model=list[BankverbindungOut], summary="Bankverbindungen auflisten")
def list_bankverbindungen(
    kunden_nr: str,
    nur_aktive: bool = Query(True),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.kunden_bankverbindungen
        WHERE tenant_id = :tid AND kunden_nr = :kunden_nr
    """
    params: dict = {"tid": tenant_id, "kunden_nr": kunden_nr}
    if nur_aktive:
        sql += " AND aktiv = true"
    sql += " ORDER BY standard DESC, bezeichnung"
    rows = db.execute(text(sql), params).fetchall()
    return [BankverbindungOut.from_row(dict(r._mapping)) for r in rows]


@router.post("/{kunden_nr}/bankverbindungen",
             response_model=BankverbindungOut, status_code=201, summary="Bankverbindung anlegen")
def create_bankverbindung(
    kunden_nr: str,
    payload: BankverbindungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Bankverbindung für einen Kunden anlegen."""
    existing_iban = db.execute(text("""
        SELECT id FROM domain_shared.kunden_bankverbindungen
        WHERE tenant_id = :tid AND kunden_nr = :kunden_nr
          AND iban = :iban AND aktiv = true
    """), {"tid": tenant_id, "kunden_nr": kunden_nr, "iban": payload.iban}).fetchone()
    if existing_iban:
        raise HTTPException(409, "Diese IBAN ist für den Kunden bereits hinterlegt.")

    # Wenn neue Standard-BV: bisherige deaktivieren
    if payload.standard:
        db.execute(text("""
            UPDATE domain_shared.kunden_bankverbindungen
            SET standard = false
            WHERE tenant_id = :tid AND kunden_nr = :kunden_nr AND aktiv = true
        """), {"tid": tenant_id, "kunden_nr": kunden_nr})

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kunden_bankverbindungen
            (id, tenant_id, kunden_nr, bezeichnung, iban, bic, bank_name,
             kontoinhaber, sepa_mandat_ref, sepa_mandat_datum, standard, aktiv)
        VALUES (:id, :tid, :kunden_nr, :bez, :iban, :bic, :bank,
                :inhaber, :mandat_ref, :mandat_datum, :standard, true)
    """), {
        "id": new_id, "tid": tenant_id, "kunden_nr": kunden_nr,
        "bez": payload.bezeichnung, "iban": payload.iban, "bic": payload.bic,
        "bank": payload.bank_name, "inhaber": payload.kontoinhaber,
        "mandat_ref": payload.sepa_mandat_ref, "mandat_datum": payload.sepa_mandat_datum,
        "standard": payload.standard,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kunden_bankverbindungen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return BankverbindungOut.from_row(dict(row._mapping))


@router.patch("/{kunden_nr}/bankverbindungen/{bv_id}/standard", summary="Standard bankverbindung setzen",
    response_model=None
)
def set_standard_bankverbindung(
    kunden_nr: str,
    bv_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Bankverbindung als Standard setzen."""
    row = db.execute(text("""
        SELECT id FROM domain_shared.kunden_bankverbindungen
        WHERE id = :id AND tenant_id = :tid AND kunden_nr = :kunden_nr AND aktiv = true
    """), {"id": bv_id, "tid": tenant_id, "kunden_nr": kunden_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Bankverbindung nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.kunden_bankverbindungen
        SET standard = (id = :bv_id)
        WHERE tenant_id = :tid AND kunden_nr = :kunden_nr AND aktiv = true
    """), {"bv_id": bv_id, "tid": tenant_id, "kunden_nr": kunden_nr})
    db.commit()
    return {"id": bv_id, "standard": True}


@router.delete("/{kunden_nr}/bankverbindungen/{bv_id}", summary="Bankverbindung löschen",
    response_model=None
)
def delete_bankverbindung(
    kunden_nr: str,
    bv_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.kunden_bankverbindungen
        SET aktiv = false
        WHERE id = :id AND tenant_id = :tid AND kunden_nr = :kunden_nr
    """), {"id": bv_id, "tid": tenant_id, "kunden_nr": kunden_nr})
    db.commit()
    return Response(status_code=204)
