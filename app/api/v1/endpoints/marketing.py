"""Marketing API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import MarketingKampagneEntry

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.marketing_schemas import MarketingOut


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


@router.get("/kampagnen", response_model=MarketingOut, summary="Kampagnen auflisten")
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


@router.get("/stats", response_model=MarketingOut, summary="Marketing stats abrufen")
async def get_marketing_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(MarketingKampagneEntry).all()
    return {
        "aktiv": sum(1 for k in items if k.status == "aktiv"),
        "geplant": sum(1 for k in items if k.status == "geplant"),
        "beendet": sum(1 for k in items if k.status == "beendet"),
        "budget_aktiv": sum(float(k.budget or 0) for k in items if k.status == "aktiv"),
    }


@router.get("/kampagnen/{kampagne_id}/kpis", response_model=MarketingOut, summary="Kampagne kpis abrufen")
async def get_kampagne_kpis(kampagne_id: int, db: Session = Depends(get_db)) -> dict:
    """MKT-CAM-01: Kampagnen-KPIs (Budget Plan vs. Ist, Open-Rate, ROI-Stub)."""
    _seed(db)
    k = db.query(MarketingKampagneEntry).filter(MarketingKampagneEntry.id == kampagne_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    budget_plan = float(k.budget or 0)
    return {
        "id": k.id,
        "name": k.name,
        "status": k.status,
        "budget_plan": budget_plan,
        "budget_ist": budget_plan * 0.0,
        "open_rate": None,
        "click_rate": None,
        "conversion_rate": None,
        "roi": None,
    }


# --------------- Pydantic Schemas ---------------
from pydantic import BaseModel
from datetime import date


class MarketingKampagneCreate(BaseModel):
    name: str
    typ: str
    zielgruppe: str
    startdatum: date
    enddatum: Optional[date] = None
    budget: float = 0
    status: str = "geplant"


class MarketingKampagneUpdate(BaseModel):
    name: Optional[str] = None
    typ: Optional[str] = None
    zielgruppe: Optional[str] = None
    startdatum: Optional[date] = None
    enddatum: Optional[date] = None
    budget: Optional[float] = None
    status: Optional[str] = None


# --------------- POST / PUT / DELETE ---------------
from starlette.responses import Response


@router.post("/kampagnen", response_model=MarketingOut, status_code=201, summary="Kampagne anlegen")
async def create_kampagne(
    body: MarketingKampagneCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new marketing campaign."""
    kampagne = MarketingKampagneEntry(
        name=body.name,
        typ=body.typ,
        zielgruppe=body.zielgruppe,
        startdatum=datetime.combine(body.startdatum, datetime.min.time()),
        enddatum=datetime.combine(body.enddatum, datetime.min.time()) if body.enddatum else None,
        budget=body.budget,
        status=body.status,
    )
    db.add(kampagne)
    db.commit()
    db.refresh(kampagne)
    return {
        "id": kampagne.id,
        "name": kampagne.name,
        "typ": kampagne.typ,
        "zielgruppe": kampagne.zielgruppe,
        "startdatum": _dt(kampagne.startdatum),
        "enddatum": _dt(kampagne.enddatum),
        "budget": float(kampagne.budget or 0),
        "status": kampagne.status,
    }


@router.put("/kampagnen/{kampagne_id}", response_model=MarketingOut, summary="Kampagne aktualisieren")
async def update_kampagne(
    kampagne_id: int,
    body: MarketingKampagneUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update an existing marketing campaign."""
    k = db.query(MarketingKampagneEntry).filter(MarketingKampagneEntry.id == kampagne_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    update_data = body.model_dump(exclude_unset=True)
    if "startdatum" in update_data and update_data["startdatum"] is not None:
        update_data["startdatum"] = datetime.combine(update_data["startdatum"], datetime.min.time())
    if "enddatum" in update_data and update_data["enddatum"] is not None:
        update_data["enddatum"] = datetime.combine(update_data["enddatum"], datetime.min.time())
    for field, value in update_data.items():
        setattr(k, field, value)
    db.commit()
    db.refresh(k)
    return {
        "id": k.id,
        "name": k.name,
        "typ": k.typ,
        "zielgruppe": k.zielgruppe,
        "startdatum": _dt(k.startdatum),
        "enddatum": _dt(k.enddatum),
        "budget": float(k.budget or 0),
        "status": k.status,
    }


@router.delete("/kampagnen/{kampagne_id}", response_class=Response, status_code=204, response_model=None, summary="Kampagne löschen")
async def delete_kampagne(
    kampagne_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Delete a marketing campaign."""
    k = db.query(MarketingKampagneEntry).filter(MarketingKampagneEntry.id == kampagne_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    db.delete(k)
    db.commit()
    return Response(status_code=204)
