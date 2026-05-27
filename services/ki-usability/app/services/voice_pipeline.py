"""
WhisperBar pipeline — combined dictate / summary / intent flows.
"""

from __future__ import annotations

import base64
import binascii
import logging
from typing import Any, Optional

from app.services.intent_resolver import intent_resolver
from app.services.local_stt import transcribe_audio
from app.services.local_tts import synthesize_speech
from app.services.voice_polish import polish_text
from app.services.voice_summary import summarize_text

logger = logging.getLogger(__name__)


async def run_voice_pipeline(
    *,
    mode: str,
    text: Optional[str] = None,
    audio_base64: Optional[str] = None,
    audio_format: str = "wav",
    language: str = "de-DE",
    tone: str = "business",
    context: Optional[dict[str, Any]] = None,
    synthesize: bool = False,
) -> dict[str, Any]:
    """
    Unified WhisperBar pipeline.
    Modes: dictate | summary | intent
    """
    ctx = context or {}
    normalized_mode = (mode or "dictate").lower()

    if normalized_mode == "dictate":
        return await _pipeline_dictate(
            text=text,
            audio_base64=audio_base64,
            audio_format=audio_format,
            language=language,
            tone=tone,
        )

    if normalized_mode == "summary":
        return await _pipeline_summary(
            text=text or "",
            language=language,
            synthesize=synthesize,
        )

    if normalized_mode == "intent":
        return await _pipeline_intent(
            text=text or "",
            context=ctx,
            tone=tone,
            audio_base64=audio_base64,
            audio_format=audio_format,
            language=language,
        )

    raise ValueError(f"Unknown pipeline mode: {mode}")


async def _pipeline_dictate(
    *,
    text: Optional[str],
    audio_base64: Optional[str],
    audio_format: str,
    language: str,
    tone: str,
) -> dict[str, Any]:
    raw = (text or "").strip()

    if audio_base64 and not raw:
        try:
            audio_bytes = base64.b64decode(audio_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            return {"mode": "dictate", "error": f"Invalid base64 audio: {exc}"}
        stt = await transcribe_audio(audio_bytes, audio_format=audio_format, language=language)
        if stt.get("error") and not stt.get("text"):
            return {"mode": "dictate", "error": stt["error"], "provider": stt.get("provider")}
        raw = (stt.get("text") or "").strip()

    if not raw:
        return {"mode": "dictate", "error": "No text or audio provided", "raw_text": "", "polished_text": ""}

    polished = await polish_text(raw, tone=tone)
    return {
        "mode": "dictate",
        "raw_text": polished["raw_text"],
        "polished_text": polished["polished_text"],
        "provider": polished["provider"],
        "polish_applied": polished["polish_applied"],
        "error": polished.get("error"),
    }


async def _pipeline_summary(
    *,
    text: str,
    language: str,
    synthesize: bool,
) -> dict[str, Any]:
    summary = await summarize_text(text)
    result: dict[str, Any] = {
        "mode": "summary",
        **summary,
    }
    if synthesize and summary.get("summary_text"):
        tts = await synthesize_speech(summary["summary_text"], language=language)
        result["tts"] = tts
    return result


async def _pipeline_intent(
    *,
    text: str,
    context: dict[str, Any],
    tone: str,
    audio_base64: Optional[str],
    audio_format: str,
    language: str,
) -> dict[str, Any]:
    working_text = (text or "").strip()

    if audio_base64 and not working_text:
        dictate = await _pipeline_dictate(
            text=None,
            audio_base64=audio_base64,
            audio_format=audio_format,
            language=language,
            tone=tone,
        )
        if dictate.get("error") and not dictate.get("polished_text"):
            return {"mode": "intent", "error": dictate["error"]}
        working_text = dictate.get("polished_text") or dictate.get("raw_text") or ""

    if not working_text:
        return {"mode": "intent", "error": "No text for intent resolution"}

    resolved = intent_resolver.resolve(working_text, context=context)
    if not resolved:
        return {
            "mode": "intent",
            "text": working_text,
            "resolved": None,
            "error": "No intent matched",
        }

    return {
        "mode": "intent",
        "text": working_text,
        "resolved": {
            "action_id": resolved.action_id,
            "params": resolved.params,
            "confidence": resolved.confidence,
            "raw_text": resolved.raw_text,
        },
    }
