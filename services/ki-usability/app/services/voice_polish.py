"""
Voice polish pipeline — raw transcript to business-ready text via Ollama.
"""

from __future__ import annotations

import logging

from app.config import settings
from app.services.ollama_client import polish_transcript

logger = logging.getLogger(__name__)


async def polish_text(raw_text: str, tone: str = "business") -> dict:
    """
    Polish STT transcript. Falls back to raw text if Ollama disabled or unreachable.
    """
    raw = (raw_text or "").strip()
    if not raw:
        return {
            "raw_text": "",
            "polished_text": "",
            "provider": "none",
            "polish_applied": False,
        }

    if not settings.VOICE_POLISH_ENABLED:
        return {
            "raw_text": raw,
            "polished_text": raw,
            "provider": "passthrough",
            "polish_applied": False,
        }

    try:
        polished, model = await polish_transcript(raw, tone=tone)
        return {
            "raw_text": raw,
            "polished_text": polished,
            "provider": f"ollama:{model}",
            "polish_applied": polished != raw,
        }
    except Exception as exc:
        logger.warning("Ollama polish failed, using raw transcript: %s", exc)
        return {
            "raw_text": raw,
            "polished_text": raw,
            "provider": "fallback-raw",
            "polish_applied": False,
            "error": str(exc),
        }
