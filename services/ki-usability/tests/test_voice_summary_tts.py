"""
Tests für Slice-013b: Voice Summary (Ollama) + TTS (Piper/Browser).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.config import settings
from app.services.local_tts import synthesize_speech
from app.services.voice_summary import summarize_text

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
client = TestClient(app)


class TestSummarizeTextService:
    def test_empty_input(self):
        result = asyncio.run(summarize_text("  "))
        assert result["summary_text"] == ""
        assert result["provider"] == "none"

    def test_ollama_success(self):
        with patch(
            "app.services.voice_summary.summarize_transcript",
            new=AsyncMock(return_value=("Kurze Zusammenfassung.", "mistral")),
        ):
            result = asyncio.run(summarize_text("Sehr langer ERP-Text " * 20))
        assert result["summary_text"] == "Kurze Zusammenfassung."
        assert result["provider"] == "ollama:mistral"
        assert result["summary_applied"] is True
        assert result["estimated_seconds"] >= 1

    def test_passthrough_when_disabled(self, monkeypatch):
        monkeypatch.setattr(settings, "VOICE_SUMMARY_ENABLED", False)
        text = " ".join(["Wort"] * 60)
        result = asyncio.run(summarize_text(text))
        assert len(result["summary_text"].split()) <= settings.VOICE_SUMMARY_MAX_WORDS
        assert result["provider"] == "passthrough"

    def test_fallback_on_ollama_error(self):
        with patch(
            "app.services.voice_summary.summarize_transcript",
            new=AsyncMock(side_effect=RuntimeError("Ollama offline")),
        ):
            result = asyncio.run(summarize_text("Fallback Text " * 30))
        assert result["provider"] == "fallback-truncate"
        assert result["summary_text"]
        assert "Ollama offline" in (result.get("error") or "")


class TestSynthesizeSpeechService:
    def test_empty_input(self):
        result = asyncio.run(synthesize_speech(""))
        assert result["provider"] == "none"

    def test_browser_hint_without_piper(self, monkeypatch):
        monkeypatch.setattr("app.services.local_tts.is_piper_available", lambda: False)
        result = asyncio.run(synthesize_speech("Hallo Welt"))
        assert result["provider"] == "browser"
        assert result["browser_hint"] is True

    def test_piper_success(self, monkeypatch):
        monkeypatch.setattr("app.services.local_tts.is_piper_available", lambda: True)
        monkeypatch.setattr(settings, "VOICE_TTS_PROVIDER", "piper")
        with patch(
            "app.services.local_tts._synthesize_piper_sync",
            return_value=("audio123", "audio/wav"),
        ):
            result = asyncio.run(synthesize_speech("Test"))
        assert result["provider"] == "piper"
        assert result["audio_base64"] == "audio123"
        assert result["content_type"] == "audio/wav"


class TestSummaryEndpoint:
    def test_summary_returns_speakable_text(self):
        with patch(
            "app.services.voice_summary.summarize_transcript",
            new=AsyncMock(return_value=("Wareneingang und Inventur.", "mistral")),
        ):
            resp = client.post(
                "/api/v1/voice/summary",
                json={"text": "Langer Text ueber Wareneingang und Inventur im Lager."},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary_text"] == "Wareneingang und Inventur."
        assert data["provider"] == "ollama:mistral"


class TestSynthesizeEndpoint:
    def test_synthesize_browser_fallback(self, monkeypatch):
        monkeypatch.setattr("app.services.local_tts.is_piper_available", lambda: False)
        resp = client.post(
            "/api/v1/voice/synthesize",
            json={"text": "Befehl ausgefuehrt.", "language": "de-DE"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["browser_hint"] is True
        assert data["provider"] == "browser"

    def test_synthesize_piper_audio(self, monkeypatch):
        monkeypatch.setattr("app.services.local_tts.is_piper_available", lambda: True)
        monkeypatch.setattr(settings, "VOICE_TTS_PROVIDER", "piper")
        with patch(
            "app.services.local_tts._synthesize_piper_sync",
            return_value=("YmFzZTY0", "audio/wav"),
        ):
            resp = client.post(
                "/api/v1/voice/synthesize",
                json={"text": "Inventur starten."},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["provider"] == "piper"
        assert data["audio_base64"] == "YmFzZTY0"
