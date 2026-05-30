"""
Kokoro TTS via OpenAI-compatible HTTP API (e.g. Kokoro-FastAPI on :8880).
"""

from __future__ import annotations

import base64
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def is_kokoro_configured() -> bool:
    return bool(settings.KOKORO_BASE_URL.strip())


async def synthesize_kokoro(text: str, language: str = "de-DE") -> tuple[str, str]:
    """
    Call Kokoro /v1/audio/speech. Returns (audio_base64, content_type).
    """
    base = settings.KOKORO_BASE_URL.rstrip("/")
    payload = {
        "model": settings.KOKORO_MODEL,
        "input": text,
        "voice": settings.KOKORO_VOICE,
        "response_format": settings.KOKORO_RESPONSE_FORMAT,
    }

    async with httpx.AsyncClient(timeout=settings.KOKORO_TIMEOUT_SEC) as client:
        response = await client.post(f"{base}/v1/audio/speech", json=payload)
        response.raise_for_status()
        audio_bytes = response.content

    if not audio_bytes:
        raise RuntimeError("Kokoro returned empty audio")

    content_type = "audio/mpeg" if settings.KOKORO_RESPONSE_FORMAT == "mp3" else "audio/wav"
    return base64.b64encode(audio_bytes).decode(), content_type
