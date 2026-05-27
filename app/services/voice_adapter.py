"""
Voice Adapter Layer — NC-003
STT/TTS Adapter mit echten Provider-Anbindungen.

Provider-Hierarchie:
  STT: 1) faster-whisper (lokal)  2) OpenAI Whisper API  3) Azure  4) Browser
  TTS: 1) OpenAI TTS          2) Azure Cognitive Speech  3) Web Speech API (Browser)

Konfiguration über Umgebungsvariablen:
  VOICE_STT_PROVIDER: faster-whisper | whisper | azure | browser (default: whisper)
  VOICE_FASTER_WHISPER_MODEL: small | medium | large-v3 (default: small)
  VOICE_FASTER_WHISPER_COMPUTE: int8 | float16 (default: int8)
  VOICE_TTS_PROVIDER: openai | azure | browser (default: openai)
  OPENAI_API_KEY: für Whisper STT + OpenAI TTS
  AZURE_SPEECH_KEY + AZURE_SPEECH_REGION: für Azure Cognitive Speech
"""

from __future__ import annotations

import base64
import io
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Provider configuration
_STT_PROVIDER = os.getenv("VOICE_STT_PROVIDER", "whisper").lower()
_TTS_PROVIDER = os.getenv("VOICE_TTS_PROVIDER", "openai").lower()
_FASTER_WHISPER_MODEL = os.getenv("VOICE_FASTER_WHISPER_MODEL", "small")
_FASTER_WHISPER_COMPUTE = os.getenv("VOICE_FASTER_WHISPER_COMPUTE", "int8")
_FASTER_WHISPER_DEVICE = os.getenv("VOICE_FASTER_WHISPER_DEVICE", "cpu")
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
_AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
_AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "westeurope")


@dataclass
class VoiceSession:
    id: str = field(default_factory=lambda: str(uuid4()))
    channel: str = "phone"
    language: str = "de-DE"
    state: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    turns: int = 0
    stt_provider: str = ""
    tts_provider: str = ""


_sessions: dict[str, VoiceSession] = {}


def get_provider_status() -> dict:
    """Return configured providers and their readiness."""
    return {
        "stt_provider": _STT_PROVIDER,
        "tts_provider": _TTS_PROVIDER,
        "stt_ready": _is_stt_ready(),
        "tts_ready": _is_tts_ready(),
        "supported_languages": ["de-DE", "en-US", "fr-FR"],
        "supported_audio_formats": ["wav", "mp3", "webm", "ogg"],
    }


def _is_stt_ready() -> bool:
    if _STT_PROVIDER == "faster-whisper":
        try:
            import faster_whisper  # noqa: F401

            return True
        except ImportError:
            return False
    if _STT_PROVIDER == "whisper":
        return bool(_OPENAI_API_KEY)
    if _STT_PROVIDER == "azure":
        return bool(_AZURE_SPEECH_KEY)
    if _STT_PROVIDER == "browser":
        return True  # Browser-seitig, kein Server-Key nötig
    return False


def _is_tts_ready() -> bool:
    if _TTS_PROVIDER == "openai":
        return bool(_OPENAI_API_KEY)
    if _TTS_PROVIDER == "azure":
        return bool(_AZURE_SPEECH_KEY)
    if _TTS_PROVIDER == "browser":
        return True
    return False


def create_session(language: str = "de-DE", channel: str = "phone") -> dict:
    session = VoiceSession(
        language=language,
        channel=channel,
        stt_provider=_STT_PROVIDER,
        tts_provider=_TTS_PROVIDER,
    )
    _sessions[session.id] = session
    logger.info("Voice session created: %s (STT=%s, TTS=%s)", session.id, _STT_PROVIDER, _TTS_PROVIDER)
    return {
        "session_id": session.id,
        "language": language,
        "state": "active",
        "stt_provider": _STT_PROVIDER,
        "tts_provider": _TTS_PROVIDER,
    }


def end_session(session_id: str) -> dict:
    session = _sessions.pop(session_id, None)
    if not session:
        return {"error": "Session not found"}
    return {"session_id": session_id, "state": "closed", "total_turns": session.turns}


