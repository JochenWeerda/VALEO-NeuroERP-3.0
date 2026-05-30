"""
Tests für Slice-015: GET /voice/status readiness.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
client = TestClient(app)


class TestVoiceStatusEndpoint:
    def test_status_returns_readiness_fields(self):
        with (
            patch(
                "app.services.voice_status.is_faster_whisper_available",
                return_value=False,
            ),
            patch(
                "app.services.voice_status._tts_ready",
                return_value=True,
            ),
            patch(
                "app.services.voice_status._ollama_reachable",
                new=AsyncMock(return_value=True),
            ),
        ):
            resp = client.get("/api/v1/voice/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stt_provider"] == "browser"
        assert data["stt_ready"] is False
        assert data["tts_ready"] is True
        assert data["ollama_reachable"] is True
        assert "voice_polish_enabled" in data
        assert "voice_summary_enabled" in data

    def test_status_stt_ready_when_faster_whisper_available(self):
        with (
            patch(
                "app.services.voice_status.is_faster_whisper_available",
                return_value=True,
            ),
            patch(
                "app.services.voice_status._tts_ready",
                return_value=False,
            ),
            patch(
                "app.services.voice_status._ollama_reachable",
                new=AsyncMock(return_value=False),
            ),
        ):
            resp = client.get("/api/v1/voice/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stt_provider"] == "faster-whisper"
        assert data["stt_ready"] is True
        assert data["ollama_reachable"] is False
