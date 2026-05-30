"""
Voice stack readiness — STT/TTS/Ollama status for ops and frontend.
"""

from __future__ import annotations

import logging

import httpx

from app.config import settings
from app.services.local_kokoro import is_kokoro_configured
from app.services.local_stt import is_faster_whisper_available
from app.services.local_tts import is_kokoro_available, is_piper_available

logger = logging.getLogger(__name__)


async def _ollama_reachable() -> bool:
    base = settings.OLLAMA_BASE_URL.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{base}/api/tags")
            return response.status_code == 200
    except Exception as exc:
        logger.debug("Ollama probe failed: %s", exc)
        return False


def _tts_ready() -> bool:
    provider = settings.VOICE_TTS_PROVIDER.lower()
    if provider == "browser":
        return True
    if provider == "piper":
        return is_piper_available()
    if provider == "kokoro":
        return is_kokoro_available()
    return False


async def get_voice_status() -> dict:
    """Aggregate voice subsystem readiness."""
    stt_ready = is_faster_whisper_available()
    tts_provider = settings.VOICE_TTS_PROVIDER.lower()
    ollama_ok = await _ollama_reachable()

    return {
        "stt_provider": "faster-whisper" if stt_ready else "browser",
        "stt_ready": stt_ready,
        "tts_provider": tts_provider,
        "tts_ready": _tts_ready(),
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_reachable": ollama_ok,
        "voice_polish_enabled": settings.VOICE_POLISH_ENABLED,
        "voice_summary_enabled": settings.VOICE_SUMMARY_ENABLED,
        "kokoro_configured": is_kokoro_configured(),
        "piper_configured": bool(settings.PIPER_MODEL_PATH),
        "faster_whisper_model": settings.FASTER_WHISPER_MODEL,
    }
