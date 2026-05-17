"""
Gelangensbestätigung API — §17a UStDV
Steuerfreie innergemeinschaftliche Lieferungen (EU).
Nachweis des Gelangens des Liefergegenstandes in das übrige Gemeinschaftsgebiet.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gelangensbestaetigung", tags=["Gelangensbestätigung", "UStDV"])

MIGRATION_HINT = (
    "Tabelle domain_compliance.gelangensbestaetigung fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)

ERINNERUNG_TAGE = 90  # §17a UStDV: Nachweis innerhalb von 3 Monaten


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class GelangensbestaetigungCreate(BaseModel):
    lieferschein_nr: str
    rechnung_nr: str
    kunde_nr: str
    bestimmungsland_code: str = Field(..., min_length=2, max_length=2, description="EU-Mitgliedstaat ISO 3166-1")
    warenwert_eur: float = Field(..., gt=0)
    versanddatum: date
    empfaenger_name: str
    empfaenger_ust_id_nr: str


class GelangensbestaetigungOut(BaseModel):
    id: str
    lieferschein_nr: str
    rechnung_nr: str
    kunde_nr: str
    bestimmungsland_code: str
    warenwert_eur: float
    versanddatum: str
    empfaenger_name: str
    empfaenger_ust_id_nr: str
    status: str  # AUSSTEHEND | ERHALTEN | ABGELAUFEN
    token: str
    erinnerung_am: str
    erhalten_am: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    d = dict(row._mapping)
    # Normalise date fields to ISO strings
    for key in ("versanddatum", "erinnerung_am", "erhalten_am", "created_at"):
        if key in d and d[key] is not None:
            val = d[key]
            if hasattr(val, "isoformat"):
                d[key] = val.isoformat()
    return d


def _gen_token() -> str:
    return str(uuid4()).replace("-", "")[:8].upper()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", summary="Gelangensbestätigungen auflisten")
def list_gelangensbestaetigung(
    status: Optional[str] = Query(None, description="AUSSTEHEND | ERHALTEN | ABGELAUFEN"),
    lieferschein_nr: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    where_clauses = []
    params: dict = {}
    if status:
        where_clauses.append("status = :status")
        params["status"] = status
    if lieferschein_nr:
        where_clauses.append("lieferschein_nr = :lieferschein_nr")
        params["lieferschein_nr"] = lieferschein_nr

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    try:
        rows = db.execute(
            text(
                f"SELECT id, lieferschein_nr, rechnung_nr, kunde_nr, bestimmungsland_code, "
                f"warenwert_eur, versanddatum, empfaenger_name, empfaenger_ust_id_nr, "
                f"status, token, erinnerung_am, erhalten_am "
                f"FROM domain_compliance.gelangensbestaetigung "
                f"{where_sql} "
                f"ORDER BY versanddatum DESC"
            ),
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("gelangensbestaetigung table not accessible: %s", exc)
        return []


@router.post("", status_code=201, summary="Gelangensbestätigung erstellen")
def create_gelangensbestaetigung(
    payload: GelangensbestaetigungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    entry_id = str(uuid4())
    token = _gen_token()
    erinnerung_am = payload.versanddatum + timedelta(days=ERINNERUNG_TAGE)

    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.gelangensbestaetigung "
                "(id, lieferschein_nr, rechnung_nr, kunde_nr, bestimmungsland_code, "
                "warenwert_eur, versanddatum, empfaenger_name, empfaenger_ust_id_nr, "
                "status, token, erinnerung_am, erhalten_am, created_at) "
                "VALUES (:id, :lieferschein_nr, :rechnung_nr, :kunde_nr, :bestimmungsland_code, "
                ":warenwert_eur, :versanddatum, :empfaenger_name, :empfaenger_ust_id_nr, "
                "'AUSSTEHEND', :token, :erinnerung_am, NULL, NOW())"
            ),
            {
                "id": entry_id,
                "lieferschein_nr": payload.lieferschein_nr,
                "rechnung_nr": payload.rechnung_nr,
                "kunde_nr": payload.kunde_nr,
                "bestimmungsland_code": payload.bestimmungsland_code,
                "warenwert_eur": payload.warenwert_eur,
                "versanddatum": payload.versanddatum,
                "empfaenger_name": payload.empfaenger_name,
                "empfaenger_ust_id_nr": payload.empfaenger_ust_id_nr,
                "token": token,
                "erinnerung_am": erinnerung_am,
            },
        )
        db.commit()
        return {
            "id": entry_id,
            "token": token,
            "erinnerung_am": erinnerung_am.isoformat(),
            "status": "AUSSTEHEND",
        }
    except Exception as exc:
        db.rollback()
        logger.error("Fehler beim Erstellen der Gelangensbestätigung: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.post("/{entry_id}/bestaetigen", summary="Gelangensbestätigung durch Empfänger bestätigen")
def bestaetigen(
    entry_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    erhalten_am = datetime.now(timezone.utc).date()
    try:
        result = db.execute(
            text(
                "UPDATE domain_compliance.gelangensbestaetigung "
                "SET status = 'ERHALTEN', erhalten_am = :erhalten_am "
                "WHERE id = :id AND status = 'AUSSTEHEND'"
            ),
            {"id": entry_id, "erhalten_am": erhalten_am},
        )
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Gelangensbestätigung nicht gefunden oder bereits bearbeitet",
            )
        return {"id": entry_id, "status": "ERHALTEN", "erhalten_am": erhalten_am.isoformat()}
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.get("/faellig", summary="Überfällige Gelangensbestätigungen")
def list_faellig(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    today = date.today()
    try:
        rows = db.execute(
            text(
                "SELECT id, lieferschein_nr, rechnung_nr, kunde_nr, empfaenger_name, "
                "bestimmungsland_code, warenwert_eur, versanddatum, token, erinnerung_am "
                "FROM domain_compliance.gelangensbestaetigung "
                "WHERE status = 'AUSSTEHEND' AND erinnerung_am <= :today "
                "ORDER BY erinnerung_am ASC"
            ),
            {"today": today},
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("gelangensbestaetigung/faellig not accessible: %s", exc)
        return []


@router.post("/{entry_id}/mahnung", summary="Erinnerung senden (Stub)")
def mahnung_senden(
    entry_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    try:
        row = db.execute(
            text(
                "SELECT token FROM domain_compliance.gelangensbestaetigung WHERE id = :id"
            ),
            {"id": entry_id},
        ).fetchone()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )
    if not row:
        raise HTTPException(status_code=404, detail="Gelangensbestätigung nicht gefunden")

    # Stub: In production this would send email/fax to empfaenger
    logger.info("Mahnung für Gelangensbestätigung %s versendet (Stub)", entry_id)
    return {"erinnerung_gesendet": True, "token": row.token}
