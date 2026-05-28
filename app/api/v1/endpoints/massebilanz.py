"""Massebilanz — Periodische Mengenbilanzierung für Rohwarenbewegungen.

Fachlicher Hintergrund (aus Referenz-ERP Wissensbasis):
  Die Massebilanz ist ein Werkzeug zur Mengenbilanzierung im Rohwarenhandel.
  In einer Rohwarekette (Lieferschein → Abschlag → Folgeabschlag → Finale)
  werden die Bewegungen des letzten massebilanzrelevanten Belegs erfasst.
  Nach dem Festschreiben einer Massebilanz können die zugehörigen Bewegungen
  nicht mehr bearbeitet werden. Stornobelege und deren Folgebelege werden
  nicht in Massebilanzen berücksichtigt.

  Anwendung: Rohwaren-Massenbilanzierung (THG-Nachhaltigkeit, Lagerbestand-
  kontrolle, Periodenabschluss im Getreide-/Ölsaatenhandel).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/massebilanz", tags=["Massebilanz"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class MassebilanzCreate(BaseModel):
    periode: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="YYYY-MM")
    artikel_nr: Optional[str] = None
    lager_nr: Optional[str] = None
    anfangsbestand_kg: Decimal = Field(default=Decimal("0"))
    bemerkung: Optional[str] = None


class BewegungCreate(BaseModel):
    massebilanz_id: str
    beleg_nr: Optional[str] = None
    beleg_typ: Optional[str] = Field(None, description="lieferschein, abschlag, finale, storno")
    buchungsdatum: date
    menge_kg: Decimal
    vorzeichen: str = Field(default="+", pattern=r"^[+-]$")
    kontrakt_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class MassebilanzOut(BaseModel):
    id: str
    periode: str
    artikel_nr: Optional[str]
    lager_nr: Optional[str]
    anfangsbestand_kg: Decimal
    zugaenge_kg: Decimal
    abgaenge_kg: Decimal
    endbestand_kg: Decimal
    differenz_kg: Decimal
    status: str
    festgeschrieben_am: Optional[datetime]
    festgeschrieben_von: Optional[str]
    bemerkung: Optional[str]
    created_at: datetime


class BewegungOut(BaseModel):
    id: str
    massebilanz_id: str
    beleg_nr: Optional[str]
    beleg_typ: Optional[str]
    buchungsdatum: date
    menge_kg: Decimal
    vorzeichen: str
    kontrakt_nr: Optional[str]
    lieferant_nr: Optional[str]
    storniert: bool
    created_at: datetime


# ── Helper ────────────────────────────────────────────────────────────────────

def _recalculate_bilanz(db, bilanz_id: str) -> None:
    """Neuberechnung Zugänge, Abgänge, Endbestand."""
    db.execute(text("""
        UPDATE domain_shared.rohware_massebilanzen mb
        SET
            zugaenge_kg  = COALESCE((
                SELECT SUM(menge_kg) FROM domain_shared.rohware_massebilanz_bewegungen
                WHERE massebilanz_id = mb.id AND vorzeichen = '+' AND NOT storniert), 0),
            abgaenge_kg  = COALESCE((
                SELECT SUM(menge_kg) FROM domain_shared.rohware_massebilanz_bewegungen
                WHERE massebilanz_id = mb.id AND vorzeichen = '-' AND NOT storniert), 0),
            endbestand_kg = mb.anfangsbestand_kg
                + COALESCE((
                    SELECT SUM(CASE vorzeichen WHEN '+' THEN menge_kg ELSE -menge_kg END)
                    FROM domain_shared.rohware_massebilanz_bewegungen
                    WHERE massebilanz_id = mb.id AND NOT storniert), 0),
            updated_at   = now()
        WHERE mb.id = :id
    """), {"id": bilanz_id})


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[MassebilanzOut], summary="Massebilanzen auflisten")
def list_massebilanzen(
    periode: Optional[str] = Query(None, description="YYYY-MM"),
    status: Optional[str] = Query(None),
    artikel_nr: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Alle Massebilanzen des Mandanten auflisten."""
    sql = """
        SELECT id, periode, artikel_nr, lager_nr, anfangsbestand_kg,
               zugaenge_kg, abgaenge_kg, endbestand_kg, differenz_kg,
               status, festgeschrieben_am, festgeschrieben_von, bemerkung, created_at
        FROM domain_shared.rohware_massebilanzen
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if periode:
        sql += " AND periode = :periode"
        params["periode"] = periode
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if artikel_nr:
        sql += " AND artikel_nr = :artikel_nr"
        params["artikel_nr"] = artikel_nr
    sql += " ORDER BY periode DESC, artikel_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [MassebilanzOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=MassebilanzOut, status_code=201, summary="Massebilanz anlegen")
def create_massebilanz(
    payload: MassebilanzCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Neue Massebilanz für eine Periode anlegen."""
    existing = db.execute(text("""
        SELECT id FROM domain_shared.rohware_massebilanzen
        WHERE tenant_id = :tid AND periode = :periode
          AND COALESCE(artikel_nr,'') = COALESCE(:artikel_nr,'')
          AND COALESCE(lager_nr,'') = COALESCE(:lager_nr,'')
    """), {"tid": tenant_id, "periode": payload.periode,
           "artikel_nr": payload.artikel_nr, "lager_nr": payload.lager_nr}).fetchone()
    if existing:
        raise HTTPException(409, "Massebilanz für diese Periode/Artikel/Lager existiert bereits.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohware_massebilanzen
            (id, tenant_id, periode, artikel_nr, lager_nr,
             anfangsbestand_kg, zugaenge_kg, abgaenge_kg, endbestand_kg,
             differenz_kg, status, bemerkung)
        VALUES (:id, :tid, :periode, :artikel_nr, :lager_nr,
                :anfang, 0, 0, :anfang, 0, 'offen', :bemerkung)
    """), {
        "id": new_id, "tid": tenant_id, "periode": payload.periode,
        "artikel_nr": payload.artikel_nr, "lager_nr": payload.lager_nr,
        "anfang": payload.anfangsbestand_kg, "bemerkung": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanzen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return MassebilanzOut(**dict(row._mapping))


@router.get("/{bilanz_id}", response_model=MassebilanzOut, summary="Massebilanz abrufen")
def get_massebilanz(
    bilanz_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanzen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": bilanz_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Massebilanz nicht gefunden.")
    return MassebilanzOut(**dict(row._mapping))


@router.post("/{bilanz_id}/bewegungen", response_model=BewegungOut, status_code=201, summary="Bewegung hinzufügen")
def add_bewegung(
    bilanz_id: str,
    payload: BewegungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Rohwarebewegung zur Massebilanz buchen."""
    bilanz = db.execute(text("""
        SELECT status FROM domain_shared.rohware_massebilanzen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": bilanz_id, "tid": tenant_id}).fetchone()
    if not bilanz:
        raise HTTPException(404, "Massebilanz nicht gefunden.")
    if bilanz.status == "festgeschrieben":
        raise HTTPException(409, "Festgeschriebene Massebilanzen können nicht mehr bebucht werden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.rohware_massebilanz_bewegungen
            (id, tenant_id, massebilanz_id, beleg_nr, beleg_typ,
             buchungsdatum, menge_kg, vorzeichen, kontrakt_nr, lieferant_nr,
             bemerkung, storniert)
        VALUES (:id, :tid, :mb_id, :beleg_nr, :beleg_typ,
                :bdatum, :menge, :vz, :ktr_nr, :lief_nr, :bem, false)
    """), {
        "id": new_id, "tid": tenant_id, "mb_id": bilanz_id,
        "beleg_nr": payload.beleg_nr, "beleg_typ": payload.beleg_typ,
        "bdatum": payload.buchungsdatum, "menge": payload.menge_kg,
        "vz": payload.vorzeichen, "ktr_nr": payload.kontrakt_nr,
        "lief_nr": payload.lieferant_nr, "bem": payload.bemerkung,
    })
    _recalculate_bilanz(db, bilanz_id)
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanz_bewegungen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return BewegungOut(**dict(row._mapping))


@router.get("/{bilanz_id}/bewegungen", response_model=list[BewegungOut], summary="Bewegungen auflisten")
def list_bewegungen(
    bilanz_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Alle Bewegungen einer Massebilanz."""
    rows = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanz_bewegungen
        WHERE massebilanz_id = :mb_id AND tenant_id = :tid
        ORDER BY buchungsdatum, created_at
    """), {"mb_id": bilanz_id, "tid": tenant_id}).fetchall()
    return [BewegungOut(**dict(r._mapping)) for r in rows]


