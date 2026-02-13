"""
Fuhrpark API Endpoints - SQLAlchemy Version
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import FahrzeugRepository, FahrerRepository, FahrzeugTourRepository
from app.domains.operations.models import Fahrzeug, Fahrer, FahrzeugTour

router = APIRouter(prefix="/fuhrpark", tags=["Fuhrpark"])


# === FAHRZEUG ENDPOINTS ===

@router.get("/fahrzeuge", response_model=List[dict])
async def list_fahrzeuge(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Fahrzeuge with optional filtering"""
    repo = FahrzeugRepository(db)
    if status:
        return repo.get_by_status(status)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/fahrzeuge/{fahrzeug_id}", response_model=dict)
async def get_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    """Get a single Fahrzeug by ID"""
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return fahrzeug


@router.post("/fahrzeuge", response_model=dict, status_code=201)
async def create_fahrzeug(
    fahrzeug_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Fahrzeug"""
    repo = FahrzeugRepository(db)
    
    # Check for duplicate Kennzeichen
    existing = repo.get_by_kennzeichen(fahrzeug_data.get("kennzeichen", ""))
    if existing:
        raise HTTPException(status_code=400, detail="Kennzeichen already exists")
    
    try:
        fahrzeug = repo.create(fahrzeug_data)
        return fahrzeug
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/fahrzeuge/{fahrzeug_id}", response_model=dict)
async def update_fahrzeug(
    fahrzeug_id: str,
    fahrzeug_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Fahrzeug"""
    repo = FahrzeugRepository(db)
    fahrzeug = repo.update(fahrzeug_id, fahrzeug_data)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return fahrzeug


@router.delete("/fahrzeuge/{fahrzeug_id}", status_code=204)
async def delete_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    """Delete a Fahrzeug"""
    repo = FahrzeugRepository(db)
    if not repo.delete(fahrzeug_id):
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")


# === FAHRER ENDPOINTS ===

@router.get("/fahrer", response_model=List[dict])
async def list_fahrer(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Fahrer with optional filtering"""
    repo = FahrerRepository(db)
    if status:
        return repo.get_by_status(status)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/fahrer/{fahrer_id}", response_model=dict)
async def get_fahrer(fahrer_id: str, db: Session = Depends(get_db)):
    """Get a single Fahrer by ID"""
    repo = FahrerRepository(db)
    fahrer = repo.get_by_id(fahrer_id)
    if not fahrer:
        raise HTTPException(status_code=404, detail=f"Fahrer {fahrer_id} not found")
    return fahrer


@router.post("/fahrer", response_model=dict, status_code=201)
async def create_fahrer(
    fahrer_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Fahrer"""
    repo = FahrerRepository(db)
    
    # Check for duplicate Personalnummer
    if fahrer_data.get("personalnummer"):
        existing = repo.get_by_personalnummer(fahrer_data["personalnummer"])
        if existing:
            raise HTTPException(status_code=400, detail="Personalnummer already exists")
    
    try:
        fahrer = repo.create(fahrer_data)
        return fahrer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/fahrer/{fahrer_id}", response_model=dict)
async def update_fahrer(
    fahrer_id: str,
    fahrer_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Fahrer"""
    repo = FahrerRepository(db)
    fahrer = repo.update(fahrer_id, fahrer_data)
    if not fahrer:
        raise HTTPException(status_code=404, detail=f"Fahrer {fahrer_id} not found")
    return fahrer


@router.delete("/fahrer/{fahrer_id}", status_code=204)
async def delete_fahrer(fahrer_id: str, db: Session = Depends(get_db)):
    """Delete a Fahrer"""
    repo = FahrerRepository(db)
    if not repo.delete(fahrer_id):
        raise HTTPException(status_code=404, detail=f"Fahrer {fahrer_id} not found")


# === TOUR ENDPOINTS ===

@router.get("/touren", response_model=List[dict])
async def list_touren(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    fahrzeug_id: Optional[str] = None,
    fahrer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all Touren with optional filtering"""
    repo = FahrzeugTourRepository(db)
    
    if fahrzeug_id:
        return repo.get_by_fahrzeug(fahrzeug_id)
    if fahrer_id:
        return repo.get_by_fahrer(fahrer_id)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/touren/{tour_id}", response_model=dict)
async def get_tour(tour_id: str, db: Session = Depends(get_db)):
    """Get a single Tour by ID"""
    repo = FahrzeugTourRepository(db)
    tour = repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.post("/touren", response_model=dict, status_code=201)
async def create_tour(
    tour_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new Tour"""
    repo = FahrzeugTourRepository(db)
    try:
        tour = repo.create(tour_data)
        return tour
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/touren/{tour_id}", response_model=dict)
async def update_tour(
    tour_id: str,
    tour_data: dict,
    db: Session = Depends(get_db)
):
    """Update a Tour"""
    repo = FahrzeugTourRepository(db)
    tour = repo.update(tour_id, tour_data)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.delete("/touren/{tour_id}", status_code=204)
async def delete_tour(tour_id: str, db: Session = Depends(get_db)):
    """Delete a Tour"""
    repo = FahrzeugTourRepository(db)
    if not repo.delete(tour_id):
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
