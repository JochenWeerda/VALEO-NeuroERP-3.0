from __future__ import annotations

from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect

from app.api.v1.endpoints import copilot_ws
from app.core import security
from app.core.config import settings
from main import app


client = TestClient(app)


@pytest.fixture()
def dev_token(monkeypatch: pytest.MonkeyPatch) -> str:
    token = "sec-test-token"
    monkeypatch.setattr(settings, "API_DEV_TOKEN", token)
    monkeypatch.setattr(security.settings, "API_DEV_TOKEN", token)
    monkeypatch.setattr(copilot_ws.settings, "API_DEV_TOKEN", token)
    return token


def test_system_metrics_return_authenticated_tenant_context(dev_token: str) -> None:
    response = client.get(
        "/api/v1/metrics/system",
        headers={
            "Authorization": f"Bearer {dev_token}",
            "X-Tenant-ID": "tenant-secure",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-secure"
    assert body["user_id"] == "dev"


def test_copilot_websocket_rejects_missing_token() -> None:
    try:
        with client.websocket_connect("/api/v1/copilot/chat"):
            raise AssertionError("websocket connection should have been rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_copilot_websocket_binds_session_to_authenticated_tenant(
    monkeypatch: pytest.MonkeyPatch,
    dev_token: str,
) -> None:
    captured_contexts: list[dict] = []

    def _fake_run_pipeline_sync(user_text: str, session_context: dict) -> dict:
        captured_contexts.append(dict(session_context))
        return {
            "status": "executed",
            "intent": {
                "intent": "knowledge_query",
                "confidence_score": 0.9,
                "category": "query",
                "risk_class": "low",
            },
            "plan": {
                "step_count": 1,
                "steps": [{"order": 1, "description": f"Echo {user_text}", "action": "query"}],
            },
        }

    monkeypatch.setattr(copilot_ws, "_run_pipeline_sync", _fake_run_pipeline_sync)

    with client.websocket_connect(
        f"/api/v1/copilot/chat?token={dev_token}&tenant_id=tenant-secure"
    ) as websocket:
        session_start = websocket.receive_json()
        assert session_start["type"] == "session_start"
        assert session_start["tenant_id"] == "tenant-secure"

        websocket.send_json(
            {
                "text": "zeige queue",
                "context": {
                    "tenant_id": "tenant-evil",
                    "user_id": "mallory",
                    "roles": ["admin"],
                    "scope": "copilot",
                },
            }
        )

        websocket.receive_json()  # state_change
        pipeline_result = websocket.receive_json()
        assert pipeline_result["type"] == "pipeline_result"

    assert captured_contexts
    assert captured_contexts[0]["tenant_id"] == "tenant-secure"
    assert captured_contexts[0]["user_id"] == "dev"
    assert captured_contexts[0]["roles"] == ["admin"]
    assert captured_contexts[0]["scope"] == "copilot"
