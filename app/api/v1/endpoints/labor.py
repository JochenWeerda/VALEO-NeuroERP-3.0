"""Labor API - DB-backed endpoints.

Mounted under `/labor` and `/qualitaet` in api.py (identische Pfade: .../labor-auftraege).
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import LaborProbe, LaborAuftragEntry

router = APIRouter(tags=["Labor"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _auftrag_to_dict(i: LaborAuftragEntry) -> dict[str, Any]:
    """Frontend erwartet camelCase fuer chargenId."""
    return {
        "id": i.id,
        "chargenId": i.chargen_id,
        "chargen_id": i.chargen_id,
        "labor": i.labor,
        "analysen": int(i.analysen or 0),
        "auftragsdatum": _dt(i.auftragsdatum) or "",
        "status": i.status,
    }


class LaborAuftragCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chargenId: Optional[str] = None
    chargen_id: Optional[str] = None
    artikel: Optional[str] = None
    labor: str = ""
    analysen: Optional[list[str]] = None
    prioritaet: Optional[str] = None
    bemerkungen: Optional[str] = None


def _seed(db: Session) -> None:
    if db.query(LaborProbe).count() == 0:
        db.add_all(
            [
                LaborProbe(
                    id="LB-SEED-2026-001",
                    probennummer="LB-2026-001",
                    typ="Qualitaetspruefung",
                    artikel="Weizen Premium",
                    datum=datetime(2026, 2, 10),
                    labor="Lufa Nord-West",
                    status="abgeschlossen",
                ),
                LaborProbe(
                    id="LB-SEED-2026-002",
                    probennummer="LB-2026-002",
                    typ="Rueckstandsanalyse",
                    artikel="Raps",
                    datum=datetime(2026, 2, 11),
                    labor="SGS",
                    status="in-bearbeitung",
                ),
            ]
        )
    if db.query(LaborAuftragEntry).count() == 0:
        db.add_all(
            [
                LaborAuftragEntry(
                    id="LA-SEED-WEI-001",
                    chargen_id="251011-WEI-001",
                    labor="Lufa Nord-West",
                    analysen=4,
                    auftragsdatum=datetime(2026, 2, 10),
                    status="in-bearbeitung",
                ),
                LaborAuftragEntry(
                    id="LA-SEED-RAP-002",
                    chargen_id="251010-RAP-002",
                    labor="SGS",
                    analysen=6,
                    auftragsdatum=datetime(2026, 2, 9),
                    status="abgeschlossen",
                ),
            ]
        )
    db.commit()


@router.get("/proben", response_model=dict, summary="Proben auflisten")
async def list_proben(status: Optional[str] = Query(None, description="Filter by status"), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    query = db.query(LaborProbe)
    if status:
        query = query.filter(LaborProbe.status == status)
    items = query.order_by(LaborProbe.datum.desc()).all()
    return {
        "items": [
            {
                "id": i.id,
                "probennummer": i.probennummer,
                "typ": i.typ,
                "artikel": i.artikel,
                "datum": _dt(i.datum),
                "labor": i.labor,
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/labor-auftraege", response_model=dict, summary="Labor auftraege auflisten")
async def list_labor_auftraege(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(LaborAuftragEntry).order_by(LaborAuftragEntry.auftragsdatum.desc()).all()
    return {
        "items": [_auftrag_to_dict(i) for i in items],
        "total": len(items),
    }


@router.get("/labor-auftraege/{entry_id}", response_model=dict, summary="Labor auftrag abrufen")
async def get_labor_auftrag(entry_id: str, db: Session = Depends(get_db)) -> dict:
    """Einzelner Labor-Auftrag fuer Detail-UI."""
    _seed(db)
    row = db.query(LaborAuftragEntry).filter(LaborAuftragEntry.id == entry_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Labor-Auftrag nicht gefunden")
    return _auftrag_to_dict(row)


@router.post("/labor-auftraege", response_model=dict, status_code=201, summary="Labor auftrag anlegen")
async def create_labor_auftrag(body: LaborAuftragCreate, db: Session = Depends(get_db)) -> dict:
    """Neuen Labor-Auftrag anlegen (Wizard `labor-auftrag.tsx`)."""
    _seed(db)
    parsed = body
    chargen = (parsed.chargenId or parsed.chargen_id or "").strip()
    if not chargen:
        raise HTTPException(status_code=422, detail="chargenId erforderlich")
    labor_name = (parsed.labor or "").strip()
    if not labor_name:
        raise HTTPException(status_code=422, detail="labor erforderlich")

    analysen_list = parsed.analysen if isinstance(parsed.analysen, list) else []
    n_analysen = len(analysen_list)

    status = "in-bearbeitung" if (parsed.prioritaet or "").lower() == "express" else "offen"
    now = datetime.now(timezone.utc)
    entry = LaborAuftragEntry(
        chargen_id=chargen,
        labor=labor_name,
        analysen=n_analysen,
        auftragsdatum=now,
        status=status,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _auftrag_to_dict(entry)


@router.get("/stats", response_model=dict, summary="Labor stats abrufen")
async def get_labor_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(LaborProbe).all()
    return {
        "abgeschlossen": sum(1 for p in items if p.status == "abgeschlossen"),
        "in-bearbeitung": sum(1 for p in items if p.status == "in-bearbeitung"),
        "ausstehend": sum(1 for p in items if p.status == "ausstehend"),
    }
