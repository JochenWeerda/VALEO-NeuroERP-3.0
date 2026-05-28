"""Pydantic schemas for the neuro event policy domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class NeuroEventPolicyOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class ValidateEventRequest(BaseModel):
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RegisterPolicyRequest(BaseModel):
    policy_id: str
    name: str
    version: str = "1.0"
    rules: dict[str, Any] = Field(default_factory=dict)
    variant_key: Optional[str] = None
    traffic_weight: Optional[float] = None


class SelectPolicyVariantRequest(BaseModel):
    seed: Optional[str] = None

