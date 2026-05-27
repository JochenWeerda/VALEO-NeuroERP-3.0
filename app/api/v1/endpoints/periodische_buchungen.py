"""Periodische Buchungen [WZA] — Wiederkehrende FIBU-Buchungen.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 03 FIBU):
  Ständig wiederkehrende Buchungen (Miete, AfA, Versicherungen) werden als
  Stammdaten mit Konto/Gegenkonto, Buchungstext, Betrag, Turnus und Laufzeit
  gepflegt. Per Stichtag werden fällige Belege zur Buchung vorgeschlagen.

  Direktsprung: [WZA] = Wiederkehrende Zahlungsanweisungen / Periodische Buchungen.

  Turnus-Werte: monatlich, quartalsweise, halbjaehrlich, jaehrlich, einmalig.
  Vorgangsklassen: ZA (Zahlungseingang/ausgang), ER (Eingangsrechnung), AR (Ausgangsrechnung).
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

router = APIRouter(prefix="/fibu/periodische-buchungen",
                   tags=["FIBU - Periodische Buchungen"])

GUELTIGE_TURNUS = {"monatlich", "quartalsweise", "halbjaehrlich", "jaehrlich", "einmalig"}
GUELTIGE_VORGANGSKLASSEN = {"ZA", "ER", "AR", "UM"}


# ── Schemas ───────────────────────────────────────────────────────────────────

class PeriodischeBuchungCreate(BaseModel):
    bezeichnung: str
    vorgangsklasse: str = "ZA"
    konto: str
    gegenkonto: str
    buchungstext: Optional[str] = None
    betrag: Decimal = Field(..., gt=0)
    turnus: str = "monatlich"
    gueltig_ab: date
    gueltig_bis: Optional[date] = None
    gesperrt: bool = False
    kostenstelle: Optional[str] = None

    def model_post_init(self, __context):
        if self.turnus not in GUELTIGE_TURNUS:
            raise ValueError(f"Ungültiger Turnus: {self.turnus}")
        if self.vorgangsklasse not in GUELTIGE_VORGANGSKLASSEN:
            raise ValueError(f"Ungültige Vorgangsklasse: {self.vorgangsklasse}")


class PeriodischeBuchungOut(BaseModel):
    id: str
    bezeichnung: str
    vorgangsklasse: str
    konto: str
    gegenkonto: str
    buchungstext: Optional[str]
    betrag: Decimal
    turnus: str
    gueltig_ab: date
    gueltig_bis: Optional[date]
    gesperrt: bool
    kostenstelle: Optional[str]
    aktiv: bool
    created_at: datetime


class FaelligBelegOut(BaseModel):
    id: str
    bezeichnung: str
    konto: str
    gegenkonto: str
    betrag: Decimal
    vorgangsklasse: str
    turnus: str
    gueltig_ab: date


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[PeriodischeBuchungOut], summary="Periodische buchungen auflisten")
def list_periodische_buchungen(
    gesperrt: Optional[bool] = Query(None),
    turnus: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.periodische_buchungen
        WHERE tenant_id = :tid AND aktiv = true
    """
    params: dict = {"tid": tenant_id}
    if gesperrt is not None:
        sql += " AND gesperrt = :gesperrt"
        params["gesperrt"] = gesperrt
    if turnus:
        sql += " AND turnus = :turnus"
        params["turnus"] = turnus
    sql += " ORDER BY bezeichnung"
    rows = db.execute(text(sql), params).fetchall()
    return [PeriodischeBuchungOut(**dict(r._mapping)) for r in rows]


@router.get("/faellig", response_model=list[FaelligBelegOut], summary="Faellige buchungen abrufen")
def get_faellige_buchungen(
    stichtag: date = Query(default=None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Gibt alle zum Stichtag fälligen, nicht gesperrten Buchungen zurück."""
    check_date = stichtag or date.today()
    rows = db.execute(text("""
        SELECT * FROM domain_shared.periodische_buchungen
        WHERE tenant_id = :tid
          AND aktiv = true
          AND gesperrt = false
          AND gueltig_ab <= :stichtag
          AND (gueltig_bis IS NULL OR gueltig_bis >= :stichtag)
        ORDER BY bezeichnung
    """), {"tid": tenant_id, "stichtag": check_date}).fetchall()
    return [FaelligBelegOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=PeriodischeBuchungOut, status_code=201, summary="Periodische buchung anlegen")
def create_periodische_buchung(
    payload: PeriodischeBuchungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.periodische_buchungen
            (id, tenant_id, bezeichnung, vorgangsklasse, konto, gegenkonto,
             buchungstext, betrag, turnus, gueltig_ab, gueltig_bis, gesperrt, kostenstelle)
        VALUES (:id, :tid, :bez, :vk, :kt, :gkt, :bt, :betr, :tur, :gab, :gbis, :gesperrt, :kst)
    """), {
        "id": new_id, "tid": tenant_id, "bez": payload.bezeichnung,
        "vk": payload.vorgangsklasse, "kt": payload.konto, "gkt": payload.gegenkonto,
        "bt": payload.buchungstext, "betr": payload.betrag, "tur": payload.turnus,
        "gab": payload.gueltig_ab, "gbis": payload.gueltig_bis,
        "gesperrt": payload.gesperrt, "kst": payload.kostenstelle,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.periodische_buchungen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return PeriodischeBuchungOut(**dict(row._mapping))


@router.patch("/{buchung_id}/sperren", summary="Buchung sperren")
def sperren_buchung(
    buchung_id: str,
    gesperrt: bool = Query(...),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    result = db.execute(text("""
        UPDATE domain_shared.periodische_buchungen SET gesperrt = :gesperrt
        WHERE id = :id AND tenant_id = :tid AND aktiv = true
    """), {"gesperrt": gesperrt, "id": buchung_id, "tid": tenant_id})
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, "Periodische Buchung nicht gefunden.")
    return {"id": buchung_id, "gesperrt": gesperrt}


@router.delete("/{buchung_id}", summary="Periodische buchung löschen")
def delete_periodische_buchung(
    buchung_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.periodische_buchungen SET aktiv = false
        WHERE id = :id AND tenant_id = :tid
    """), {"id": buchung_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)
