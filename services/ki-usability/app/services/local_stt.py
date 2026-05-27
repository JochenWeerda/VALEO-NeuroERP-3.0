"""
Local STT via faster-whisper (optional dependency, lazy-loaded).
"""

from __future__ import annotations

import asyncio
import io
import logging
import tempfile
from functools import lru_cache
from typing import Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_whisper_model():
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper not installed. pip install faster-whisper"
        ) from exc

    return WhisperModel(
        settings.FASTER_WHISPER_MODEL,
        device=settings.FASTER_WHISPER_DEVICE,
        compute_type=settings.FASTER_WHISPER_COMPUTE,
    )


def _transcribe_sync(audio_bytes: bytes, audio_format: str, language: str) -> Tuple[str, float]:
    model = _get_whisper_model()
    lang = language.split("-")[0] if language else "de"

    suffix = f".{audio_format}" if audio_format else ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        segments, info = model.transcribe(tmp.name, language=lang, vad_filter=True)

    parts = []
    logprobs = []
    for seg in segments:
        if seg.text.strip():
            parts.append(seg.text.strip())
        if seg.avg_logprob is not None:
            logprobs.append(seg.avg_logprob)

    text = " ".join(parts).strip()
    if logprobs:
        import math

        avg = sum(logprobs) / len(logprobs)
        confidence = min(1.0, max(0.0, math.exp(avg)))
    else:
        confidence = 0.85 if text else 0.0

    return text, confidence


async def transcribe_audio(
    audio_bytes: bytes,
    audio_format: str = "wav",
    language: str = "de-DE",
) -> dict:
    """Transcribe audio bytes with faster-whisper in a thread pool."""
    if not audio_bytes:
        return {"text": "", "confidence": 0.0, "provider": "faster-whisper", "error": "Empty audio"}

    try:
        text, confidence = await asyncio.to_thread(
            _transcribe_sync, audio_bytes, audio_format, language
        )
        return {
            "text": text,
            "confidence": confidence,
            "provider": "faster-whisper",
            "language": language,
        }
    except Exception as exc:
        logger.exception("faster-whisper transcription failed")
        return {
            "text": "",
            "confidence": 0.0,
            "provider": "faster-whisper",
            "error": str(exc),
        }


def is_faster_whisper_available() -> bool:
    try:
        import faster_whisper  # noqa: F401

        return True
    except ImportError:
        return False
