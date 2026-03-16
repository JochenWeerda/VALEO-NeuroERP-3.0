from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agents


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(agents.router, prefix="/api/v1/agents")
    return TestClient(app)


def test_genxais_capabilities_endpoint_lists_productive_capabilities():
    client = _client()

    response = client.get("/api/v1/agents/genxais/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert [item["capability_key"] for item in payload] == [
        "bestellvorschlag_assistant",
        "finance_skonto_assistant",
        "compliance_copilot",
    ]
