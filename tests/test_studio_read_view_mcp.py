"""MCP read views preserve the caller's authority and only perform safe reads."""

from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.core.screen_definitions_admin_workbench import build_webhooks_workbench
from app.services import mcp_mask_actions as mm
from valeo_cli import support


@pytest.fixture
def definition(monkeypatch):
    definition = build_webhooks_workbench()
    monkeypatch.setattr(mm, "_definition", lambda screen, tenant: definition)
    return definition


def history(definition):
    return next(a for a in mm.iter_actions(definition) if a["key"] == "history")


def request(**changes):
    parameters = {"screen_id": "admin/webhooks-liste", "action": "history", "entity_id": "id/1 ?"}
    parameters.update(changes.pop("parameters", {}))
    return SimpleNamespace(parameters=parameters, mode=changes.pop("mode", "execute"),
                           idempotency_key=changes.pop("idempotency_key", None), **changes)


def target(status=200):
    calls = []
    def handle(req):
        calls.append(req)
        return httpx.Response(status, json=[{"erfolgreich": True}] if status == 200 else {"detail": "forbidden"})
    return calls, httpx.MockTransport(handle)


def test_canonical_action_policy_matches_cli(definition):
    action = history(definition)
    assert support.support(action).supported
    assert support.policy_block(action, is_agent=True) is None
    assert mm.agent_block(action) is None
    for flag in ("forbiddenForAgents", "humanApprovalRequired"):
        restricted = {**action, flag: True}
        assert support.policy_block(restricted, is_agent=True)
        assert mm.agent_block(restricted) is not None


def test_get_forwards_only_bearer_and_escapes_id(definition):
    calls, transport = target()
    result = mm.execute(request(), "tenant-a", "Bearer agent-token", transport=transport)
    assert result["result"] == [{"erfolgreich": True}]
    [call] = calls
    assert call.method == "GET"
    assert call.url.raw_path == b"/api/v1/webhooks/id%2F1%20%3F/zustellversuche"
    assert call.headers["authorization"] == "Bearer agent-token"
    assert "x-tenant-id" not in call.headers and call.content == b""


@pytest.mark.parametrize("params, mode", [
    ({"entity_id": None}, "execute"), ({"entity_id": ".."}, "execute"),
    ({"input": {"tenant_id": "other"}}, "execute"), ({"input": {"x": 1}}, "execute"),
    ({"audit_reason": "reason"}, "execute"), ({"unexpected": "x"}, "execute"),
    ({}, "dryRun"), ({}, "validate"), ({}, "propose"),
])
def test_invalid_arguments_do_not_reach_target(definition, params, mode):
    calls, transport = target()
    with pytest.raises(HTTPException) as error:
        mm.execute(request(parameters=params, mode=mode), "tenant-a", "Bearer t", transport=transport)
    assert error.value.status_code == 422 and not calls


@pytest.mark.parametrize("endpoint", [
    "https://evil.invalid/api/v1/webhooks/{id}/zustellversuche",
    "/api/v1/webhooks/../zustellversuche",
    "/api/v1/webhooks/{mandant_id}/zustellversuche",
    "/api/v1/unregistered/{id}/zustellversuche",
])
def test_foreign_or_invalid_paths_are_blocked(definition, endpoint):
    history(definition)["readView"]["endpoint"] = endpoint
    calls, transport = target()
    with pytest.raises(HTTPException) as error:
        mm.execute(request(), "tenant-a", "Bearer t", transport=transport)
    assert error.value.status_code == 403 and not calls


@pytest.mark.parametrize("flag", ["forbiddenForAgents", "humanApprovalRequired"])
def test_agent_flags_block_before_read(definition, flag):
    history(definition)[flag] = True
    calls, transport = target()
    with pytest.raises(HTTPException) as error:
        mm.execute(request(), "tenant-a", "Bearer t", transport=transport)
    assert error.value.status_code == 403 and not calls


def test_upstream_403_is_preserved(definition):
    calls, transport = target(403)
    with pytest.raises(HTTPException) as error:
        mm.execute(request(), "tenant-a", "Bearer t", transport=transport)
    assert error.value.status_code == 403 and len(calls) == 1
