"""Zinsabrechnung — Zinsen auf Rohware-Einlagerungskontrakte.

Fachlicher Hintergrund (aus Referenz-ERP Wissensbasis):
  Bei der Einlagerung von Rohware (Getreide, Ölsaaten) entstehen für den
  Landwirt Zinsgutschriften auf den hinterlegten Warenwert. Die Zinsabrechnung
  berechnet den Zinsbetrag auf Basis des Kontraktwerts, des Zinssatzes und des
  Einlagerungszeitraums.

  Prozess: Berechnen → Drucken/Mailversand → Buchen → optional Stornieren
  Anwendung: ZIB (Zinsabrechnungs-Bearbeitung) im Referenz-ERP
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


router = APIRouter(prefix="/zinsabrechnung", tags=["Zinsabrechnung"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ZinsabrechnungCreate(BaseModel):
    kontrakt_nr: str
    lieferant_nr: str
    lieferant_name: Optional[str] = None
    zinssatz_prozent: Decimal = Field(..., gt=0, description="Jahreszinssatz in %")
    basisbetrag_eur: Decimal = Field(..., gt=0, description="Abrechnungsgrundlage (Warenwert)")
    von_datum: date
    bis_datum: date
    mwst_satz: Decimal = Field(default=Decimal("19.0"))
    buchungs_periode: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")
    bemerkung: Optional[str] = None


class ZinsabrechnungOut(BaseModel):
    id: str
    kontrakt_nr: str
    lieferant_nr: str
    lieferant_name: Optional[str]
    zinssatz_prozent: Decimal
    basisbetrag_eur: Decimal
    von_datum: date
    bis_datum: date
    tage: int
    zinsbetrag_eur: Decimal
    mwst_satz: Decimal
    mwst_betrag_eur: Optional[Decimal]
    status: str
    beleg_nr: Optional[str]
    buchungs_periode: Optional[str]
    storno_von_id: Optional[str]
    bemerkung: Optional[str]
    created_at: datetime


# ── Helper ────────────────────────────────────────────────────────────────────

def _berechne_zins(basisbetrag: Decimal, zinssatz: Decimal,
                   von: date, bis: date) -> tuple[int, Decimal, Decimal]:
    """Berechnet Zinsbetrag nach Tagesbasis (Referenz: 360 Tage/Jahr)."""
    tage = (bis - von).days
    if tage < 0:
        raise ValueError("bis_datum muss nach von_datum liegen.")
    zinsbetrag = (basisbetrag * zinssatz / 100 * tage / 360).quantize(Decimal("0.01"))
    mwst = (zinsbetrag * Decimal("0.19")).quantize(Decimal("0.01"))
    return tage, zinsbetrag, mwst


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ZinsabrechnungOut], summary="Zinsabrechnungen auflisten")
def list_zinsabrechnungen(
    kontrakt_nr: Optional[str] = Query(None),
    lieferant_nr: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    periode: Optional[str] = Query(None, description="YYYY-MM"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if kontrakt_nr:
        sql += " AND kontrakt_nr = :ktr"
        params["ktr"] = kontrakt_nr
    if lieferant_nr:
        sql += " AND lieferant_nr = :lief"
        params["lief"] = lieferant_nr
    if status:
        sql += " AND status = :status"
        params["status"] = status
    if periode:
        sql += " AND buchungs_periode = :periode"
        params["periode"] = periode
    sql += " ORDER BY created_at DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [ZinsabrechnungOut(**dict(r._mapping)) for r in rows]


@router.post("/berechnen", response_model=ZinsabrechnungOut, status_code=201, summary="Zinsabrechnung berechne")
def berechne_zinsabrechnung(
    payload: ZinsabrechnungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zinsabrechnung berechnen und als Entwurf anlegen."""
    try:
        tage, zinsbetrag, mwst = _berechne_zins(
            payload.basisbetrag_eur, payload.zinssatz_prozent,
            payload.von_datum, payload.bis_datum,
        )
    except ValueError as e:
        raise HTTPException(422, str(e)) from e

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kontrakt_zinsabrechnungen
            (id, tenant_id, kontrakt_nr, lieferant_nr, lieferant_name,
             zinssatz_prozent, basisbetrag_eur, von_datum, bis_datum,
             tage, zinsbetrag_eur, mwst_satz, mwst_betrag_eur,
             status, buchungs_periode, bemerkung)
        VALUES (:id, :tid, :ktr_nr, :lief_nr, :lief_name,
                :zinssatz, :basis, :von, :bis,
                :tage, :zins, :mwst_satz, :mwst_betrag,
                'offen', :periode, :bem)
    """), {
        "id": new_id, "tid": tenant_id,
        "ktr_nr": payload.kontrakt_nr, "lief_nr": payload.lieferant_nr,
        "lief_name": payload.lieferant_name,
        "zinssatz": payload.zinssatz_prozent, "basis": payload.basisbetrag_eur,
        "von": payload.von_datum, "bis": payload.bis_datum,
        "tage": tage, "zins": zinsbetrag,
        "mwst_satz": payload.mwst_satz, "mwst_betrag": mwst,
        "periode": payload.buchungs_periode, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return ZinsabrechnungOut(**dict(row._mapping))


@router.post("/{zins_id}/drucken", summary="Zinsabrechnung drucke",
    response_model=ZinsabrechnungOut
)
def drucke_zinsabrechnung(
    zins_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zinsabrechnung auf 'gedruckt' setzen und Druckdaten zurückgeben."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": zins_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Zinsabrechnung nicht gefunden.")
    if row.status == "storniert":
        raise HTTPException(409, "Stornierte Zinsabrechnungen können nicht gedruckt werden.")

    db.execute(text("""
        UPDATE domain_shared.kontrakt_zinsabrechnungen
        SET status = 'gedruckt', updated_at = now()
        WHERE id = :id
    """), {"id": zins_id})
    db.commit()

    r = dict(row._mapping)
    return {
        "id": r["id"],
        "druckdaten": {
            "kontrakt_nr": r["kontrakt_nr"],
            "lieferant_nr": r["lieferant_nr"],
            "lieferant_name": r["lieferant_name"],
            "von_datum": str(r["von_datum"]),
            "bis_datum": str(r["bis_datum"]),
            "tage": r["tage"],
            "zinssatz": float(r["zinssatz_prozent"]),
            "basisbetrag_eur": float(r["basisbetrag_eur"]),
            "zinsbetrag_eur": float(r["zinsbetrag_eur"]),
            "mwst_betrag_eur": float(r["mwst_betrag_eur"] or 0),
            "gesamtbetrag_eur": float(r["zinsbetrag_eur"]) + float(r["mwst_betrag_eur"] or 0),
        },
        "status": "gedruckt",
    }


@router.post("/{zins_id}/buchen", response_model=ZinsabrechnungOut, summary="Zinsabrechnung buche")
def buche_zinsabrechnung(
    zins_id: str,
    beleg_nr: Optional[str] = None,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zinsabrechnung buchen (FIBU-Übernahme)."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": zins_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Zinsabrechnung nicht gefunden.")
    if row.status in ("gebucht", "storniert"):
        raise HTTPException(409, f"Status '{row.status}' erlaubt keine Buchung.")

    generated_beleg = beleg_nr or f"ZIB-{zins_id[:8].upper()}"
    db.execute(text("""
        UPDATE domain_shared.kontrakt_zinsabrechnungen
        SET status = 'gebucht', beleg_nr = :beleg_nr, updated_at = now()
        WHERE id = :id
    """), {"id": zins_id, "beleg_nr": generated_beleg})
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen WHERE id = :id
    """), {"id": zins_id}).fetchone()
    return ZinsabrechnungOut(**dict(row._mapping))


