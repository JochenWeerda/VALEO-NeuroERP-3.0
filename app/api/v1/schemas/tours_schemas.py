"""Pydantic schemas for the tours domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class DeliveryNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dn_no: str
    status: str
    created_at: Optional[datetime] = None
    reference: Optional[DeliveryNoteReference] = None
    items_summary: Optional[ItemsSummary] = None


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


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    at: datetime
    type: str
    by: Optional[UserInfo] = None


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