@router.post("/{bilanz_id}/festschreiben", response_model=MassebilanzOut, summary="Festschreiben")
def festschreiben(
    bilanz_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Massebilanz festschreiben — danach keine Änderungen mehr möglich.

    Fachlich: Nach dem Festschreiben einer Massebilanz lassen sich die
    dazugehörigen Bewegungen nicht mehr bearbeiten (Referenz-ERP Verhalten).
    """
    bilanz = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanzen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": bilanz_id, "tid": tenant_id}).fetchone()
    if not bilanz:
        raise HTTPException(404, "Massebilanz nicht gefunden.")
    if bilanz.status == "festgeschrieben":
        raise HTTPException(409, "Massebilanz ist bereits festgeschrieben.")

    _recalculate_bilanz(db, bilanz_id)
    db.execute(text("""
        UPDATE domain_shared.rohware_massebilanzen
        SET status = 'festgeschrieben',
            festgeschrieben_am = now(),
            differenz_kg = endbestand_kg - anfangsbestand_kg - zugaenge_kg + abgaenge_kg,
            updated_at = now()
        WHERE id = :id
    """), {"id": bilanz_id})
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanzen WHERE id = :id
    """), {"id": bilanz_id}).fetchone()
    return MassebilanzOut(**dict(row._mapping))


@router.get("/{bilanz_id}/bericht", summary="Bericht massebilanz",
    response_model=MassebilanzOut
)
def massebilanz_bericht(
    bilanz_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Massebilanz-Kompaktbericht mit Bewegungsübersicht."""
    bilanz = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanzen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": bilanz_id, "tid": tenant_id}).fetchone()
    if not bilanz:
        raise HTTPException(404, "Massebilanz nicht gefunden.")

    bewegungen = db.execute(text("""
        SELECT * FROM domain_shared.rohware_massebilanz_bewegungen
        WHERE massebilanz_id = :id AND NOT storniert
        ORDER BY buchungsdatum, created_at
    """), {"id": bilanz_id}).fetchall()

    b = dict(bilanz._mapping)
    return {
        "massebilanz": b,
        "bewegungen": [dict(m._mapping) for m in bewegungen],
        "zusammenfassung": {
            "anfangsbestand_kg": float(b["anfangsbestand_kg"]),
            "zugaenge_kg": float(b["zugaenge_kg"]),
            "abgaenge_kg": float(b["abgaenge_kg"]),
            "endbestand_kg": float(b["endbestand_kg"]),
            "differenz_kg": float(b["differenz_kg"]),
            "anzahl_bewegungen": len(bewegungen),
        },
    }
