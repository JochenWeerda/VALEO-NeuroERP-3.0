"""Pydantic schemas for the position overrides domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class OverrideRequestIn(BaseModel):
    branch_id: Optional[str] = None
    article_id: str = Field(..., max_length=64)
    period_key: str = Field(..., max_length=20)
    reason: str = Field(..., min_length=1)
    related_doc_type: Optional[str] = None
    related_doc_id: Optional[str] = None


class OverrideApproveIn(BaseModel):
    comment: str = Field(..., min_length=1)
    valid_days: int = Field(14, ge=1, le=365)


class OverrideRejectIn(BaseModel):
    comment: str = Field(..., min_length=1)


class OverrideOut(BaseModel):
    override_id: str
    branch_id: Optional[str] = None
    article_id: str
    period_key: str
    requested_by: Optional[str] = None
    requested_at: Optional[datetime] = None
    reason: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    comment: Optional[str] = None
    related_doc_type: Optional[str] = None
    related_doc_id: Optional[str] = None
    tenant_id: str
    created_at: Optional[datetime] = None

