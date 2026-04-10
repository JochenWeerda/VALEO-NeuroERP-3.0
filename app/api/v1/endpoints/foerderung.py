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


# --------------- Pydantic Schemas ---------------
from pydantic import BaseModel
from datetime import date


class FoerderAntragCreate(BaseModel):
    nummer: str
    programm: str
    antragsdatum: date
    flaeche: float = 0
    betrag: float = 0
    status: str = "entwurf"


class FoerderAntragUpdate(BaseModel):
    programm: Optional[str] = None
    antragsdatum: Optional[date] = None
    flaeche: Optional[float] = None
    betrag: Optional[float] = None
    status: Optional[str] = None


# --------------- POST / PUT ---------------
from fastapi import HTTPException


@router.post("/antraege", response_model=dict, status_code=201)
async def create_antrag(
    body: FoerderAntragCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new Foerderantrag."""
    antrag = FoerderAntrag(
        nummer=body.nummer,
        programm=body.programm,
        antragsdatum=datetime.combine(body.antragsdatum, datetime.min.time()),
        flaeche=body.flaeche,
        betrag=body.betrag,
        status=body.status,
    )
    db.add(antrag)
    db.commit()
    db.refresh(antrag)
    return {
        "id": antrag.id,
        "nummer": antrag.nummer,
        "programm": antrag.programm,
        "antragsdatum": _dt(antrag.antragsdatum),
        "flaeche": float(antrag.flaeche or 0),
        "betrag": float(antrag.betrag or 0),
        "status": antrag.status,
    }


@router.put("/antraege/{antrag_id}", response_model=dict)
async def update_antrag(
    antrag_id: int,
    body: FoerderAntragUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update an existing Foerderantrag."""
    antrag = db.query(FoerderAntrag).filter(FoerderAntrag.id == antrag_id).first()
    if not antrag:
        raise HTTPException(status_code=404, detail="Antrag nicht gefunden")
    update_data = body.model_dump(exclude_unset=True)
    if "antragsdatum" in update_data and update_data["antragsdatum"] is not None:
        update_data["antragsdatum"] = datetime.combine(update_data["antragsdatum"], datetime.min.time())
    for field, value in update_data.items():
        setattr(antrag, field, value)
    db.commit()
    db.refresh(antrag)
    return {
        "id": antrag.id,
        "nummer": antrag.nummer,
        "programm": antrag.programm,
        "antragsdatum": _dt(antrag.antragsdatum),
        "flaeche": float(antrag.flaeche or 0),
        "betrag": float(antrag.betrag or 0),
        "status": antrag.status,
    }
