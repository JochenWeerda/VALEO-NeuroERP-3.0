"""
Waage API Endpoints - SQLAlchemy Version
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect as sa_inspect

from app.core.database import get_db
from app.domains.operations.repository import WaageRepository, WiegungRepository
from app.domains.operations.models import Waage, Wiegung

router = APIRouter(prefix="/waage", tags=["Waage"])


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_dict(model: Any) -> dict:
    if model is None:
        return {}
    mapper = sa_inspect(model.__class__)
    data = {}
    for column in mapper.columns:
        key = column.key
        data[key] = _serialize_value(getattr(model, key))
    return data


def _to_list(models: List[Any]) -> List[dict]:
    return [_to_dict(model) for model in models]


# === WAAGE ENDPOINTS ===

@router.get("/waagen", response_model=List[dict])
async def list_waagen(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Waagen with optional filtering"""
    repo = WaageRepository(db)
    if status:
        return _to_list(repo.get_by_status(status))
    return _to_list(repo.get_all(skip=skip, limit=limit))


@router.get("/waagen/{waage_id}", response_model=dict)
async def get_waage(waage_id: str, db: Session = Depends(get_db)):
    """Get a single Waage by ID"""
    repo = WaageRepository(db)
    waage = repo.get_by_id(waage_id)
    if not waage:
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")
    return _to_dict(waage)


@router.post("/waagen", response_model=dict, status_code=201)
async def create_waage(
    waage_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Waage"""
    repo = WaageRepository(db)
    try:
        waage = repo.create(waage_data)
        return _to_dict(waage)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/waagen/{waage_id}", response_model=dict)
async def update_waage(
    waage_id: str,
    waage_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Waage"""
    repo = WaageRepository(db)
    waage = repo.update(waage_id, waage_data)
    if not waage:
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")
    return _to_dict(waage)


@router.delete("/waagen/{waage_id}", status_code=204)
async def delete_waage(waage_id: str, db: Session = Depends(get_db)):
    """Delete a Waage"""
    repo = WaageRepository(db)
    if not repo.delete(waage_id):
        raise HTTPException(status_code=404, detail=f"Waage {waage_id} not found")


# === WIEGUNG ENDPOINTS ===

@router.get("/wiegungen", response_model=List[dict])
async def list_wiegungen(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    waage_id: Optional[str] = None,
    kennzeichen: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Wiegungen with optional filtering"""
    repo = WiegungRepository(db)
    
    if waage_id:
        return _to_list(repo.get_by_waage(waage_id))
    if kennzeichen:
        return _to_list(repo.get_by_kennzeichen(kennzeichen))
    return _to_list(repo.get_all(skip=skip, limit=limit))


@router.get("/wiegungen/{wiegung_id}", response_model=dict)
async def get_wiegung(wiegung_id: str, db: Session = Depends(get_db)):
    """Get a single Wiegung by ID"""
    repo = WiegungRepository(db)
    wiegung = repo.get_by_id(wiegung_id)
    if not wiegung:
        raise HTTPException(status_code=404, detail=f"Wiegung {wiegung_id} not found")
    return _to_dict(wiegung)


@router.post("/wiegungen", response_model=dict, status_code=201)
async def create_wiegung(
    wiegung_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Wiegung"""
    repo = WiegungRepository(db)
    
    # Auto-calculate netto if not provided
    if "brutto" in wiegung_data and "tara" in wiegung_data and "netto" not in wiegung_data:
        wiegung_data["netto"] = wiegung_data["brutto"] - wiegung_data["tara"]
    
    try:
        wiegung = repo.create(wiegung_data)
        return _to_dict(wiegung)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/wiegungen/{wiegung_id}", status_code=204)
async def delete_wiegung(wiegung_id: str, db: Session = Depends(get_db)):
    """Delete a Wiegung"""
    repo = WiegungRepository(db)
    if not repo.delete(wiegung_id):
        raise HTTPException(status_code=404, detail=f"Wiegung {wiegung_id} not found")
