"""The live delegated runtime must persist one unit or confirm no success."""
import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services import mask_action_runtime_service as runtime


def run(db, **options):
    execute = options.pop("execute_fn", lambda *_: {"summary": "saved"})
    async def delegate(session, payload, entity, tenant):
        return execute(session, payload, entity, tenant)["summary"]
    return asyncio.run(runtime.run_delegated_mask_action(
        db, action_key="save", entity_type="test", entity_id="record", tenant_id="tenant",
        body=options.pop("body", {}), check_fn=options.pop("check_fn", AsyncMock(return_value=[])),
        delegate_fn=delegate, outbox_event_type="test.saved", **options))


@pytest.mark.parametrize("mode", ["dryrun", "EXECUTE", "", None, [], {}])
def test_invalid_mode_never_calls_executor_or_database(mode):
    db, execute = Mock(), Mock()
    result = run(db, body={"_mode": mode}, execute_fn=execute)
    assert not result.success
    assert result.validationErrors[0]["field"] == "_mode"
    execute.assert_not_called()
    assert not db.mock_calls


@pytest.mark.parametrize("failure", ["mutation", "audit", "outbox", "commit"])
def test_every_transaction_failure_returns_no_success_ids(failure, caplog):
    db = Mock()
    execute = Mock(return_value={"summary": "saved"})
    error = SQLAlchemyError("relation secret_table does not exist; applicant_email=private@example.test")
    if failure == "mutation":
        execute.side_effect = error
    elif failure == "audit":
        db.execute.side_effect = error
    elif failure == "outbox":
        db.execute.side_effect = [None, error]
    else:
        db.commit.side_effect = error
    result = run(db, execute_fn=execute)
    assert not result.success
    assert result.auditEntryId is None
    assert result.outboxEventId is None
    assert result.affectedIds is None
    assert "secret_table" not in result.error
    assert "private@example.test" not in result.error
    assert "secret_table" not in caplog.text
    assert "private@example.test" not in caplog.text
    assert db.rollback.call_count == 2
    if failure != "commit":
        db.commit.assert_not_called()


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose"])
def test_preview_modes_do_not_write(mode):
    db, execute = Mock(), Mock()
    result = run(db, body={"_mode": mode}, execute_fn=execute)
    assert result.success
    execute.assert_not_called()
    db.execute.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_called_once()


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose", "execute"])
def test_every_mode_obeys_the_real_business_blocker(mode):
    db, execute = Mock(), Mock()
    errors = [{"field": "status", "message": "Endgueltiger Stand", "severity": "blocking"}]
    check = AsyncMock(return_value=errors)
    result = run(db, body={"_mode": mode, "status": "closed"}, check_fn=check, execute_fn=execute)
    assert not result.success
    assert result.validationErrors == errors
    assert result.proposedChanges is None
    check.assert_awaited_once_with(db, {"status": "closed"}, "record", "tenant")
    execute.assert_not_called()
    db.execute.assert_not_called()
    db.commit.assert_not_called()


def test_expected_business_detail_is_preserved():
    result = run(Mock(), check_fn=AsyncMock(side_effect=HTTPException(409, "Vier-Augen-Prinzip verletzt")))
    assert not result.success
    assert result.error == "Vier-Augen-Prinzip verletzt"


def test_retired_second_runtime_cannot_be_reused():
    for symbol in ("run_mask_action", "ExecuteFn", "_default_propose"):
        assert not hasattr(runtime, symbol), symbol


def database(*, audit=True, outbox=True):
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.connection.driver_connection.create_function("NOW", 0, lambda: "2026-10-09T00:00:00Z")
        connection.execute(text("ATTACH DATABASE ':memory:' AS domain_crm"))
        connection.execute(text("CREATE TABLE records (id TEXT PRIMARY KEY, value TEXT)"))
        connection.execute(text("INSERT INTO records VALUES ('record', 'before')"))
        if audit:
            connection.execute(text("CREATE TABLE domain_crm.crm_action_audit_log (id TEXT PRIMARY KEY, tenant_id TEXT, action_key TEXT, entity_type TEXT, entity_id TEXT, idempotency_key TEXT, audit_reason TEXT, performed_at TEXT, result_summary TEXT)"))
        if outbox:
            connection.execute(text("CREATE TABLE outbox_events (id TEXT PRIMARY KEY, event_type TEXT, aggregate_id TEXT, payload TEXT, timestamp TEXT, published BOOLEAN, retry_count INTEGER, tenant_id TEXT)"))
    return engine


