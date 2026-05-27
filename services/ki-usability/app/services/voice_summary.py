"""
Voice summary pipeline — long text to ~15s speakable summary via Ollama.
"""

from __future__ import annotations

import logging

from app.config import settings
from app.services.ollama_client import summarize_transcript

logger = logging.getLogger(__name__)


async def summarize_text(raw_text: str, max_words: int | None = None) -> dict:
    """
    Summarize text for voice readback (~15 seconds speakable).
    Falls back to truncated raw text if Ollama disabled or unreachable.
    """
    raw = (raw_text or "").strip()
    limit = max_words or settings.VOICE_SUMMARY_MAX_WORDS
    if not raw:
        return {
            "source_text": "",
            "summary_text": "",
            "provider": "none",
            "summary_applied": False,
            "estimated_seconds": 0,
        }

    if not settings.VOICE_SUMMARY_ENABLED:
        summary = _truncate_words(raw, limit)
        return {
            "source_text": raw,
            "summary_text": summary,
            "provider": "passthrough",
            "summary_applied": summary != raw,
            "estimated_seconds": _estimate_seconds(summary),
        }

    try:
        summary, model = await summarize_transcript(raw, max_words=limit)
        return {
            "source_text": raw,
            "summary_text": summary,
            "provider": f"ollama:{model}",
            "summary_applied": summary != raw,
            "estimated_seconds": _estimate_seconds(summary),
        }
    except Exception as exc:
        logger.warning("Ollama summary failed, using truncated source: %s", exc)
        summary = _truncate_words(raw, limit)
        return {
            "source_text": raw,
            "summary_text": summary,
            "provider": "fallback-truncate",
            "summary_applied": summary != raw,
            "estimated_seconds": _estimate_seconds(summary),
            "error": str(exc),
        }


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;:") + "…"


def _estimate_seconds(text: str) -> int:
    """Rough German TTS duration estimate (~150 wpm)."""
    words = len(text.split())
    return max(1, round(words / 2.5))
