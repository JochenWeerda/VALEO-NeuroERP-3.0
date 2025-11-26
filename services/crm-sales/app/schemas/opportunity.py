"""Pydantic schemas for Opportunities."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    """Base opportunity schema."""
    number: Optional[str] = Field(None, max_length=64)  # Auto-generated if not provided
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field("EUR", max_length=3)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_revenue: Optional[float] = Field(None, ge=0)  # Calculated: amount * probability
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    status: str = "prospecting"
    stage: str = "initial_contact"
    lead_source: Optional[str] = Field(None, max_length=128)
    source: Optional[str] = Field(None, max_length=128)  # Lead source (web, referral, etc.)
    campaign_id: Optional[UUID] = None
    assigned_to: Optional[str] = Field(None, max_length=64)
    owner_id: Optional[str] = Field(None, max_length=64)  # Alias for assigned_to
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    notes: Optional[str] = None


class OpportunityCreate(OpportunityBase):
    """Schema for creating opportunities."""
    tenant_id: str = Field(..., max_length=64)


class OpportunityUpdate(BaseModel):
    """Schema for updating opportunities."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    probability: Optional[float] = Field(None, ge=0, le=100)
    expected_revenue: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    lead_source: Optional[str] = Field(None, max_length=128)
    source: Optional[str] = Field(None, max_length=128)
    campaign_id: Optional[UUID] = None
    assigned_to: Optional[str] = Field(None, max_length=64)
    owner_id: Optional[str] = Field(None, max_length=64)
    customer_id: Optional[UUID] = None
    contact_id: Optional[UUID] = None
    notes: Optional[str] = None


class Opportunity(OpportunityBase):
    """Full opportunity schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class OpportunityStageBase(BaseModel):
    """Base opportunity stage schema."""
    name: str = Field(..., max_length=128)
    stage_key: str = Field(..., max_length=64)
    order: float = Field(0, ge=0)
    probability_default: Optional[float] = Field(None, ge=0, le=100)
    required_fields: Optional[str] = None  # JSON array as string
    is_closed: bool = False
    is_won: bool = False


class OpportunityStageCreate(OpportunityStageBase):
    """Schema for creating opportunity stages."""
    tenant_id: str = Field(..., max_length=64)


class OpportunityStageUpdate(BaseModel):
    """Schema for updating opportunity stages."""
    name: Optional[str] = Field(None, max_length=128)
    order: Optional[float] = Field(None, ge=0)
    probability_default: Optional[float] = Field(None, ge=0, le=100)
    required_fields: Optional[str] = None
    is_closed: Optional[bool] = None
    is_won: Optional[bool] = None


class OpportunityStage(OpportunityStageBase):
    """Full opportunity stage schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OpportunityHistoryBase(BaseModel):
    """Base opportunity history schema."""
    field_name: str = Field(..., max_length=128)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: str = Field(..., max_length=64)
    change_reason: Optional[str] = None


class OpportunityHistoryCreate(OpportunityHistoryBase):
    """Schema for creating opportunity history."""
    opportunity_id: UUID


class OpportunityHistory(OpportunityHistoryBase):
    """Full opportunity history schema."""
    id: UUID
    opportunity_id: UUID
    changed_at: datetime

    class Config:
        from_attributes = True


class PipelineAggregation(BaseModel):
    """Pipeline aggregation schema."""
    stage: str
    count: int
    total_amount: float
    total_expected_revenue: float
    avg_probability: float


class ForecastData(BaseModel):
    """Forecast data schema."""
    period: str  # e.g., "2025-01"
    stage: Optional[str] = None
    owner_id: Optional[str] = None
    count: int
    total_amount: float
    total_expected_revenue: float