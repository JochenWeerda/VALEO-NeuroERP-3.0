"""
Rüstliste (Kommissioniervorbereitung)
Analog externe Agrar-ERP-Plattform l3c-lager Rüstliste
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RuestlistePosition(BaseModel):
    artikel_nr: str
    menge: float
    lagerplatz: Optional[str] = None


class RuestlisteCreate(BaseModel):
    auftrag_nr: str
    positionen: list[RuestlistePosition]
    erstellt_fuer: str
    prioritaet: str = "NORMAL"  # NORMAL / HOCH / EILIG


class RuestlisteOut(BaseModel):
    id: str
    ruestlisten_nr: str
    auftrag_nr: str
    status: str
    positionen: list[dict[str, Any]]
    erstellt_fuer: str
    prioritaet: str
    erstellt_am: Optional[str] = None
    verarbeitet_am: Optional[str] = None


class RuestlisteBearbeiten(BaseModel):
    bemerkung: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gen_nr() -> str:
    today = date.today().strftime("%Y%m%d")
    seq = int(uuid.uuid4().int % 9999) + 1
    return f"RL-{today}-{seq:04d}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[RuestlisteOut], tags=["lager", "ruestliste"], summary="Ruestlisten auflisten")
def list_ruestlisten(
    status: Optional[str] = Query(None, description="Filter by status (OFFEN/IN_BEARBEITUNG/VERARBEITET/ABGEBROCHEN)"),
    db: Session = Depends(get_db),
) -> list[RuestlisteOut]:
    """List Rüstlisten, optionally filtered by status."""
    try:
        if status:
            rows = db.execute(
                text(
                    "SELECT id, ruestlisten_nr, auftrag_nr, status, positionen, erstellt_fuer, prioritaet, "
                    "erstellt_am, verarbeitet_am FROM domain_inventory.ruestlisten WHERE status = :status ORDER BY erstellt_am DESC"
                ),
                {"status": status},
            ).mappings().all()
        else:
            rows = db.execute(
                text(
                    "SELECT id, ruestlisten_nr, auftrag_nr, status, positionen, erstellt_fuer, prioritaet, "
                    "erstellt_am, verarbeitet_am FROM domain_inventory.ruestlisten ORDER BY erstellt_am DESC"
                )
            ).mappings().all()
        return [RuestlisteOut(**dict(r)) for r in rows]
    except Exception:  # noqa: BLE001
        return []


@router.post("", response_model=RuestlisteOut, status_code=201, tags=["lager", "ruestliste"], summary="Ruestliste anlegen")
def create_ruestliste(payload: RuestlisteCreate, db: Session = Depends(get_db)) -> RuestlisteOut:
    """Create a new Rüstliste with status=OFFEN."""
    new_id = str(uuid.uuid4())
    nr = _gen_nr()
    now = _now_iso()
    positionen_data = [p.model_dump() for p in payload.positionen]
    import json
    try:
        db.execute(
            text(
                "INSERT INTO domain_inventory.ruestlisten "
                "(id, ruestlisten_nr, auftrag_nr, status, positionen, erstellt_fuer, prioritaet, erstellt_am) "
                "VALUES (:id, :nr, :auftrag_nr, 'OFFEN', :positionen, :erstellt_fuer, :prioritaet, :erstellt_am)"
            ),
            {
                "id": new_id,
                "nr": nr,
                "auftrag_nr": payload.auftrag_nr,
                "positionen": json.dumps(positionen_data),
                "erstellt_fuer": payload.erstellt_fuer,
                "prioritaet": payload.prioritaet,
                "erstellt_am": now,
            },
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=str(exc),
            headers={"X-Migration-Hint": "CREATE TABLE domain_inventory.ruestlisten (...)"},
        ) from exc

    return RuestlisteOut(
        id=new_id,
        ruestlisten_nr=nr,
        auftrag_nr=payload.auftrag_nr,
        status="OFFEN",
        positionen=positionen_data,
        erstellt_fuer=payload.erstellt_fuer,
        prioritaet=payload.prioritaet,
        erstellt_am=now,
    )


@router.get("/{id}/positionen", tags=["lager", "ruestliste"], summary="Positionen abrufen")
def get_positionen(id: str, db: Session = Depends(get_db)) -> dict:
    """Return positions for a Rüstliste by id."""
    try:
        row = db.execute(
            text("SELECT positionen FROM domain_inventory.ruestlisten WHERE id = :id"),
            {"id": id},
        ).first()
        if row is None:
            raise HTTPException(status_code=404, detail="Rüstliste nicht gefunden")
        import json
        pos = row[0]
        if isinstance(pos, str):
            pos = json.loads(pos)
        return {"id": id, "positionen": pos}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _set_status(nr: str, new_status: str, allowed_from: list[str], db: Session, verarbeitet: bool = False) -> dict:
    """Generic status transition helper."""
    try:
        row = db.execute(
            text("SELECT id, status FROM domain_inventory.ruestlisten WHERE ruestlisten_nr = :nr"),
            {"nr": nr},
        ).first()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if row is None:
        raise HTTPException(status_code=404, detail="Rüstliste nicht gefunden")
    current_status = row[1]
    if current_status not in allowed_from:
        raise HTTPException(
            status_code=409,
            detail=f"Status-Übergang von '{current_status}' nach '{new_status}' nicht erlaubt",
        )
    extra = ""
    params: dict = {"nr": nr, "status": new_status}
    if verarbeitet:
        params["verarbeitet_am"] = _now_iso()
        extra = ", verarbeitet_am = :verarbeitet_am"
    try:
        db.execute(
            text(f"UPDATE domain_inventory.ruestlisten SET status = :status{extra} WHERE ruestlisten_nr = :nr"),  # noqa: S608  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params,
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"ruestlisten_nr": nr, "status": new_status}


@router.post("/{nr}/bearbeiten", tags=["lager", "ruestliste"], summary="Bearbeiten")
def bearbeiten(nr: str, db: Session = Depends(get_db)) -> dict:
    """Set Rüstliste to IN_BEARBEITUNG (irreversible)."""
    return _set_status(nr, "IN_BEARBEITUNG", ["OFFEN"], db)


@router.post("/{nr}/verarbeitet", tags=["lager", "ruestliste"], summary="Verarbeitet")
def verarbeitet(nr: str, db: Session = Depends(get_db)) -> dict:
    """Complete Rüstliste — set to VERARBEITET."""
    return _set_status(nr, "VERARBEITET", ["IN_BEARBEITUNG"], db, verarbeitet=True)


@router.post("/{nr}/verarbeitet/bemerkung", tags=["lager", "ruestliste"], summary="Hinzufuegen bemerkung")
def bemerkung_hinzufuegen(nr: str, payload: RuestlisteBearbeiten, db: Session = Depends(get_db)) -> dict:
    """Add a note to an already-completed Rüstliste."""
    try:
        row = db.execute(
            text("SELECT id FROM domain_inventory.ruestlisten WHERE ruestlisten_nr = :nr"),
            {"nr": nr},
        ).first()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if row is None:
        raise HTTPException(status_code=404, detail="Rüstliste nicht gefunden")
    try:
        db.execute(
            text("UPDATE domain_inventory.ruestlisten SET bemerkung = :b WHERE ruestlisten_nr = :nr"),
            {"b": payload.bemerkung, "nr": nr},
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"ruestlisten_nr": nr, "bemerkung": payload.bemerkung}


@router.post("/{nr}/abbrechen", tags=["lager", "ruestliste"], summary="Abbrechen")
def abbrechen(nr: str, db: Session = Depends(get_db)) -> dict:
    """Cancel a Rüstliste (only from OFFEN or IN_BEARBEITUNG)."""
    return _set_status(nr, "ABGEBROCHEN", ["OFFEN", "IN_BEARBEITUNG"], db)
