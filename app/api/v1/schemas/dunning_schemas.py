"""Pydantic schemas for the dunning domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class DunningRuleCreate(BaseModel):
    """Schema for creating a dunning rule"""
    level: int = Field(..., ge=1, le=3)
    days_overdue_min: int = Field(..., ge=0)
    days_overdue_max: Optional[int] = Field(None, ge=0)
    fee_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    fee_percentage: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    interest_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    payment_deadline_days: int = Field(default=14, ge=1)
    block_customer: bool = Field(default=False)
    escalate_to_collection: bool = Field(default=False)
    description_template: str
    active: bool = Field(default=True)


class DunningRuleResponse(BaseModel):
    """Response schema for dunning rule"""
    id: str
    level: int
    days_overdue_min: int
    days_overdue_max: Optional[int]
    fee_amount: Decimal
    fee_percentage: Decimal
    interest_rate: Decimal
    payment_deadline_days: int
    block_customer: bool
    escalate_to_collection: bool
    description_template: str
    active: bool
    created_at: datetime
    updated_at: datetime


class DunningCreate(BaseModel):
    """Schema for creating a dunning notice"""
    op_id: str = Field(..., description="Open item ID")
    debtor_id: str = Field(..., description="Debtor ID")
    dunning_level: int = Field(..., ge=1, le=3)
    dunning_date: date
    due_date: date
    open_amount: Decimal = Field(..., ge=0)
    custom_fee: Optional[Decimal] = Field(None, ge=0, description="Override calculated fee")
    custom_interest: Optional[Decimal] = Field(None, ge=0, description="Override calculated interest")
    notes: Optional[str] = None


class DunningResponse(BaseModel):
    """Response schema for dunning notice"""
    id: str
    op_id: str
    debtor_id: str
    dunning_level: int
    dunning_date: date
    due_date: date
    open_amount: Decimal
    dunning_fee: Decimal
    interest: Decimal
    total_amount: Decimal
    payment_deadline: date
    status: str
    sent_date: Optional[date]
    payment_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProcessDunningRequest(BaseModel):
    """Request to process dunning for overdue items"""
    debtor_id: Optional[str] = Field(None, description="Process for specific debtor")
    op_ids: Optional[List[str]] = Field(None, description="Process for specific open items")
    auto_apply_rules: bool = Field(default=True, description="Automatically apply dunning rules")
    tenant_id: str = Field(default="system")
    as_of_date: Optional[date] = Field(None, description="Stichtag für Überfälligkeit (default: heute)")


class DunningRunRequest(BaseModel):
    """Request to start a dunning run (all overdue items as of date)"""
    as_of_date: date = Field(..., description="Stichtag (YYYY-MM-DD)")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (default: system)")


class DunningRunResponse(BaseModel):
    """Response after starting a dunning run"""
    run_id: str
    notices_created: int

