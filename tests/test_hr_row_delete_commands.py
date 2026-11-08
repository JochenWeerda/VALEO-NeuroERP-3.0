"""HR deletion command guards; no MCP capability is enabled by these tests."""
from unittest.mock import MagicMock
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.services import hr_row_delete_commands as service

NOW = "a" * 64
USER = {"sub": "person-1", "roles": ["PERSONAL_BEARBEITEN"],
        "raw": {"tenant_id": "tenant-a", "identity_type": "human"}}


def command(kind="onboarding", **changes):
    return service.HrDeleteCommand(kind=kind, entity_id="row-1", expected_revision=NOW,
                                   idempotency_key="key-1", **changes)


@pytest.fixture
def dependencies(monkeypatch):
    calls = []
    monkeypatch.setattr(service, "current_identity", lambda: SimpleNamespace(subject="person-1", tenant_id="tenant-a", roles={"PERSONAL_BEARBEITEN"}, claims={"identity_type": "human"}))
    monkeypatch.setattr(service, "lock_and_replay", lambda *a, **kw: calls.append(("replay", kw)) or None)
    monkeypatch.setattr(service, "store_execution", lambda *a, **kw: calls.append(("store", kw)))
    monkeypatch.setattr(service, "_write_audit", lambda *a, **kw: calls.append(("audit", kw)) or "audit-1")
    monkeypatch.setattr(service, "_write_outbox", lambda *a, **kw: calls.append(("outbox", kw)) or "outbox-1")
    return calls


def db_with_row(version=NOW, rowcount=1):
    db = MagicMock()
    read, deleted = MagicMock(), MagicMock()
    read.mappings.return_value.first.return_value = None if version is None else {"revision": version}
    deleted.rowcount = rowcount
    db.execute.side_effect = [MagicMock(), read, deleted]
    return db


@pytest.mark.parametrize("kind", ["onboarding", "qualification", "assignment"])
def test_delete_is_scoped_versioned_audited_and_caller_commits(kind, dependencies):
    db = db_with_row()
    result = service.delete_hr_row(db, command(kind), tenant="tenant-a")
    sql_calls = db.execute.call_args_list
    assert len(sql_calls) == 3
    assert sql_calls[1].args[1] == {"tenant": "tenant-a", "id": "row-1"}
    assert sql_calls[2].args[1] == {"tenant": "tenant-a", "id": "row-1"}
    assert result["auditEntryId"] == "audit-1" and result["outboxEventId"] == "outbox-1"
    assert [entry[0] for entry in dependencies] == ["replay", "audit", "outbox", "store"]
    assert dependencies[1][1]["performed_by"] == "person-1"
    db.commit.assert_not_called()


@pytest.mark.parametrize("user,tenant", [
    ({**USER, "roles": []}, "tenant-a"),
    ({**USER, "sub": ""}, "tenant-a"),
    (USER, "tenant-b"),
    ({**USER, "raw": {"tenant_id": "tenant-a", "identity_type": "agent"}}, "tenant-a"),
    ({**USER, "raw": {"tenant_id": "tenant-a"}}, "tenant-a"),
    ({**USER, "raw": {"tenant_id": "tenant-a", "identity_type": "human", "act": {"sub": "agent"}}}, "tenant-a"),
    ({**USER, "raw": {"tenant_id": "tenant-a", "identity_type": "human", "agent_id": "agent"}}, "tenant-a"),
])
def test_identity_role_and_agent_policy_precede_any_database_work(user, tenant, dependencies, monkeypatch):
    raw = user.get("raw") or {}
    monkeypatch.setattr(service, "current_identity", lambda: SimpleNamespace(subject=user.get("sub"), tenant_id=raw.get("tenant_id"), roles=set(user.get("roles") or []), claims=raw))
    db = db_with_row()
    with pytest.raises(HTTPException) as error:
        service.delete_hr_row(db, command(), tenant=tenant)
    assert error.value.status_code == 403
    assert dependencies == []
    db.execute.assert_not_called()


@pytest.mark.parametrize("version,status", [(None, 404), ("b" * 64, 409)])
def test_missing_or_stale_row_never_mutates(version, status, dependencies):
    db = db_with_row(version)
    with pytest.raises(HTTPException) as error:
        service.delete_hr_row(db, command(), tenant="tenant-a")
    assert error.value.status_code == status
    assert db.execute.call_count == 2
    assert [entry[0] for entry in dependencies] == ["replay"]


def test_replay_returns_without_touching_hr_row(monkeypatch, dependencies):
    monkeypatch.setattr(service, "lock_and_replay", lambda *args, **kwargs: {"success": True, "replayed": True})
    db = db_with_row()
    assert service.delete_hr_row(db, command(), tenant="tenant-a")["replayed"] is True
    db.execute.assert_not_called()


def test_command_rejects_untrusted_fields_and_invalid_revision():
    with pytest.raises(ValidationError):
        service.HrDeleteCommand(kind="assignment", entity_id="x", expected_revision="invalid",
                                idempotency_key="k", tenant_id="other")

@pytest.mark.parametrize("previous_actor,previous_hash", [("other", "a" * 64), ("person-1", "b" * 64)])
def test_replay_rejects_changed_actor_or_payload_without_rolling_back_caller(previous_actor, previous_hash):
    from app.services.command_idempotency import lock_and_replay
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": previous_actor, "payload_hash": previous_hash, "result": {"success": True},
    }
    with pytest.raises(HTTPException) as error:
        lock_and_replay(db, tenant="tenant-a", command="hr.assignment.delete.v1", key="key-1", actor="person-1", fingerprint="a" * 64)
    assert error.value.status_code == 409
    db.rollback.assert_not_called()


