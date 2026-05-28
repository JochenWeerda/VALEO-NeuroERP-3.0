"""Pydantic schemas for the ki usability domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class ActionOut(BaseModel):
    id: str
    label: str
    label_en: str | None = None
    shortcut: str | None = None
    description: str | None = None
    category: str = "action"
    domain: str | None = None
    mask: str | None = None
    intent_phrases: list[str] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    surfaces: list[ActionSurface] = Field(default_factory=list)
    context_scope: ActionContextScope
    relevance_score: int
    priority: int
    default_params: dict[str, Any] = Field(default_factory=dict)


class ActionListResponse(BaseModel):
    actions: list[ActionOut]
    total: int


class VoiceResolveIn(BaseModel):
    text: str
    context: dict[str, Any] | None = None


class VoiceResolveOut(BaseModel):
    action_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    confidence: float
    raw_text: str

