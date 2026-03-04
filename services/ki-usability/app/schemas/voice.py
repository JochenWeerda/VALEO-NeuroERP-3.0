"""
Voice resolve schemas
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class VoiceResolveIn(BaseModel):
    """Input for voice-to-intent resolution."""

    text: str = Field(..., description="Transcribed text (e.g. from Web Speech API)")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Context: domain, mask, tenant_id",
    )


class VoiceResolveOut(BaseModel):
    """Resolved intent from voice text."""

    action_id: str = Field(..., description="Resolved action ID")
    params: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0..1")
    raw_text: str = Field(..., description="Original input text")
