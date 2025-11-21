from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import ORMModel


class Location(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None


class CropEntry(BaseModel):
    crop: str
    area: float


class LivestockEntry(BaseModel):
    type: str
    count: int


class FarmProfileCreate(BaseModel):
    farm_name: str = Field(..., max_length=255)
    owner: str = Field(..., max_length=150)
    total_area: float = Field(..., ge=0)
    crops: list[CropEntry] | None = None
    livestock: list[LivestockEntry] | None = None
    location: Location | None = None
    certifications: list[str] | None = None
    notes: str | None = None
    customer_id: UUID | None = None


class FarmProfileUpdate(BaseModel):
    farm_name: str | None = Field(default=None, max_length=255)
    owner: str | None = Field(default=None, max_length=150)
    total_area: float | None = Field(default=None, ge=0)
    crops: list[CropEntry] | None = None
    livestock: list[LivestockEntry] | None = None
    location: Location | None = None
    certifications: list[str] | None = None
    notes: str | None = None
    customer_id: UUID | None = None


class FarmProfileRead(ORMModel):
    id: UUID
    tenant_id: str
    farm_name: str
    owner: str
    total_area: float
    crops: list[dict] | None
    livestock: list[dict] | None
    location: dict | None
    certifications: list[str] | None
    notes: str | None
    customer_id: UUID | None
    customer_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class FarmProfileListResponse(BaseModel):
    items: list[FarmProfileRead]
    total: int
