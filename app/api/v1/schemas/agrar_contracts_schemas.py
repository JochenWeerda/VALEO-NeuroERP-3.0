"""Pydantic schemas for the agrar contracts domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AgrarContractOut(BaseSchema):
    id: str
    contract_number: str
    contract_type: ContractType
    harvest_year: int
    partner_id: str
    article_id: str
    pricing_model: PricingModel
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = None
    currency: str = "EUR"
    total_quantity_kg: float
    remaining_quantity_kg: float
    status: ContractStatus
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AgrarContractCreate(BaseModel):
    contract_number: str = Field(..., min_length=3, max_length=50)
    contract_type: ContractType
    harvest_year: int = Field(..., ge=2000, le=2100)
    partner_id: str
    article_id: str
    pricing_model: PricingModel
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = Field(default=None, ge=0)
    currency: str = "EUR"
    total_quantity_kg: float = Field(..., gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class AgrarContractUpdate(BaseModel):
    partner_id: Optional[str] = None
    article_id: Optional[str] = None
    pricing_model: Optional[PricingModel] = None
    pool_group_id: Optional[str] = None
    fixed_price: Optional[float] = Field(default=None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: Optional[ContractStatus] = None


class ContractAllocationCreate(BaseModel):
    allocation_quantity_kg: float = Field(..., gt=0)
    ticket_id: Optional[str] = None
    note: Optional[str] = None


class ContractAllocationOut(BaseSchema):
    id: str
    contract_id: str
    ticket_id: Optional[str] = None
    allocation_quantity_kg: float
    allocated_at: Optional[datetime] = None
    note: Optional[str] = None