def mutate(session, payload, entity, tenant):
    session.execute(text("UPDATE records SET value='after' WHERE id='record'"))
    return {"summary": "saved"}


@pytest.mark.parametrize("missing", ["audit", "outbox"])
def test_actual_missing_persistence_table_leaves_everything_unchanged(missing):
    engine = database(audit=missing != "audit", outbox=missing != "outbox")
    with Session(engine) as db:
        result = run(db, execute_fn=mutate)
        assert not result.success
        assert db.execute(text("SELECT value FROM records")).scalar_one() == "before"
        if missing == "outbox":
            assert db.execute(text("SELECT COUNT(*) FROM domain_crm.crm_action_audit_log")).scalar_one() == 0
    engine.dispose()


def test_actual_mutation_failure_rolls_back_audit_and_outbox():
    engine = database()
    def failing_mutation(session, *args):
        session.execute(text("UPDATE records SET value='after' WHERE id='record'"))
        raise HTTPException(409, "Fachweg lehnt ab")
    with Session(engine) as db:
        result = run(db, execute_fn=failing_mutation)
        assert not result.success
        assert db.execute(text("SELECT value FROM records")).scalar_one() == "before"
        assert db.execute(text("SELECT COUNT(*) FROM domain_crm.crm_action_audit_log")).scalar_one() == 0
        assert db.execute(text("SELECT COUNT(*) FROM outbox_events")).scalar_one() == 0
    engine.dispose()


@pytest.mark.parametrize("inner_commit", [False, True])
def test_actual_commit_persists_mutation_and_returned_audit_and_event_ids(inner_commit):
    engine = database()
    def successful_mutation(session, *args):
        result = mutate(session, *args)
        if inner_commit:
            session.commit()
        return result
    with Session(engine) as db:
        result = run(db, execute_fn=successful_mutation)
        assert result.success
    with Session(engine) as verify:
        assert verify.execute(text("SELECT value FROM records")).scalar_one() == "after"
        audit = verify.execute(text("SELECT id, tenant_id FROM domain_crm.crm_action_audit_log")).one()
        event = verify.execute(text("SELECT id, tenant_id FROM outbox_events")).one()
        assert audit.id == result.auditEntryId
        assert event.id == result.outboxEventId
        assert audit.tenant_id == event.tenant_id == "tenant"
        assert result.affectedIds == ["record"]
    engine.dispose()


@pytest.mark.parametrize("status", [500, 503])
def test_wrapped_storage_errors_do_not_leak_through_http_exception(status, caplog):
    error = HTTPException(status, "SQL: secret_table; applicant_email=private@example.test")
    result = run(Mock(), execute_fn=Mock(side_effect=error))
    assert not result.success
    assert "secret_table" not in result.error
    assert "private@example.test" not in result.error
    assert "secret_table" not in caplog.text
    assert "private@example.test" not in caplog.text


def test_delegate_commit_cannot_escape_outer_rollback_when_later_rejected():
    engine = database()
    def commit_then_reject(session, *args):
        session.execute(text("UPDATE records SET value='after' WHERE id='record'"))
        session.commit()
        raise HTTPException(409, "Fachweg nach innerem Commit abgelehnt")
    with Session(engine) as db:
        result = run(db, execute_fn=commit_then_reject)
        assert not result.success
        assert db.execute(text("SELECT value FROM records")).scalar_one() == "before"
        assert db.execute(text("SELECT COUNT(*) FROM domain_crm.crm_action_audit_log")).scalar_one() == 0
        assert db.execute(text("SELECT COUNT(*) FROM outbox_events")).scalar_one() == 0
    engine.dispose()
