"""Marketing API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import MarketingKampagneEntry

router = APIRouter(prefix="/marketing", tags=["Marketing"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _seed(db: Session) -> None:
    if db.query(MarketingKampagneEntry).count() > 0:
        return
    db.add_all(
        [
            MarketingKampagneEntry(
                name="Herbst-Aktion Weizen",
                typ="E-Mail",
                zielgruppe="Landwirte",
                startdatum=datetime(2025, 10, 1),
                enddatum=datetime(2025, 10, 31),
                budget=2500,
                status="beendet",
            ),
            MarketingKampagneEntry(
                name="Fruehjahrs-Duenger-Kampagne",
                typ="Newsletter",
                zielgruppe="Ackerbau",
                startdatum=datetime(2026, 2, 15),
                enddatum=datetime(2026, 3, 31),
                budget=3000,
                status="aktiv",
            ),
        ]
    )
    db.commit()


@router.get("/kampagnen", response_model=dict)
async def list_kampagnen(status: Optional[str] = Query(None, description="Filter by status"), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    query = db.query(MarketingKampagneEntry)
    if status:
        query = query.filter(MarketingKampagneEntry.status == status)
    items = query.order_by(MarketingKampagneEntry.startdatum.desc()).all()
    return {
        "items": [
            {
                "id": i.id,
                "name": i.name,
                "typ": i.typ,
                "zielgruppe": i.zielgruppe,
                "startdatum": _dt(i.startdatum),
                "enddatum": _dt(i.enddatum),
                "budget": float(i.budget or 0),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/stats", response_model=dict)
async def get_marketing_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(MarketingKampagneEntry).all()
    return {
        "aktiv": sum(1 for k in items if k.status == "aktiv"),
        "geplant": sum(1 for k in items if k.status == "geplant"),
        "beendet": sum(1 for k in items if k.status == "beendet"),
        "budget_aktiv": sum(float(k.budget or 0) for k in items if k.status == "aktiv"),
    }
