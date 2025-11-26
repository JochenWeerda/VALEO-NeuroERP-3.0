"""Pydantic schemas for segments."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class SegmentBase(BaseModel):
    """Base segment schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., description="dynamic, static, hybrid")
    status: str = Field(default="active", description="active, inactive, archived")


class SegmentCreate(SegmentBase):
    """Schema for creating a segment."""
    tenant_id: str
    rules: Optional[dict] = None  # JSON structure for rules


class SegmentUpdate(BaseModel):
    """Schema for updating a segment."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    rules: Optional[dict] = None


class Segment(SegmentBase):
    """Full segment schema."""
    id: UUID
    tenant_id: str
    rules: Optional[dict] = None
    member_count: int = 0
    last_calculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class SegmentRuleBase(BaseModel):
    """Base segment rule schema."""
    field: str = Field(..., description="Field path, e.g., 'contact.email_domain'")
    operator: str = Field(..., description="equals, contains, greater_than, etc.")
    value: dict = Field(..., description="Value(s) for the rule")
    logical_operator: Optional[str] = Field(None, description="AND, OR")
    order: int = Field(default=0, description="Order of rule evaluation")


class SegmentRuleCreate(SegmentRuleBase):
    """Schema for creating a segment rule."""
    segment_id: UUID


class SegmentRuleUpdate(BaseModel):
    """Schema for updating a segment rule."""
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[dict] = None
    logical_operator: Optional[str] = None
    order: Optional[int] = None


class SegmentRule(SegmentRuleBase):
    """Full segment rule schema."""
    id: UUID
    segment_id: UUID

    class Config:
        from_attributes = True


class SegmentMemberBase(BaseModel):
    """Base segment member schema."""
    contact_id: UUID


class SegmentMemberCreate(SegmentMemberBase):
    """Schema for adding a member to a segment."""
    segment_id: UUID
    added_by: Optional[str] = None


class SegmentMember(SegmentMemberBase):
    """Full segment member schema."""
    id: UUID
    segment_id: UUID
    added_at: datetime
    added_by: Optional[str] = None
    removed_at: Optional[datetime] = None
    removed_by: Optional[str] = None

    class Config:
        from_attributes = True


class SegmentPerformance(BaseModel):
    """Segment performance metrics."""
    id: UUID
    segment_id: UUID
    date: datetime
    period_type: str
    member_count: int
    active_members: int
    campaign_count: int
    conversion_rate: Optional[float] = None
    revenue: Optional[float] = None

    class Config:
        from_attributes = True


class SegmentCalculateRequest(BaseModel):
    """Request to recalculate a segment."""
    force_full: bool = Field(default=False, description="Force full recalculation")


class SegmentExportRequest(BaseModel):
    """Request to export a segment."""
    format: str = Field(default="csv", description="csv, json")
    include_fields: Optional[list[str]] = Field(None, description="Fields to include in export")

