"""
Tours API - Verladung/Tour Management
RESTful API for Tours with Stops, Delivery Notes, and Events
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.core.database import get_db
from app.domains.verladung.repository import (
    TourRepository,
    TourStopRepository,
    TourDeliveryNoteRepository,
    TourEventRepository
)
from app.domains.verladung.models import (
    TourStatus, StopStatus, DeliveryNoteStatus, EventType
)

router = APIRouter(prefix="/tours", tags=["Verladung", "Tours"])


# === Pydantic Schemas ===

class DriverInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    name: Optional[str] = None


class VehicleInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    plate: Optional[str] = None
    type: Optional[str] = None


class CustomerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    name: Optional[str] = None


class DropoffInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address_id: Optional[str] = None
    label: Optional[str] = None
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class TimeWindow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_: Optional[datetime] = None
    to: Optional[datetime] = None


class DeliveryNoteReference(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: Optional[str] = None
    customer_ref: Optional[str] = None


class ItemsSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lines: Optional[int] = None
    pieces: Optional[int] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None


class DeliveryNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dn_no: str
    status: str
    created_at: Optional[datetime] = None
    reference: Optional[DeliveryNoteReference] = None
    items_summary: Optional[ItemsSummary] = None


class StopTotals(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    delivery_notes: int = 0
    pieces: int = 0
    weight_kg: float = 0
    volume_m3: float = 0


class StopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sequence: int
    status: str
    customer: Optional[CustomerInfo] = None
    dropoff: Optional[DropoffInfo] = None
    time_window: Optional[TimeWindow] = None
    delivery_notes: List[DeliveryNoteResponse] = []
    totals: StopTotals = StopTotals()


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[str] = None
    name: Optional[str] = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    at: datetime
    type: str
    by: Optional[UserInfo] = None


class TourTotals(BaseModel):
    stops: int = 0
    delivery_notes: int = 0
    pieces: int = 0
    weight_kg: float = 0
    volume_m3: float = 0


class TourResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tour_no: str
    date: datetime
    week: Optional[str] = None
    type: str
    status: str
    driver: Optional[DriverInfo] = None
    vehicle: Optional[VehicleInfo] = None
    planned_departure_at: Optional[datetime] = None
    actual_departure_at: Optional[datetime] = None
    notes: Optional[str] = None
    stops: List[StopResponse] = []
    totals: TourTotals = TourTotals()
    events: List[EventResponse] = []

class CreateTourRequest(BaseModel):
    date: datetime
    type: Optional[str] = "stueckgut"
    driver_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    planned_departure_at: Optional[datetime] = None
    notes: Optional[str] = None


class CreateStopRequest(BaseModel):
    sequence: Optional[int] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    address_id: Optional[str] = None
    address_label: Optional[str] = None
    street: Optional[str] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "DE"
    time_window_from: Optional[datetime] = None
    time_window_to: Optional[datetime] = None
    notes: Optional[str] = None


class AssignDeliveryNotesRequest(BaseModel):
    delivery_note_ids: List[str]


# === TOUR ENDPOINTS ===

@router.get("", response_model=List[TourResponse])
async def list_tours(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """List all tours with optional filtering"""
    repo = TourRepository(db)
    tours = repo.get_all(
        skip=skip, limit=limit, status=status,
        date_from=date_from, date_to=date_to
    )
    return tours


@router.get("/week/{week}", response_model=List[TourResponse])
async def get_tours_by_week(week: str, db: Session = Depends(get_db)):
    """Get all tours for a specific week (e.g., 2026-W07)"""
    repo = TourRepository(db)
    return repo.get_by_week(week)


@router.get("/today", response_model=List[TourResponse])
async def get_today_tours(db: Session = Depends(get_db)):
    """Get all tours for today"""
    repo = TourRepository(db)
    _today = datetime.utcnow().date()  # noqa: F841
    # Create a date object for comparison
    from datetime import date
    today_date = date.today()
    return repo.get_by_date(today_date)


@router.get("/{tour_id}", response_model=TourResponse)
async def get_tour(tour_id: str, db: Session = Depends(get_db)):
    """Get a single tour with all details"""
    tour_repo = TourRepository(db)
    stop_repo = TourStopRepository(db)
    event_repo = TourEventRepository(db)
    dn_repo = TourDeliveryNoteRepository(db)
    
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    # Load stops with delivery notes
    stops = stop_repo.get_all(tour_id)
    for stop in stops:
        stop.delivery_notes = dn_repo.get_all(stop.id)
    
    # Load events
    events = event_repo.get_all(tour_id)
    
    return {
        **tour.__dict__,
        "stops": stops,
        "events": events
    }


@router.post("", response_model=TourResponse, status_code=201)
async def create_tour(
    tour_data: CreateTourRequest,
    db: Session = Depends(get_db)
):
    """Create a new tour"""
    repo = TourRepository(db)
    
    data = tour_data.model_dump()
    
    # Calculate week from date
    if data.get("date"):
        week = data["date"].isocalendar()
        data["week"] = f"{week[0]}-W{week[1]:02d}"
    
    tour = repo.create(data)
    return tour


@router.patch("/{tour_id}", response_model=TourResponse)
async def update_tour(
    tour_id: str,
    tour_data: dict,
    db: Session = Depends(get_db)
):
    """Update a tour"""
    repo = TourRepository(db)
    tour = repo.update(tour_id, tour_data)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.delete("/{tour_id}", status_code=204)
async def delete_tour(tour_id: str, db: Session = Depends(get_db)):
    """Delete a tour"""
    repo = TourRepository(db)
    if not repo.delete(tour_id):
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")


# === STATUS ENDPOINTS ===

@router.post("/{tour_id}/start-loading", response_model=TourResponse)
async def start_loading(
    tour_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    db: Session = Depends(get_db)
):
    """Mark tour as loading"""
    repo = TourRepository(db)
    tour = repo.start_loading(tour_id, user_id, user_name)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.post("/{tour_id}/finish-loading", response_model=TourResponse)
async def finish_loading(
    tour_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    db: Session = Depends(get_db)
):
    """Mark loading as finished, tour in transit"""
    repo = TourRepository(db)
    tour = repo.finish_loading(tour_id, user_id, user_name)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.post("/{tour_id}/dispatch", response_model=TourResponse)
async def dispatch_tour(
    tour_id: str,
    user_id: str = Query(...),
    user_name: str = Query(...),
    db: Session = Depends(get_db)
):
    """Dispatch a tour (mark as dispatched and departed)"""
    repo = TourRepository(db)
    tour = repo.dispatch(tour_id, user_id, user_name)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


# === STOP ENDPOINTS ===

@router.get("/{tour_id}/stops", response_model=List[StopResponse])
async def list_stops(tour_id: str, db: Session = Depends(get_db)):
    """List all stops for a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourStopRepository(db)
    return repo.get_all(tour_id)


