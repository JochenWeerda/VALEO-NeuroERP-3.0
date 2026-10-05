"""Persistence failures must never be reported as successful mask actions."""
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.mask_action_runtime_service import run_mask_action


def run(db, **options):
    return run_mask_action(db, action_key="save", entity_type="test", entity_id="record",
                           tenant_id="tenant", body=options.pop("body", {}), **options)


@pytest.mark.parametrize("mode", ["dryrun", "EXECUTE", "", None, [], {}])
def test_invalid_mode_never_calls_executor_or_database(mode):
    db, execute = Mock(), Mock()
    result = run(db, body={"_mode": mode}, execute_fn=execute)
    assert not result.success
    assert result.validationErrors[0]["field"] == "_mode"
    execute.assert_not_called()
    assert not db.mock_calls


@pytest.mark.parametrize("failure", ["mutation", "audit", "outbox", "commit"])
def test_every_transaction_failure_returns_no_success_ids(failure):
    db = Mock()
    execute = Mock(return_value={"summary": "saved"})
    error = RuntimeError('relation secret_table does not exist')
    if failure == "mutation":
        execute.side_effect = error
    elif failure == "audit":
        db.execute.side_effect = error
    elif failure == "outbox":
        db.execute.side_effect = [None, error]
    else:
        db.commit.side_effect = error
    result = run(db, execute_fn=execute, outbox_event_type="test.saved")
    assert not result.success
    assert result.auditEntryId is None
    assert result.outboxEventId is None
    assert result.affectedIds is None
    assert "secret_table" not in result.error
    db.rollback.assert_called_once()
    if failure != "commit":
        db.commit.assert_not_called()


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose"])
def test_preview_modes_do_not_write(mode):
    db, execute = Mock(), Mock()
    result = run(db, body={"_mode": mode}, execute_fn=execute)
    assert result.success
    execute.assert_not_called()
    assert not db.mock_calls


def test_actual_mutation_rolls_back_when_audit_table_is_missing():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE records (id TEXT PRIMARY KEY, value TEXT)"))
        connection.execute(text("INSERT INTO records VALUES ('record', 'before')"))
    with Session(engine) as db:
        def mutate(session, payload, entity, tenant):
            session.execute(text("UPDATE records SET value='after' WHERE id='record'"))
            return {"summary": "saved"}
        result = run(db, execute_fn=mutate)
        assert not result.success
        assert db.execute(text("SELECT value FROM records")).scalar_one() == "before"
    engine.dispose()


def test_actual_commit_persists_mutation_and_returned_audit_id():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("ATTACH DATABASE ':memory:' AS domain_crm"))
        connection.execute(text("CREATE TABLE records (id TEXT PRIMARY KEY, value TEXT)"))
        connection.execute(text("INSERT INTO records VALUES ('record', 'before')"))
        connection.execute(text('''CREATE TABLE domain_crm.crm_action_audit_log (
            id TEXT PRIMARY KEY, tenant_id TEXT, action_key TEXT, entity_type TEXT,
            entity_id TEXT, idempotency_key TEXT, audit_reason TEXT, performed_at TEXT,
            result_summary TEXT)'''))
    with Session(engine) as db:
        def mutate(session, payload, entity, tenant):
            session.execute(text("UPDATE records SET value='after' WHERE id='record'"))
            return {"summary": "saved"}
        result = run(db, execute_fn=mutate)
        assert result.success
    with Session(engine) as verify:
        assert verify.execute(text("SELECT value FROM records")).scalar_one() == "after"
        audit = verify.execute(text("SELECT id, tenant_id FROM domain_crm.crm_action_audit_log")).one()
        assert audit.id == result.auditEntryId
        assert audit.tenant_id == "tenant"
    engine.dispose()
