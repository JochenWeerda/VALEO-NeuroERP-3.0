"""
ROHWARE-SCHEMA-001 â€” Abrechnungsschema-Katalog fÃ¼r Rohwaren (Getreide, Raps, Mais, etc.)

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
  domain_shared.rohware_abrechnungsschemata
  domain_shared.rohware_schema_lines
"""

import uuid
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services import rohware_schema_service as schemas

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


class RohwareOut(BaseSchema):
    """Typed response schema for RohwareOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_tables(db: Session) -> None:
    """Raise 503 if required tables are missing."""
    try:
        db.execute(text("SELECT 1 FROM domain_shared.rohware_abrechnungsschemata LIMIT 1"))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


def _reject_tenant_override(payload: Dict[str, Any], tenant_id: str) -> None:
    if "tenant_id" in payload and payload["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Mandantenkontext stimmt nicht überein")


def _require_schema(db: Session, schema_id: str, tenant_id: str) -> None:
    row = db.execute(
        text("SELECT id FROM domain_shared.rohware_abrechnungsschemata WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": schema_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Schema nicht gefunden")


# ---------------------------------------------------------------------------
# Schema CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=list[RohwareOut], summary="Schemata auflisten")
async def list_schemata(
    rohwaren_gruppe: Optional[str] = Query(None, description="GE | RO | SA | MA"),
    status: Optional[str] = Query(None, description="AKTIV | ENTWURF | ARCHIV"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Abrechnungsschemata (optional gefiltert)."""
    try:
        _check_tables(db)
        conditions = ["s.tenant_id = :tenant_id"]
        params: Dict[str, Any] = {"skip": skip, "limit": limit, "tenant_id": tenant_id}
        if rohwaren_gruppe:
            conditions.append("g.gruppe_nr = :rohwaren_gruppe")
            params["rohwaren_gruppe"] = rohwaren_gruppe
        if status:
            conditions.append("s.status = :status")
            params["status"] = status

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = db.execute(
            text(f"SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id {where} ORDER BY s.gueltig_ab DESC NULLS LAST LIMIT :limit OFFSET :skip"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).mappings().all()
        return [dict(r) for r in rows]
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.post("", response_model=RohwareOut, status_code=201, summary="Schema anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_schema(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Neues Abrechnungsschema anlegen (Status=ENTWURF)."""
    try:
        _reject_tenant_override(payload, tenant_id)
        schemas.validate_header(payload, create=True)
        _check_tables(db)
        group = schemas.group_id(db, tenant_id, group_id=payload.get("gruppe_id"), group_code=payload.get("rohwaren_gruppe"))
        schema_id = schemas.create(db, tenant_id,
            schema_code=payload.get("schema_code") or f"SCH-{uuid.uuid4().hex[:8].upper()}",
            name=payload.get("name", ""), group=group,
            valid_from=payload.get("gueltig_ab"), valid_until=payload.get("gueltig_bis"),
            version=payload.get("version", 1))
        db.commit()
        row = db.execute(text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
                         {"id": schema_id, "tenant_id": tenant_id}).mappings().fetchone()
        return dict(row)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.get("/{schema_id}", response_model=RohwareOut, summary="Schema abrufen")
async def get_schema(schema_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Schema-Detail inkl. Positionen."""
    try:
        _check_tables(db)
        schema = db.execute(
            text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().fetchone()
        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        lines = db.execute(
            text("SELECT * FROM domain_shared.rohware_schema_lines WHERE tenant_id = :tenant_id AND schema_id = :id AND EXISTS (SELECT 1 FROM domain_shared.rohware_abrechnungsschemata s WHERE s.id = :id AND s.tenant_id = :tenant_id) ORDER BY sort_order"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().all()
        result = dict(schema)
        result["lines"] = [dict(l) for l in lines]
        return result
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.patch("/{schema_id}", response_model=RohwareOut, summary="Schema aktualisieren", dependencies=SCHREIBEN["LAGER"])
async def update_schema(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Schema aktualisieren â€” nur im Status ENTWURF erlaubt."""
    try:
        _reject_tenant_override(payload, tenant_id)
        schemas.validate_header(payload)
        _check_tables(db)
        row = db.execute(
            text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Schema {schema_id} nicht gefunden")
        if row["status"] != "ENTWURF":
            raise HTTPException(
                status_code=422,
                detail="Nur Schemata im Status ENTWURF kÃ¶nnen bearbeitet werden",
            )
        schemas.validate_header(payload, existing=row)
        mapping = {"schema_code": "schema_nr", "name": "bezeichnung", "gueltig_ab": "gueltig_ab", "gueltig_bis": "gueltig_bis", "version": "version"}
        updates = {column: payload[key] for key, column in mapping.items() if key in payload}
        if "rohwaren_gruppe" in payload or "gruppe_id" in payload:
            updates["gruppe_id"] = schemas.group_id(db, tenant_id, group_id=payload.get("gruppe_id"), group_code=payload.get("rohwaren_gruppe"))
        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = :{k}" for k in updates)
        db.execute(
            text(f"UPDATE domain_shared.rohware_abrechnungsschemata SET {set_clause} WHERE id = :id AND tenant_id = :tenant_id"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            {**updates, "id": schema_id, "tenant_id": tenant_id},
        )
        db.commit()
        updated = db.execute(
            text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.post("/{schema_id}/aktivieren", response_model=RohwareOut, summary="Aktivieren", dependencies=SCHREIBEN["LAGER"])
async def aktivieren(schema_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Setzt Status ENTWURF â†’ AKTIV. Voraussetzung: gueltig_ab muss gesetzt sein."""
    try:
        _check_tables(db)
        schemas.transition(db, tenant_id, schema_id, "AKTIV")
        db.commit()
        updated = db.execute(
            text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.post("/{schema_id}/archivieren", response_model=RohwareOut, summary="Archivieren", dependencies=SCHREIBEN["LAGER"])
async def archivieren(schema_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Setzt Status AKTIV â†’ ARCHIV."""
    try:
        _check_tables(db)
        schemas.transition(db, tenant_id, schema_id, "ARCHIV")
        db.commit()
        updated = db.execute(
            text("SELECT s.*, s.schema_nr AS schema_code, s.bezeichnung AS name, g.gruppe_nr AS rohwaren_gruppe FROM domain_shared.rohware_abrechnungsschemata s JOIN domain_shared.rohwarengruppen g ON g.id = s.gruppe_id AND g.tenant_id = s.tenant_id WHERE s.id = :id AND s.tenant_id = :tenant_id"),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().fetchone()
        return dict(updated)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


# ---------------------------------------------------------------------------
# Schema Lines
# ---------------------------------------------------------------------------

@router.get("/{schema_id}/lines", response_model=list[RohwareOut], summary="Lines auflisten")
async def list_lines(schema_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    """Alle Positionen eines Schemas."""
    try:
        _check_tables(db)
        _require_schema(db, schema_id, tenant_id)
        lines = db.execute(
            text(
                "SELECT * FROM domain_shared.rohware_schema_lines WHERE tenant_id = :tenant_id AND schema_id = :id AND EXISTS (SELECT 1 FROM domain_shared.rohware_abrechnungsschemata s WHERE s.id = :id AND s.tenant_id = :tenant_id) ORDER BY sort_order"
            ),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().all()
        return [dict(l) for l in lines]
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.post("/{schema_id}/lines", response_model=RohwareOut, status_code=201, summary="Line hinzufÃ¼gen", dependencies=SCHREIBEN["LAGER"])
async def add_line(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Position zu einem Schema hinzufÃ¼gen."""
    try:
        _reject_tenant_override(payload, tenant_id)
        _check_tables(db)
        _require_schema(db, schema_id, tenant_id)
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
        result = db.execute(
            text(
                """
                INSERT INTO domain_shared.rohware_schema_lines
                    (id, tenant_id, schema_id, positions_typ, bezeichnung, berechnungsformel, einheit, sort_order, created_at)
                SELECT :id, :tenant_id, :schema_id, :positions_typ, :bezeichnung, :berechnungsformel, :einheit, :sort_order, :created_at
                WHERE EXISTS (SELECT 1 FROM domain_shared.rohware_abrechnungsschemata s WHERE s.id = :schema_id AND s.tenant_id = :tenant_id)
                """
            ),
            {**row, "tenant_id": tenant_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schema nicht gefunden")
        db.commit()
        return row
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


@router.delete("/{schema_id}/lines/{line_id}", status_code=204, response_class=Response, response_model=None, summary="Line lÃ¶schen", dependencies=SCHREIBEN["LAGER"])
async def delete_line(
    schema_id: str,
    line_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Position aus Schema entfernen."""
    try:
        _check_tables(db)
        result = db.execute(
            text(
                "DELETE FROM domain_shared.rohware_schema_lines WHERE tenant_id = :tenant_id AND id = :line_id AND schema_id = :schema_id AND EXISTS (SELECT 1 FROM domain_shared.rohware_abrechnungsschemata s WHERE s.id = :schema_id AND s.tenant_id = :tenant_id)"
            ),
            {"line_id": line_id, "schema_id": schema_id, "tenant_id": tenant_id},
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Position {line_id} in Schema {schema_id} nicht gefunden",
            )
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")


# ---------------------------------------------------------------------------
# Testrechnung
# ---------------------------------------------------------------------------

def _eval_formula(formula: str, context: Dict[str, float]) -> Optional[float]:
    from app.services.rohware_formula import evaluate_formula

    return evaluate_formula(formula, context)


@router.post("/{schema_id}/testrechnung", response_model=RohwareOut, summary="Testrechnung", dependencies=SCHREIBEN["LAGER"])
async def testrechnung(
    schema_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Berechnet Testpreis anhand der Schema-Formeln.
    Body: { basis_preis, feuchte, hl_gewicht, bruch, menge_kg }
    """
    try:
        _reject_tenant_override(payload, tenant_id)
        _check_tables(db)
        _require_schema(db, schema_id, tenant_id)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")

    import math

    defaults = {"basis_preis": 0, "feuchte": 14.0, "hl_gewicht": 76.0,
                "bruch": 0.0, "menge_kg": 1000.0}
    context: Dict[str, float] = {}
    for name, default in defaults.items():
        value = payload.get(name, default)
        try:
            if type(value) not in (int, float, str):
                raise ValueError
            number = float(value)
            if not math.isfinite(number):
                raise ValueError
            context[name] = number
        except (ValueError, TypeError, OverflowError):
            raise HTTPException(status_code=422, detail=f"Ungültiger numerischer Eingabewert: {name}")


    try:
        lines = db.execute(
            text(
                "SELECT * FROM domain_shared.rohware_schema_lines WHERE tenant_id = :tenant_id AND schema_id = :id AND EXISTS (SELECT 1 FROM domain_shared.rohware_abrechnungsschemata s WHERE s.id = :id AND s.tenant_id = :tenant_id) ORDER BY sort_order"
            ),
            {"id": schema_id, "tenant_id": tenant_id},
        ).mappings().all()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbank nicht verfügbar")

    if not lines:
        raise HTTPException(status_code=404, detail=f"Schema {schema_id} hat keine Positionen")

    positionen = []
    gesamt_preis = 0.0

    for line in lines:
        formula = line.get("berechnungsformel") or ""
        wert = _eval_formula(formula, context)
        if wert is None:
            raise HTTPException(status_code=422, detail=f"Ungültige Formel in Position {line['id']}")
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
            if not math.isfinite(gesamt_preis):
                raise HTTPException(status_code=422, detail="Berechnungsergebnis außerhalb des gültigen Bereichs")

    gesamt_wert_menge = gesamt_preis * context["menge_kg"] / 1000
    if not math.isfinite(gesamt_wert_menge):
        raise HTTPException(status_code=422, detail="Berechnungsergebnis außerhalb des gültigen Bereichs")

    return {
        "schema_id": schema_id,
        "eingabewerte": context,
        "positionen": positionen,
        "gesamt_preis": round(gesamt_preis, 4),
        "gesamt_wert_menge": round(gesamt_wert_menge, 2),
    }

