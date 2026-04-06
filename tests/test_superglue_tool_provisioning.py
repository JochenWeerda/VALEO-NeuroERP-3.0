import httpx

from app.integrations.adapters.superglue.client import SuperglueClient
from app.integrations.services.superglue_tool_provisioning import (
    build_superglue_tool_lifecycle_summary,
    provision_superglue_pilot_tools,
    provision_superglue_tenant_connectors,
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


def test_provision_superglue_tenant_connectors_creates_systems_and_tools(monkeypatch):
    requests: list[tuple[str, str, dict | None]] = []

    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.refresh_superglue_sync_snapshot",
        lambda client=None: {"provider_key": "superglue", "tool_count": 3},
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.list_superglue_connector_bindings",
        lambda tenant_id: [
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="document_search")
        ],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        payload = None
        if request.content:
            payload = __import__("json").loads(request.content.decode("utf-8"))
        requests.append((request.method, request.url.path, payload))
        if request.method == "GET":
            return httpx.Response(404, json={"error": "missing"})
        if request.method == "POST" and request.url.path in {"/v1/systems", "/v1/tools"}:
            return httpx.Response(201, json={"ok": True})
        raise AssertionError(f"unexpected request: {request.method} {request.url.path}")

    client = SuperglueClient(base_url="https://api.superglue.dev", transport=httpx.MockTransport(handler))

    result = provision_superglue_tenant_connectors("tenant-a", client)

    assert result["tenant_id"] == "tenant-a"
    assert result["systems_created"] == ["tenant-a.document_search.system"]
    assert result["tools_created"] == ["tenant-a.sg.document.search"]
    system_create = next(payload for method, path, payload in requests if method == "POST" and path == "/v1/systems")
    tool_create = next(payload for method, path, payload in requests if method == "POST" and path == "/v1/tools")
    assert system_create["metadata"]["tenantId"] == "tenant-a"
    assert tool_create["id"] == "tenant-a.sg.document.search"
    assert tool_create["steps"][0]["config"]["systemId"] == "tenant-a.document_search.system"


def test_build_superglue_tool_lifecycle_summary_surfaces_connector_bindings(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.list_superglue_connector_bindings",
        lambda tenant_id: [
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="customer_profile")
        ],
    )

    summary = build_superglue_tool_lifecycle_summary("tenant-a")

    assert summary["tenant_id"] == "tenant-a"
    assert summary["connector_count"] == 1
    assert summary["connectors"][0]["tool_id"] == "tenant-a.sg.customer.profile.preview"


def test_provision_superglue_generic_domain_connector_builds_request_tool(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.refresh_superglue_sync_snapshot",
        lambda client=None: {"provider_key": "superglue", "tool_count": 9},
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_tool_provisioning.list_superglue_connector_bindings",
        lambda tenant_id: [
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="finance_export")
        ],
    )
    requests: list[tuple[str, str, dict | None]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = None
        if request.content:
            payload = __import__("json").loads(request.content.decode("utf-8"))
        requests.append((request.method, request.url.path, payload))
        if request.method == "GET":
            return httpx.Response(404, json={"error": "missing"})
        return httpx.Response(201, json={"ok": True})

    client = SuperglueClient(base_url="https://api.superglue.dev", transport=httpx.MockTransport(handler))

    result = provision_superglue_tenant_connectors("tenant-a", client)

    assert result["tools_created"] == ["tenant-a.sg.finance.export.bundle"]
    tool_create = next(payload for method, path, payload in requests if method == "POST" and path == "/v1/tools")
    assert tool_create["steps"][0]["config"]["method"] == "POST"
