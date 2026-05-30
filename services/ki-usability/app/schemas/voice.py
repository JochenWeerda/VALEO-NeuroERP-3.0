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


class VoiceStatusOut(BaseModel):
    """Voice stack readiness."""

    stt_provider: str
    stt_ready: bool
    tts_provider: str
    tts_ready: bool
    ollama_base_url: str
    ollama_reachable: bool
    voice_polish_enabled: bool
    voice_summary_enabled: bool
    kokoro_configured: bool = False
    piper_configured: bool = False
    faster_whisper_model: str = "small"


class VoiceSummaryIn(BaseModel):
    """Input for voice summary."""

    text: str = Field(..., min_length=1, description="Source text to summarize")
    max_words: Optional[int] = Field(default=None, ge=10, le=120)


class VoiceSummaryOut(BaseModel):
    """Speakable summary (~15s)."""

    source_text: str
    summary_text: str
    provider: str
    summary_applied: bool = False
    estimated_seconds: int = 0
    error: Optional[str] = None


class VoiceSynthesizeIn(BaseModel):
    """Input for local TTS."""

    text: str = Field(..., min_length=1, description="Text to speak")
    language: str = Field(default="de-DE")


class VoiceSynthesizeOut(BaseModel):
    """TTS result — Piper audio or browser hint."""

    text: str
    provider: str
    browser_hint: bool = False
    audio_base64: Optional[str] = None
    content_type: Optional[str] = None
    language: str = "de-DE"
    hint: Optional[str] = None
    error: Optional[str] = None


class VoicePipelineIn(BaseModel):
    """WhisperBar unified pipeline input."""

    mode: str = Field(..., description="dictate | summary | intent")
    text: Optional[str] = Field(default=None, description="Text or clipboard content")
    audio_base64: Optional[str] = Field(default=None, description="Optional STT audio")
    audio_format: str = Field(default="wav")
    language: str = Field(default="de-DE")
    tone: str = Field(default="business")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    synthesize: bool = Field(default=False, description="TTS for summary mode")


class VoicePipelineOut(BaseModel):
    """WhisperBar pipeline result (mode-specific fields)."""

    mode: str
    raw_text: Optional[str] = None
    polished_text: Optional[str] = None
    source_text: Optional[str] = None
    summary_text: Optional[str] = None
    provider: Optional[str] = None
    polish_applied: Optional[bool] = None
    summary_applied: Optional[bool] = None
    estimated_seconds: Optional[int] = None
    text: Optional[str] = None
    resolved: Optional[Dict[str, Any]] = None
    tts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
