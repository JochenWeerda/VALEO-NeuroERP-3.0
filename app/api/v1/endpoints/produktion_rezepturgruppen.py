"""Rezepturgruppen und Produktions-Schnellerfassung für Mischfutter.

Fachlicher Hintergrund (Referenz-ERP Wissensbasis, Domain 11):
  Rezepturgruppen ordnen Rezepturen nach Tierart und Nutzungsrichtung.
  Beispiele: Rind-Milch, Schwein-Mast, Geflügel-Aufzucht.

  Die Produktions-Schnellerfassung (SPA 962) ermöglicht die schnelle
  Buchung von Standardproduktionen ohne den vollständigen Produktionsmasken-
  Workflow. Ideal für täglich wiederkehrende Standardmischungen.
  ACHTUNG: Schnellerfassung hat nicht den vollen Leistungsumfang des
  Standard-Produktionsmoduls (PROB/PROE).
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.core.database import get_db
from app.core.dependencies import get_tenant_id
from app.core.uuid7 import uuid7

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/produktion/mischfutter", tags=["Produktion - Mischfutter"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class RezepturGruppeCreate(BaseModel):
    gruppe_nr: str = Field(..., max_length=20)
    bezeichnung: str
    tierart: Optional[str] = None
    nutzungsrichtung: Optional[str] = None


class RezepturGruppeOut(BaseModel):
    id: str
    gruppe_nr: str
    bezeichnung: str
    tierart: Optional[str]
    nutzungsrichtung: Optional[str]
    aktiv: bool
    created_at: datetime


class SchnellerfassungCreate(BaseModel):
    bezeichnung: str
    rezept_id: Optional[str] = None
    rezept_name: Optional[str] = None
    standard_menge_t: Optional[Decimal] = None
    ziel_lager_id: Optional[str] = None
    abteilung: Optional[str] = None


class SchnellerfassungOut(BaseModel):
    id: str
    bezeichnung: str
    rezept_id: Optional[str]
    rezept_name: Optional[str]
    standard_menge_t: Optional[Decimal]
    ziel_lager_id: Optional[str]
    abteilung: Optional[str]
    letzter_einsatz: Optional[datetime]
    anzahl_auftraege: int
    aktiv: bool
    created_at: datetime


class SchnellerfassungBuchenPayload(BaseModel):
    menge_t: Decimal = Field(..., gt=0)
    chargen_id: Optional[str] = None
    bemerkung: Optional[str] = None


# ── Rezepturgruppen ───────────────────────────────────────────────────────────

@router.get("/rezepturgruppen", response_model=list[RezepturGruppeOut], summary="Rezepturgruppen auflisten")
def list_rezepturgruppen(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    rows = db.execute(text("""
        SELECT * FROM domain_shared.futtermittel_rezepturgruppen
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY gruppe_nr
    """), {"tid": tenant_id}).fetchall()
    return [RezepturGruppeOut(**dict(r._mapping)) for r in rows]


@router.post("/rezepturgruppen", response_model=RezepturGruppeOut, status_code=201, summary="Rezepturgruppe anlegen")
def create_rezepturgruppe(
    payload: RezepturGruppeCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    existing = db.execute(text("""
        SELECT id FROM domain_shared.futtermittel_rezepturgruppen
        WHERE tenant_id = :tid AND gruppe_nr = :nr AND aktiv = true
    """), {"tid": tenant_id, "nr": payload.gruppe_nr}).fetchone()
    if existing:
        raise HTTPException(409, f"Rezepturgruppe {payload.gruppe_nr} existiert bereits.")

    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_rezepturgruppen
            (id, tenant_id, gruppe_nr, bezeichnung, tierart, nutzungsrichtung, aktiv)
        VALUES (:id, :tid, :nr, :bez, :tierart, :nutz, true)
    """), {
        "id": new_id, "tid": tenant_id, "nr": payload.gruppe_nr,
        "bez": payload.bezeichnung, "tierart": payload.tierart,
        "nutz": payload.nutzungsrichtung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.futtermittel_rezepturgruppen WHERE id = :id
    """), {"id": new_id}).fetchone()
    return RezepturGruppeOut(**dict(row._mapping))


@router.delete("/rezepturgruppen/{gruppe_id}", summary="Rezepturgruppe löschen",
    response_model=CompatFlexOut
)
def delete_rezepturgruppe(
    gruppe_id: str,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    db.execute(text("""
        UPDATE domain_shared.futtermittel_rezepturgruppen
        SET aktiv = false WHERE id = :id AND tenant_id = :tid
    """), {"id": gruppe_id, "tid": tenant_id})
    db.commit()
    return Response(status_code=204)


# ── Schnellerfassung ──────────────────────────────────────────────────────────

@router.get("/schnellerfassung", response_model=list[SchnellerfassungOut], summary="Schnellerfassung auflisten")
def list_schnellerfassung(
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Alle Schnellerfassungsvorlagen — für täglich wiederkehrende Produktionen."""
    rows = db.execute(text("""
        SELECT * FROM domain_shared.futtermittel_schnellerfassung
        WHERE tenant_id = :tid AND aktiv = true
        ORDER BY anzahl_auftraege DESC, bezeichnung
    """), {"tid": tenant_id}).fetchall()
    return [SchnellerfassungOut(**dict(r._mapping)) for r in rows]


@router.post("/schnellerfassung", response_model=SchnellerfassungOut, status_code=201, summary="Schnellerfassung anlegen")
def create_schnellerfassung(
    payload: SchnellerfassungCreate,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Neue Schnellerfassungsvorlage anlegen."""
    new_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_schnellerfassung
            (id, tenant_id, bezeichnung, rezept_id, rezept_name,
             standard_menge_t, ziel_lager_id, abteilung, anzahl_auftraege, aktiv)
        VALUES (:id, :tid, :bez, :rezept_id, :rezept_name,
                :menge, :lager, :abt, 0, true)
    """), {
        "id": new_id, "tid": tenant_id, "bez": payload.bezeichnung,
        "rezept_id": payload.rezept_id, "rezept_name": payload.rezept_name,
        "menge": payload.standard_menge_t, "lager": payload.ziel_lager_id,
        "abt": payload.abteilung,
    })
    db.commit()
    row = db.execute(text("""
        SELECT * FROM domain_shared.futtermittel_schnellerfassung WHERE id = :id
    """), {"id": new_id}).fetchone()
    return SchnellerfassungOut(**dict(row._mapping))


