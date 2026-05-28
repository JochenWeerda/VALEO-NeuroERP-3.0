"""Pydantic schemas for the ap approval workflow domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ApprovalRuleCreate(BaseModel):
    """Schema for creating an approval rule"""
    name: str = Field(..., min_length=1, max_length=100, description="Rule name")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")
    conditions: List[ApprovalRuleCondition] = Field(..., min_length=1, description="Conditions that trigger this rule")
    required_approvals: int = Field(..., ge=1, le=4, description="Number of required approvals (2/3/4-eyes)")
    approval_roles: List[str] = Field(..., min_length=1, description="Roles that can approve (e.g., ['manager', 'finance'])")
    priority: int = Field(default=0, description="Rule priority (higher = checked first)")
    active: bool = Field(default=True, description="Active status")


class ApprovalRuleResponse(BaseModel):
    """Response schema for approval rule"""
    id: str
    name: str
    description: Optional[str]
    conditions: List[Dict[str, Any]]
    required_approvals: int
    approval_roles: List[str]
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class ApprovalRequest(BaseModel):
    """Schema for requesting approval"""
    invoice_id: str = Field(..., description="AP Invoice ID")
    requested_by: str = Field(..., description="User requesting approval")
    comment: Optional[str] = Field(None, description="Comment/notes")


class ApprovalStatusResponse(BaseModel):
    """Response schema for approval status"""
    invoice_id: str
    status: str  # pending, approved, rejected, partially_approved
    required_approvals: int
    current_approvals: int
    approvals: List[Dict[str, Any]]
    rejections: List[Dict[str, Any]]
    applicable_rule: Optional[Dict[str, Any]]
    can_post: bool
    can_pay: bool

