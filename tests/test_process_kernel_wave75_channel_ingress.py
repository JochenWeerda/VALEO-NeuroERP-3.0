"""
Wave 75 - Signed Slack/Teams ingress for channel work surfaces.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import channel_work_surfaces
from app.core.config import settings
from app.core.channel_ingress import format_slack_dispatch_result, normalize_slack_event


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(channel_work_surfaces.router)
    return TestClient(app)


def _slack_signed_request(payload: dict, secret: str = "slack-secret") -> tuple[str, dict[str, str]]:
    body = json.dumps(payload, separators=(",", ":"))
    ts = str(int(time.time()))
    digest = hmac.new(
        secret.encode("utf-8"),
        f"v0:{ts}:{body}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return body, {
        "X-Slack-Request-Timestamp": ts,
        "X-Slack-Signature": f"v0={digest}",
        "Content-Type": "application/json",
    }


def _teams_signed_request(payload: dict, secret: str = "teams-secret") -> tuple[str, dict[str, str]]:
    body_text = json.dumps(payload, separators=(",", ":"))
    body = body_text.encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return body_text, {
        "X-Teams-Signature": digest,
        "Content-Type": "application/json",
    }


def test_slack_url_verification_returns_challenge(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    payload = {"type": "url_verification", "challenge": "abc-123"}
    body, headers = _slack_signed_request(payload)
    response = client.post("/channels/slack/events", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"challenge": "abc-123"}


def test_slack_event_rejects_invalid_signature(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    payload = {"event": {"text": "oidc login", "metadata": {"intent": "knowledge_query"}}}
    response = client.post(
        "/channels/slack/events",
        data=json.dumps(payload),
        headers={
            "X-Slack-Request-Timestamp": str(int(time.time())),
            "X-Slack-Signature": "v0=bad",
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 401


def test_slack_event_dispatches_knowledge_query(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    posted: list[dict] = []
    monkeypatch.setattr(
        "app.api.v1.endpoints.channel_work_surfaces.dispatch_channel_ingress",
        lambda db, envelope: {
            "intent": envelope.intent,
            "result": {"kanal": envelope.kanal.value, "query": envelope.query, "rolle": envelope.rolle},
        },
    )
    async def _capture_post(payload, dispatch_result):
        posted.append(dispatch_result)
        return {"ok": True}
    monkeypatch.setattr("app.api.v1.endpoints.channel_work_surfaces.maybe_post_slack_response", _capture_post)
    payload = {
        "event": {
            "text": "<@UAPP> oidc login",
            "user": "U123",
            "channel": "C123",
            "ts": "1710000000.100",
            "metadata": {"intent": "knowledge_query", "rolle": "support", "tenant_id": "t1"},
        }
    }
    body, headers = _slack_signed_request(payload)
    response = client.post("/channels/slack/events", content=body, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "knowledge_query"
    assert body["result"]["kanal"] == "SLACK"
    assert body["result"]["query"] == "oidc login"
    assert posted and posted[0]["intent"] == "knowledge_query"


def test_slack_event_dispatches_process_execute(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    monkeypatch.setattr(
        "app.api.v1.endpoints.channel_work_surfaces.dispatch_channel_ingress",
        lambda db, envelope: {"intent": envelope.intent, "result": {"thread_id": "cht-1"}},
    )
    async def _capture_post(payload, dispatch_result):
        return {"ok": True}
    monkeypatch.setattr("app.api.v1.endpoints.channel_work_surfaces.maybe_post_slack_response", _capture_post)
    payload = {
        "event": {
            "text": "",
            "metadata": {
                "intent": "process_execute",
                "rolle": "settlement_manager",
                "tenant_id": "t1",
                "payload": {
                    "process_definition_key": "quality_to_settlement",
                    "command_name": "FinalizeAgrarSettlement",
                    "aggregate_type": "agrar_settlement",
                    "aggregate_id": "SET-1",
                    "command_payload": {"status": "DRAFT"},
                    "idempotency_key": "slack-1",
                },
            },
        }
    }
    body, headers = _slack_signed_request(payload)
    response = client.post("/channels/slack/events", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["intent"] == "process_execute"


def test_slack_event_ignores_bot_messages(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    payload = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "subtype": "bot_message",
            "bot_id": "B123",
            "channel": "C123",
            "text": "bot echo",
        },
    }
    body, headers = _slack_signed_request(payload)
    response = client.post("/channels/slack/events", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"ignored": True, "reason": "bot_or_non_user_event"}


def test_teams_event_rejects_invalid_signature(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_TEAMS_WEBHOOK_SECRET", "teams-secret")
    payload = {"text": "oidc login", "channelData": {"metadata": {"intent": "knowledge_query"}}}
    response = client.post(
        "/channels/teams/events",
        data=json.dumps(payload),
        headers={"X-Teams-Signature": "bad", "Content-Type": "application/json"},
    )
    assert response.status_code == 401


def test_teams_event_dispatches_knowledge_query(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_TEAMS_WEBHOOK_SECRET", "teams-secret")
    monkeypatch.setattr(
        "app.api.v1.endpoints.channel_work_surfaces.dispatch_channel_ingress",
        lambda db, envelope: {
            "intent": envelope.intent,
            "result": {"kanal": envelope.kanal.value, "channel_user_id": envelope.channel_user_id},
        },
    )
    payload = {
        "text": "angebot freigabe",
        "from": {"id": "teams-user-1"},
        "channelData": {"metadata": {"intent": "knowledge_query", "rolle": "vertrieb", "tenant_id": "t1"}},
    }
    body, headers = _teams_signed_request(payload)
    response = client.post("/channels/teams/events", content=body, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "knowledge_query"
    assert body["result"]["kanal"] == "TEAMS"
    assert body["result"]["channel_user_id"] == "teams-user-1"


def test_teams_event_dispatches_approval_decision(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_TEAMS_WEBHOOK_SECRET", "teams-secret")
    monkeypatch.setattr(
        "app.api.v1.endpoints.channel_work_surfaces.dispatch_channel_ingress",
        lambda db, envelope: {"intent": envelope.intent, "result": {"status": "accepted"}},
    )
    payload = {
        "text": "genehmigt",
        "from": {"id": "teams-user-2"},
        "channelData": {
            "metadata": {
                "intent": "approval_decision",
                "rolle": "teamleiter",
                "tenant_id": "t1",
                "payload": {
                    "thread_id": "cht-99",
                    "decision": "GENEHMIGT",
                    "approver_role": "teamleiter",
                },
            }
        },
    }
    body, headers = _teams_signed_request(payload)
    response = client.post("/channels/teams/events", content=body, headers=headers)
    assert response.status_code == 200
    assert response.json()["intent"] == "approval_decision"


def test_slack_event_returns_400_for_unknown_intent(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_SIGNING_SECRET", "slack-secret")
    payload = {"event": {"text": "x", "metadata": {"intent": "does_not_exist"}}}
    body, headers = _slack_signed_request(payload)
    response = client.post("/channels/slack/events", content=body, headers=headers)
    assert response.status_code == 400


def test_normalize_slack_event_strips_bot_mention():
    envelope = normalize_slack_event(
        {
            "event": {
                "text": "<@UAPP> oidc login",
                "user": "U123",
                "metadata": {"intent": "knowledge_query", "rolle": "support", "tenant_id": "t1"},
            }
        }
    )
    assert envelope.query == "oidc login"


def test_normalize_slack_event_supports_direct_messages_without_mention():
    envelope = normalize_slack_event(
        {
            "event": {
                "type": "message",
                "channel": "D123",
                "channel_type": "im",
                "text": "oidc login",
                "user": "U123",
            }
        }
    )
    assert envelope.intent == "knowledge_query"
    assert envelope.query == "oidc login"
    assert envelope.channel_user_id == "U123"


def test_normalize_slack_event_maps_app_home_opened_to_help_query():
    envelope = normalize_slack_event(
        {
            "event": {
                "type": "app_home_opened",
                "user": "U123",
            }
        }
    )
    assert envelope.intent == "knowledge_query"
    assert envelope.query == "hilfe"


@pytest.mark.asyncio
async def test_maybe_post_slack_response_posts_threaded_reply(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "CHANNEL_SLACK_BOT_TOKEN", "xoxb-test")

    captured: dict[str, object] = {}

    class _DummyResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"ok": True, "ts": "1710000000.200"}

    class _DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url: str, headers: dict[str, str], json: dict[str, object]):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return _DummyResponse()

    monkeypatch.setattr("app.core.channel_ingress.httpx.AsyncClient", _DummyClient)

    from app.core.channel_ingress import maybe_post_slack_response

    payload = {
        "event": {
            "type": "app_mention",
            "channel": "C123",
            "ts": "1710000000.100",
            "text": "<@UAPP> oidc login",
            "user": "U123",
        }
    }
    dispatch_result = {
        "intent": "knowledge_query",
        "result": {"answer": "OIDC Login ist ueber Keycloak verfuegbar.", "knowledge_ids": ["KNW-SUP-001"]},
    }

    result = await maybe_post_slack_response(payload, dispatch_result)
    assert result == {"ok": True, "ts": "1710000000.200"}
    assert captured["url"] == "https://slack.com/api/chat.postMessage"
    assert captured["json"] == {
        "channel": "C123",
        "text": "OIDC Login ist ueber Keycloak verfuegbar.\n\nQuellen: KNW-SUP-001",
        "unfurl_links": False,
        "unfurl_media": False,
        "thread_ts": "1710000000.100",
    }
    assert str(captured["headers"]).find("Bearer xoxb-test") >= 0


def test_format_slack_dispatch_result_for_process_thread():
    text = format_slack_dispatch_result(
        {
            "intent": "process_execute",
            "result": {
                "message": "FinalizeAgrarSettlement ist im Kanal erfasst und wartet auf Freigabe.",
                "status": "pending_approval",
                "thread_id": "cht-1",
            },
        }
    )
    assert "pending_approval" in text
    assert "cht-1" in text
