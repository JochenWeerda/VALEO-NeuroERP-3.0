"""PostgreSQL HR contracts on the shared probe; all own data is rolled back."""
import os
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.services import hr_row_delete_commands as service

TENANT = "00000000-0000-0000-0000-000000000001"
OTHER = "00000000-0000-0000-0000-000000000002"
TABLES = {"qualification": "qualification_profiles", "assignment": "training_assignments", "onboarding": "onboarding_runs"}


@pytest.fixture
def probe(monkeypatch):
    raw = os.environ.get("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("explicit shared probe URL required")
    url = make_url(raw)
    assert url.database == "valeo_probe"
    engine = create_engine(url, connect_args={"connect_timeout": 5, "application_name": "agent:hr-row-delete"})
    identity = SimpleNamespace(subject="hr-row-delete-test", tenant_id=TENANT,
                               roles={"PERSONAL_BEARBEITEN"}, claims={"identity_type": "human"})
    monkeypatch.setattr(service, "current_identity", lambda: identity)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET LOCAL lock_timeout = '3s'"))
            connection.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            yield connection
        finally:
            transaction.rollback()
    engine.dispose()


def seed(connection, kind, tenant):
    row, parent = str(uuid4()), str(uuid4())
    params = {"id": row, "tenant": tenant, "employee": f"probe-{row}", "parent": parent}
    if kind == "qualification":
        connection.execute(text("INSERT INTO domain_hr.qualification_profiles "
            "(id, tenant_id, employee_ref, role_code, qualification_level, skills) "
            "VALUES (:id, :tenant, :employee, 'probe', 'basic', '[]'::jsonb)"), params)
    elif kind == "assignment":
        connection.execute(text("INSERT INTO domain_hr.training_courses (id, tenant_id, course_code, title) "
            "VALUES (:parent, :tenant, :parent, 'probe')"), params)
        connection.execute(text("INSERT INTO domain_hr.training_assignments (id, tenant_id, employee_ref, course_id) "
            "VALUES (:id, :tenant, :employee, :parent)"), params)
    else:
        connection.execute(text("INSERT INTO domain_hr.onboarding_checklists (id, tenant_id, checklist_code, title) "
            "VALUES (:parent, :tenant, :parent, 'probe')"), params)
        connection.execute(text("INSERT INTO domain_hr.onboarding_runs (id, tenant_id, employee_ref, checklist_id) "
            "VALUES (:id, :tenant, :employee, :parent)"), params)
    table = TABLES[kind]
    version = connection.execute(text(f"SELECT encode(sha256(convert_to(to_jsonb(r)::text, 'UTF8')), 'hex') FROM domain_hr.{table} r WHERE id=:id AND tenant_id=:tenant"), params).scalar_one()
    return row, version


@pytest.mark.parametrize("kind", TABLES)
def test_postgres_replay_version_and_foreign_isolation(probe, kind):
    own, version = seed(probe, kind, TENANT)
    foreign, _ = seed(probe, kind, OTHER)
    key = f"probe-{own}"
    def command(row=own, revision=version, request_key=key):
        return service.HrDeleteCommand(kind=kind, entity_id=row, expected_revision=revision, idempotency_key=request_key)
    with Session(bind=probe, join_transaction_mode="create_savepoint") as db:
        with pytest.raises(HTTPException) as stale:
            service.delete_hr_row(db, command(revision="b" * 64, request_key=f"stale-{own}"), tenant=TENANT)
        assert stale.value.status_code == 409
        with pytest.raises(HTTPException) as forbidden:
            service.delete_hr_row(db, command(row=foreign, request_key=f"foreign-{own}"), tenant=TENANT)
        assert forbidden.value.status_code == 404
        result = service.delete_hr_row(db, command(), tenant=TENANT)
        assert result["success"] and service.delete_hr_row(db, command(), tenant=TENANT)["replayed"]
        with pytest.raises(HTTPException) as collision:
            service.delete_hr_row(db, command(row=foreign), tenant=TENANT)
        assert collision.value.status_code == 409
        assert probe.execute(text(f"SELECT count(*) FROM domain_hr.{TABLES[kind]} WHERE id=:id AND tenant_id=:tenant"),
                             {"id": foreign, "tenant": OTHER}).scalar_one() == 1
        db.rollback()
    assert probe.execute(text(f"SELECT count(*) FROM domain_hr.{TABLES[kind]} WHERE id=:id AND tenant_id=:tenant"),
                         {"id": own, "tenant": TENANT}).scalar_one() == 1
    assert probe.execute(text("SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:tool AND idempotency_key=:key"),
                         {"tenant": TENANT, "tool": f"hr.{kind}.delete.v1", "key": key}).scalar_one() == 0


@pytest.mark.parametrize("failure", ["_write_audit", "_write_outbox"])
def test_postgres_failure_rolls_back_business_and_side_effects(probe, monkeypatch, failure):
    own, version = seed(probe, "qualification", TENANT)
    key = f"failure-{own}"
    original = getattr(service, failure)
    def fail(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("synthetic failure")
    monkeypatch.setattr(service, failure, fail)
    with Session(bind=probe, join_transaction_mode="create_savepoint") as db:
        with pytest.raises(RuntimeError):
            service.delete_hr_row(db, service.HrDeleteCommand(kind="qualification", entity_id=own,
                expected_revision=version, idempotency_key=key), tenant=TENANT)
        db.rollback()
    assert probe.execute(text("SELECT count(*) FROM domain_hr.qualification_profiles WHERE id=:id AND tenant_id=:tenant"),
                         {"id": own, "tenant": TENANT}).scalar_one() == 1
    assert probe.execute(text("SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE entity_id=:id AND tenant_id=:tenant"),
                         {"id": own, "tenant": TENANT}).scalar_one() == 0
    assert probe.execute(text("SELECT count(*) FROM outbox_events WHERE aggregate_id=:id AND tenant_id=:tenant"),
                         {"id": own, "tenant": TENANT}).scalar_one() == 0


@pytest.mark.parametrize("kind", TABLES)
def test_postgres_valeo_app_rls_and_agent_capability(probe, monkeypatch, kind):
    from app.services import mcp_write_capability

    own, version = seed(probe, kind, TENANT)
    foreign, _ = seed(probe, kind, OTHER)
    principal = SimpleNamespace(subject="hr-agent-test", tenant_id=TENANT,
                                roles={"PERSONAL_BEARBEITEN"}, scopes={"masks:write"},
                                claims={"identity_type": "agent"})
    monkeypatch.setattr(service, "current_identity", lambda: principal)
    entry = {"domain_command": f"hr.{kind}.delete.v1", "endpoint": service._ENDPOINTS[kind],
             "screen_id": service._SCREENS[kind], "action": "loeschen", "command_version": 1,
             "agent_write_enabled": True, "agent_roles": ["PERSONAL_BEARBEITEN"]}
    monkeypatch.setattr(mcp_write_capability, "_entries", lambda: [entry])
    probe.execute(text("SET LOCAL ROLE valeo_app"))
    probe.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {"tenant": TENANT})
    visible = probe.execute(text(f"SELECT id FROM domain_hr.{TABLES[kind]} WHERE id IN (:own, :foreign)"),
                            {"own": own, "foreign": foreign}).scalars().all()
    assert visible == [own]
    with Session(bind=probe, join_transaction_mode="create_savepoint") as db:
        for altered in ({"scopes": set()}, {"roles": {"PERSONAL_LESEN"}}):
            denied = SimpleNamespace(**{**vars(principal), **altered})
            monkeypatch.setattr(service, "current_identity", lambda: denied)
            with pytest.raises(HTTPException) as error:
                service.delete_hr_row(db, service.HrDeleteCommand(kind=kind, entity_id=own,
                    expected_revision=version, idempotency_key=f"denied-{own}"), tenant=TENANT)
            assert error.value.status_code == 403
        monkeypatch.setattr(service, "current_identity", lambda: principal)
        with pytest.raises(HTTPException) as foreign_error:
            service.delete_hr_row(db, service.HrDeleteCommand(kind=kind, entity_id=foreign,
                expected_revision=version, idempotency_key=f"foreign-{own}"), tenant=TENANT)
        assert foreign_error.value.status_code == 404
        result = service.delete_hr_row(db, service.HrDeleteCommand(kind=kind, entity_id=own,
            expected_revision=version, idempotency_key=f"delete-{own}"), tenant=TENANT)
        assert result["success"]
        db.rollback()
    assert probe.execute(text(f"SELECT count(*) FROM domain_hr.{TABLES[kind]} WHERE id=:id"), {"id": own}).scalar_one() == 1


@pytest.mark.parametrize("kind", TABLES)
def test_same_timestamp_changed_state_rejects_old_revision(probe, kind):
    own, old_revision = seed(probe, kind, TENANT)
    # NOW() is transaction-stable: this changes notes while retaining the original updated_at.
    table = TABLES[kind]
    before = probe.execute(text(f"SELECT updated_at FROM domain_hr.{table} WHERE id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT}).scalar_one()
    field = "state='{}'::jsonb || jsonb_build_object('probe', 'changed')" if kind == "onboarding" else "notes='changed'"
    probe.execute(text(f"UPDATE domain_hr.{table} SET {field}, updated_at=NOW() WHERE id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT})
    after = probe.execute(text(f"SELECT updated_at FROM domain_hr.{table} WHERE id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT}).scalar_one()
    assert before == after
    with Session(bind=probe, join_transaction_mode="create_savepoint") as db:
        with pytest.raises(HTTPException) as error:
            service.delete_hr_row(db, service.HrDeleteCommand(kind=kind, entity_id=own,
                expected_revision=old_revision, idempotency_key=f"stale-state-{own}"), tenant=TENANT)
        assert error.value.status_code == 409
        db.rollback()
    assert probe.execute(text(f"SELECT count(*) FROM domain_hr.{table} WHERE id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT}).scalar_one() == 1
    assert probe.execute(text("SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE entity_id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT}).scalar_one() == 0
    assert probe.execute(text("SELECT count(*) FROM outbox_events WHERE aggregate_id=:id AND tenant_id=:tenant"), {"id": own, "tenant": TENANT}).scalar_one() == 0


@pytest.mark.parametrize("kind", TABLES)
def test_list_revision_matches_command_across_session_timezones(probe, kind):
    from app.api.v1.endpoints import training
    own, revision = seed(probe, kind, TENANT)
    probe.execute(text("SET LOCAL TIME ZONE 'Pacific/Honolulu'"))
    with Session(bind=probe, join_transaction_mode="create_savepoint") as db:
        if kind == "qualification":
            call = training.list_qualifications(employee_ref=None, tenant_id=TENANT, db=db)
        elif kind == "assignment":
            call = training.list_assignments(employee_ref=None, status=None, tenant_id=TENANT, db=db)
        else:
            call = training.list_runs(employee_ref=None, status=None, tenant_id=TENANT, db=db)
        with pytest.raises(StopIteration) as stop:
            call.send(None)
        rows = stop.value.value
        assert next(row for row in rows if row["id"] == own)["revision"] == revision
        result = service.delete_hr_row(db, service.HrDeleteCommand(kind=kind, entity_id=own,
            expected_revision=revision, idempotency_key=f"list-{own}"), tenant=TENANT)
        event = probe.execute(text("SELECT payload FROM outbox_events WHERE id=:id AND tenant_id=:tenant"),
                              {"id": result["outboxEventId"], "tenant": TENANT}).scalar_one()
        if isinstance(event, str):
            import json
            event = json.loads(event)
        assert event["actor_id"] == "hr-row-delete-test" and event["audit_id"] == result["auditEntryId"]
        assert event["correlation_id"]
        db.rollback()