@router.post("/{zins_id}/stornieren", response_model=ZinsabrechnungOut, summary="Zinsabrechnung storniere")
def storniere_zinsabrechnung(
    zins_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zinsabrechnung stornieren und Stornobeleg erzeugen."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen
        WHERE id = :id AND tenant_id = :tid
    """), {"id": zins_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Zinsabrechnung nicht gefunden.")
    if row.status == "storniert":
        raise HTTPException(409, "Bereits storniert.")

    r = dict(row._mapping)
    # Stornobeleg als Gegenbuchung
    storno_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.kontrakt_zinsabrechnungen
            (id, tenant_id, kontrakt_nr, lieferant_nr, lieferant_name,
             zinssatz_prozent, basisbetrag_eur, von_datum, bis_datum,
             tage, zinsbetrag_eur, mwst_satz, mwst_betrag_eur,
             status, buchungs_periode, storno_von_id, bemerkung)
        VALUES (:id, :tid, :ktr_nr, :lief_nr, :lief_name,
                :zinssatz, :basis, :von, :bis,
                :tage, :zins, :mwst_satz, :mwst_betrag,
                'gebucht', :periode, :orig_id, :bem)
    """), {
        "id": storno_id, "tid": tenant_id,
        "ktr_nr": r["kontrakt_nr"], "lief_nr": r["lieferant_nr"],
        "lief_name": r["lieferant_name"],
        "zinssatz": r["zinssatz_prozent"], "basis": -abs(Decimal(str(r["basisbetrag_eur"]))),
        "von": r["von_datum"], "bis": r["bis_datum"],
        "tage": r["tage"], "zins": -abs(Decimal(str(r["zinsbetrag_eur"]))),
        "mwst_satz": r["mwst_satz"],
        "mwst_betrag": -abs(Decimal(str(r["mwst_betrag_eur"] or 0))),
        "periode": r["buchungs_periode"], "orig_id": zins_id,
        "bem": f"Storno von {zins_id}",
    })
    db.execute(text("""
        UPDATE domain_shared.kontrakt_zinsabrechnungen
        SET status = 'storniert', updated_at = now()
        WHERE id = :id
    """), {"id": zins_id})
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.kontrakt_zinsabrechnungen WHERE id = :id
    """), {"id": zins_id}).fetchone()
    return ZinsabrechnungOut(**dict(row._mapping))
