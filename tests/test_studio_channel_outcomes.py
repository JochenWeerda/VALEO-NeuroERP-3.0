"""Adapter parity against one HTTP target, without pretending to prove domain rules.

Use a real Studio-generated schema/action and real CLI/MCP adapters. The target's
business outcome and the authenticated principal are test boundaries. PostgreSQL,
OIDC verification, the MCP execution engine and browser dialogs are not exercised.
"""
import base64
import io
import json
from types import SimpleNamespace
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core import identity_context
from app.services import mcp_mask_actions
from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from app.services.studio_entity_compiler import entity_action_binding, registered_definition
from app.services.studio_entity_contracts import EntityRegistration, EntitySpec
from valeo_cli import cli

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def generated():
    spec = EntitySpec(name="studio_channel_outcome", domain="crm", label="Synthetic",
                      columns=[{"name": "name", "type": "text", "nullable": False}])
    entry = EntityRegistration(spec=spec, writes_enabled=True, agent_roles=["CRM_BEARBEITEN"])
    return spec, registered_definition(entry)


@pytest.fixture
def channels(generated, monkeypatch):
    spec, definition = generated
    screen_id = definition["id"]
    action = definition["actions"][0]
    binding = entity_action_binding(spec, "create")
    capability = {**binding, "command_version": 1, "agent_write_enabled": True,
                  "agent_roles": ["CRM_BEARBEITEN"]}
    monkeypatch.setattr(mcp_tool_registry_service, "get_tool",
                        lambda _: {"write_capabilities": [capability]})
    monkeypatch.setattr(mcp_mask_actions, "_definition", lambda sid, tenant: definition)
    monkeypatch.setattr(identity_context, "current_identity", lambda: SimpleNamespace(
        roles=frozenset({"CRM_BEARBEITEN"}), scopes=frozenset({"masks:write"})))
    encoded = base64.urlsafe_b64encode(json.dumps({"identity_type": "human"}).encode()).decode().rstrip("=")
    token = "synthetic." + encoded + ".unsigned"
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", token)
    monkeypatch.setenv("VALEO_API_URL", "http://testserver")
    state = {"status": 200, "body": {"success": True}, "calls": []}
    app = FastAPI()

    async def target(request: Request, body):
        state["calls"].append((dict(request.headers), await request.json()))
        return JSONResponse(state["body"], status_code=state["status"])

    target.__annotations__["body"] = spec.flat_command_model()
    app.add_api_route(action["commandEndpoint"], target, methods=["POST"])

    @app.get("/api/v1/masks/" + screen_id + "/screen-definition")
    def screen_definition():
        return definition

    with TestClient(app) as client:
        def forward(request):
            response = client.request(request.method, request.url.path,
                                      headers=dict(request.headers), content=request.content)
            return httpx.Response(response.status_code, content=response.content, request=request)

        @app.post("/synthetic/mcp-adapter")
        def mcp_adapter():
            request = SimpleNamespace(mode="execute", idempotency_key=str(UUID(int=1)), parameters={
                "screen_id": screen_id, "action": action["key"], "input": {"name": "Synthetic"},
                "audit_reason": "Synthetic contract verification", "confirm": True})
            return mcp_mask_actions.execute(request, "synthetic-tenant", "Bearer " + token,
                                            transport=httpx.MockTransport(forward))

        yield state, client, token, definition, action


@pytest.mark.parametrize("status,detail,exit_code", [
    (403, "Fachrolle erforderlich", 3),
    (409, {"code": "approval_required", "gruende": ["unabhaengige_freigabe"]}, 1),
    (422, [{"loc": ["body", "reason"], "msg": "Begruendung erforderlich"}], 4),
])
def test_target_rejection_never_becomes_adapter_success(channels, status, detail, exit_code):
    state, client, token, definition, action = channels
    state.update(status=status, body={"detail": detail})
    body = {"name": "Synthetic", "_auditReason": "Synthetic contract verification",
            "_idempotencyKey": str(UUID(int=1))}
    direct = client.post(action["commandEndpoint"], headers={"Authorization": "Bearer " + token}, json=body)
    lines = []
    result = cli.main(["ausfuehren", definition["id"], action["key"], "--daten", "-",
                       "--grund", body["_auditReason"], "--idempotenz", body["_idempotencyKey"],
                       "--ja", "--json"], http=client, out=lines.append,
                      stdin=io.StringIO(json.dumps({"name": "Synthetic"})))
    adapted = client.post("/synthetic/mcp-adapter")
    assert direct.status_code == adapted.status_code == status
    assert adapted.json() == direct.json()  # Structured public rejection must survive transport.
    assert result == exit_code
    assert not any(line.startswith("OK") for line in lines)
    reason = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    assert reason in "\n".join(lines)
    assert len(state["calls"]) == 3
    for headers, sent in state["calls"]:
        assert headers["authorization"] == "Bearer " + token
        assert "x-tenant-id" not in headers
        assert sent == body


@pytest.mark.parametrize("success", [True, False])
def test_explicit_target_outcome_controls_adapter_success(channels, success):
    state, client, token, definition, action = channels
    state["body"] = {"success": success, "summary": "Synthetic target outcome"}
    lines = []
    code = cli.main(["ausfuehren", definition["id"], action["key"], "--feld", "name=Synthetic",
                     "--grund", "Synthetic contract verification", "--idempotenz", str(UUID(int=1)),
                     "--ja", "--json"], http=client, out=lines.append)
    adapted = client.post("/synthetic/mcp-adapter")
    assert code == (0 if success else 1)
    assert json.loads(lines[-1]) == state["body"]
    assert adapted.status_code == 200
    assert adapted.json()["success"] is success
    assert adapted.json()["result"] == state["body"]
    assert len(state["calls"]) == 2