async def transcribe(
    session_id: str,
    audio_format: str = "wav",
    audio_data: Optional[bytes] = None,
) -> dict:
    """Transcribe audio to text using configured STT provider."""
    session = _sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}
    session.turns += 1

    if not audio_data:
        return {
            "session_id": session_id,
            "turn": session.turns,
            "text": "",
            "language": session.language,
            "confidence": 0.0,
            "error": "No audio data provided",
        }

    try:
        if _STT_PROVIDER == "faster-whisper":
            text, confidence = await _faster_whisper_transcribe(audio_data, audio_format, session.language)
        elif _STT_PROVIDER == "whisper":
            text, confidence = await _whisper_transcribe(audio_data, audio_format, session.language)
        elif _STT_PROVIDER == "azure":
            text, confidence = await _azure_stt(audio_data, audio_format, session.language)
        elif _STT_PROVIDER == "browser":
            # Browser-based STT: audio already transcribed client-side
            return {
                "session_id": session_id,
                "turn": session.turns,
                "text": "",
                "language": session.language,
                "confidence": 0.0,
                "provider": "browser",
                "hint": "Use Web Speech API on client side; send transcribed text directly",
            }
        else:
            return {
                "session_id": session_id,
                "turn": session.turns,
                "text": "",
                "confidence": 0.0,
                "error": f"Unknown STT provider: {_STT_PROVIDER}",
            }

        return {
            "session_id": session_id,
            "turn": session.turns,
            "text": text,
            "language": session.language,
            "confidence": confidence,
            "provider": _STT_PROVIDER,
        }
    except Exception as exc:
        logger.exception("STT failed for session %s", session_id)
        return {
            "session_id": session_id,
            "turn": session.turns,
            "text": "",
            "confidence": 0.0,
            "error": str(exc),
            "provider": _STT_PROVIDER,
        }


async def synthesize(session_id: str, text: str) -> dict:
    """Synthesize text to audio using configured TTS provider."""
    session = _sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    if not text.strip():
        return {"session_id": session_id, "text": text, "error": "Empty text"}

    try:
        if _TTS_PROVIDER == "openai":
            audio_b64, content_type = await _openai_tts(text, session.language)
        elif _TTS_PROVIDER == "azure":
            audio_b64, content_type = await _azure_tts(text, session.language)
        elif _TTS_PROVIDER == "browser":
            return {
                "session_id": session_id,
                "text": text,
                "provider": "browser",
                "hint": "Use Web Speech API SpeechSynthesis on client side",
            }
        else:
            return {
                "session_id": session_id,
                "text": text,
                "error": f"Unknown TTS provider: {_TTS_PROVIDER}",
            }

        return {
            "session_id": session_id,
            "text": text,
            "audio_base64": audio_b64,
            "content_type": content_type,
            "provider": _TTS_PROVIDER,
        }
    except Exception as exc:
        logger.exception("TTS failed for session %s", session_id)
        return {
            "session_id": session_id,
            "text": text,
            "error": str(exc),
            "provider": _TTS_PROVIDER,
        }


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

_faster_whisper_model = None


def _get_faster_whisper_model():
    global _faster_whisper_model
    if _faster_whisper_model is None:
        from faster_whisper import WhisperModel

        _faster_whisper_model = WhisperModel(
            _FASTER_WHISPER_MODEL,
            device=_FASTER_WHISPER_DEVICE,
            compute_type=_FASTER_WHISPER_COMPUTE,
        )
    return _faster_whisper_model


