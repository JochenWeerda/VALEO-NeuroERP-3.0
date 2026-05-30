"""Pydantic schemas for the channels domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class ChannelOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class EmailIngressRequest(BaseModel):
    from_address: str
    to_address: str = "system@valeo-erp.de"
    subject: str
    body_text: str
    body_html: Optional[str] = None
    message_id: Optional[str] = None
    in_reply_to: Optional[str] = None


class GenericMessageRequest(BaseModel):
    channel: str = Field(..., description="whatsapp | email | chat | voice | api")
    sender_id: str
    text: str
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatStartRequest(BaseModel):
    user_id: str = Field(...)
    context: Optional[dict[str, Any]] = None


class ChatMessageRequest(BaseModel):
    text: str = Field(...)
    user_id: str = Field("")

