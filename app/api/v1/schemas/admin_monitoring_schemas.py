"""Pydantic schemas for the admin monitoring domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AdminAlertsResponse(BaseModel):
    active: int
    critical: int
    warning: int
    system_status: Literal["online", "degraded", "offline"]
    items: list[AdminAlert]


class MonitoringRuleIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    metric: str = Field(..., min_length=1, max_length=80)
    level: Literal["critical", "warning", "info"] = "warning"
    threshold: float | None = None
    operator: Literal["gt", "gte", "lt", "lte", "eq", "neq"] = "gte"
    active: bool = True
    escalation_minutes: int = Field(default=30, ge=0, le=10080)
    channel_ids: list[str] = Field(default_factory=list)


class MonitoringRuleOut(MonitoringRuleIn):
    id: str


class MonitoringChannelIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    channel_type: Literal["email", "sms", "webhook", "chatops"] = "email"
    target: str = Field(..., min_length=1, max_length=255)
    active: bool = True


class MonitoringChannelOut(MonitoringChannelIn):
    id: str


class SchedulerJobIn(BaseModel):
    code: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=140)
    cron: str = Field(..., min_length=5, max_length=120)
    process: str = Field(..., min_length=1, max_length=80)
    active: bool = True
    retry_max: int = Field(default=3, ge=0, le=100)
    timeout_seconds: int = Field(default=300, ge=10, le=86400)
    channel_ids: list[str] = Field(default_factory=list)


class SchedulerJobOut(SchedulerJobIn):
    id: str

