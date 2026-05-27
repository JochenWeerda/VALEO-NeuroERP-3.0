"""
POST /voice/resolve - Resolve transcribed text to action_id + params
POST /voice/polish  - Ollama business-ready text polishing
POST /voice/transcribe - Local faster-whisper STT (base64 audio)
"""

import base64
import binascii

from fastapi import APIRouter, HTTPException

from app.schemas.voice import (
    VoicePolishIn,
    VoicePolishOut,
    VoiceResolveIn,
    VoiceResolveOut,
    VoiceTranscribeIn,
    VoiceTranscribeOut,
)
from app.services.intent_resolver import intent_resolver
from app.services.local_stt import is_faster_whisper_available, transcribe_audio
from app.services.voice_polish import polish_text

router = APIRouter()


@router.post("/resolve", response_model=VoiceResolveOut | None)
def resolve_voice(body: VoiceResolveIn) -> VoiceResolveOut | None:
    """
    Resolve voice text to an action.
    Returns action_id, params, confidence. None if no intent matched (client gets 200 + null).
    """
    context = body.context or {}
    return intent_resolver.resolve(body.text, context=context)


@router.post("/polish", response_model=VoicePolishOut)
async def polish_voice(body: VoicePolishIn) -> VoicePolishOut:
    """Polish raw STT transcript to business-ready German text via Ollama."""
    result = await polish_text(body.text, tone=body.tone)
    return VoicePolishOut(**result)


@router.post("/transcribe", response_model=VoiceTranscribeOut)
async def transcribe_voice(body: VoiceTranscribeIn) -> VoiceTranscribeOut:
    """Transcribe base64 audio locally via faster-whisper."""
    if not is_faster_whisper_available():
        raise HTTPException(
            503,
            detail="faster-whisper not installed on ki-usability service",
        )
    try:
        audio_bytes = base64.b64decode(body.audio_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(400, detail=f"Invalid base64 audio: {exc}") from exc

    result = await transcribe_audio(
        audio_bytes,
        audio_format=body.audio_format,
        language=body.language,
    )
    if result.get("error") and not result.get("text"):
        raise HTTPException(502, detail=result["error"])
    return VoiceTranscribeOut(**result)
