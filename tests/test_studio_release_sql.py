"""Shared-probe SQL evidence tests; each test rolls back its own outer transaction."""
from uuid import uuid4
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services import studio_draft_store as store
from app.core import studio_release as release
from app.services import studio_process_simulation as simulation
from app.services.studio_propose import propose_studio_draft

pytestmark=[pytest.mark.integration, pytest.mark.needs_live_db]

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

@pytest.fixture
def sql_candidate(monkeypatch):
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt
    assert pruefstand_erlaubt(engine.url), "Only the declared shared test database is allowed"
    monkeypatch.setattr(simulation, "_configured_probe", lambda: engine)
    connection=engine.connect();outer=connection.begin()
    own=str(uuid4())
    connection.execute(text("INSERT INTO domain_shared.tenants(id,name,domain) VALUES (:id,'Studio SQL evidence',:domain)"),
                       {"id":own,"domain":own+".example.invalid"})
    monkeypatch.setattr(store,"_prefer_memory",False)
    monkeypatch.setattr(store,"_use_sql",lambda:True)
    monkeypatch.setattr(store,"_sql_session",lambda:Session(bind=connection,join_transaction_mode="create_savepoint",expire_on_commit=False))
    definition=propose_studio_draft("Artikel");definition["domain"]="agrar"
    definition["actions"]=[];definition["agentContract"]["availableActions"]=[];definition["agentContract"]["editableFields"]=[]
    draft=store.save_draft(own,"editor",definition)
    item=store.set_status(own,draft["id"],"editor","review",expected_snapshot=draft)
    try:
        yield item
    finally:
        assert outer.is_active
        outer.rollback();connection.close()
        with engine.connect() as verify:
            assert verify.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id=:id"),{"id":own}).scalar_one()==0


def test_sql_real_evidence_is_durable_replayable_and_publishable(sql_candidate,monkeypatch):
    item=sql_candidate;key=str(uuid4())
    entries=store.list_history(item["tenant_id"],item["id"])
    assert entries[-1]["revision"]==item["revision"]
    assert store.history_event(item["tenant_id"],item["id"],revision=entries[-1]["previous_revision"]) is not None
    result=store.simulate_draft(item["tenant_id"],item["id"],"editor",item["revision"],key)
    assert result["simulation"]["passed"] is True,result["simulation"]
    monkeypatch.setattr(release,"simulate_candidate",lambda _:pytest.fail("Replay must not run the chain again"))
    assert store.simulate_draft(item["tenant_id"],item["id"],"editor",item["revision"],key)==result
    event=store.history_event(item["tenant_id"],item["id"],event_id=key)
    assert event["snapshot"]["simulation"]==result["simulation"]
    assert store.count_history(item["tenant_id"],item["id"])==3
    published=store.set_status(item["tenant_id"],item["id"],"reviewer","published_temp",expected_snapshot=item)
    assert published["status"]=="published_temp"


def test_sql_evidence_insert_failure_cannot_publish(sql_candidate,monkeypatch):
    item=sql_candidate
    monkeypatch.setattr(release,"simulate_candidate",lambda _: {"passed":False})
    def fail(*args,**kwargs):
        raise RuntimeError("synthetic evidence insertion failure")
    with monkeypatch.context() as phase:
        phase.setattr(store,"_append_sql_history",fail)
        with pytest.raises(RuntimeError,match="insertion failure"):
            store.simulate_draft(item["tenant_id"],item["id"],"editor",item["revision"],str(uuid4()))
    assert store.count_history(item["tenant_id"],item["id"])==2
    with pytest.raises(ValueError,match="simulation_fuer_diese_revision_fehlt"):
        store.set_status(item["tenant_id"],item["id"],"reviewer","published_temp",expected_snapshot=item)
    assert store.get_draft(item["tenant_id"],item["id"])["status"]=="review"


def test_sql_foreign_tenant_cannot_simulate_or_read_evidence(sql_candidate):
    item=sql_candidate
    with pytest.raises(KeyError):
        store.simulate_draft(str(uuid4()),item["id"],"foreign",item["revision"],str(uuid4()))
    assert store.list_history("foreign",item["id"])==[]


def test_shared_probe_busy_does_not_persist_failed_evidence(sql_candidate):
    from app.core.studio_release import SimulationBusy
    item=sql_candidate;engine=simulation._configured_probe()
    with engine.connect() as held:
        transaction=held.begin()
        held.execute(text("SELECT pg_advisory_xact_lock(hashtextextended('valeo.studio.simulation.grain.v1', 0))"))
        try:
            with pytest.raises(SimulationBusy):
                store.simulate_draft(item["tenant_id"],item["id"],"editor",item["revision"],str(uuid4()))
        finally:
            transaction.rollback()
    assert store.count_history(item["tenant_id"],item["id"])==2
