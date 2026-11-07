"""Transactional HR command evidence using real SQLite transactions, not PostgreSQL/RLS."""
import re
import hashlib
import sqlite3
from datetime import datetime, timezone
from unittest.mock import patch
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.services import hr_row_delete_commands as service

NOW = datetime(2026, 11, 7, tzinfo=timezone.utc)
USER = {"sub": "person-1", "roles": ["PERSONAL_BEARBEITEN"],
        "raw": {"tenant_id": "tenant-a", "identity_type": "human"}}


@pytest.fixture(autouse=True)
def verified_identity(monkeypatch):
    monkeypatch.setattr(service, "current_identity", lambda: SimpleNamespace(subject="person-1", tenant_id="tenant-a", roles={"PERSONAL_BEARBEITEN"}, claims={"identity_type": "human"}))


@pytest.fixture
def session():
    sqlite3.register_converter("HR_TIMESTAMP", lambda value: datetime.fromisoformat(value.decode()))
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"detect_types": sqlite3.PARSE_DECLTYPES})
    @event.listens_for(engine, "connect")
    def connect(connection, _):
        connection.isolation_level = None
        for schema in ("domain_hr", "domain_crm", "public"):
            connection.execute(f"ATTACH DATABASE ':memory:' AS {schema}")
        connection.create_function("NOW", 0, lambda: NOW.isoformat())
        connection.create_function("hr_revision", 3, lambda entity, tenant, updated: hashlib.sha256(f"{entity}:{tenant}:{updated}".encode()).hexdigest())
        connection.create_function("pg_advisory_xact_lock", 1, lambda _: 0)
    @event.listens_for(engine, "begin")
    def begin(connection):
        connection.exec_driver_sql("BEGIN")
    @event.listens_for(engine, "before_cursor_execute", retval=True)
    def representations(connection, cursor, statement, parameters, context, many):
        statement = re.sub(r" FOR UPDATE", "", statement, flags=re.I)
        if statement.startswith("SET LOCAL TIME ZONE"):
            statement = "SELECT 1"
        statement = re.sub(r"SELECT encode\(sha256\(convert_to\(to_jsonb\(r\)::text, 'UTF8'\)\), 'hex'\) AS revision", "SELECT hr_revision(id, tenant_id, updated_at) AS revision", statement, flags=re.I)
        statement = re.sub(r"CAST\((\?) AS jsonb\)", r"\1", statement, flags=re.I)
        params = tuple(value.isoformat(sep=' ') if isinstance(value, datetime) else value for value in parameters)
        return statement, params
    with engine.begin() as connection:
        for table in ("onboarding_runs", "qualification_profiles", "training_assignments"):
            connection.exec_driver_sql(f"CREATE TABLE domain_hr.{table} (id TEXT, tenant_id TEXT, updated_at HR_TIMESTAMP, PRIMARY KEY (tenant_id, id))")
            connection.execute(text(f"INSERT INTO domain_hr.{table} VALUES (:id, :tenant, :version)"),
                               [{"id": "row-a", "tenant": "tenant-a", "version": NOW},
                                {"id": "row-b", "tenant": "tenant-b", "version": NOW}])
        connection.exec_driver_sql("CREATE TABLE public.mcp_tool_executions (tenant_id TEXT, tool_name TEXT, idempotency_key TEXT, actor_id TEXT, payload_hash TEXT, result TEXT, PRIMARY KEY(tenant_id, tool_name, idempotency_key))")
        connection.exec_driver_sql("CREATE TABLE domain_crm.crm_action_audit_log (id TEXT, tenant_id TEXT, action_key TEXT, entity_type TEXT, entity_id TEXT, idempotency_key TEXT, audit_reason TEXT, performed_at TEXT, result_summary TEXT, performed_by TEXT)")
        connection.exec_driver_sql("CREATE TABLE outbox_events (id TEXT, event_type TEXT, aggregate_id TEXT, payload TEXT, timestamp TEXT, published BOOLEAN, retry_count INTEGER, tenant_id TEXT)")
    with Session(engine) as db:
        yield db
    engine.dispose()


def cmd(kind, entity="row-a", key="key-1", version=None):
    version = version or hashlib.sha256(f"{entity}:tenant-a:{NOW.isoformat(sep=' ')}".encode()).hexdigest()
    return service.HrDeleteCommand(kind=kind, entity_id=entity, expected_revision=version, idempotency_key=key)


def count(db, table):
    return db.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


@pytest.mark.parametrize("kind,table", [("onboarding", "onboarding_runs"), ("qualification", "qualification_profiles"), ("assignment", "training_assignments")])
def test_real_transaction_replay_and_foreign_row(session, kind, table):
    result = service.delete_hr_row(session, cmd(kind), tenant="tenant-a")
    session.commit()
    assert count(session, f"domain_hr.{table}") == 1
    assert session.execute(text(f"SELECT tenant_id FROM domain_hr.{table}")).scalar_one() == "tenant-b"
    assert service.delete_hr_row(session, cmd(kind), tenant="tenant-a") == {**result, "replayed": True}
    assert count(session, "domain_crm.crm_action_audit_log") == 1
    assert count(session, "outbox_events") == 1
    with pytest.raises(HTTPException) as conflict:
        service.delete_hr_row(session, cmd(kind, "row-b"), tenant="tenant-a")
    assert conflict.value.status_code == 409


@pytest.mark.parametrize("failure", ["audit", "outbox", "replay"])
def test_failure_rolls_back_business_change_and_all_side_effects(session, failure):
    name = {"audit": "_write_audit", "outbox": "_write_outbox", "replay": "store_execution"}[failure]
    original = getattr(service, name)
    def fail(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("synthetic failure")
    with patch.object(service, name, side_effect=fail):
        with pytest.raises(RuntimeError):
            service.delete_hr_row(session, cmd("qualification"), tenant="tenant-a")
        session.rollback()
    assert count(session, "domain_hr.qualification_profiles") == 2
    assert count(session, "domain_crm.crm_action_audit_log") == 0
    assert count(session, "outbox_events") == 0
    assert count(session, "public.mcp_tool_executions") == 0
