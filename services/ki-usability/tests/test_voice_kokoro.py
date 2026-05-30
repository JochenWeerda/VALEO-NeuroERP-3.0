"""
Tests für Slice-014: Kokoro TTS provider.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from app.config import settings
from app.services.local_tts import synthesize_speech


class TestKokoroTts:
    def test_kokoro_success(self, monkeypatch):
        monkeypatch.setattr(settings, "VOICE_TTS_PROVIDER", "kokoro")
        with patch(
            "app.services.local_tts.is_kokoro_available",
            return_value=True,
        ), patch(
            "app.services.local_tts.synthesize_kokoro",
            new=AsyncMock(return_value=("audio123", "audio/mpeg")),
        ):
            result = asyncio.run(synthesize_speech("Hallo Welt"))
        assert result["provider"] == "kokoro"
        assert result["audio_base64"] == "audio123"
        assert result["browser_hint"] is False

    def test_kokoro_fallback_on_error(self, monkeypatch):
        monkeypatch.setattr(settings, "VOICE_TTS_PROVIDER", "kokoro")
        with patch(
            "app.services.local_tts.is_kokoro_available",
            return_value=True,
        ), patch(
            "app.services.local_tts.synthesize_kokoro",
            new=AsyncMock(side_effect=RuntimeError("Kokoro offline")),
        ):
            result = asyncio.run(synthesize_speech("Test"))
        assert result["provider"] == "browser"
        assert result["browser_hint"] is True
        assert "Kokoro offline" in (result.get("error") or "")
