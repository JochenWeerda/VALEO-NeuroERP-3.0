"""Artikelstoffstrom — THG/CO2-Bewertung und Nachhaltigkeitsattribute je Artikel.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 17 Artikel):
  Der Stoffstromanteil je Artikel ermöglicht die Berechnung von
  THG-Treibhausgasemissionswerten (gCO2eq/MJ) für nachhaltige Rohstoffe.
  Basis: RED II / EU Renewable Energy Directive.

  Pflege: Anbauland, Rohstoffkategorie, CO2-Äquivalent, THG-Wert,
  ISCC-Zertifizierung, RED-Konformität.

  Verwendung: Nachhaltigkeitsberichte, ENNI-Meldungen, eRechnung
  (NaWaRo-Angaben), Massebilanz-THG-Auswertung.
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

router = APIRouter(prefix="/artikel/stoffstrom", tags=["Artikelstamm - Stoffstrom & THG"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class StoffstromCreate(BaseModel):
    artikel_nr: str
    anbauland: Optional[str] = Field(None, max_length=50,
                                     description="ISO 3166-2 Ländercode, z.B. DE, FR")
    rohstoff_kategorie: Optional[str] = None
    co2_aequivalent_kg_per_t: Optional[Decimal] = Field(None,
        description="kg CO2-Äquivalent pro Tonne")
    thg_wert: Optional[Decimal] = Field(None,
        description="THG-Treibhausgasemissionswert in gCO2eq/MJ")
    nachhaltig: bool = True
    iscc_zertifiziert: bool = False
    red_konform: bool = False
    gueltig_ab: Optional[date] = None
    gueltig_bis: Optional[date] = None
    bemerkung: Optional[str] = None


class StoffstromOut(BaseModel):
    id: str
    artikel_nr: str
    anbauland: Optional[str]
    rohstoff_kategorie: Optional[str]
    co2_aequivalent_kg_per_t: Optional[Decimal]
    thg_wert: Optional[Decimal]
    nachhaltig: bool
    iscc_zertifiziert: bool
    red_konform: bool
    gueltig_ab: Optional[date]
    gueltig_bis: Optional[date]
    bemerkung: Optional[str]
    created_at: datetime
    updated_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[StoffstromOut], summary="Stoffstrom auflisten")
def list_stoffstrom(
    artikel_nr: Optional[str] = Query(None),
    nur_nachhaltig: bool = Query(False),
    iscc: bool = Query(False),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = """
        SELECT * FROM domain_shared.artikel_stoffstrom
        WHERE tenant_id = :tid
    """
    params: dict = {"tid": tenant_id}
    if artikel_nr:
        sql += " AND artikel_nr = :artikel_nr"
        params["artikel_nr"] = artikel_nr
    if nur_nachhaltig:
        sql += " AND nachhaltig = true"
    if iscc:
        sql += " AND iscc_zertifiziert = true"
    sql += " ORDER BY artikel_nr, gueltig_ab DESC"
    rows = db.execute(text(sql), params).fetchall()
    return [StoffstromOut(**dict(r._mapping)) for r in rows]


@router.get("/artikel/{artikel_nr}", response_model=list[StoffstromOut], summary="Stoffstrom fuer artikel abrufen")
def get_stoffstrom_fuer_artikel(
    artikel_nr: str,
    stichtag: Optional[date] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Aktuelle Stoffstrom-Bewertungen für einen Artikel."""
    check_date = stichtag or date.today()
    rows = db.execute(text("""
        SELECT * FROM domain_shared.artikel_stoffstrom
        WHERE tenant_id = :tid AND artikel_nr = :art_nr
          AND (gueltig_ab IS NULL OR gueltig_ab <= :stichtag)
          AND (gueltig_bis IS NULL OR gueltig_bis >= :stichtag)
        ORDER BY gueltig_ab DESC
    """), {"tid": tenant_id, "art_nr": artikel_nr, "stichtag": check_date}).fetchall()
    return [StoffstromOut(**dict(r._mapping)) for r in rows]


