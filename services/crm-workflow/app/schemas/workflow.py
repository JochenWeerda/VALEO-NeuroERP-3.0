"""Pydantic schemas for Workflows."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: str = "draft"
    trigger_conditions: dict = Field(..., description="Conditions that trigger the workflow")
    actions: List[dict] = Field(..., description="List of actions to execute")


class WorkflowCreate(WorkflowBase):
    """Schema for creating workflows."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class WorkflowUpdate(BaseModel):
    """Schema for updating workflows."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    trigger_conditions: Optional[dict] = None
    actions: Optional[List[dict]] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class Workflow(WorkflowBase):
    """Full workflow schema."""
    id: UUID
    tenant_id: str
    is_active: bool = True
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TriggerBase(BaseModel):
    """Base trigger schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    trigger_type: str = Field(..., description="event, schedule, or manual")
    event_type: Optional[str] = Field(None, max_length=128)
    schedule_cron: Optional[str] = Field(None, max_length=128)
    conditions: dict = Field(..., description="Filter conditions")
    workflow_id: UUID
    is_active: bool = True


class TriggerCreate(TriggerBase):
    """Schema for creating triggers."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class Trigger(TriggerBase):
    """Full trigger schema."""
    id: UUID
    tenant_id: str
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowExecution(BaseModel):
    """Workflow execution schema."""
    id: UUID
    workflow_id: UUID
    status: str
    trigger_event: dict
    execution_context: dict
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    """Base notification schema."""
    notification_type: str = Field(..., description="email, in_app, sms, webhook")
    recipient: str = Field(..., max_length=255)
    subject: str = Field(..., max_length=255)
    message: str


class NotificationCreate(NotificationBase):
    """Schema for creating notifications."""
    tenant_id: str = Field(..., max_length=64)
    workflow_execution_id: Optional[UUID] = None


class Notification(NotificationBase):
    """Full notification schema."""
    id: UUID
    tenant_id: str
    status: str = "pending"
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    workflow_execution_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True