"""Pydantic schemas for the webhooks domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class WebhookOut(BaseSchema):
    id: str
    url: str
    event_area: str
    is_active: bool = True


class WebhookCreate(BaseModel):
    url: HttpUrl
    event_area: str
    secret: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_webhook_url(cls, v: HttpUrl) -> HttpUrl:
        validate_outbound_http_target(str(v))
        return v


class EventAreaOut(BaseModel):
    name: str
    description: str