@router.post("", response_model=StoffstromOut, status_code=201, summary="Stoffstrom anlegen")
def create_stoffstrom(
    payload: StoffstromCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_stoffstrom
            (id, tenant_id, artikel_nr, anbauland, rohstoff_kategorie,
             co2_aequivalent_kg_per_t, thg_wert,
             nachhaltig, iscc_zertifiziert, red_konform,
             gueltig_ab, gueltig_bis, bemerkung)
        VALUES (:id, :tid, :art_nr, :anbau, :rohstoff,
                :co2, :thg, :nach, :iscc, :red, :von, :bis, :bem)
    """), {
        "id": new_id, "tid": tenant_id, "art_nr": payload.artikel_nr,
        "anbau": payload.anbauland, "rohstoff": payload.rohstoff_kategorie,
        "co2": payload.co2_aequivalent_kg_per_t, "thg": payload.thg_wert,
        "nach": payload.nachhaltig, "iscc": payload.iscc_zertifiziert,
        "red": payload.red_konform, "von": payload.gueltig_ab,
        "bis": payload.gueltig_bis, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_stoffstrom WHERE id = :id
    """), {"id": new_id}).fetchone()
    return StoffstromOut(**dict(row._mapping))


@router.put("/{stoffstrom_id}", response_model=StoffstromOut, summary="Stoffstrom aktualisieren")
def update_stoffstrom(
    stoffstrom_id: str,
    payload: StoffstromCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.artikel_stoffstrom
        WHERE id = :id AND tenant_id = :tid
    """), {"id": stoffstrom_id, "tid": tenant_id}).fetchone()
    if not row:
        raise HTTPException(404, "Stoffstrom-Eintrag nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.artikel_stoffstrom
        SET artikel_nr = :art_nr, anbauland = :anbau, rohstoff_kategorie = :rohstoff,
            co2_aequivalent_kg_per_t = :co2, thg_wert = :thg,
            nachhaltig = :nach, iscc_zertifiziert = :iscc, red_konform = :red,
            gueltig_ab = :von, gueltig_bis = :bis, bemerkung = :bem,
            updated_at = now()
        WHERE id = :id
    """), {
        "id": stoffstrom_id, "art_nr": payload.artikel_nr,
        "anbau": payload.anbauland, "rohstoff": payload.rohstoff_kategorie,
        "co2": payload.co2_aequivalent_kg_per_t, "thg": payload.thg_wert,
        "nach": payload.nachhaltig, "iscc": payload.iscc_zertifiziert,
        "red": payload.red_konform, "von": payload.gueltig_ab,
        "bis": payload.gueltig_bis, "bem": payload.bemerkung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_stoffstrom WHERE id = :id
    """), {"id": stoffstrom_id}).fetchone()
    return StoffstromOut(**dict(row._mapping))


@router.delete("/{stoffstrom_id}", summary="Stoffstrom löschen")
def delete_stoffstrom(
    stoffstrom_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        DELETE FROM domain_shared.artikel_stoffstrom
        WHERE id = :id AND tenant_id = :tid
    """), {"id": stoffstrom_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


@router.get("/report/thg-summary", summary="Summary thg")
def thg_summary(
    anbauland: Optional[str] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """THG-Zusammenfassung: CO2-Äquivalente je Rohstoffkategorie und Anbauland."""
    sql = """
        SELECT rohstoff_kategorie, anbauland,
               COUNT(*) as anzahl_artikel,
               AVG(co2_aequivalent_kg_per_t) as avg_co2,
               AVG(thg_wert) as avg_thg,
               SUM(CASE WHEN iscc_zertifiziert THEN 1 ELSE 0 END) as iscc_count,
               SUM(CASE WHEN red_konform THEN 1 ELSE 0 END) as red_count
        FROM domain_shared.artikel_stoffstrom
        WHERE tenant_id = :tid AND nachhaltig = true
    """
    params: dict = {"tid": tenant_id}
    if anbauland:
        sql += " AND anbauland = :anbauland"
        params["anbauland"] = anbauland
    sql += " GROUP BY rohstoff_kategorie, anbauland ORDER BY rohstoff_kategorie"
    rows = db.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in rows]
