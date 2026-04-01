from __future__ import annotations

import importlib
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.api.v1.endpoints import websocket as realtime_ws
from app.core import security
from app.core.config import settings
from main import app

policy_router_module = importlib.import_module("app.policy.router")


client = TestClient(app)


@pytest.fixture(autouse=True)
def _configure_dev_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(security.settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(realtime_ws.settings, "API_DEV_TOKEN", "dev-token")
    monkeypatch.setattr(policy_router_module.settings, "API_DEV_TOKEN", "dev-token")


def test_pos_websocket_rejects_missing_token() -> None:
    try:
        with client.websocket_connect("/api/v1/ws/pos/T-1"):
            raise AssertionError("websocket connection should have been rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_pos_websocket_scopes_terminal_registry_by_tenant() -> None:
    with client.websocket_connect("/api/v1/ws/pos/T-1?token=dev-token&tenant_id=tenant-a"):
        with client.websocket_connect("/api/v1/ws/pos/T-1?token=dev-token&tenant_id=tenant-b"):
            assert "tenant-a:T-1" in realtime_ws.active_terminals
            assert "tenant-b:T-1" in realtime_ws.active_terminals
            assert len(realtime_ws.active_terminals) == 2


def test_workflow_websocket_rejects_missing_token() -> None:
    try:
        with client.websocket_connect("/api/v1/ws/workflow/WF-1"):
            raise AssertionError("websocket connection should have been rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_workflow_websocket_reads_tenant_scoped_status(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    def _fake_cache_get_json(key: str):
        captured.append(key)
        return {"step": "approved"}

    monkeypatch.setattr("app.core.cache.cache_get_json", _fake_cache_get_json)

    with client.websocket_connect("/api/v1/ws/workflow/WF-1?token=dev-token&tenant_id=tenant-a") as websocket:
        websocket.send_json({"action": "status"})
        response = websocket.receive_json()

    assert captured == ["workflow:tenant-a:WF-1:status"]
    assert response["tenant_id"] == "tenant-a"
    assert response["data"] == {"step": "approved"}


def test_policy_websocket_rejects_missing_token() -> None:
    try:
        with client.websocket_connect("/api/mcp/policy/ws"):
            raise AssertionError("websocket connection should have been rejected")
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


def test_policy_websocket_accepts_dev_token() -> None:
    with client.websocket_connect("/api/mcp/policy/ws?token=dev-token") as websocket:
        websocket.send_text("ping")
