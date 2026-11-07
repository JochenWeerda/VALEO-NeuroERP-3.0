"""HR deletion command guards; no MCP capability is enabled by these tests."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.services import hr_row_delete_commands as service

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)
USER = {"sub": "person-1", "roles": ["PERSONAL_BEARBEITEN"],
        "raw": {"tenant_id": "tenant-a", "identity_type": "human"}}


def command(kind="onboarding", **changes):
    return service.HrDeleteCommand(kind=kind, entity_id="row-1", expected_updated_at=NOW,
                                   idempotency_key="key-1", **changes)


@pytest.fixture
def dependencies(monkeypatch):
    calls = []
    monkeypatch.setattr(service, "_advisory_lock", lambda *a: calls.append(("lock", a)))
    monkeypatch.setattr(service, "_replay_or_none", lambda *a: calls.append(("replay", a)) or None)
    monkeypatch.setattr(service, "_write_audit", lambda *a, **kw: calls.append(("audit", kw)) or "audit-1")
    monkeypatch.setattr(service, "_write_outbox", lambda *a, **kw: calls.append(("outbox", kw)) or "outbox-1")
    monkeypatch.setattr(service, "_store_execution", lambda *a, **kw: calls.append(("store", kw)))
    return calls


def db_with_row(version=NOW, rowcount=1):
    db = MagicMock()
    read, deleted = MagicMock(), MagicMock()
    read.mappings.return_value.first.return_value = None if version is None else {"updated_at": version}
    deleted.rowcount = rowcount
    db.execute.side_effect = [read, deleted]
    return db


@pytest.mark.parametrize("kind", ["onboarding", "qualification", "assignment"])
def test_delete_is_scoped_versioned_audited_and_caller_commits(kind, dependencies):
    db = db_with_row()
    result = service.delete_hr_row(db, command(kind), user=USER, tenant="tenant-a")
    sql_calls = db.execute.call_args_list
    assert len(sql_calls) == 2
    assert sql_calls[0].args[1] == {"tenant": "tenant-a", "id": "row-1"}
    assert sql_calls[1].args[1] == {"tenant": "tenant-a", "id": "row-1", "version": NOW}
    assert result["auditEntryId"] == "audit-1" and result["outboxEventId"] == "outbox-1"
    assert [entry[0] for entry in dependencies] == ["lock", "replay", "audit", "outbox", "store"]
    assert dependencies[2][1]["performed_by"] == "person-1"
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
def test_identity_role_and_agent_policy_precede_any_database_work(user, tenant, dependencies):
    db = db_with_row()
    with pytest.raises(HTTPException) as error:
        service.delete_hr_row(db, command(), user=user, tenant=tenant)
    assert error.value.status_code == 403
    assert dependencies == []
    db.execute.assert_not_called()


@pytest.mark.parametrize("version,status", [(None, 404), (datetime(2026, 11, 6, tzinfo=timezone.utc), 409)])
def test_missing_or_stale_row_never_mutates(version, status, dependencies):
    db = db_with_row(version)
    with pytest.raises(HTTPException) as error:
        service.delete_hr_row(db, command(), user=USER, tenant="tenant-a")
    assert error.value.status_code == status
    assert db.execute.call_count == 1
    assert [entry[0] for entry in dependencies] == ["lock", "replay"]


def test_replay_returns_without_touching_hr_row(monkeypatch, dependencies):
    monkeypatch.setattr(service, "_replay_or_none", lambda *args: {"success": True, "replayed": True})
    db = db_with_row()
    assert service.delete_hr_row(db, command(), user=USER, tenant="tenant-a")["replayed"] is True
    db.execute.assert_not_called()


def test_command_rejects_untrusted_fields_and_naive_timestamp():
    with pytest.raises(ValidationError):
        service.HrDeleteCommand(kind="assignment", entity_id="x", expected_updated_at="2026-11-07T00:00:00",
                                idempotency_key="k", tenant_id="other")

@pytest.mark.parametrize("previous_actor,previous_hash", [("other", "hash"), ("person-1", "other")])
def test_replay_rejects_changed_actor_or_payload_without_rolling_back_caller(previous_actor, previous_hash):
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": previous_actor, "payload_hash": previous_hash, "result": {"success": True},
    }
    with pytest.raises(HTTPException) as error:
        service._replay_or_none(db, "tenant-a", "hr.assignment.delete.v1", "key-1", "person-1", "hash")
    assert error.value.status_code == 409
    db.rollback.assert_not_called()


def test_replay_of_same_actor_and_payload_keeps_caller_transaction():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": "person-1", "payload_hash": "hash", "result": '{"success": true}',
    }
    assert service._replay_or_none(db, "tenant-a", "hr.assignment.delete.v1", "key-1", "person-1", "hash") == {
        "success": True, "replayed": True,
    }
    db.rollback.assert_not_called()


def test_audit_failure_is_propagated_and_never_stored_as_success(monkeypatch, dependencies):
    def fail_audit(*args, **kwargs):
        raise RuntimeError("audit unavailable")
    monkeypatch.setattr(service, "_write_audit", fail_audit)
    db = db_with_row()
    with pytest.raises(RuntimeError, match="audit unavailable"):
        service.delete_hr_row(db, command(), user=USER, tenant="tenant-a")
    assert [entry[0] for entry in dependencies] == ["lock", "replay"]
    db.commit.assert_not_called()
