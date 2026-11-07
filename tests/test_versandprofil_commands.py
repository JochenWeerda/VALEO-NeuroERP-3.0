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
    db.commit.assert_called_once()
    assert any("INSERT INTO public.mcp_tool_executions" in str(call.args[0]) for call in db.execute.call_args_list)


def test_audit_failure_rolls_back_and_does_not_commit(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    monkeypatch.setattr(command, "_write_audit", Mock(side_effect=RuntimeError("audit")))
    db = db_with({"id": "p1", "aktiv": True})
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, "t1", request())
    assert error.value.status_code == 503
    db.rollback.assert_called_once()
    db.commit.assert_not_called()


@pytest.mark.parametrize("identity, tenant", [
    (principal(tenant_id="other"), "t1"),
    (principal(roles=set()), "t1"),
    (principal(claims={"identity_type": "service"}), "t1"),
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
        db.rollback.assert_called_once()


def test_replay_rejects_different_actor_without_mutation(monkeypatch):
    monkeypatch.setattr(command, "current_identity", principal)
    audit = Mock()
    monkeypatch.setattr(command, "_write_audit", audit)
    db = db_with({"id": "p1", "aktiv": False},
                 {"actor_id": "other", "payload_hash": "other", "result": {"success": True}})
    with pytest.raises(HTTPException) as error:
        command.deactivate_profile(db, "t1", request())
    assert error.value.status_code == 409
    db.rollback.assert_called_once()
    db.commit.assert_not_called()
    audit.assert_not_called()
