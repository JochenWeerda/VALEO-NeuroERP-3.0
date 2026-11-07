"""Non-database contracts for the unregistered shipping profile command."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.services import versandprofil_commands as command


def principal(**changes):
    values = {"tenant_id": "t1", "roles": {"LAGER_BEARBEITEN"}, "subject": "u1",
              "claims": {"identity_type": "human"}}
    return SimpleNamespace(**(values | changes))


def request(**changes):
    return command.DeactivateProfileV1(**({"profile_id": "p1", "expected_active": True,
                                          "idempotency_key": "k1", "reason": "Nicht mehr benoetigt"} | changes))


def db_with(row, previous=None):
    db = Mock()
    def execute(sql, params):
        result = Mock()
        query = str(sql)
        result.mappings.return_value.first.return_value = row if "FROM domain_shared.versandprofile" in query else previous
        return result
    db.execute.side_effect = execute
    return db


def test_deactivate_commits_audit_outbox_and_replay_record(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    audit = Mock(return_value="a1")
    monkeypatch.setattr(command, "_write_audit", audit)
    db = db_with({"id": "p1", "aktiv": True})
    result = command.deactivate_profile(db, "t1", request())
    assert result["success"] and not result["replayed"]
    audit.assert_called_once()
    db.add.assert_called_once()
    db.commit.assert_not_called()
    assert any("INSERT INTO public.mcp_tool_executions" in str(call.args[0]) for call in db.execute.call_args_list)


def test_audit_failure_rolls_back_and_does_not_commit(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    monkeypatch.setattr(command, "_write_audit", Mock(side_effect=RuntimeError("audit")))
    db = db_with({"id": "p1", "aktiv": True})
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, "t1", request())
    assert error.value.status_code == 503
    db.rollback.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("identity, tenant", [
    (principal(tenant_id="other"), "t1"),
    (principal(roles=set()), "t1"),
    (principal(claims={"identity_type": "service"}), "t1"),
    (principal(claims={}), "t1"),
    (principal(claims={"identity_type": "human", "agent_id": "a"}), "t1"),
    (principal(claims={"identity_type": "human", "act": {"sub": "a"}}), "t1"),
])
def test_unauthorized_or_unreleased_agent_cannot_write(monkeypatch, identity, tenant):
    monkeypatch.setattr(command, "current_identity", lambda: identity)
    db = Mock()
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, tenant, request())
    assert error.value.status_code == 403
    db.execute.assert_not_called()


def test_changed_or_foreign_target_is_rejected(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    for row, status in ((None, 404), ({"id": "p1", "aktiv": False}, 409)):
        db = db_with(row)
        with pytest.raises(HTTPException) as error:
            command.deactivate_profile(db, "t1", request())
        assert error.value.status_code == status
        db.commit.assert_not_called()
        db.rollback.assert_not_called()


def test_replay_rejects_different_actor_without_mutation(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    audit = Mock()
    monkeypatch.setattr(command, "_write_audit", audit)
    db = db_with({"id": "p1", "aktiv": False},
                 {"actor_id": "other", "payload_hash": "other", "result": {"success": True}})
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, "t1", request())
    assert error.value.status_code == 409
    db.rollback.assert_not_called()
    db.commit.assert_not_called()
    audit.assert_not_called()


def test_rest_command_shares_service_and_old_delete_is_closed(monkeypatch):
    from app.api.v1.endpoints import versandprofile as endpoint
    called = Mock(return_value={"success": True})
    monkeypatch.setattr(command, "deactivate_profile", called)
    payload = endpoint.VersandprofilDeactivateInput.model_validate({
        "expected_active": True, "_idempotencyKey": "k1", "_auditReason": "Grund"})
    db = Mock()
    assert endpoint.deactivate_versandprofil("p1", payload, db=db, tenant_id="t1") == {"success": True}
    assert called.call_args.args[1] == "t1"
    assert called.call_args.args[2] == request(reason="Grund")
    with pytest.raises(HTTPException) as error:
        endpoint.delete_versandprofil("old-profile-number")
    assert error.value.status_code == 410


def test_rest_rejects_preview_and_inactive_state_before_service(monkeypatch):
    from app.api.v1.endpoints import versandprofile as endpoint
    called = Mock()
    monkeypatch.setattr(command, "deactivate_profile", called)
    for changes in ({"_mode": "dryRun"}, {"expected_active": False}):
        payload = endpoint.VersandprofilDeactivateInput.model_validate({
            "expected_active": True, "_idempotencyKey": "k1", "_auditReason": "Grund", **changes})
        with pytest.raises(HTTPException) as error:
            endpoint.deactivate_versandprofil("p1", payload, db=Mock(), tenant_id="t1")
        assert error.value.status_code == 422
    called.assert_not_called()


def test_registered_agent_capability_and_scope_are_enforced_in_service(monkeypatch):
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service
    cap = {"domain_command": "logistik.versandprofil.deactivate.v1",
           "endpoint": "/api/v1/logistik/versand/profile/{entity_id}/actions/deactivate",
           "screen_id": "logistik/versandprofile", "action": "loeschen", "command_version": 1,
           "agent_write_enabled": True, "agent_roles": ["LAGER_BEARBEITEN"]}
    monkeypatch.setattr(mcp_tool_registry_service, "get_tool", lambda _: {"write_capabilities": [cap]})
    db = db_with({"id": "p1", "aktiv": True})
    monkeypatch.setattr(command, "_write_audit", Mock(return_value="audit"))
    agent = principal(claims={"identity_type": "service"}, scopes={"masks:write"})
    monkeypatch.setattr(command, "current_identity", lambda: agent)
    assert command.deactivate_profile(db, "t1", request())["success"]
    db.reset_mock()
    agent.scopes = set()
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, "t1", request())
    assert error.value.status_code == 403
    db.execute.assert_not_called()


def test_mcp_shipping_transport_reaches_same_registered_command_with_agent_identity(monkeypatch):
    import json
    from copy import deepcopy
    from app.api.v1.endpoints import versandprofile as endpoint
    from app.core import identity_context
    from app.core.screen_definitions import get_screen_definition
    from app.services import mcp_mask_actions as mm
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service
    import httpx

    cap = {"domain_command": "logistik.versandprofil.deactivate.v1",
           "endpoint": "/api/v1/logistik/versand/profile/{entity_id}/actions/deactivate",
           "screen_id": "logistik/versandprofile", "action": "loeschen", "command_version": 1,
           "agent_write_enabled": True, "agent_roles": ["LAGER_BEARBEITEN"]}
    monkeypatch.setattr(mcp_tool_registry_service, "get_tool", lambda _: {"write_capabilities": [cap]})
    definition = deepcopy(get_screen_definition("logistik/versandprofile"))
    action = next(a for a in mm.iter_actions(definition) if a["key"] == "loeschen")
    action.pop("forbiddenForAgents", None)
    monkeypatch.setattr(mm, "_definition", lambda *_: definition)
    agent = principal(claims={"identity_type": "service"}, scopes={"masks:write"})
    monkeypatch.setattr(identity_context, "current_identity", lambda: agent)
    monkeypatch.setattr(command, "current_identity", lambda: agent)
    monkeypatch.setattr(command, "_write_audit", Mock(return_value="audit"))
    db = db_with({"id": "p1", "aktiv": True})
    calls = []
    def target(http_request):
        calls.append(http_request)
        body = endpoint.VersandprofilDeactivateInput.model_validate(json.loads(http_request.content))
        result = endpoint.deactivate_versandprofil("p1", body, db=db, tenant_id="t1")
        return httpx.Response(200, json=result)
    req = SimpleNamespace(parameters={"screen_id": "logistik/versandprofile", "action": "loeschen",
                                     "entity_id": "p1", "input": {"expected_active": True}, "audit_reason": "Grund", "confirm": True},
                          mode="execute", idempotency_key="k1")
    result = mm.execute(req, "t1", "Bearer agent-token", transport=httpx.MockTransport(target))
    assert result["success"] and result["result"]["profile_id"] == "p1"
    assert len(calls) == 1 and calls[0].headers["authorization"] == "Bearer agent-token"
    assert "x-tenant-id" not in calls[0].headers
    db.commit.assert_called_once()
