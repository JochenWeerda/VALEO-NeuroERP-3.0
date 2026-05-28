"""
Genossenschaft API — Aktionärs- und Gesellschafterverwaltung
Mitgliederverwaltung, Anteilsbuchungen, Kapitalübersicht für eingetragene Genossenschaften (eG).
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.genossenschaft_schemas import GenossenschaftOut


router = APIRouter(prefix="/genossenschaft", tags=["Genossenschaft"])

MIGRATION_HINT = (
    "Tabelle domain_shared.genossenschaft_mitglieder fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class MitgliedCreate(BaseModel):
    mitglieds_nr: Optional[str] = None  # auto-generated if omitted
    name: str
    adresse: str
    eintrittsdatum: date
    genossenschaftsanteile: int = Field(default=0, ge=0)
    anteilswert_eur: float = Field(default=100.0, gt=0)
    status: str = Field(default="AKTIV", description="AKTIV | RUHEND | AUSGETRETEN")
    iban: str
    bank_name: str


class MitgliedPatch(BaseModel):
    name: Optional[str] = None
    adresse: Optional[str] = None
    genossenschaftsanteile: Optional[int] = None
    anteilswert_eur: Optional[float] = None
    status: Optional[str] = None
    iban: Optional[str] = None
    bank_name: Optional[str] = None


class AnteilsbewegungCreate(BaseModel):
    bewegungstyp: str = Field(
        ...,
        description="ZEICHNUNG | ERHOEHUNG | TEILRUECKZAHLUNG | VOLLRUECKZAHLUNG | TRANSFER",
    )
    anzahl_anteile: int = Field(..., gt=0)
    wert_eur: float = Field(..., gt=0)
    datum: date
    bemerkung: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    return dict(row._mapping)


def _gen_mitglieds_nr(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    try:
        row = db.execute(
            text(
                "SELECT COUNT(*) AS cnt FROM domain_shared.genossenschaft_mitglieder "
                "WHERE mitglieds_nr LIKE :pattern"
            ),
            {"pattern": f"M-{year}-%"},
        ).fetchone()
        seq = (row.cnt if row else 0) + 1
    except Exception:
        seq = 1
    return f"M-{year}-{seq:05d}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/mitglieder", summary="Mitgliederliste",
    response_model=list[GenossenschaftOut]
)
def list_mitglieder(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, mitglieds_nr, name, adresse, eintrittsdatum, "
                "genossenschaftsanteile, anteilswert_eur, status, iban, bank_name, created_at "
                "FROM domain_shared.genossenschaft_mitglieder "
                "ORDER BY mitglieds_nr"
            )
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("genossenschaft_mitglieder table not accessible: %s", exc)
        return []


@router.post("/mitglieder", status_code=201, summary="Mitglied anlegen",
    response_model=IDResponse
)
def create_mitglied(
    payload: MitgliedCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    mitglied_id = str(uuid4())
    mitglieds_nr = payload.mitglieds_nr or _gen_mitglieds_nr(db)
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.genossenschaft_mitglieder "
                "(id, mitglieds_nr, name, adresse, eintrittsdatum, "
                "genossenschaftsanteile, anteilswert_eur, status, iban, bank_name, created_at) "
                "VALUES (:id, :nr, :name, :adresse, :eintrittsdatum, "
                ":anteile, :anteilswert, :status, :iban, :bank_name, NOW())"
            ),
            {
                "id": mitglied_id,
                "nr": mitglieds_nr,
                "name": payload.name,
                "adresse": payload.adresse,
                "eintrittsdatum": payload.eintrittsdatum,
                "anteile": payload.genossenschaftsanteile,
                "anteilswert": payload.anteilswert_eur,
                "status": payload.status,
                "iban": payload.iban,
                "bank_name": payload.bank_name,
            },
        )
        db.commit()
        return {"id": mitglied_id, "mitglieds_nr": mitglieds_nr, "status": "angelegt"}
    except Exception as exc:
        db.rollback()
        logger.error("Fehler beim Anlegen des Mitglieds: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.get("/mitglieder/{mitglied_id}", summary="Mitglied Detailansicht",
    response_model=GenossenschaftOut
)
def get_mitglied(
    mitglied_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    try:
        row = db.execute(
            text(
                "SELECT id, mitglieds_nr, name, adresse, eintrittsdatum, "
                "genossenschaftsanteile, anteilswert_eur, status, iban, bank_name, created_at "
                "FROM domain_shared.genossenschaft_mitglieder "
                "WHERE id = :id"
            ),
            {"id": mitglied_id},
        ).fetchone()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )
    if not row:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")

    mitglied = _row_to_dict(row)

    # Anteilsbewegungen
    try:
        bewegungen = db.execute(
            text(
                "SELECT id, bewegungstyp, anzahl_anteile, wert_eur, datum, bemerkung, created_at "
                "FROM domain_shared.genossenschaft_anteilsbewegungen "
                "WHERE mitglieds_id = :id ORDER BY datum DESC"
            ),
            {"id": mitglied_id},
        ).fetchall()
        mitglied["anteilsbewegungen"] = [_row_to_dict(b) for b in bewegungen]
    except Exception:
        mitglied["anteilsbewegungen"] = []

    return mitglied


@router.patch("/mitglieder/{mitglied_id}", summary="Mitglied aktualisieren",
    response_model=IDResponse
)
def patch_mitglied(
    mitglied_id: str,
    payload: MitgliedPatch,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übergeben")

    field_map = {
        "name": "name",
        "adresse": "adresse",
        "genossenschaftsanteile": "genossenschaftsanteile",
        "anteilswert_eur": "anteilswert_eur",
        "status": "status",
        "iban": "iban",
        "bank_name": "bank_name",
    }
    set_clauses = ", ".join(f"{field_map[k]} = :{k}" for k in updates)
    params = {**updates, "id": mitglied_id}

    try:
        db.execute(
            text(
                f"UPDATE domain_shared.genossenschaft_mitglieder "
                f"SET {set_clauses} WHERE id = :id"
            ),
            params,
        )
        db.commit()
        return {"id": mitglied_id, "status": "aktualisiert"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.post("/mitglieder/{mitglied_id}/anteilsbewegung", status_code=201, summary="Anteilsbewegung buchen",
    response_model=IDResponse
)
def create_anteilsbewegung(
    mitglied_id: str,
    payload: AnteilsbewegungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    bewegung_id = str(uuid4())

    # Determine sign for balance adjustment
    sign = -1 if payload.bewegungstyp in ("TEILRUECKZAHLUNG", "VOLLRUECKZAHLUNG") else 1
    delta = sign * payload.anzahl_anteile

    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.genossenschaft_anteilsbewegungen "
                "(id, mitglieds_id, bewegungstyp, anzahl_anteile, wert_eur, datum, bemerkung, created_at) "
                "VALUES (:id, :mitglieds_id, :typ, :anzahl, :wert, :datum, :bemerkung, NOW())"
            ),
            {
                "id": bewegung_id,
                "mitglieds_id": mitglied_id,
                "typ": payload.bewegungstyp,
                "anzahl": payload.anzahl_anteile,
                "wert": payload.wert_eur,
                "datum": payload.datum,
                "bemerkung": payload.bemerkung,
            },
        )
        # Update member balance
        db.execute(
            text(
                "UPDATE domain_shared.genossenschaft_mitglieder "
                "SET genossenschaftsanteile = genossenschaftsanteile + :delta "
                "WHERE id = :id"
            ),
            {"delta": delta, "id": mitglied_id},
        )
        db.commit()
        return {"id": bewegung_id, "mitglieds_id": mitglied_id, "delta_anteile": delta, "status": "gebucht"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.get("/kapitaluebersicht", summary="Genossenschaftliches Kapital — Aggregatübersicht",
    response_model=GenossenschaftOut
)
def kapitaluebersicht(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    empty = {
        "total_mitglieder": 0,
        "total_anteile": 0,
        "total_kapital_eur": 0.0,
        "aktiv": 0,
        "ruhend": 0,
        "ausgetreten": 0,
    }
    try:
        row = db.execute(
            text(
                "SELECT "
                "  COUNT(*) AS total_mitglieder, "
                "  COALESCE(SUM(genossenschaftsanteile), 0) AS total_anteile, "
                "  COALESCE(SUM(genossenschaftsanteile * anteilswert_eur), 0.0) AS total_kapital_eur, "
                "  COUNT(*) FILTER (WHERE status = 'AKTIV') AS aktiv, "
                "  COUNT(*) FILTER (WHERE status = 'RUHEND') AS ruhend, "
                "  COUNT(*) FILTER (WHERE status = 'AUSGETRETEN') AS ausgetreten "
                "FROM domain_shared.genossenschaft_mitglieder"
            )
        ).fetchone()
        if not row:
            return empty
        return {
            "total_mitglieder": row.total_mitglieder or 0,
            "total_anteile": row.total_anteile or 0,
            "total_kapital_eur": float(row.total_kapital_eur or 0.0),
            "aktiv": row.aktiv or 0,
            "ruhend": row.ruhend or 0,
            "ausgetreten": row.ausgetreten or 0,
        }
    except Exception as exc:
        logger.warning("kapitaluebersicht not accessible: %s", exc)
        return empty
