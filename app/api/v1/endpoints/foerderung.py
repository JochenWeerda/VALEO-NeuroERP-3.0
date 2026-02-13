"""Foerderung API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import FoerderAntrag

router = APIRouter(prefix="/foerderung", tags=["Foerderung"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _seed(db: Session) -> None:
    if db.query(FoerderAntrag).count() > 0:
        return
    db.add_all(
        [
            FoerderAntrag(
                nummer="FA-2026-001",
                programm="Greening",
                antragsdatum=datetime(2026, 3, 15),
                flaeche=250,
                betrag=21250,
                status="bewilligt",
            ),
            FoerderAntrag(
                nummer="FA-2026-002",
                programm="Junglandwirte",
                antragsdatum=datetime(2026, 4, 1),
                flaeche=120,
                betrag=15000,
                status="eingereicht",
            ),
        ]
    )
    db.commit()


@router.get("/antraege", response_model=dict)
async def list_antraege(status: Optional[str] = Query(None, description="Filter by status"), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    query = db.query(FoerderAntrag)
    if status:
        query = query.filter(FoerderAntrag.status == status)
    items = query.order_by(FoerderAntrag.antragsdatum.desc()).all()
    payload = [
        {
            "id": i.id,
            "nummer": i.nummer,
            "programm": i.programm,
            "antragsdatum": _dt(i.antragsdatum),
            "flaeche": float(i.flaeche or 0),
            "betrag": float(i.betrag or 0),
            "status": i.status,
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "sum_betrag": sum(i["betrag"] for i in payload),
    }


@router.get("/stats", response_model=dict)
async def get_foerderung_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(FoerderAntrag).all()
    return {
        "bewilligt": sum(1 for a in items if a.status == "bewilligt"),
        "eingereicht": sum(1 for a in items if a.status == "eingereicht"),
        "entwurf": sum(1 for a in items if a.status == "entwurf"),
        "betrag_bewilligt": sum(float(a.betrag or 0) for a in items if a.status == "bewilligt"),
    }
