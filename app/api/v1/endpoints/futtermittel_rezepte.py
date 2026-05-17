"""
Futtermittel Rezepturverwaltung

Endpunkte:
  GET/POST  /futtermittel/rezepte                            — Liste / Erstellen
  GET       /futtermittel/rezepte/{id}                       — Detail mit Zutaten
  POST      /futtermittel/rezepte/{id}/ingredients           — Zutat hinzufügen
  PATCH     /futtermittel/rezepte/{id}/ingredients/{iid}     — Anteil ändern
  DELETE    /futtermittel/rezepte/{id}/ingredients/{iid}     — Zutat entfernen
  POST      /futtermittel/rezepte/{id}/copy                  — Kopie mit neuer Version
  POST      /futtermittel/rezepte/{id}/activate              — ENTWURF→AKTIV
  GET       /futtermittel/rezepte/{id}/naehrstoffanalyse     — Berechnetes Nährstoffprofil
  GET       /futtermittel/rezepte/{id}/deklaration           — EU-konforme Inhaltsangabe
  GET       /futtermittel/rezepte/{id}/etikett               — EU 2017/2279 Etikettdaten

Tabellen (schema: domain_futtermittel):
  feed_recipes         — Rezeptur-Stamm
  recipe_ingredients   — Zutaten mit Anteilen
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/futtermittel/rezepte", tags=["futtermittel", "rezepte"])

_DDL = """
CREATE SCHEMA IF NOT EXISTS domain_futtermittel;

CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_recipes (
    id                TEXT PRIMARY KEY,
    recipe_code       TEXT NOT NULL,
    name              TEXT NOT NULL,
    tierart           TEXT NOT NULL DEFAULT 'SONSTIGE',
    produktionsphase  TEXT NOT NULL DEFAULT 'SONSTIGE',
    status            TEXT NOT NULL DEFAULT 'ENTWURF',
    version           INT NOT NULL DEFAULT 1,
    erstellt_am       TIMESTAMPTZ DEFAULT NOW(),
    erstellt_von      TEXT,
    tenant_id         TEXT NOT NULL,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domain_futtermittel.recipe_ingredients (
    id             TEXT PRIMARY KEY,
    recipe_id      TEXT NOT NULL,
    material_id    TEXT NOT NULL,
    anteil_percent NUMERIC(8,4) NOT NULL,
    min_anteil     NUMERIC(8,4),
    max_anteil     NUMERIC(8,4),
    sort_order     INT NOT NULL DEFAULT 0,
    tenant_id      TEXT NOT NULL
);
"""


def _ensure_tables(db: Session) -> None:
    for stmt in _DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            db.execute(text(stmt))
    db.commit()


def _row_to_dict(row) -> dict:
    return dict(row._mapping)


TIERARTEN = {"RIND", "SCHWEIN", "GEFLUEGEL", "PFERD", "SONSTIGE"}
PHASEN = {"AUFZUCHT", "MAST", "LAKTATION", "SONSTIGE"}
STATUSWERTE = {"ENTWURF", "AKTIV", "ARCHIV"}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RezeptIn(BaseModel):
    recipe_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    tierart: str = "SONSTIGE"
    produktionsphase: str = "SONSTIGE"
    erstellt_von: Optional[str] = None


class IngredientIn(BaseModel):
    material_id: str = Field(..., min_length=1)
    anteil_percent: float = Field(..., gt=0, le=100)
    min_anteil: Optional[float] = None
    max_anteil: Optional[float] = None
    sort_order: int = 0


class IngredientPatch(BaseModel):
    anteil_percent: Optional[float] = Field(None, gt=0, le=100)
    min_anteil: Optional[float] = None
    max_anteil: Optional[float] = None
    sort_order: Optional[int] = None


# ---------------------------------------------------------------------------
# Helper: fetch recipe with auth
# ---------------------------------------------------------------------------

def _get_recipe_or_404(db: Session, rezept_id: str, tenant_id: str) -> dict:
    row = db.execute(text("""
        SELECT * FROM domain_futtermittel.feed_recipes
        WHERE id = :id AND tenant_id = :tenant_id
    """), {"id": rezept_id, "tenant_id": tenant_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Rezept '{rezept_id}' nicht gefunden")
    return _row_to_dict(row)


def _get_ingredients(db: Session, rezept_id: str, tenant_id: str) -> List[dict]:
    rows = db.execute(text("""
        SELECT ri.*, frm.name AS material_name, frm.material_code
        FROM domain_futtermittel.recipe_ingredients ri
        LEFT JOIN domain_futtermittel.feed_raw_materials frm
            ON frm.id = ri.material_id AND frm.tenant_id = ri.tenant_id
        WHERE ri.recipe_id = :recipe_id AND ri.tenant_id = :tenant_id
        ORDER BY ri.sort_order, ri.anteil_percent DESC
    """), {"recipe_id": rezept_id, "tenant_id": tenant_id}).fetchall()
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("")
async def list_rezepte(
    tierart: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        _ensure_tables(db)
        sql = text("""
            SELECT id, recipe_code, name, tierart, produktionsphase,
                   status, version, erstellt_am, erstellt_von, updated_at
            FROM domain_futtermittel.feed_recipes
            WHERE tenant_id = :tenant_id
              AND (:tierart IS NULL OR tierart = :tierart)
              AND (:status IS NULL OR status = :status)
            ORDER BY name
        """)
        rows = db.execute(sql, {"tenant_id": tenant_id, "tierart": tierart, "status": status}).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.exception("list_rezepte failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("", status_code=201)
async def create_rezept(
    payload: RezeptIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if payload.tierart not in TIERARTEN:
        raise HTTPException(status_code=422, detail=f"Ungültige Tierart. Erlaubt: {sorted(TIERARTEN)}")
    if payload.produktionsphase not in PHASEN:
        raise HTTPException(status_code=422, detail=f"Ungültige Produktionsphase. Erlaubt: {sorted(PHASEN)}")
    try:
        _ensure_tables(db)
        new_id = uuid7()
        sql = text("""
            INSERT INTO domain_futtermittel.feed_recipes
                (id, recipe_code, name, tierart, produktionsphase, status, version, erstellt_von, tenant_id)
            VALUES
                (:id, :recipe_code, :name, :tierart, :produktionsphase, 'ENTWURF', 1, :erstellt_von, :tenant_id)
            RETURNING *
        """)
        row = db.execute(sql, {
            "id": new_id,
            "tenant_id": tenant_id,
            **payload.model_dump(),
        }).fetchone()
        db.commit()
        return _row_to_dict(row)
    except Exception as exc:
        db.rollback()
        logger.exception("create_rezept failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/{rezept_id}")
async def get_rezept(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        _ensure_tables(db)
        rezept = _get_recipe_or_404(db, rezept_id, tenant_id)
        rezept["zutaten"] = _get_ingredients(db, rezept_id, tenant_id)
        return rezept
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("get_rezept failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("/{rezept_id}/ingredients", status_code=201)
async def add_ingredient(
    rezept_id: str,
    payload: IngredientIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        _ensure_tables(db)
        _get_recipe_or_404(db, rezept_id, tenant_id)
        new_id = uuid7()
        sql = text("""
            INSERT INTO domain_futtermittel.recipe_ingredients
                (id, recipe_id, material_id, anteil_percent, min_anteil, max_anteil, sort_order, tenant_id)
            VALUES
                (:id, :recipe_id, :material_id, :anteil_percent, :min_anteil, :max_anteil, :sort_order, :tenant_id)
            RETURNING *
        """)
        row = db.execute(sql, {
            "id": new_id,
            "recipe_id": rezept_id,
            "tenant_id": tenant_id,
            **payload.model_dump(),
        }).fetchone()
        db.commit()
        return _row_to_dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("add_ingredient failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.patch("/{rezept_id}/ingredients/{ingredient_id}")
async def update_ingredient(
    rezept_id: str,
    ingredient_id: str,
    payload: IngredientPatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren angegeben")
    try:
        _ensure_tables(db)
        set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
        sql = text(f"""
            UPDATE domain_futtermittel.recipe_ingredients
            SET {set_clauses}
            WHERE id = :id AND recipe_id = :recipe_id AND tenant_id = :tenant_id
            RETURNING *
        """)
        row = db.execute(sql, {"id": ingredient_id, "recipe_id": rezept_id, "tenant_id": tenant_id, **updates}).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("update_ingredient failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")
    if not row:
        raise HTTPException(status_code=404, detail=f"Zutat '{ingredient_id}' nicht gefunden")
    return _row_to_dict(row)


@router.delete("/{rezept_id}/ingredients/{ingredient_id}", status_code=204)
async def delete_ingredient(
    rezept_id: str,
    ingredient_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        _ensure_tables(db)
        db.execute(text("""
            DELETE FROM domain_futtermittel.recipe_ingredients
            WHERE id = :id AND recipe_id = :recipe_id AND tenant_id = :tenant_id
        """), {"id": ingredient_id, "recipe_id": rezept_id, "tenant_id": tenant_id})
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("delete_ingredient failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("/{rezept_id}/copy", status_code=201)
async def copy_rezept(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Kopie des Rezepts mit erhöhter Version erstellen."""
    try:
        _ensure_tables(db)
        orig = _get_recipe_or_404(db, rezept_id, tenant_id)
        new_id = uuid7()
        new_version = (orig.get("version") or 1) + 1
        sql = text("""
            INSERT INTO domain_futtermittel.feed_recipes
                (id, recipe_code, name, tierart, produktionsphase, status, version, erstellt_von, tenant_id)
            VALUES
                (:id, :recipe_code, :name, :tierart, :produktionsphase, 'ENTWURF', :version, :erstellt_von, :tenant_id)
            RETURNING *
        """)
        new_rezept = db.execute(sql, {
            "id": new_id,
            "recipe_code": orig["recipe_code"] + f"-v{new_version}",
            "name": orig["name"] + f" (v{new_version})",
            "tierart": orig["tierart"],
            "produktionsphase": orig["produktionsphase"],
            "version": new_version,
            "erstellt_von": orig.get("erstellt_von"),
            "tenant_id": tenant_id,
        }).fetchone()

        # Copy ingredients
        orig_ingredients = _get_ingredients(db, rezept_id, tenant_id)
        for ing in orig_ingredients:
            db.execute(text("""
                INSERT INTO domain_futtermittel.recipe_ingredients
                    (id, recipe_id, material_id, anteil_percent, min_anteil, max_anteil, sort_order, tenant_id)
                VALUES
                    (:id, :recipe_id, :material_id, :anteil_percent, :min_anteil, :max_anteil, :sort_order, :tenant_id)
            """), {
                "id": uuid7(),
                "recipe_id": new_id,
                "material_id": ing["material_id"],
                "anteil_percent": ing["anteil_percent"],
                "min_anteil": ing.get("min_anteil"),
                "max_anteil": ing.get("max_anteil"),
                "sort_order": ing.get("sort_order", 0),
                "tenant_id": tenant_id,
            })

        db.commit()
        result = _row_to_dict(new_rezept)
        result["zutaten"] = _get_ingredients(db, new_id, tenant_id)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("copy_rezept failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("/{rezept_id}/activate")
async def activate_rezept(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Rezept von ENTWURF auf AKTIV setzen. Validiert: Anteile müssen 100% ergeben."""
    try:
        _ensure_tables(db)
        rezept = _get_recipe_or_404(db, rezept_id, tenant_id)
        if rezept["status"] != "ENTWURF":
            raise HTTPException(status_code=409, detail=f"Rezept ist bereits '{rezept['status']}'. Nur ENTWURF kann aktiviert werden.")

        # Validate ingredient sum
        summe_row = db.execute(text("""
            SELECT COALESCE(SUM(anteil_percent), 0) AS summe
            FROM domain_futtermittel.recipe_ingredients
            WHERE recipe_id = :recipe_id AND tenant_id = :tenant_id
        """), {"recipe_id": rezept_id, "tenant_id": tenant_id}).fetchone()
        summe = float(summe_row.summe)
        if abs(summe - 100.0) > 0.01:
            raise HTTPException(
                status_code=422,
                detail=f"Anteile müssen 100% ergeben, aktuell: {summe:.4f}%"
            )

        row = db.execute(text("""
            UPDATE domain_futtermittel.feed_recipes
            SET status = 'AKTIV', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
            RETURNING *
        """), {"id": rezept_id, "tenant_id": tenant_id}).fetchone()
        db.commit()
        return _row_to_dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("activate_rezept failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/{rezept_id}/naehrstoffanalyse")
async def naehrstoffanalyse(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Berechnetes Nährstoffprofil: Summe(anteil/100 * material.naehrstoff) je Nährstoff.
    Ergebnisse sind auf frische Substanz-Basis; DM-korrigierte Werte werden zusätzlich ausgegeben."""
    try:
        _ensure_tables(db)
        _get_recipe_or_404(db, rezept_id, tenant_id)

        sql = text("""
            SELECT
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.energie_me_mj, 0))    AS energie_me_mj,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.rohprotein_g, 0))     AS rohprotein_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.rohfett_g, 0))        AS rohfett_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.rohfaser_g, 0))       AS rohfaser_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.rohasche_g, 0))       AS rohasche_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.lysin_g, 0))          AS lysin_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.methionin_g, 0))      AS methionin_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.calcium_g, 0))        AS calcium_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.phosphor_g, 0))       AS phosphor_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.natrium_g, 0))        AS natrium_g,
                SUM(ri.anteil_percent / 100.0 * COALESCE(frm.dry_matter_percent, 88.0)) AS dry_matter_percent
            FROM domain_futtermittel.recipe_ingredients ri
            JOIN domain_futtermittel.feed_raw_materials frm
                ON frm.id = ri.material_id AND frm.tenant_id = ri.tenant_id
            WHERE ri.recipe_id = :recipe_id AND ri.tenant_id = :tenant_id
        """)
        row = db.execute(sql, {"recipe_id": rezept_id, "tenant_id": tenant_id}).fetchone()
        result = _row_to_dict(row)

        # DM-korrigierte Werte (je kg TM)
        dm = float(result.get("dry_matter_percent") or 88.0) / 100.0
        dm_korrigiert: Dict[str, Any] = {}
        for key, val in result.items():
            if key != "dry_matter_percent" and val is not None:
                dm_korrigiert[f"{key}_dm"] = round(float(val) / dm, 4) if dm > 0 else None
        result.update(dm_korrigiert)

        # Round floats
        for k in list(result.keys()):
            if result[k] is not None:
                try:
                    result[k] = round(float(result[k]), 4)
                except (TypeError, ValueError):
                    pass

        return {"rezept_id": rezept_id, "naehrstoffe": result, "basis": "frische_substanz"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("naehrstoffanalyse failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/{rezept_id}/deklaration")
async def deklaration(
    rezept_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """EU-konforme Inhaltsangabe: Zutaten absteigend nach Anteil,
    analytische Bestandteile (RP, RFe, RFA, RA, ME)."""
    try:
        _ensure_tables(db)
        rezept = _get_recipe_or_404(db, rezept_id, tenant_id)

        ingredients = db.execute(text("""
            SELECT ri.anteil_percent,
                   COALESCE(frm.name, ri.material_id) AS material_name,
                   frm.rohprotein_g, frm.rohfett_g, frm.rohfaser_g, frm.rohasche_g, frm.energie_me_mj,
                   frm.dry_matter_percent
            FROM domain_futtermittel.recipe_ingredients ri
            LEFT JOIN domain_futtermittel.feed_raw_materials frm
                ON frm.id = ri.material_id AND frm.tenant_id = ri.tenant_id
            WHERE ri.recipe_id = :recipe_id AND ri.tenant_id = :tenant_id
            ORDER BY ri.anteil_percent DESC
        """), {"recipe_id": rezept_id, "tenant_id": tenant_id}).fetchall()

        zutaten_liste = [
            f"{r.material_name} {round(float(r.anteil_percent), 1)}%"
            for r in ingredients
        ]

        # Aggregate analytische Bestandteile
        rp = rfe = rfa = ra = me = 0.0
        for r in ingredients:
            a = float(r.anteil_percent) / 100.0
            rp  += a * float(r.rohprotein_g  or 0)
            rfe += a * float(r.rohfett_g     or 0)
            rfa += a * float(r.rohfaser_g    or 0)
            ra  += a * float(r.rohasche_g    or 0)
            me  += a * float(r.energie_me_mj or 0)

        return {
            "rezept_id": rezept_id,
            "name": rezept["name"],
            "tierart": rezept["tierart"],
            "zutaten_liste": zutaten_liste,
            "analytische_bestandteile": {
                "rohprotein_percent": round(rp / 10, 2),    # g/kg → %
                "rohfett_percent":    round(rfe / 10, 2),
                "rohfaser_percent":   round(rfa / 10, 2),
                "rohasche_percent":   round(ra / 10, 2),
                "energie_me_mj_kg":   round(me, 3),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("deklaration failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/{rezept_id}/etikett")
async def etikett(
    rezept_id: str,
    hersteller_adresse: Optional[str] = Query(None),
    eu_registrierungsnummer: Optional[str] = Query(None),
    charge_referenz: Optional[str] = Query(None),
    mindesthaltbarkeit_tage: Optional[int] = Query(90),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Strukturierte Etikettdaten gem. EU 2017/2279."""
    try:
        _ensure_tables(db)
        rezept = _get_recipe_or_404(db, rezept_id, tenant_id)

        ingredients = db.execute(text("""
            SELECT ri.anteil_percent,
                   COALESCE(frm.name, ri.material_id) AS material_name,
                   frm.rohprotein_g, frm.rohfett_g, frm.rohfaser_g, frm.rohasche_g
            FROM domain_futtermittel.recipe_ingredients ri
            LEFT JOIN domain_futtermittel.feed_raw_materials frm
                ON frm.id = ri.material_id AND frm.tenant_id = ri.tenant_id
            WHERE ri.recipe_id = :recipe_id AND ri.tenant_id = :tenant_id
            ORDER BY ri.anteil_percent DESC
        """), {"recipe_id": rezept_id, "tenant_id": tenant_id}).fetchall()

        zutaten_liste = [
            f"{r.material_name} {round(float(r.anteil_percent), 1)}%"
            for r in ingredients
        ]

        rp = rfe = rfa = ra = 0.0
        for r in ingredients:
            a = float(r.anteil_percent) / 100.0
            rp  += a * float(r.rohprotein_g or 0)
            rfe += a * float(r.rohfett_g    or 0)
            rfa += a * float(r.rohfaser_g   or 0)
            ra  += a * float(r.rohasche_g   or 0)

        return {
            "produktname": rezept["name"],
            "tierart": rezept["tierart"],
            "hersteller_adresse": hersteller_adresse or "",
            "mindesthaltbarkeit_tage": mindesthaltbarkeit_tage,
            "zutaten_liste": zutaten_liste,
            "analytische_bestandteile": {
                "rp_percent":  round(rp  / 10, 2),
                "rfe_percent": round(rfe / 10, 2),
                "rfa_percent": round(rfa / 10, 2),
                "ra_percent":  round(ra  / 10, 2),
            },
            "zusatzstoffe": [],
            "eu_registrierungsnummer": eu_registrierungsnummer or "",
            "charge_referenz": charge_referenz or "",
            "rechtsgrundlage": "EU 2017/2279",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("etikett failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")
