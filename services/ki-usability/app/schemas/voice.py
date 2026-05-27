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


class VoicePolishIn(BaseModel):
    """Input for transcript polishing."""

    text: str = Field(..., min_length=1, description="Raw STT transcript")
    tone: str = Field(default="business", description="business | casual | formal")


class VoicePolishOut(BaseModel):
    """Polished transcript."""

    raw_text: str
    polished_text: str
    provider: str = Field(..., description="ollama:model | passthrough | fallback-raw")
    polish_applied: bool = False
    error: Optional[str] = None


class VoiceTranscribeIn(BaseModel):
    """Audio upload for local STT (base64-encoded)."""

    audio_base64: str = Field(..., description="Base64-encoded audio (wav/webm/mp3)")
    audio_format: str = Field(default="wav", description="wav | webm | mp3 | ogg")
    language: str = Field(default="de-DE")


class VoiceTranscribeOut(BaseModel):
    """STT result."""

    text: str
    confidence: float = 0.0
    provider: str = "faster-whisper"
    language: str = "de-DE"
    error: Optional[str] = None
