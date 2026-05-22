"""Zahlungsbedingungen [ZABD] — Zahlungsziel, Skonto, Zahlungsart.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Zahlungsbedingungen steuern Fälligkeit und Skontogewährung auf Belegen.
  Zwei Skontostufen (Skonto1/Skonto2), manuelles Fälligkeitsdatum-Flag,
  sowie Zahlungsart (Überweisung, Lastschrift, Scheck, Kasse, Vorkasse).

  Schlüsselfelder: ZABD-Nr + Bezeichnung + Zahlungsziel + Skonto-Parameter.
  Hinterlegung am Kunden-/Lieferantenstamm und am Beleg.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/fibu/zahlungsbedingungen",
                   tags=["FIBU - Zahlungsbedingungen"])

GUELTIGE_ZAHLUNGSARTEN = {"ueberweisung", "lastschrift", "scheck", "kasse", "vorkasse"}


# ── Schemas ───────────────────────────────────────────────────────────────────

class ZahlungsbedingungCreate(BaseModel):
    zabd_nr: str = Field(..., max_length=20)
    bezeichnung: str
    zahlungsziel_tage: int = Field(30, ge=0)
    skonto1_tage: Optional[int] = Field(None, ge=0)
    skonto1_prozent: Optional[float] = Field(None, ge=0, le=100)
    skonto2_tage: Optional[int] = Field(None, ge=0)
    skonto2_prozent: Optional[float] = Field(None, ge=0, le=100)
    netto_tage: Optional[int] = Field(30, ge=0)
    manuelles_datum: bool = False
    zahlungsart: str = "ueberweisung"

    def model_post_init(self, __context):
        if self.zahlungsart not in GUELTIGE_ZAHLUNGSARTEN:
            raise ValueError(f"Ungültige Zahlungsart: {self.zahlungsart}")


class ZahlungsbedingungOut(BaseModel):
    id: str
    zabd_nr: str
    bezeichnung: str
    zahlungsziel_tage: int
    skonto1_tage: Optional[int]
    skonto1_prozent: Optional[float]
    skonto2_tage: Optional[int]
    skonto2_prozent: Optional[float]
    netto_tage: Optional[int]
    manuelles_datum: bool
    zahlungsart: str
    aktiv: bool
    created_at: datetime


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ZahlungsbedingungOut])
def list_zahlungsbedingungen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.zahlungsbedingungen
        WHERE tenant_id = :tid AND aktiv = true ORDER BY zabd_nr
    """), {"tid": tenant_id}).fetchall()
    return [ZahlungsbedingungOut(**dict(r._mapping)) for r in rows]


@router.get("/{zabd_nr}", response_model=ZahlungsbedingungOut)
def get_zahlungsbedingung(
    zabd_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.zahlungsbedingungen
        WHERE tenant_id = :tid AND zabd_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": zabd_nr}).fetchone()
    if not row:
        raise HTTPException(404, f"Zahlungsbedingung {zabd_nr} nicht gefunden.")
    return ZahlungsbedingungOut(**dict(row._mapping))


@router.post("", response_model=ZahlungsbedingungOut, status_code=201)
def create_zahlungsbedingung(
    payload: ZahlungsbedingungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    if db.execute(text("""
        SELECT id FROM domain_shared.zahlungsbedingungen
        WHERE tenant_id = :tid AND zabd_nr = :nr
    """), {"tid": tenant_id, "nr": payload.zabd_nr}).fetchone():
        raise HTTPException(409, f"Zahlungsbedingung {payload.zabd_nr} bereits vorhanden.")
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.zahlungsbedingungen
            (id, tenant_id, zabd_nr, bezeichnung, zahlungsziel_tage,
             skonto1_tage, skonto1_prozent, skonto2_tage, skonto2_prozent,
             netto_tage, manuelles_datum, zahlungsart)
        VALUES (:id, :tid, :nr, :bez, :zt, :s1t, :s1p, :s2t, :s2p, :nt, :md, :za)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.zabd_nr,
        "bez": payload.bezeichnung, "zt": payload.zahlungsziel_tage,
        "s1t": payload.skonto1_tage, "s1p": payload.skonto1_prozent,
        "s2t": payload.skonto2_tage, "s2p": payload.skonto2_prozent,
        "nt": payload.netto_tage, "md": payload.manuelles_datum,
        "za": payload.zahlungsart,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.zahlungsbedingungen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ZahlungsbedingungOut(**dict(row._mapping))


@router.delete("/{zabd_nr}")
def delete_zahlungsbedingung(
    zabd_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.zahlungsbedingungen SET aktiv = false
        WHERE tenant_id = :tid AND zabd_nr = :nr
    """), {"tid": tenant_id, "nr": zabd_nr})
    db.commit()
    return Response(status_code=204)
