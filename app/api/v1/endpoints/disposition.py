"""Disposition API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import DispositionPosition

router = APIRouter(prefix="/disposition", tags=["Disposition"])


def _seed(db: Session) -> None:
    if db.query(DispositionPosition).count() > 0:
        return
    db.add_all(
        [
            DispositionPosition(
                artikel="Weizen Premium",
                artikel_id="ART-001",
                bestand=120,
                mindestbestand=200,
                bedarf=80,
                empfehlung="Nachbestellen: 100 t",
                prioritaet="hoch",
            ),
            DispositionPosition(
                artikel="Raps",
                artikel_id="ART-002",
                bestand=85,
                mindestbestand=100,
                bedarf=15,
                empfehlung="Nachbestellen: 50 t",
                prioritaet="mittel",
            ),
            DispositionPosition(
                artikel="NPK 15-15-15",
                artikel_id="ART-003",
                bestand=250,
                mindestbestand=150,
                bedarf=0,
                empfehlung="Ausreichend",
                prioritaet="niedrig",
            ),
        ]
    )
    db.commit()


@router.get("", response_model=dict)
async def list_disposition(
    prioritaet: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> dict:
    _seed(db)
    query = db.query(DispositionPosition)
    if prioritaet:
        query = query.filter(DispositionPosition.prioritaet == prioritaet)

    items = query.limit(limit).all()
    payload = [
        {
            "id": i.id,
            "artikel": i.artikel,
            "artikel_id": i.artikel_id,
            "bestand": float(i.bestand or 0),
            "mindestbestand": float(i.mindestbestand or 0),
            "bedarf": float(i.bedarf or 0),
            "empfehlung": i.empfehlung,
            "prioritaet": i.prioritaet,
        }
        for i in items
    ]

    return {
        "items": payload,
        "total": len(payload),
        "sum_bedarf": sum(d["bedarf"] for d in payload),
        "sum_bestand": sum(d["bestand"] for d in payload),
    }


@router.get("/stats", response_model=dict)
async def get_disposition_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    all_items = db.query(DispositionPosition).all()
    hoch = sum(1 for d in all_items if d.prioritaet == "hoch")
    mittel = sum(1 for d in all_items if d.prioritaet == "mittel")
    niedrig = sum(1 for d in all_items if d.prioritaet == "niedrig")

    nachbestellen = [d for d in all_items if float(d.bestand or 0) < float(d.mindestbestand or 0)]

    return {
        "total_positionen": len(all_items),
        "nachbestellen_anzahl": len(nachbestellen),
        "nachbestellen_wert": sum((float(d.mindestbestand or 0) - float(d.bestand or 0)) * 500 for d in nachbestellen),
        "nach_kategorie": {
            "hoch": hoch,
            "mittel": mittel,
            "niedrig": niedrig,
        },
        "generated_at": datetime.utcnow().isoformat(),
    }
