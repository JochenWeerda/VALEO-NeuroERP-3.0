"""
Futtermittel Rohwaren-Stamm mit NÃ¤hrstoffprofil

Endpunkte:
  GET/POST  /futtermittel/rohwaren                   â€” Liste / Erstellen
  GET/PATCH /futtermittel/rohwaren/{id}               â€” Detail / Update
  GET       /futtermittel/rohwaren/{id}/analysen      â€” Analyse-Historie
  POST      /futtermittel/rohwaren/{id}/analysen      â€” Neue Laboranalyse
  GET       /futtermittel/rohwaren/vergleich          â€” NÃ¤hrstoffvergleich mehrerer Rohwaren

Tabellen (schema: domain_futtermittel):
  feed_raw_materials       â€” Rohwaren-Stamm mit NÃ¤hrstoffprofil
  raw_material_analyses    â€” Laboranalysen (JSONB werte)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.futtermittel_rohwaren_schemas import FuttermittelRohwarenOut


router = APIRouter(prefix="/futtermittel/rohwaren", tags=["futtermittel", "rohwaren"])

_DDL = """
CREATE SCHEMA IF NOT EXISTS domain_futtermittel;

CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_raw_materials (
    id               TEXT PRIMARY KEY,
    material_code    TEXT NOT NULL,
    name             TEXT NOT NULL,
    kategorie        TEXT NOT NULL DEFAULT 'SONSTIGE',
    dry_matter_percent NUMERIC(6,3),
    energie_me_mj    NUMERIC(8,4),
    rohprotein_g     NUMERIC(8,4),
    rohfett_g        NUMERIC(8,4),
    rohfaser_g       NUMERIC(8,4),
    rohasche_g       NUMERIC(8,4),
    lysin_g          NUMERIC(8,4),
    methionin_g      NUMERIC(8,4),
    calcium_g        NUMERIC(8,4),
    phosphor_g       NUMERIC(8,4),
    natrium_g        NUMERIC(8,4),
    gueltig_ab       DATE,
    gueltig_bis      DATE,
    tenant_id        TEXT NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domain_futtermittel.raw_material_analyses (
    id              TEXT PRIMARY KEY,
    material_id     TEXT NOT NULL,
    analyse_datum   DATE,
    labor_ref       TEXT,
    analysiert_von  TEXT,
    werte           JSONB DEFAULT '{}'::JSONB,
    tenant_id       TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
"""


def _ensure_tables(db: Session) -> None:
    """Create schema/tables if they don't exist yet."""
    for stmt in _DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            db.execute(text(stmt))
    db.commit()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

KATEGORIEN = {"GETREIDE", "LEGUMINOSEN", "OELKUCHEN", "MINERAL", "FETT", "SONSTIGE"}


class RohwareIn(BaseModel):
    material_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    kategorie: str = "SONSTIGE"
    dry_matter_percent: Optional[float] = None
    energie_me_mj: Optional[float] = None
    rohprotein_g: Optional[float] = None
    rohfett_g: Optional[float] = None
    rohfaser_g: Optional[float] = None
    rohasche_g: Optional[float] = None
    lysin_g: Optional[float] = None
    methionin_g: Optional[float] = None
    calcium_g: Optional[float] = None
    phosphor_g: Optional[float] = None
    natrium_g: Optional[float] = None
    gueltig_ab: Optional[str] = None
    gueltig_bis: Optional[str] = None


class RohwarePatch(BaseModel):
    name: Optional[str] = None
    kategorie: Optional[str] = None
    dry_matter_percent: Optional[float] = None
    energie_me_mj: Optional[float] = None
    rohprotein_g: Optional[float] = None
    rohfett_g: Optional[float] = None
    rohfaser_g: Optional[float] = None
    rohasche_g: Optional[float] = None
    lysin_g: Optional[float] = None
    methionin_g: Optional[float] = None
    calcium_g: Optional[float] = None
    phosphor_g: Optional[float] = None
    natrium_g: Optional[float] = None
    gueltig_ab: Optional[str] = None
    gueltig_bis: Optional[str] = None


class AnalyseIn(BaseModel):
    analyse_datum: Optional[str] = None
    labor_ref: Optional[str] = None
    analysiert_von: Optional[str] = None
    werte: Dict[str, Any] = Field(default_factory=dict)


def _row_to_dict(row) -> dict:
    return dict(row._mapping)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[FuttermittelRohwarenOut], summary="Rohwaren auflisten")
async def list_rohwaren(
    kategorie: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Rohwaren-Stammdaten."""
    try:
        _ensure_tables(db)
        sql = text("""
            SELECT id, material_code, name, kategorie,
                   dry_matter_percent, energie_me_mj,
                   rohprotein_g, rohfett_g, rohfaser_g, rohasche_g,
                   lysin_g, methionin_g, calcium_g, phosphor_g, natrium_g,
                   gueltig_ab, gueltig_bis, created_at, updated_at
            FROM domain_futtermittel.feed_raw_materials
            WHERE tenant_id = :tenant_id
              AND (:kategorie IS NULL OR kategorie = :kategorie)
              AND (:search IS NULL OR name ILIKE '%' || :search || '%'
                   OR material_code ILIKE '%' || :search || '%')
            ORDER BY name
        """)
        rows = db.execute(sql, {"tenant_id": tenant_id, "kategorie": kategorie, "search": search}).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.exception("list_rohwaren failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("", status_code=201, summary="Rohware anlegen",
    response_model=FuttermittelRohwarenOut
)
async def create_rohware(
    payload: RohwareIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Rohware anlegen."""
    if payload.kategorie not in KATEGORIEN:
        raise HTTPException(status_code=422, detail=f"UngÃ¼ltige Kategorie. Erlaubt: {sorted(KATEGORIEN)}")
    try:
        _ensure_tables(db)
        new_id = uuid7()
        sql = text("""
            INSERT INTO domain_futtermittel.feed_raw_materials
                (id, material_code, name, kategorie,
                 dry_matter_percent, energie_me_mj,
                 rohprotein_g, rohfett_g, rohfaser_g, rohasche_g,
                 lysin_g, methionin_g, calcium_g, phosphor_g, natrium_g,
                 gueltig_ab, gueltig_bis, tenant_id)
            VALUES
                (:id, :material_code, :name, :kategorie,
                 :dry_matter_percent, :energie_me_mj,
                 :rohprotein_g, :rohfett_g, :rohfaser_g, :rohasche_g,
                 :lysin_g, :methionin_g, :calcium_g, :phosphor_g, :natrium_g,
                 :gueltig_ab, :gueltig_bis, :tenant_id)
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
        logger.exception("create_rohware failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/vergleich", summary="Rohwaren vergleich",
    response_model=FuttermittelRohwarenOut
)
async def vergleich_rohwaren(
    ids: str = Query(..., description="Komma-getrennte IDs"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """NÃ¤hrstoffvergleich mehrerer Rohwaren nebeneinander."""
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if not id_list:
        raise HTTPException(status_code=422, detail="Parameter 'ids' darf nicht leer sein")
    try:
        _ensure_tables(db)
        sql = text("""
            SELECT id, material_code, name, kategorie,
                   dry_matter_percent, energie_me_mj,
                   rohprotein_g, rohfett_g, rohfaser_g, rohasche_g,
                   lysin_g, methionin_g, calcium_g, phosphor_g, natrium_g
            FROM domain_futtermittel.feed_raw_materials
            WHERE tenant_id = :tenant_id
              AND id = ANY(:ids)
            ORDER BY name
        """)
        rows = db.execute(sql, {"tenant_id": tenant_id, "ids": id_list}).fetchall()
        items = [_row_to_dict(r) for r in rows]

        naehrstoffe = [
            "dry_matter_percent", "energie_me_mj",
            "rohprotein_g", "rohfett_g", "rohfaser_g", "rohasche_g",
            "lysin_g", "methionin_g", "calcium_g", "phosphor_g", "natrium_g",
        ]
        tabelle: Dict[str, Dict[str, Any]] = {}
        for ns in naehrstoffe:
            tabelle[ns] = {item["name"]: item.get(ns) for item in items}

        return {
            "rohwaren": [{k: v for k, v in item.items() if k in ("id", "name", "material_code", "kategorie")} for item in items],
            "naehrstoffe_tabelle": tabelle,
        }
    except Exception as exc:
        logger.exception("vergleich_rohwaren failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.get("/{rohware_id}", summary="Rohware abrufen",
    response_model=FuttermittelRohwarenOut
)
async def get_rohware(
    rohware_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Rohware-Detail inkl. NÃ¤hrstoffprofil."""
    try:
        _ensure_tables(db)
        sql = text("""
            SELECT * FROM domain_futtermittel.feed_raw_materials
            WHERE id = :id AND tenant_id = :tenant_id
        """)
        row = db.execute(sql, {"id": rohware_id, "tenant_id": tenant_id}).fetchone()
    except Exception as exc:
        logger.exception("get_rohware failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")
    if not row:
        raise HTTPException(status_code=404, detail=f"Rohware '{rohware_id}' nicht gefunden")
    return _row_to_dict(row)


@router.patch("/{rohware_id}", summary="Rohware aktualisieren",
    response_model=FuttermittelRohwarenOut
)
async def update_rohware(
    rohware_id: str,
    payload: RohwarePatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Rohware-Stamm aktualisieren."""
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren angegeben")
    try:
        _ensure_tables(db)
        set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
        # nosec S608 â€” reviewed-safe: column names code-controlled, values parameterized
        sql = text(f"""
            UPDATE domain_futtermittel.feed_raw_materials
            SET {set_clauses}, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
            RETURNING *
        """)
        row = db.execute(sql, {"id": rohware_id, "tenant_id": tenant_id, **updates}).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("update_rohware failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")
    if not row:
        raise HTTPException(status_code=404, detail=f"Rohware '{rohware_id}' nicht gefunden")
    return _row_to_dict(row)


@router.get("/{rohware_id}/analysen", summary="Analysen auflisten",
    response_model=list[FuttermittelRohwarenOut]
)
async def list_analysen(
    rohware_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Laboranalysen fÃ¼r eine Rohware."""
    try:
        _ensure_tables(db)
        sql = text("""
            SELECT id, material_id, analyse_datum, labor_ref, analysiert_von, werte, created_at
            FROM domain_futtermittel.raw_material_analyses
            WHERE material_id = :material_id AND tenant_id = :tenant_id
            ORDER BY analyse_datum DESC, created_at DESC
        """)
        rows = db.execute(sql, {"material_id": rohware_id, "tenant_id": tenant_id}).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.exception("list_analysen failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")


@router.post("/{rohware_id}/analysen", status_code=201, summary="Analyse anlegen",
    response_model=FuttermittelRohwarenOut
)
async def create_analyse(
    rohware_id: str,
    payload: AnalyseIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Laboranalyse fÃ¼r eine Rohware erfassen."""
    try:
        _ensure_tables(db)
        # Verify material exists
        check = db.execute(text("""
            SELECT id FROM domain_futtermittel.feed_raw_materials
            WHERE id = :id AND tenant_id = :tenant_id
        """), {"id": rohware_id, "tenant_id": tenant_id}).fetchone()
        if not check:
            raise HTTPException(status_code=404, detail=f"Rohware '{rohware_id}' nicht gefunden")

        new_id = uuid7()
        sql = text("""
            INSERT INTO domain_futtermittel.raw_material_analyses
                (id, material_id, analyse_datum, labor_ref, analysiert_von, werte, tenant_id)
            VALUES
                (:id, :material_id, :analyse_datum, :labor_ref, :analysiert_von, :werte::JSONB, :tenant_id)
            RETURNING *
        """)
        row = db.execute(sql, {
            "id": new_id,
            "material_id": rohware_id,
            "analyse_datum": payload.analyse_datum,
            "labor_ref": payload.labor_ref,
            "analysiert_von": payload.analysiert_von,
            "werte": json.dumps(payload.werte),
            "tenant_id": tenant_id,
        }).fetchone()
        db.commit()
        return _row_to_dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_analyse failed: %s", exc)
        raise HTTPException(status_code=503, detail="Datenbank nicht erreichbar")

