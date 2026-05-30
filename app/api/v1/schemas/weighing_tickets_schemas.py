"""Pydantic schemas for the weighing tickets domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class WeighingTicketOut(BaseSchema):
    id: str
    ticket_number: str
    scale_id: Optional[str] = None
    vehicle_plate: Optional[str] = None
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = None
    protein_pct: Optional[float] = None
    impurities_pct: Optional[float] = None
    hl_weight: Optional[float] = None
    billing_weight: Optional[float] = None
    quality_data: Optional[dict[str, Any]] = None
    contract_id: Optional[str] = None
    allocated_quantity_kg: Optional[float] = None
    allocation_status: Optional[str] = "unallocated"
    status: str = "open"
    direction: str = "in"
    reference_doc: Optional[str] = None
    article_group: Optional[str] = None
    article_id: Optional[str] = None
    notes: Optional[str] = None


class WeighingTicketCreate(BaseModel):
    ticket_number: str
    scale_id: Optional[str] = None
    vehicle_plate: Optional[str] = None
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    protein_pct: Optional[float] = Field(default=None, ge=0, le=100)
    impurities_pct: Optional[float] = Field(default=None, ge=0, le=100)
    hl_weight: Optional[float] = Field(default=None, ge=0)
    billing_weight: Optional[float] = Field(default=None, ge=0)
    quality_data: Optional[dict[str, Any]] = None
    direction: str = "in"
    reference_doc: Optional[str] = None
    article_group: Optional[str] = None
    article_id: Optional[str] = None
    notes: Optional[str] = None


class WeighingTicketUpdate(BaseModel):
    gross_weight: Optional[float] = None
    tare_weight: Optional[float] = None
    net_weight: Optional[float] = None
    first_weighing_at: Optional[datetime] = None
    second_weighing_at: Optional[datetime] = None
    moisture_pct: Optional[float] = Field(default=None, ge=0, le=100)
    protein_pct: Optional[float] = Field(default=None, ge=0, le=100)
    impurities_pct: Optional[float] = Field(default=None, ge=0, le=100)
    hl_weight: Optional[float] = Field(default=None, ge=0)
    billing_weight: Optional[float] = Field(default=None, ge=0)
    quality_data: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    vehicle_plate: Optional[str] = None
    article_group: Optional[str] = None
    article_id: Optional[str] = None
    notes: Optional[str] = None


class WeighingTicketContractAllocationRequest(BaseModel):
    contract_id: str
    allocation_quantity_kg: Optional[float] = Field(default=None, gt=0)
    note: Optional[str] = None


class WeighingTicketContractAllocationOut(BaseSchema):
    ticket_id: str
    contract_id: str
    allocation_id: str
    allocation_quantity_kg: float
    contract_remaining_quantity_kg: float
    contract_status: str


class ArticleGroupOut(BaseModel):
    warengruppe: str
    count: int

