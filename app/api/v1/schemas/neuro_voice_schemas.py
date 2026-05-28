"""Auto-generated domain schemas for neuro voice.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class NeuroVoiceOut(BaseSchema):
    """Response schema for neuro voice endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class SessionRequest(BaseModel):
    language: str = Field("de-DE")
    channel: str = Field("phone")


class TranscribeRequest(BaseModel):
    session_id: str
    audio_format: str = Field("wav")


class SynthesizeRequest(BaseModel):
    session_id: str
    text: str