@router.post("/{tour_id}/stops", response_model=StopResponse, status_code=201)
async def create_stop(
    tour_id: str,
    stop_data: CreateStopRequest,
    db: Session = Depends(get_db)
):
    """Create a new stop on a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourStopRepository(db)
    data = stop_data.model_dump()
    data["tour_id"] = tour_id
    
    stop = repo.create(data)
    return stop


@router.post("/{tour_id}/stops/{stop_id}/delivery-notes", response_model=List[DeliveryNoteResponse])
async def assign_delivery_notes(
    tour_id: str,
    stop_id: str,
    data: AssignDeliveryNotesRequest,
    db: Session = Depends(get_db)
):
    """Assign delivery notes to a stop"""
    dn_repo = TourDeliveryNoteRepository(db)
    dns = dn_repo.assign_to_stop(tour_id, stop_id, data.delivery_note_ids)
    return dns


@router.post("/{tour_id}/stops/{stop_id}/deliver", response_model=DeliveryNoteResponse)
async def mark_delivered(
    tour_id: str,
    stop_id: str,
    delivery_note_id: str,
    db: Session = Depends(get_db)
):
    """Mark a delivery note as delivered"""
    dn_repo = TourDeliveryNoteRepository(db)
    dn = dn_repo.mark_delivered(delivery_note_id)
    if not dn:
        raise HTTPException(status_code=404, detail=f"Delivery note {delivery_note_id} not found")
    return dn


# === EVENTS ENDPOINTS ===

@router.get("/{tour_id}/events", response_model=List[EventResponse])
async def list_events(tour_id: str, db: Session = Depends(get_db)):
    """List all events for a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourEventRepository(db)
    return repo.get_all(tour_id)
