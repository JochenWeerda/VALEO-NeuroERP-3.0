"""
Ollama HTTP client for local LLM tasks (polish, summary).
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

POLISH_SYSTEM_PROMPT = (
    "Du bist ein deutscher Business-Assistent fuer ERP-Diktate. "
    "Bereinige das Transkript: entferne Fuellwoerter und Wiederholungen, "
    "korrigiere Grammatik leicht, behalte Fachbegriffe und den Ton bei. "
    "Antworte nur mit dem bereinigten Text, ohne Erklaerung."
)

SUMMARY_SYSTEM_PROMPT = (
    "Du bist ein deutscher Business-Assistent fuer ERP-Sprachausgabe. "
    "Fasse den Text in maximal der angegebenen Wortanzahl zusammen — "
    "klar, praegnant, zum Vorlesen geeignet. "
    "Antworte nur mit der Zusammenfassung, ohne Einleitung oder Erklaerung."
)


async def ollama_generate(
    user_prompt: str,
    *,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> tuple[str, str]:
    """
    Call Ollama /api/chat. Returns (content, model_used).
    Raises RuntimeError on connection or API errors.
    """
    base = settings.OLLAMA_BASE_URL.rstrip("/")
    model_name = model or settings.OLLAMA_POLISH_MODEL
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 512},
    }

    async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SEC) as client:
        response = await client.post(f"{base}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    content = (data.get("message") or {}).get("content", "").strip()
    if not content:
        raise RuntimeError("Ollama returned empty content")
    return content, model_name


async def polish_transcript(raw_text: str, tone: str = "business") -> tuple[str, str]:
    """Polish raw STT transcript via Ollama."""
    tone_hint = {
        "business": "Geschaeftlich und klar formulieren.",
        "casual": "Natuerlich und locker formulieren, aber professionell.",
        "formal": "Formell und praezise formulieren.",
    }.get(tone, "Geschaeftlich und klar formulieren.")

    prompt = (
        f"{tone_hint}\n\n"
        f"Rohtranskript:\n{raw_text.strip()}\n\n"
        "Bereinigter Text:"
    )
    return await ollama_generate(prompt, system=POLISH_SYSTEM_PROMPT)


async def summarize_transcript(raw_text: str, max_words: int = 45) -> tuple[str, str]:
    """Summarize text for ~15s voice readback via Ollama."""
    prompt = (
        f"Fasse den folgenden Text in hoechstens {max_words} Woertern zusammen "
        f"(ca. 15 Sekunden Vorlesezeit).\n\n"
        f"Text:\n{raw_text.strip()}\n\n"
        "Zusammenfassung:"
    )
    model = settings.OLLAMA_SUMMARY_MODEL or settings.OLLAMA_POLISH_MODEL
    return await ollama_generate(prompt, system=SUMMARY_SYSTEM_PROMPT, model=model)