def test_replay_of_same_actor_and_payload_keeps_caller_transaction():
    from app.services.command_idempotency import lock_and_replay
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": "person-1", "payload_hash": "a" * 64, "result": '{"success": true}',
    }
    assert lock_and_replay(db, tenant="tenant-a", command="hr.assignment.delete.v1", key="key-1", actor="person-1", fingerprint="a" * 64) == {
        "success": True, "replayed": True,
    }
    db.rollback.assert_not_called()


def test_audit_failure_is_propagated_and_never_stored_as_success(monkeypatch, dependencies):
    def fail_audit(*args, **kwargs):
        raise RuntimeError("audit unavailable")
    monkeypatch.setattr(service, "_write_audit", fail_audit)
    db = db_with_row()
    with pytest.raises(RuntimeError, match="audit unavailable"):
        service.delete_hr_row(db, command(), tenant="tenant-a")
    assert [entry[0] for entry in dependencies] == ["replay"]
    db.commit.assert_not_called()

@pytest.mark.parametrize("kind,screen", [("onboarding", "personal/onboarding"), ("qualification", "personal/qualifikationen"), ("assignment", "personal/schulungen")])
def test_agent_requires_exact_capability_role_and_scope(monkeypatch, dependencies, kind, screen):
    from app.services import mcp_write_capability
    principal = SimpleNamespace(subject="agent-1", tenant_id="tenant-a", roles={"PERSONAL_BEARBEITEN"},
                                scopes={"masks:write"}, claims={"identity_type": "agent"})
    monkeypatch.setattr(service, "current_identity", lambda: principal)
    entry = {"domain_command": f"hr.{kind}.delete.v1", "endpoint": service._ENDPOINTS[kind],
             "screen_id": screen, "action": "loeschen", "command_version": 1,
             "agent_write_enabled": True, "agent_roles": ["PERSONAL_BEARBEITEN"]}
    monkeypatch.setattr(mcp_write_capability, "_entries", lambda: [entry])
    assert service.delete_hr_row(db_with_row(), command(kind), tenant="tenant-a")["success"]
    for change in ({"scopes": set()}, {"roles": {"PERSONAL_LESEN"}}, {"claims": {"identity_type": "human", "act": {"sub": "agent"}}}):
        bad = SimpleNamespace(**{**vars(principal), **change})
        monkeypatch.setattr(service, "current_identity", lambda: bad)
        db = db_with_row()
        with pytest.raises(HTTPException) as error:
            service.delete_hr_row(db, command(kind), tenant="tenant-a")
        assert error.value.status_code == 403
        db.execute.assert_not_called()


@pytest.mark.parametrize('kind,screen,path', [
    ('onboarding', 'personal/onboarding', '/api/v1/training/onboarding/runs/{entity_id}/actions/loeschen'),
    ('qualification', 'personal/qualifikationen', '/api/v1/training/qualifications/{entity_id}/actions/loeschen'),
    ('assignment', 'personal/schulungen', '/api/v1/training/assignments/{entity_id}/actions/loeschen'),
])
def test_registered_mcp_transport_delegates_to_the_same_hr_command(monkeypatch, dependencies, kind, screen, path):
    import json
    from copy import deepcopy
    import httpx
    from app.api.v1.endpoints import training
    from app.core import identity_context
    from app.core.screen_definitions import get_screen_definition
    from app.services import mcp_mask_actions as mm
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service

    cap = {'domain_command': f'hr.{kind}.delete.v1', 'endpoint': path, 'screen_id': screen,
           'action': 'loeschen', 'command_version': 1, 'agent_write_enabled': True,
           'agent_roles': ['PERSONAL_BEARBEITEN']}
    monkeypatch.setattr(mcp_tool_registry_service, 'get_tool', lambda _: {'write_capabilities': [cap]})
    definition = deepcopy(get_screen_definition(screen))
    action = next(a for a in mm.iter_actions(definition) if a['key'] == 'loeschen')
    action.pop('forbiddenForAgents', None)
    monkeypatch.setattr(mm, '_definition', lambda *_: definition)
    actor = SimpleNamespace(subject='agent-1', tenant_id='tenant-a', roles={'PERSONAL_BEARBEITEN'},
                            scopes={'masks:write'}, claims={'identity_type': 'service'})
    monkeypatch.setattr(identity_context, 'current_identity', lambda: actor)
    monkeypatch.setattr(service, 'current_identity', lambda: actor)
    db = db_with_row()
    seen = []
    def target(request):
        seen.append(request)
        body = training.HrDeleteBody.model_validate(json.loads(request.content))
        result = training._execute_hr_delete(db, 'tenant-a', kind, 'row-1', body)
        return httpx.Response(200, json=result)
    request = SimpleNamespace(parameters={'screen_id': screen, 'action': 'loeschen', 'entity_id': 'row-1',
                                          'input': {'expected_revision': NOW}, 'confirm': True},
                              mode='execute', idempotency_key='key-1')
    result = mm.execute(request, 'tenant-a', 'Bearer synthetic-token', transport=httpx.MockTransport(target))
    assert result['success'] and result['result']['entity_id'] == 'row-1'
    assert len(seen) == 1 and seen[0].headers['authorization'] == 'Bearer synthetic-token'
    assert 'x-tenant-id' not in seen[0].headers
    db.commit.assert_called_once()
