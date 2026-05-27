"""
Tests für Slice-013c: Voice Pipeline endpoint.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
client = TestClient(app)


class TestVoicePipelineEndpoint:
    def test_dictate_mode(self):
        with patch(
            "app.services.voice_pipeline.polish_text",
            new=AsyncMock(
                return_value={
                    "raw_text": "aeh hallo",
                    "polished_text": "Hallo.",
                    "provider": "ollama:mistral",
                    "polish_applied": True,
                }
            ),
        ):
            resp = client.post(
                "/api/v1/voice/pipeline",
                json={"mode": "dictate", "text": "aeh hallo"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "dictate"
        assert data["polished_text"] == "Hallo."

    def test_summary_mode(self):
        with patch(
            "app.services.voice_pipeline.summarize_text",
            new=AsyncMock(
                return_value={
                    "source_text": "lang",
                    "summary_text": "Kurz.",
                    "provider": "ollama:mistral",
                    "summary_applied": True,
                    "estimated_seconds": 2,
                }
            ),
        ):
            resp = client.post(
                "/api/v1/voice/pipeline",
                json={"mode": "summary", "text": "Sehr langer Text " * 10},
            )
        assert resp.status_code == 200
        assert resp.json()["summary_text"] == "Kurz."

    def test_intent_mode(self):
        with patch(
            "app.services.voice_pipeline.intent_resolver.resolve",
            return_value=type(
                "R",
                (),
                {
                    "action_id": "nav-lager",
                    "params": {},
                    "confidence": 0.9,
                    "raw_text": "Lager oeffnen",
                },
            )(),
        ):
            resp = client.post(
                "/api/v1/voice/pipeline",
                json={"mode": "intent", "text": "Lager oeffnen", "context": {"domain": "lager"}},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["resolved"]["action_id"] == "nav-lager"

    def test_invalid_mode(self):
        resp = client.post("/api/v1/voice/pipeline", json={"mode": "unknown"})
        assert resp.status_code == 400