@router.post("/schnellerfassung/{vorlage_id}/buchen", summary="Schnellerfassung buche",
    response_model=None
)
def buche_schnellerfassung(
    vorlage_id: str,
    payload: SchnellerfassungBuchenPayload,
    db=Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Produktionsauftrag aus Schnellerfassungsvorlage erzeugen.

    Fachlich: Schnellerfassung erzeugt einen vereinfachten Produktionsauftrag
    ohne vollständigen Workflow. Für komplexe Produktionen PROB/PROE verwenden.
    """
    vorlage = db.execute(text("""
        SELECT * FROM domain_shared.futtermittel_schnellerfassung
        WHERE id = :id AND tenant_id = :tid AND aktiv = true
    """), {"id": vorlage_id, "tid": tenant_id}).fetchone()
    if not vorlage:
        raise HTTPException(404, "Schnellerfassungsvorlage nicht gefunden.")

    v = dict(vorlage._mapping)
    chargen_id = payload.chargen_id or f"CH-SCHNELL-{vorlage_id[:6].upper()}"

    # Produktionsauftrag anlegen
    auftrag_id = uuid7()
    db.execute(text("""
        INSERT INTO domain_shared.futtermittel_produktionsauftraege
            (id, tenant_id, chargen_id, rezept_id, rezept_name,
             menge_t, status, erstellt_von, bemerkung)
        VALUES (:id, :tid, :chargen_id, :rezept_id, :rezept_name,
                :menge, 'freigegeben', 'Schnellerfassung', :bem)
    """), {
        "id": auftrag_id, "tid": tenant_id,
        "chargen_id": chargen_id,
        "rezept_id": v["rezept_id"],
        "rezept_name": v["rezept_name"] or "Schnellerfassung",
        "menge": payload.menge_t,
        "bem": payload.bemerkung or f"Via Schnellerfassung: {v['bezeichnung']}",
    })

    # Vorlage-Statistik aktualisieren
    db.execute(text("""
        UPDATE domain_shared.futtermittel_schnellerfassung
        SET anzahl_auftraege = anzahl_auftraege + 1,
            letzter_einsatz = now()
        WHERE id = :id
    """), {"id": vorlage_id})
    db.commit()

    return {
        "auftrag_id": auftrag_id,
        "chargen_id": chargen_id,
        "rezept_name": v["rezept_name"],
        "menge_t": float(payload.menge_t),
        "status": "freigegeben",
        "hinweis": "Schnellerfassung: vereinfachter Auftrag ohne vollständigen Workflow.",
    }
