"""Pydantic schemas for the booking templates domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class BookingTemplateCreate(BaseModel):
    """Schema for creating a booking template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    category: str = Field(default="GENERAL", description="Template category")
    trigger_type: str = Field(default="MANUAL", description="Trigger type: MANUAL, SCHEDULED, EVENT")
    trigger_config: Optional[Dict[str, Any]] = Field(None, description="Trigger configuration (cron, event type, etc.)")
    lines: List[BookingTemplateLine] = Field(..., min_length=2, description="Template lines")
    default_amount: Optional[Decimal] = Field(None, ge=0, description="Default amount for percentage-based calculations")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code")
    active: bool = Field(default=True, description="Active status")


class BookingTemplateUpdate(BaseModel):
    """Schema for updating a booking template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    lines: Optional[List[BookingTemplateLine]] = None
    default_amount: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    active: Optional[bool] = None


class BookingTemplateResponse(BaseModel):
    """Response schema for booking template"""
    id: str
    name: str
    description: Optional[str]
    category: str
    trigger_type: str
    trigger_config: Optional[Dict[str, Any]]
    lines: List[BookingTemplateLine]
    default_amount: Optional[Decimal]
    currency: str
    active: bool
    created_at: datetime
    updated_at: datetime


class ApplyTemplateRequest(BaseModel):
    """Request to apply a booking template"""
    template_id: Optional[str] = Field(None, description="Template ID (optional, taken from URL path)")
    amount: Optional[Decimal] = Field(None, ge=0, description="Amount to use (overrides template default)")
    entry_date: date = Field(..., description="Entry date for the journal entry")
    description: Optional[str] = Field(None, description="Override description")
    reference: Optional[str] = Field(None, description="Reference document")
    variables: Optional[Dict[str, Any]] = Field(None, description="Variables for template placeholders")


class ApplyTemplateResponse(BaseModel):
    """Response for applying a template"""
    journal_entry_id: str
    entry_number: str
    total_debit: Decimal
    total_credit: Decimal
    applied_at: datetime