async def _faster_whisper_transcribe(
    audio_data: bytes, audio_format: str, language: str
) -> tuple[str, float]:
    """Local faster-whisper transcription (privacy-first, no cloud)."""
    import asyncio
    import math
    import tempfile

    lang = language.split("-")[0] if language else "de"
    suffix = f".{audio_format}" if audio_format else ".wav"

    def _run() -> tuple[str, float]:
        model = _get_faster_whisper_model()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()
            segments, _info = model.transcribe(tmp.name, language=lang, vad_filter=True)
        parts: list[str] = []
        logprobs: list[float] = []
        for seg in segments:
            if seg.text.strip():
                parts.append(seg.text.strip())
            if seg.avg_logprob is not None:
                logprobs.append(seg.avg_logprob)
        text = " ".join(parts).strip()
        if logprobs:
            avg = sum(logprobs) / len(logprobs)
            confidence = min(1.0, max(0.0, math.exp(avg)))
        else:
            confidence = 0.85 if text else 0.0
        return text, confidence

    return await asyncio.to_thread(_run)


async def _whisper_transcribe(audio_data: bytes, audio_format: str, language: str) -> tuple[str, float]:
    """OpenAI Whisper API transcription."""
    import httpx

    if not _OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured for Whisper STT")

    lang_code = language.split("-")[0]  # "de-DE" → "de"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {_OPENAI_API_KEY}"},
            files={"file": (f"audio.{audio_format}", io.BytesIO(audio_data), f"audio/{audio_format}")},
            data={
                "model": "whisper-1",
                "language": lang_code,
                "response_format": "verbose_json",
            },
        )
        response.raise_for_status()
        result = response.json()

    text = result.get("text", "")
    # Whisper verbose_json includes segment-level avg_logprob; approximate confidence
    segments = result.get("segments", [])
    if segments:
        import math
        avg_logprob = sum(s.get("avg_logprob", -1) for s in segments) / len(segments)
        confidence = min(1.0, max(0.0, math.exp(avg_logprob)))
    else:
        confidence = 0.85 if text else 0.0

    return text, confidence


async def _azure_stt(audio_data: bytes, audio_format: str, language: str) -> tuple[str, float]:
    """Azure Cognitive Services Speech-to-Text."""
    import httpx

    if not _AZURE_SPEECH_KEY:
        raise RuntimeError("AZURE_SPEECH_KEY not configured for Azure STT")

    content_type_map = {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "webm": "audio/webm",
    }
    ct = content_type_map.get(audio_format, "audio/wav")

    url = (
        f"https://{_AZURE_SPEECH_REGION}.stt.speech.microsoft.com"
        f"/speech/recognition/conversation/cognitiveservices/v1"
        f"?language={language}&format=detailed"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers={
                "Ocp-Apim-Subscription-Key": _AZURE_SPEECH_KEY,
                "Content-Type": ct,
            },
            content=audio_data,
        )
        response.raise_for_status()
        result = response.json()

    if result.get("RecognitionStatus") != "Success":
        return "", 0.0

    best = result.get("NBest", [{}])[0]
    return best.get("Display", ""), best.get("Confidence", 0.0)


async def _openai_tts(text: str, language: str) -> tuple[str, str]:
    """OpenAI TTS API synthesis."""
    import httpx

    if not _OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured for OpenAI TTS")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {_OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "tts-1",
                "input": text,
                "voice": "nova",  # Good for German
                "response_format": "mp3",
            },
        )
        response.raise_for_status()
        audio_b64 = base64.b64encode(response.content).decode()

    return audio_b64, "audio/mpeg"


async def _azure_tts(text: str, language: str) -> tuple[str, str]:
    """Azure Cognitive Services Text-to-Speech."""
    import httpx

    if not _AZURE_SPEECH_KEY:
        raise RuntimeError("AZURE_SPEECH_KEY not configured for Azure TTS")

    # Map language to Azure voice name
    voice_map = {
        "de-DE": "de-DE-KatjaNeural",
        "en-US": "en-US-JennyNeural",
        "fr-FR": "fr-FR-DeniseNeural",
    }
    voice = voice_map.get(language, "de-DE-KatjaNeural")

    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">'
        f'<voice name="{voice}">{text}</voice></speak>'
    )

    url = f"https://{_AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers={
                "Ocp-Apim-Subscription-Key": _AZURE_SPEECH_KEY,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
            },
            content=ssml.encode("utf-8"),
        )
        response.raise_for_status()
        audio_b64 = base64.b64encode(response.content).decode()

    return audio_b64, "audio/mpeg"
