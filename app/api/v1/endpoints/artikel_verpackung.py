"""Artikelverpackung [AVP] — Gebinde-Stammdaten (1-3 Stufen).

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 17 Artikelstamm):
  Artikelverpackungen [AVP] definieren die Gebinde-Hierarchie eines Artikels.
  Ein Gebinde kann bis zu 3 Stufen haben (SPA 591/592/593):
  - Stufe 1: Einzelgebinde (z.B. Flasche, Beutel, Sack)
  - Stufe 2: Sammelgebinde (z.B. Karton mit 6 Flaschen, Tray)
  - Stufe 3: Versandgebinde (z.B. Palette mit 48 Kartons)

  Artikelverpackungen können anzeigbar ("Artikel Gebinde anzeigen") und
  für die Berechnung von Brutto/Netto-Gewichten bei der Waage herangezogen werden.
  Angebrochene Gebinde: SPA 189 steuert Anzahl-Ermittlung.

  Löschverhalten: Bei Löschung wird nur Löschkennzeichen gesetzt (keine
  physische Löschung) — Referenz-ERP-konformes Verhalten [AVP].
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/artikel/verpackungen",
                   tags=["Artikelstamm - Verpackung & Gebinde"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ArtikelVerpackungCreate(BaseModel):
    verpackungs_nr: str = Field(..., max_length=20)
    bezeichnung: str
    stufen: int = Field(default=1, ge=1, le=3,
                        description="Gebinde-Stufen: 1=einstufig, 2=zweistufig, 3=dreistufig")
    # Stufe 1
    stufe1_bezeichnung: Optional[str] = None
    stufe1_menge: Optional[Decimal] = Field(None, gt=0)
    stufe1_einheit: Optional[str] = Field(None, max_length=10)
    stufe1_gewicht_kg: Optional[Decimal] = Field(None, ge=0)
    # Stufe 2
    stufe2_bezeichnung: Optional[str] = None
    stufe2_einheiten_pro_stufe2: Optional[int] = Field(None, gt=0)
    stufe2_gewicht_kg: Optional[Decimal] = Field(None, ge=0)
    # Stufe 3
    stufe3_bezeichnung: Optional[str] = None
    stufe3_einheiten_pro_stufe3: Optional[int] = Field(None, gt=0)
    stufe3_gewicht_kg: Optional[Decimal] = Field(None, ge=0)

    @model_validator(mode="after")
    def validate_stufen(self) -> "ArtikelVerpackungCreate":
        if self.stufen >= 2 and not self.stufe2_einheiten_pro_stufe2:
            raise ValueError("stufe2_einheiten_pro_stufe2 ist Pflicht bei stufen >= 2.")
        if self.stufen >= 3 and not self.stufe3_einheiten_pro_stufe3:
            raise ValueError("stufe3_einheiten_pro_stufe3 ist Pflicht bei stufen = 3.")
        return self


class ArtikelVerpackungOut(BaseModel):
    id: str
    verpackungs_nr: str
    bezeichnung: str
    stufen: int
    stufe1_bezeichnung: Optional[str]
    stufe1_menge: Optional[Decimal]
    stufe1_einheit: Optional[str]
    stufe1_gewicht_kg: Optional[Decimal]
    stufe2_bezeichnung: Optional[str]
    stufe2_einheiten_pro_stufe2: Optional[int]
    stufe2_gewicht_kg: Optional[Decimal]
    stufe3_bezeichnung: Optional[str]
    stufe3_einheiten_pro_stufe3: Optional[int]
    stufe3_gewicht_kg: Optional[Decimal]
    aktiv: bool
    created_at: datetime


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ArtikelVerpackungOut], summary="Verpackungen auflisten")
def list_verpackungen(
    nur_aktive: bool = Query(True),
    stufen: Optional[int] = Query(None, description="Filter nach Stufen-Anzahl"),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    sql = "SELECT * FROM domain_shared.artikel_verpackungen WHERE tenant_id = :tid"
    params: dict = {"tid": tenant_id}
    if nur_aktive:
        sql += " AND aktiv = true"
    if stufen:
        sql += " AND stufen = :stufen"
        params["stufen"] = stufen
    sql += " ORDER BY verpackungs_nr"
    rows = db.execute(text(sql), params).fetchall()
    return [ArtikelVerpackungOut(**dict(r._mapping)) for r in rows]


@router.get("/{verpackungs_nr}", response_model=ArtikelVerpackungOut, summary="Verpackung abrufen")
def get_verpackung(
    verpackungs_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_verpackungen
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {"tid": tenant_id, "nr": verpackungs_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Artikelverpackung nicht gefunden.")
    return ArtikelVerpackungOut(**dict(row._mapping))


@router.post("", response_model=ArtikelVerpackungOut, status_code=201, summary="Verpackung anlegen")
def create_verpackung(
    payload: ArtikelVerpackungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.artikel_verpackungen
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {"tid": tenant_id, "nr": payload.verpackungs_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Artikelverpackung {payload.verpackungs_nr} bereits vorhanden.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.artikel_verpackungen
            (id, tenant_id, verpackungs_nr, bezeichnung, stufen,
             stufe1_bezeichnung, stufe1_menge, stufe1_einheit, stufe1_gewicht_kg,
             stufe2_bezeichnung, stufe2_einheiten_pro_stufe2, stufe2_gewicht_kg,
             stufe3_bezeichnung, stufe3_einheiten_pro_stufe3, stufe3_gewicht_kg, aktiv)
        VALUES (:id, :tid, :nr, :bez, :stufen,
                :s1b, :s1m, :s1e, :s1g,
                :s2b, :s2e2, :s2g,
                :s3b, :s3e3, :s3g, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.verpackungs_nr,
        "bez": payload.bezeichnung, "stufen": payload.stufen,
        "s1b": payload.stufe1_bezeichnung, "s1m": payload.stufe1_menge,
        "s1e": payload.stufe1_einheit, "s1g": payload.stufe1_gewicht_kg,
        "s2b": payload.stufe2_bezeichnung, "s2e2": payload.stufe2_einheiten_pro_stufe2,
        "s2g": payload.stufe2_gewicht_kg, "s3b": payload.stufe3_bezeichnung,
        "s3e3": payload.stufe3_einheiten_pro_stufe3, "s3g": payload.stufe3_gewicht_kg,
    })
    db.commit()
    row = db.execute(text(
        "SELECT * FROM domain_shared.artikel_verpackungen WHERE id = :id"
    ), {"id": new_id}).fetchone()
    return ArtikelVerpackungOut(**dict(row._mapping))


@router.put("/{verpackungs_nr}", response_model=ArtikelVerpackungOut, summary="Verpackung aktualisieren")
def update_verpackung(
    verpackungs_nr: str,
    payload: ArtikelVerpackungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    row = db.execute(text("""
        SELECT id FROM domain_shared.artikel_verpackungen
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {"tid": tenant_id, "nr": verpackungs_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Artikelverpackung nicht gefunden.")

    db.execute(text("""
        UPDATE domain_shared.artikel_verpackungen
        SET bezeichnung = :bez, stufen = :stufen,
            stufe1_bezeichnung = :s1b, stufe1_menge = :s1m,
            stufe1_einheit = :s1e, stufe1_gewicht_kg = :s1g,
            stufe2_bezeichnung = :s2b, stufe2_einheiten_pro_stufe2 = :s2e2,
            stufe2_gewicht_kg = :s2g, stufe3_bezeichnung = :s3b,
            stufe3_einheiten_pro_stufe3 = :s3e3, stufe3_gewicht_kg = :s3g
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {
        "tid": tenant_id, "nr": verpackungs_nr, "bez": payload.bezeichnung,
        "stufen": payload.stufen, "s1b": payload.stufe1_bezeichnung,
        "s1m": payload.stufe1_menge, "s1e": payload.stufe1_einheit,
        "s1g": payload.stufe1_gewicht_kg, "s2b": payload.stufe2_bezeichnung,
        "s2e2": payload.stufe2_einheiten_pro_stufe2, "s2g": payload.stufe2_gewicht_kg,
        "s3b": payload.stufe3_bezeichnung, "s3e3": payload.stufe3_einheiten_pro_stufe3,
        "s3g": payload.stufe3_gewicht_kg,
    })
    db.commit()
    updated = db.execute(text("""
        SELECT * FROM domain_shared.artikel_verpackungen
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {"tid": tenant_id, "nr": verpackungs_nr}).fetchone()
    return ArtikelVerpackungOut(**dict(updated._mapping))


@router.delete("/{verpackungs_nr}", summary="Verpackung löschen",
    response_model=None
)
def delete_verpackung(
    verpackungs_nr: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Setzt Löschkennzeichen — keine physische Löschung (Referenz-ERP-konformes Verhalten [AVP])."""
    db.execute(text("""
        UPDATE domain_shared.artikel_verpackungen SET aktiv = false
        WHERE tenant_id = :tid AND verpackungs_nr = :nr
    """), {"tid": tenant_id, "nr": verpackungs_nr})
    db.commit()
    return Response(status_code=204)


@router.get("/{verpackungs_nr}/gesamtgewicht", summary="Gesamtgewicht berechne",
    response_model=None
)
def berechne_gesamtgewicht(
    verpackungs_nr: str,
    anzahl_stufe3: Optional[int] = Query(None),
    anzahl_stufe2: Optional[int] = Query(None),
    anzahl_stufe1: Optional[int] = Query(None),
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Gesamtgewicht einer Verpackungseinheit berechnen."""
    row = db.execute(text("""
        SELECT * FROM domain_shared.artikel_verpackungen
        WHERE tenant_id = :tid AND verpackungs_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": verpackungs_nr}).fetchone()
    if not row:
        raise HTTPException(404, "Artikelverpackung nicht gefunden.")

    v = dict(row._mapping)
    gewicht = Decimal("0")

    if anzahl_stufe3 and v.get("stufe3_gewicht_kg"):
        gewicht += Decimal(str(v["stufe3_gewicht_kg"])) * anzahl_stufe3
    if anzahl_stufe2 and v.get("stufe2_gewicht_kg"):
        gewicht += Decimal(str(v["stufe2_gewicht_kg"])) * anzahl_stufe2
    if anzahl_stufe1 and v.get("stufe1_gewicht_kg"):
        gewicht += Decimal(str(v["stufe1_gewicht_kg"])) * anzahl_stufe1

    return {
        "verpackungs_nr": verpackungs_nr,
        "gesamtgewicht_kg": float(gewicht),
        "stufen": v["stufen"],
    }
