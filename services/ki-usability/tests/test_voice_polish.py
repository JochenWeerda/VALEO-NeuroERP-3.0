"""
Tests für Slice-013a: Voice Polish (Ollama) + /voice/polish Endpoint.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.config import settings
from app.services.voice_polish import polish_text

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
client = TestClient(app)


class TestPolishTextService:
    def test_empty_input(self):
        result = asyncio.run(polish_text("   "))
        assert result["raw_text"] == ""
        assert result["polished_text"] == ""
        assert result["provider"] == "none"
        assert result["polish_applied"] is False

    def test_ollama_success(self):
        with patch(
            "app.services.voice_polish.polish_transcript",
            new=AsyncMock(return_value=("Wareneingang buchen bitte.", "mistral")),
        ):
            result = asyncio.run(polish_text("äh wareneingang buchen bitte"))
        assert result["raw_text"] == "äh wareneingang buchen bitte"
        assert result["polished_text"] == "Wareneingang buchen bitte."
        assert result["provider"] == "ollama:mistral"
        assert result["polish_applied"] is True

    def test_passthrough_when_disabled(self, monkeypatch):
        monkeypatch.setattr(settings, "VOICE_POLISH_ENABLED", False)
        result = asyncio.run(polish_text("Rohtext unveraendert"))
        assert result["polished_text"] == "Rohtext unveraendert"
        assert result["provider"] == "passthrough"
        assert result["polish_applied"] is False

    def test_fallback_on_ollama_error(self):
        with patch(
            "app.services.voice_polish.polish_transcript",
            new=AsyncMock(side_effect=RuntimeError("Ollama offline")),
        ):
            result = asyncio.run(polish_text("Fallback Rohtext"))
        assert result["polished_text"] == "Fallback Rohtext"
        assert result["provider"] == "fallback-raw"
        assert result["polish_applied"] is False
        assert "Ollama offline" in (result.get("error") or "")


class TestPolishEndpoint:
    def test_polish_returns_raw_and_polished(self):
        with patch(
            "app.services.voice_polish.polish_transcript",
            new=AsyncMock(return_value=("Inventur starten.", "mistral")),
        ):
            resp = client.post(
                "/api/v1/voice/polish",
                json={"text": "äh inventur starten", "tone": "business"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["raw_text"] == "äh inventur starten"
        assert data["polished_text"] == "Inventur starten."
        assert data["provider"] == "ollama:mistral"
        assert data["polish_applied"] is True

    def test_polish_validation_empty_text(self):
        resp = client.post("/api/v1/voice/polish", json={"text": ""})
        assert resp.status_code == 422


class TestTranscribeEndpoint:
    def test_transcribe_503_without_faster_whisper(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.endpoints.voice.is_faster_whisper_available",
            lambda: False,
        )
        resp = client.post(
            "/api/v1/voice/transcribe",
            json={"audio_base64": "dGVzdA==", "audio_format": "wav"},
        )
        assert resp.status_code == 503

    def test_transcribe_invalid_base64(self, monkeypatch):
        monkeypatch.setattr(
            "app.api.v1.endpoints.voice.is_faster_whisper_available",
            lambda: True,
        )
        resp = client.post(
            "/api/v1/voice/transcribe",
            json={"audio_base64": "!!!not-base64!!!", "audio_format": "wav"},
        )
        assert resp.status_code == 400
