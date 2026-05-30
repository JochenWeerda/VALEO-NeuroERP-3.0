"""Pydantic schemas for the logistics tours domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class LogisticsTourOut(BaseSchema):
    """Typed response schema for LogisticsTourOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class TourStopIn(BaseModel):
    stop_order: Optional[int] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    customer_id: Optional[str] = None
    delivery_note_ref: Optional[str] = None
    planned_arrival: Optional[datetime] = None


class TourIn(BaseModel):
    date: Optional[datetime] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    status: Optional[str] = "GEPLANT"
    notes: Optional[str] = None
    stops: Optional[List[TourStopIn]] = []


class TourEventIn(BaseModel):
    event_type: str  # START/STOP/PAUSE/GPS/DELIVERY/PROBLEM
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None
    driver_ref: Optional[str] = None


class PodIn(BaseModel):
    signature_base64: str
    recipient_name: str
    delivered_at: str
    notes: Optional[str] = None
    photo_base64: Optional[str] = None

