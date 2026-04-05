import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.services.superglue_tool_provisioning import (
    provision_superglue_pilot_tools,
    run_superglue_pilot_smoke,
)


def test_provision_superglue_pilot_tools_creates_missing_tools(monkeypatch):
    requests: list[tuple[str, str, dict | None]] = []
    sync_calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = httpx.Request(
            request.method,
            request.url,
            content=request.content,
            headers=request.headers,
        )
        payload = None
        if body.content:
            payload = __import__("json").loads(body.content.decode("utf-8"))
        requests.append((request.method, request.url.path, payload))
        if request.method == "GET":
            return httpx.Response(404, json={"error": "Tool not found"})
        if request.method == "POST" and request.url.path == "/v1/tools":
            return httpx.Response(201, json={"success": True})
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.refresh_superglue_sync_snapshot",
        lambda client=None: sync_calls.append("refresh") or {"provider_key": "superglue", "tool_count": 3},
    )
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )

    result = provision_superglue_pilot_tools(client)

    assert result["created"] == [
        "sg.document.search",
        "sg.partner.adapter.preview",
        "sg.customer.profile.preview",
    ]
    assert result["updated"] == []
    assert sync_calls == ["refresh"]
    create_payloads = [payload for method, path, payload in requests if method == "POST" and path == "/v1/tools"]
    assert len(create_payloads) == 3
    assert create_payloads[0]["id"] == "sg.document.search"


def test_provision_superglue_pilot_tools_updates_existing_tools(monkeypatch):
    requests: list[tuple[str, str, dict | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = None
        if request.content:
            payload = __import__("json").loads(request.content.decode("utf-8"))
        requests.append((request.method, request.url.path, payload))
        if request.method == "GET":
            tool_id = request.url.path.rsplit("/", 1)[-1]
            return httpx.Response(200, json={"id": tool_id, "steps": []})
        if request.method == "PUT":
            return httpx.Response(200, json={"success": True})
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.refresh_superglue_sync_snapshot",
        lambda client=None: {"provider_key": "superglue", "tool_count": 3},
    )
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )

    result = provision_superglue_pilot_tools(client)

    assert result["created"] == []
    assert result["updated"] == [
        "sg.document.search",
        "sg.partner.adapter.preview",
        "sg.customer.profile.preview",
    ]
    update_payloads = [payload for method, path, payload in requests if method == "PUT" and path.startswith("/v1/tools/")]
    assert len(update_payloads) == 3
    assert "id" not in update_payloads[0]


def test_run_superglue_pilot_smoke_uses_provisioned_tool():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/tools/sg.document.search/run"
        payload = __import__("json").loads(request.content.decode("utf-8"))
        assert payload["inputs"]["query"] == "smoke-check"
        return httpx.Response(
            200,
            json={
                "runId": "run-smoke",
                "status": "success",
                "data": {"documents": [{"id": "doc-smoke"}]},
            },
        )

    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(handler),
    )

    result = run_superglue_pilot_smoke(client)

    assert result["run_id"] == "run-smoke"
    assert result["status"] == "success"
    assert result["data"]["documents"][0]["id"] == "doc-smoke"
