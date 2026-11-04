"""
Wave 71 - Slack/Teams work surfaces backed by the knowledge core.
"""
from __future__ import annotations

from fastapi import FastAPI
from testgrenze import ALLE_FACHROLLEN, ersetze_nutzer
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints import channel_work_surfaces
from app.core.tenant import get_tenant_id


@pytest.fixture
def client(require_db) -> TestClient:
    app = FastAPI()
    ersetze_nutzer(app, *ALLE_FACHROLLEN)
    app.include_router(channel_work_surfaces.router)
    # Der Mandant kommt aus der Anmeldung (bis 28.10.2026 aus Rumpf/Query bzw. Nachrichten-Metadaten).
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app)


def test_slack_knowledge_query_returns_contextual_answer(client: TestClient):
    response = client.post(
        "/channels/slack/knowledge-query",
        json={
            "rolle": "support",
            "query": "oidc login",
            "tenant_id": "tenant-a",
            "capability_key": "support_assistant",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kanal"] == "SLACK"
    assert "KNW-SUP-001" in body["knowledge_ids"]
    assert "KNW-SUP-001" in {entry["knowledge_id"] for entry in body["citations"]}
    assert "OIDC" in body["answer"] or "Login" in body["answer"] or "oidc" in body["query"]


def test_teams_knowledge_query_returns_standards(client: TestClient):
    response = client.post(
        "/channels/teams/knowledge-query",
        json={
            "rolle": "vertrieb",
            "query": "angebot freigabe",
            "tenant_id": "tenant-a",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["kanal"] == "TEAMS"
    assert "KNW-SOP-001" in body["knowledge_ids"]
    assert any("standard" in item.lower() for item in body["standards"])


def test_channel_knowledge_query_requires_supported_channel(client: TestClient):
    response = client.post(
        "/channels/email/knowledge-query",
        json={"rolle": "support", "query": "oidc"},
    )
    assert response.status_code == 400


def test_channel_knowledge_query_requires_query(client: TestClient):
    response = client.post(
        "/channels/slack/knowledge-query",
        json={"rolle": "support", "query": "   "},
    )
    assert response.status_code == 400
