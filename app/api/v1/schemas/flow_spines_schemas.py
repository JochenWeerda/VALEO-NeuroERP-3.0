"""Pydantic schemas for the flow spines domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class FlowSpineOut(BaseSchema):
    """Typed response schema for FlowSpineOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class InstanceCreateRequest(BaseModel):
    label: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    partner_name: Optional[str] = None
    subject: Optional[str] = None
    entry_mode: Optional[str] = None
    linked_document_id: Optional[str] = None
    linked_document_type: Optional[str] = None


class TransitionRequest(BaseModel):
    node_id: str
    new_status: str
    action_label: str
    user_id: Optional[str] = None


class AgentActionRequest(BaseModel):
    action: str
    node_id: Optional[str] = None
    instance_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None


class InstanceUpdateRequest(BaseModel):
    label: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    partner_name: Optional[str] = None
    subject: Optional[str] = None
    entry_mode: Optional[str] = None
    linked_document_id: Optional[str] = None
    linked_document_type: Optional[str] = None
    business_status: Optional[str] = None
    assigned_owner: Optional[str] = None
    resume_node_id: Optional[str] = None
    resume_route: Optional[str] = None
    resume_payload: Optional[dict[str, Any]] = None
    user_id: Optional[str] = None


class InstanceSaveRequest(BaseModel):
    resume_node_id: Optional[str] = None
    resume_route: Optional[str] = None
    resume_payload: dict[str, Any] = Field(default_factory=dict)
    business_status: Optional[str] = None
    assigned_owner: Optional[str] = None
    action_label: Optional[str] = None
    note: Optional[str] = None
    user_id: Optional[str] = None


class LifecycleActionRequest(BaseModel):
    business_status: Optional[str] = None
    node_id: Optional[str] = None
    assigned_owner: Optional[str] = None
    action_label: Optional[str] = None
    reason_category: Optional[str] = None
    reason_code: Optional[str] = None
    reason_note: Optional[str] = None
    blocked_until: Optional[str] = None
    user_id: Optional[str] = None


class ResumeRequest(BaseModel):
    user_id: Optional[str] = None
    action_label: Optional[str] = None

