"""Labor API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import LaborProbe, LaborAuftragEntry

router = APIRouter(prefix="/labor", tags=["Labor"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _seed(db: Session) -> None:
    if db.query(LaborProbe).count() == 0:
        db.add_all(
            [
                LaborProbe(
                    probennummer="LB-2026-001",
                    typ="Qualitaetspruefung",
                    artikel="Weizen Premium",
                    datum=datetime(2026, 2, 10),
                    labor="Lufa Nord-West",
                    status="abgeschlossen",
                ),
                LaborProbe(
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
                    chargen_id="251011-WEI-001",
                    labor="Lufa Nord-West",
                    analysen=4,
                    auftragsdatum=datetime(2026, 2, 10),
                    status="in-bearbeitung",
                ),
                LaborAuftragEntry(
                    chargen_id="251010-RAP-002",
                    labor="SGS",
                    analysen=6,
                    auftragsdatum=datetime(2026, 2, 9),
                    status="abgeschlossen",
                ),
            ]
        )
    db.commit()


@router.get("/proben", response_model=dict)
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


@router.get("/labor-auftraege", response_model=dict)
async def list_labor_auftraege(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(LaborAuftragEntry).order_by(LaborAuftragEntry.auftragsdatum.desc()).all()
    return {
        "items": [
            {
                "id": i.id,
                "chargen_id": i.chargen_id,
                "labor": i.labor,
                "analysen": int(i.analysen or 0),
                "auftragsdatum": _dt(i.auftragsdatum),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/stats", response_model=dict)
async def get_labor_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(LaborProbe).all()
    return {
        "abgeschlossen": sum(1 for p in items if p.status == "abgeschlossen"),
        "in-bearbeitung": sum(1 for p in items if p.status == "in-bearbeitung"),
        "ausstehend": sum(1 for p in items if p.status == "ausstehend"),
    }
