"""Two-session replay contract on valeo_probe; only uniquely owned rows are cleaned."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.services import hr_row_delete_commands as service, mcp_write_capability

TENANT = "00000000-0000-0000-0000-000000000001"
ACTION = "hr.qualification.delete.v1"


@pytest.mark.skipif(not os.environ.get("TEST_DATABASE_URL"), reason="explicit shared probe URL required")
def test_parallel_identical_hr_commands_produce_one_effect_and_one_replay(monkeypatch):
    url = make_url(os.environ["TEST_DATABASE_URL"])
    assert url.database == "valeo_probe"
    assert os.environ.get("PGAPPNAME") == "agent:hr-row-delete-concurrency"
    engine = create_engine(url, poolclass=NullPool, connect_args={"connect_timeout": 5})
    row_id, key = str(uuid4()), f"hr-race-{uuid4()}"
    actor = f"hr-race-{uuid4()}"
    principal = SimpleNamespace(subject=actor, tenant_id=TENANT, roles={"PERSONAL_BEARBEITEN"},
                                scopes={"masks:write"}, claims={"identity_type": "agent"})
    monkeypatch.setattr(service, "current_identity", lambda: principal)
    capability = {"domain_command": ACTION, "endpoint": service._ENDPOINTS["qualification"],
                  "screen_id": service._SCREENS["qualification"], "action": "loeschen",
                  "command_version": 1, "agent_write_enabled": True,
                  "agent_roles": ["PERSONAL_BEARBEITEN"]}
    monkeypatch.setattr(mcp_write_capability, "_entries", lambda: [capability])
    seeded = False
    try:
        with engine.begin() as conn:
            conn.execute(text("SET LOCAL ROLE valeo_app"))
            conn.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {"tenant": TENANT})
            conn.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            conn.execute(text("INSERT INTO domain_hr.qualification_profiles "
                "(id, tenant_id, employee_ref, role_code, qualification_level, skills) "
                "VALUES (:id, :tenant, :employee, 'probe', 'basic', '[]'::jsonb)"),
                {"id": row_id, "tenant": TENANT, "employee": f"probe-{row_id}"})
            version = conn.execute(text("SELECT encode(sha256(convert_to(to_jsonb(r)::text, 'UTF8')), 'hex') FROM domain_hr.qualification_profiles r WHERE id=:id AND tenant_id=:tenant"), {"id": row_id, "tenant": TENANT}).scalar_one()
        seeded = True
        rendezvous = Barrier(2, timeout=15)
        def run():
            with engine.begin() as conn:
                conn.execute(text("SET LOCAL ROLE valeo_app"))
                conn.execute(text("SET LOCAL lock_timeout = '10s'"))
                conn.execute(text("SET LOCAL statement_timeout = '20s'"))
                conn.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {"tenant": TENANT})
                pid = conn.execute(text("SELECT pg_backend_pid()")).scalar_one()
                with Session(bind=conn, join_transaction_mode="create_savepoint") as db:
                    rendezvous.wait()
                    result = service.delete_hr_row(db, service.HrDeleteCommand(kind="qualification", entity_id=row_id,
                        expected_revision=version, idempotency_key=key), tenant=TENANT)
                    db.commit()
                return pid, result
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: run(), range(2)))
        assert results[0][0] != results[1][0]
        answers = [result for _, result in results]
        assert sorted(answer["replayed"] for answer in answers) == [False, True]
        assert answers[0]["auditEntryId"] == answers[1]["auditEntryId"]
        assert answers[0]["outboxEventId"] == answers[1]["outboxEventId"]
        with engine.begin() as conn:
            conn.execute(text("SET LOCAL ROLE valeo_app"))
            conn.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {"tenant": TENANT})
            params = {"tenant": TENANT, "id": row_id, "action": ACTION, "key": key}
            assert conn.execute(text("SELECT count(*) FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id"), params).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:tenant AND entity_id=:id AND action_key=:action AND idempotency_key=:key"), params).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM outbox_events WHERE tenant_id=:tenant AND aggregate_id=:id AND event_type=:action"), params).scalar_one() == 1
            assert conn.execute(text("SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:action AND idempotency_key=:key"), params).scalar_one() == 1
    finally:
        if seeded:
            with engine.begin() as conn:
                conn.execute(text("SET LOCAL ROLE valeo_app"))
                conn.execute(text("SELECT set_config('app.tenant_id', :tenant, true)"), {"tenant": TENANT})
                params = {"tenant": TENANT, "id": row_id, "action": ACTION, "key": key}
                conn.execute(text("DELETE FROM outbox_events WHERE tenant_id=:tenant AND aggregate_id=:id AND event_type=:action"), params)
                conn.execute(text("DELETE FROM domain_crm.crm_action_audit_log WHERE tenant_id=:tenant AND entity_id=:id AND action_key=:action AND idempotency_key=:key"), params)
                conn.execute(text("DELETE FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:action AND idempotency_key=:key"), params)
                conn.execute(text("DELETE FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id"), params)
                assert conn.execute(text("SELECT count(*) FROM outbox_events WHERE tenant_id=:tenant AND aggregate_id=:id AND event_type=:action"), params).scalar_one() == 0
                assert conn.execute(text("SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:tenant AND entity_id=:id AND action_key=:action AND idempotency_key=:key"), params).scalar_one() == 0
                assert conn.execute(text("SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:tenant AND tool_name=:action AND idempotency_key=:key"), params).scalar_one() == 0
                assert conn.execute(text("SELECT count(*) FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant AND id=:id"), params).scalar_one() == 0
        engine.dispose()
