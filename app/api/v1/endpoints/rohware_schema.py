"""
ROHWARE-SCHEMA-001 — Abrechnungsschema-Katalog für Rohwaren (Getreide, Raps, Mais, etc.)

Endpoints:
  GET  /rohware/schemata
  POST /rohware/schemata
  GET  /rohware/schemata/{schema_id}
  PATCH /rohware/schemata/{schema_id}
  POST /rohware/schemata/{schema_id}/aktivieren
  POST /rohware/schemata/{schema_id}/archivieren
  GET  /rohware/schemata/{schema_id}/lines
  POST /rohware/schemata/{schema_id}/lines
  DELETE /rohware/schemata/{schema_id}/lines/{line_id}
  POST /rohware/schemata/{schema_id}/testrechnung

Tables (created by Alembic migration, not here):
  rohware_schemata
  rohware_schema_lines
"""

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MIGRATION_503 = {
    "detail": "Rohware-Schema-Tabellen noch nicht migriert",
    "migration_hint": "alembic upgrade head",
}


def _check_tables(db: Session) -> None:
    """Raise 503 if required tables are missing."""
    try:
        db.execute(text("SELECT 1 FROM rohware_schemata LIMIT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail=_MIGRATION_503["detail"])


# ---------------------------------------------------------------------------
# Schema CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=List[dict])
async def list_schemata(
    rohwaren_gruppe: Optional[str] = Query(None, description="GE | RO | SA | MA"),
    status: Optional[str] = Query(None, description="AKTIV | ENTWURF | ARCHIV"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Liste aller Abrechnungsschemata (optional gefiltert)."""
    try:
        _check_tables(db)
        conditions = []
        params: Dict[str, Any] = {"skip": skip, "limit": limit}
        if rohwaren_gruppe:
            conditions.append("rohwaren_gruppe = :rohwaren_gruppe")
            params["rohwaren_gruppe"] = rohwaren_gruppe
        if status:
            conditions.append("status = :status")
            params["status"] = status
        if tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = tenant_id

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = db.execute(
            text(f"SELECT * FROM rohware_schemata {where} ORDER BY gueltig_ab DESC NULLS LAST LIMIT :limit OFFSET :skip"),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.post("", response_model=dict, status_code=201)
async def create_schema(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Neues Abrechnungsschema anlegen (Status=ENTWURF)."""
    try:
        _check_tables(db)
        schema_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        row = {
            "id": schema_id,
            "schema_code": payload.get("schema_code", f"SCH-{schema_id[:8].upper()}"),
            "name": payload.get("name", ""),
            "rohwaren_gruppe": payload.get("rohwaren_gruppe", "GE"),
            "gueltig_ab": payload.get("gueltig_ab"),
            "gueltig_bis": payload.get("gueltig_bis"),
            "version": payload.get("version", 1),
            "status": "ENTWURF",
            "tenant_id": payload.get("tenant_id"),
            "created_at": now,
            "updated_at": now,
        }
        db.execute(
            text(
                """
                INSERT INTO rohware_schemata
                    (id, schema_code, name, rohwaren_gruppe, gueltig_ab, gueltig_bis,
                     version, status, tenant_id, created_at, updated_at)
                VALUES
                    (:id, :schema_code, :name, :rohwaren_gruppe, :gueltig_ab, :gueltig_bis,
                     :version, :status, :tenant_id, :created_at, :updated_at)
                """
            ),
            row,
        )
        db.commit()
        return row
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.get("/{schema_id}", response_model=dict)
async def get_schema(schema_id: str, db: Session = Depends(get_db)):
    """Schema-Detail inkl. Positionen."""
    try:
        _check_tables(db)
        schema = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        lines = db.execute(
            text("SELECT * FROM rohware_schema_lines WHERE schema_id = :id ORDER BY sort_order"),
            {"id": schema_id},
        ).mappings().all()
        result = dict(schema)
        result["lines"] = [dict(l) for l in lines]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.patch("/{schema_id}", response_model=dict)
async def update_schema(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Schema aktualisieren — nur im Status ENTWURF erlaubt."""
    try:
        _check_tables(db)
        row = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        if row["status"] != "ENTWURF":
            raise HTTPException(
                status_code=422,
                detail="Nur Schemata im Status ENTWURF können bearbeitet werden",
            )
        allowed = {"schema_code", "name", "rohwaren_gruppe", "gueltig_ab", "gueltig_bis", "version"}
        updates = {k: v for k, v in payload.items() if k in allowed}
        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = :{k}" for k in updates)
        db.execute(
            text(f"UPDATE rohware_schemata SET {set_clause} WHERE id = :id"),
            {**updates, "id": schema_id},
        )
        db.commit()
        updated = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.post("/{schema_id}/aktivieren", response_model=dict)
async def aktivieren(schema_id: str, db: Session = Depends(get_db)):
    """Setzt Status ENTWURF → AKTIV. Voraussetzung: gueltig_ab muss gesetzt sein."""
    try:
        _check_tables(db)
        row = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        if row["status"] != "ENTWURF":
            raise HTTPException(
                status_code=422,
                detail=f"Schema ist bereits '{row['status']}' — Aktivierung nur aus ENTWURF möglich",
            )
        if not row.get("gueltig_ab"):
            raise HTTPException(
                status_code=422,
                detail="gueltig_ab muss gesetzt sein, bevor ein Schema aktiviert werden kann",
            )
        db.execute(
            text(
                "UPDATE rohware_schemata SET status = 'AKTIV', updated_at = :now WHERE id = :id"
            ),
            {"now": datetime.utcnow().isoformat(), "id": schema_id},
        )
        db.commit()
        updated = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.post("/{schema_id}/archivieren", response_model=dict)
async def archivieren(schema_id: str, db: Session = Depends(get_db)):
    """Setzt Status AKTIV → ARCHIV."""
    try:
        _check_tables(db)
        row = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        if row["status"] != "AKTIV":
            raise HTTPException(
                status_code=422,
                detail=f"Schema ist '{row['status']}' — Archivierung nur aus AKTIV möglich",
            )
        db.execute(
            text(
                "UPDATE rohware_schemata SET status = 'ARCHIV', updated_at = :now WHERE id = :id"
            ),
            {"now": datetime.utcnow().isoformat(), "id": schema_id},
        )
        db.commit()
        updated = db.execute(
            text("SELECT * FROM rohware_schemata WHERE id = :id"),
            {"id": schema_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


# ---------------------------------------------------------------------------
# Schema Lines
# ---------------------------------------------------------------------------

@router.get("/{schema_id}/lines", response_model=List[dict])
async def list_lines(schema_id: str, db: Session = Depends(get_db)):
    """Alle Positionen eines Schemas."""
    try:
        _check_tables(db)
        lines = db.execute(
            text(
                "SELECT * FROM rohware_schema_lines WHERE schema_id = :id ORDER BY sort_order"
            ),
            {"id": schema_id},
        ).mappings().all()
        return [dict(l) for l in lines]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.post("/{schema_id}/lines", response_model=dict, status_code=201)
async def add_line(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Position zu einem Schema hinzufügen."""
    try:
        _check_tables(db)
        line_id = str(uuid.uuid4())
        row = {
            "id": line_id,
            "schema_id": schema_id,
            "positions_typ": payload.get("positions_typ", "GRUNDPREIS"),
            "bezeichnung": payload.get("bezeichnung", ""),
            "berechnungsformel": payload.get("berechnungsformel", ""),
            "einheit": payload.get("einheit", "EUR/t"),
            "sort_order": payload.get("sort_order", 10),
            "created_at": datetime.utcnow().isoformat(),
        }
        db.execute(
            text(
                """
                INSERT INTO rohware_schema_lines
                    (id, schema_id, positions_typ, bezeichnung, berechnungsformel, einheit, sort_order, created_at)
                VALUES
                    (:id, :schema_id, :positions_typ, :bezeichnung, :berechnungsformel, :einheit, :sort_order, :created_at)
                """
            ),
            row,
        )
        db.commit()
        return row
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


@router.delete("/{schema_id}/lines/{line_id}", status_code=204, response_class=Response)
async def delete_line(
    schema_id: str,
    line_id: str,
    db: Session = Depends(get_db),
):
    """Position aus Schema entfernen."""
    try:
        _check_tables(db)
        result = db.execute(
            text(
                "DELETE FROM rohware_schema_lines WHERE id = :line_id AND schema_id = :schema_id"
            ),
            {"line_id": line_id, "schema_id": schema_id},
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Position {line_id} in Schema {schema_id} nicht gefunden",
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")


# ---------------------------------------------------------------------------
# Testrechnung
# ---------------------------------------------------------------------------

def _eval_formula(formula: str, context: Dict[str, float]) -> Optional[float]:
    """
    Wertet eine einfache Berechnungsformel aus.
    Erlaubte Variablen: basis_preis, feuchte, hl_gewicht, bruch, menge_kg,
                        feuchte_abzug_prozent (= max(0, feuchte - 14.0))
    Nur arithmetische Operatoren und die o.g. Variablen erlaubt.
    """
    safe_context = {
        **context,
        "feuchte_abzug_prozent": max(0.0, context.get("feuchte", 14.0) - 14.0),
        "abs": abs,
        "max": max,
        "min": min,
        "round": round,
    }
    try:
        result = eval(formula, {"__builtins__": {}}, safe_context)  # noqa: S307
        return float(result)
    except Exception:
        return None


@router.post("/{schema_id}/testrechnung", response_model=dict)
async def testrechnung(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    Berechnet Testpreis anhand der Schema-Formeln.
    Body: { basis_preis, feuchte, hl_gewicht, bruch, menge_kg }
    """
    try:
        _check_tables(db)
    except HTTPException:
        raise

    context: Dict[str, float] = {
        "basis_preis": float(payload.get("basis_preis", 0)),
        "feuchte": float(payload.get("feuchte", 14.0)),
        "hl_gewicht": float(payload.get("hl_gewicht", 76.0)),
        "bruch": float(payload.get("bruch", 0.0)),
        "menge_kg": float(payload.get("menge_kg", 1000.0)),
    }

    try:
        lines = db.execute(
            text(
                "SELECT * FROM rohware_schema_lines WHERE schema_id = :id ORDER BY sort_order"
            ),
            {"id": schema_id},
        ).mappings().all()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")

    if not lines:
        raise HTTPException(status_code=404, detail=f"Schema {schema_id} hat keine Positionen")

    positionen = []
    gesamt_preis = 0.0

    for line in lines:
        formula = line.get("berechnungsformel") or ""
        wert = _eval_formula(formula, context)
        positionen.append(
            {
                "positions_typ": line["positions_typ"],
                "bezeichnung": line["bezeichnung"],
                "berechnungsformel": formula,
                "einheit": line.get("einheit"),
                "berechneter_wert": wert,
                "fehler": wert is None,
            }
        )
        if wert is not None:
            gesamt_preis += wert

    return {
        "schema_id": schema_id,
        "eingabewerte": context,
        "positionen": positionen,
        "gesamt_preis": round(gesamt_preis, 4),
        "gesamt_wert_menge": round(gesamt_preis * context["menge_kg"] / 1000, 2),
    }
