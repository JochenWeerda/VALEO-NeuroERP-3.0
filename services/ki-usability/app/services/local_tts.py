"""
Local TTS via Piper (optional) with browser fallback hint.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def is_piper_available() -> bool:
    """True if Piper Python package or CLI + model path is configured."""
    if _piper_python_available():
        return bool(settings.PIPER_MODEL_PATH and Path(settings.PIPER_MODEL_PATH).exists())
    exe = settings.PIPER_EXECUTABLE or "piper"
    return bool(
        settings.PIPER_MODEL_PATH
        and Path(settings.PIPER_MODEL_PATH).exists()
        and shutil.which(exe)
    )


def _piper_python_available() -> bool:
    try:
        import piper  # noqa: F401

        return True
    except ImportError:
        return False


def _synthesize_piper_sync(text: str) -> tuple[str, str]:
    """Returns (audio_base64, content_type)."""
    model_path = settings.PIPER_MODEL_PATH
    if not model_path or not Path(model_path).exists():
        raise RuntimeError(f"Piper model not found: {model_path}")

    if _piper_python_available():
        return _synthesize_piper_python(text, model_path)

    exe = settings.PIPER_EXECUTABLE or "piper"
    if not shutil.which(exe):
        raise RuntimeError(f"Piper executable not found: {exe}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        out_path = tmp.name

    try:
        proc = subprocess.run(
            [exe, "--model", model_path, "--output_file", out_path],
            input=text.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"Piper CLI failed: {stderr.strip() or proc.returncode}")
        audio_bytes = Path(out_path).read_bytes()
        if not audio_bytes:
            raise RuntimeError("Piper produced empty audio")
        return base64.b64encode(audio_bytes).decode(), "audio/wav"
    finally:
        try:
            os.unlink(out_path)
        except OSError:
            pass


def _synthesize_piper_python(text: str, model_path: str) -> tuple[str, str]:
    import io
    import wave

    from piper import PiperVoice

    voice = PiperVoice.load(model_path)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        voice.synthesize(text, wav_file)
    audio_bytes = buf.getvalue()
    if not audio_bytes:
        raise RuntimeError("Piper Python synthesize produced empty audio")
    return base64.b64encode(audio_bytes).decode(), "audio/wav"


async def synthesize_speech(text: str, language: str = "de-DE") -> dict:
    """
    Synthesize speech locally via Piper when available.
    Otherwise return browser SpeechSynthesis hint for the client.
    """
    raw = (text or "").strip()
    if not raw:
        return {
            "text": "",
            "provider": "none",
            "browser_hint": False,
        }

    provider = settings.VOICE_TTS_PROVIDER.lower()
    if provider == "browser" or not is_piper_available():
        return {
            "text": raw,
            "provider": "browser",
            "browser_hint": True,
            "language": language,
            "hint": "Use Web Speech API SpeechSynthesis on client side",
        }

    try:
        audio_b64, content_type = await asyncio.to_thread(_synthesize_piper_sync, raw)
        return {
            "text": raw,
            "audio_base64": audio_b64,
            "content_type": content_type,
            "provider": "piper",
            "browser_hint": False,
            "language": language,
        }
    except Exception as exc:
        logger.warning("Piper TTS failed, returning browser hint: %s", exc)
        return {
            "text": raw,
            "provider": "browser",
            "browser_hint": True,
            "language": language,
            "hint": "Use Web Speech API SpeechSynthesis on client side",
            "error": str(exc),
        }
