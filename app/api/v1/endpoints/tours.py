"""
Tours API - Verladung/Tour Management
RESTful API for Tours with Stops, Delivery Notes, and Events
"""

from typing import Optional, List
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.core.database import get_db
from app.core.business_time import business_today
from app.core.tenant import get_tenant_id
from app.auth.deps import get_current_user, anmeldename
from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.domains.verladung.models import EventType
from app.domains.verladung.repository import (
    TourRepository,
    TourStopRepository,
    TourDeliveryNoteRepository,
    TourEventRepository
)
from app.infrastructure.eventbus.outbox import OutboxPublisher

from app.api.v1.schemas.base import BaseSchema
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


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

@router.get("", response_model=List[TourResponse], summary="Tours auflisten")
async def list_tours(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """List all tours with optional filtering"""
    repo = TourRepository(db, tenant_id)
    tours = repo.get_all(
        skip=skip, limit=limit, status=status,
        date_from=date_from, date_to=date_to
    )
    return tours


@router.get("/week/{week}", response_model=List[TourResponse], summary="Tours by week abrufen")
async def get_tours_by_week(week: str, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """Get all tours for a specific week (e.g., 2026-W07)"""
    repo = TourRepository(db, tenant_id)
    return repo.get_by_week(week)


@router.get("/today", response_model=List[TourResponse], summary="Today tours abrufen")
async def get_today_tours(db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """Get all tours for today"""
    repo = TourRepository(db, tenant_id)
    return repo.get_by_date(business_today())


@router.get("/{tour_id}", response_model=TourResponse, summary="Tour abrufen")
async def get_tour(tour_id: str, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """Get a single tour with all details"""
    tour_repo = TourRepository(db, tenant_id)
    stop_repo = TourStopRepository(db, tenant_id)
    event_repo = TourEventRepository(db, tenant_id)
    dn_repo = TourDeliveryNoteRepository(db, tenant_id)
    
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    # Load stops with delivery notes
    stops = stop_repo.get_all(tour_id)
    stops = [{**stop.__dict__, "delivery_notes": dn_repo.get_all(stop.id)} for stop in stops]
    
    # Load events
    events = event_repo.get_all(tour_id)
    
    return {
        **tour.__dict__,
        "stops": stops,
        "events": events
    }


@router.post("", response_model=TourResponse, status_code=201, summary="Tour anlegen", dependencies=SCHREIBEN["LOGISTIK"])
async def create_tour(
    tour_data: CreateTourRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new tour"""
    repo = TourRepository(db, tenant_id)
    
    data = tour_data.model_dump()
    
    # Calculate week from date
    if data.get("date"):
        week = data["date"].isocalendar()
        data["week"] = f"{week[0]}-W{week[1]:02d}"
    
    tour = repo.create(data)
    return tour


@router.patch("/{tour_id}", response_model=TourResponse, summary="Tour aktualisieren", dependencies=SCHREIBEN["LOGISTIK"])
async def update_tour(
    tour_id: str,
    tour_data: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update a tour"""
    repo = TourRepository(db, tenant_id)
    allowed = set(CreateTourRequest.model_fields) | {"tour_no"}
    if set(tour_data) - allowed:
        raise HTTPException(status_code=422, detail="Unsupported or managed tour fields")
    tour = repo.update(tour_id, tour_data)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


@router.delete("/{tour_id}", status_code=204, response_class=Response, response_model=None, summary="Tour löschen", dependencies=SCHREIBEN["LOGISTIK"])
async def delete_tour(tour_id: str, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """Delete a tour"""
    repo = TourRepository(db, tenant_id)
    if not repo.delete(tour_id):
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")


# === STATUS ENDPOINTS ===

async def _publish_loading_outbox(
    db: Session,
    *,
    tour_id: str,
    event_type: str,
    user_id: str,
    user_name: str,
    tenant_id: str,
) -> None:
    """Gleicher Outbox+SSE-Pfad wie weighing_tickets / disposition assignment."""
    outbox = OutboxPublisher(db, get_event_publisher())
    await outbox.store_event(
        IntegrationEvent(
            aggregate_id=tour_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            payload={
                "id": tour_id,
                "tour_id": tour_id,
                "user_id": user_id,
                "user_name": user_name,
            },
        ),
        tenant_id=tenant_id,
        mirror_on_store=False,
    )


@router.post("/{tour_id}/start-loading", response_model=TourResponse, summary="Loading starten", dependencies=SCHREIBEN["LOGISTIK"])
async def start_loading(
    tour_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Authenticated loading transition; status, audit and outbox commit together."""
    user_id = current_user.get("sub")
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(status_code=401, detail="Verified actor required")
    user_name = anmeldename(current_user)
    try:
        repo = TourRepository(db, tenant_id)
        tour = repo.start_loading(tour_id, user_id, user_name, commit=False)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        await _publish_loading_outbox(
            db, tour_id=tour_id, event_type=EventType.LOADING_STARTED.value,
            user_id=user_id, user_name=user_name, tenant_id=tenant_id,
        )
        db.commit()
        db.refresh(tour)
        return tour
    except Exception:
        db.rollback()
        raise


@router.post("/{tour_id}/finish-loading", response_model=TourResponse, summary="Loading finish", dependencies=SCHREIBEN["LOGISTIK"])
async def finish_loading(
    tour_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Authenticated loading transition; status, audit and outbox commit together."""
    user_id = current_user.get("sub")
    if not isinstance(user_id, str) or not user_id.strip():
        raise HTTPException(status_code=401, detail="Verified actor required")
    user_name = anmeldename(current_user)
    try:
        repo = TourRepository(db, tenant_id)
        tour = repo.finish_loading(tour_id, user_id, user_name, commit=False)
        if not tour:
            raise HTTPException(status_code=404, detail="Tour not found")
        await _publish_loading_outbox(
            db, tour_id=tour_id, event_type=EventType.LOADING_FINISHED.value,
            user_id=user_id, user_name=user_name, tenant_id=tenant_id,
        )
        db.commit()
        db.refresh(tour)
        return tour
    except Exception:
        db.rollback()
        raise


@router.post("/{tour_id}/dispatch", response_model=TourResponse, summary="Tour dispatch", dependencies=SCHREIBEN["LOGISTIK"])
async def dispatch_tour(
    tour_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Dispatch a tour (mark as dispatched and departed)"""
    user_id = current_user["sub"]
    user_name = anmeldename(current_user)
    repo = TourRepository(db, tenant_id)
    tour = repo.dispatch(tour_id, user_id, user_name)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    return tour


# === STOP ENDPOINTS ===

@router.get("/{tour_id}/stops", response_model=List[StopResponse], summary="Stops auflisten")
async def list_stops(tour_id: str, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """List all stops for a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db, tenant_id)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourStopRepository(db, tenant_id)
    return repo.get_all(tour_id)


@router.post("/{tour_id}/stops", response_model=StopResponse, status_code=201, summary="Stop anlegen", dependencies=SCHREIBEN["LOGISTIK"])
async def create_stop(
    tour_id: str,
    stop_data: CreateStopRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new stop on a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db, tenant_id)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourStopRepository(db, tenant_id)
    data = stop_data.model_dump()
    data["tour_id"] = tour_id
    
    stop = repo.create(data)
    return stop


@router.post("/{tour_id}/stops/{stop_id}/delivery-notes", response_model=List[DeliveryNoteResponse], summary="Delivery notes zuweisen", dependencies=SCHREIBEN["LOGISTIK"])
async def assign_delivery_notes(
    tour_id: str,
    stop_id: str,
    data: AssignDeliveryNotesRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Assign delivery notes to a stop"""
    dn_repo = TourDeliveryNoteRepository(db, tenant_id)
    dns = dn_repo.assign_to_stop(tour_id, stop_id, data.delivery_note_ids)
    return dns


@router.post("/{tour_id}/stops/{stop_id}/deliver", response_model=DeliveryNoteResponse, summary="Delivered markieren", dependencies=SCHREIBEN["LOGISTIK"])
async def mark_delivered(
    tour_id: str,
    stop_id: str,
    delivery_note_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mark a delivery note as delivered"""
    dn_repo = TourDeliveryNoteRepository(db, tenant_id)
    dn_repo.require_tour(tour_id)
    dn_repo.require_stop(stop_id, tour_id)
    candidate = dn_repo.get_by_id(delivery_note_id)
    if candidate is None or candidate.tour_id != tour_id or candidate.stop_id != stop_id:
        raise HTTPException(status_code=404, detail="Delivery note not found")
    dn = dn_repo.mark_delivered(delivery_note_id)
    if not dn:
        raise HTTPException(status_code=404, detail=f"Delivery note {delivery_note_id} not found")
    return dn


# === EVENTS ENDPOINTS ===

@router.get("/{tour_id}/events", response_model=List[EventResponse], summary="Events auflisten")
async def list_events(tour_id: str, db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),):
    """List all events for a tour"""
    # Verify tour exists
    tour_repo = TourRepository(db, tenant_id)
    tour = tour_repo.get_by_id(tour_id)
    if not tour:
        raise HTTPException(status_code=404, detail=f"Tour {tour_id} not found")
    
    repo = TourEventRepository(db, tenant_id)
    return repo.get_all(tour_id)
