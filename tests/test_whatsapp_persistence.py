"""Real shared PostgreSQL transactions; only unique rows owned by this module."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services import whatsapp_notify_service as service

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]
A = "wa-probe-" + uuid.uuid4().hex
B = "wa-probe-" + uuid.uuid4().hex


@pytest.fixture(scope="module")
def engine():
    url = os.environ.get("TEST_DATABASE_URL") or (os.environ.get("DATABASE_URL") if os.environ.get("GITHUB_ACTIONS") == "true" else None)
    if not url:
        pytest.skip("Explicit shared TEST_DATABASE_URL required; no development DB fallback")
    engine = create_engine(url, connect_args={"connect_timeout": 5})
    with engine.begin() as db:
        db.execute(text("SELECT 1 FROM domain_shared.channel_process_threads LIMIT 0"))
        for tenant in (A, B):
            db.execute(text("INSERT INTO domain_shared.tenants (id,name,domain) VALUES (:id,'WhatsApp owned probe',:domain)"), {"id": tenant, "domain": tenant + ".invalid"})
    yield engine
    with engine.begin() as db:
        db.execute(text("DELETE FROM domain_shared.channel_process_threads WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id IN (:a,:b)"), {"a": A, "b": B})
    engine.dispose()


@pytest.fixture(autouse=True)
def own_rows(engine):
    yield
    with engine.begin() as db:
        db.execute(text("DELETE FROM domain_shared.channel_process_threads WHERE tenant_id IN (:a,:b)"), {"a": A, "b": B})


def prepare(db, *, tenant=A, key="request-1", actor="verified-actor", phone="+491700000001", doc="RE-1"):
    return service.send_dokument_ready(tenant, phone, None, None, "Rechnung", doc, db=db, actor=actor, idempotency_key=key)


def counts(engine):
    with engine.connect() as db:
        params = {"a": A, "b": B}
        rows = db.execute(text("SELECT count(*) FROM domain_shared.channel_process_threads WHERE tenant_id IN (:a,:b)"), params).scalar_one()
        audit = db.execute(text("SELECT count(*) FROM domain_shared.channel_thread_audit_items a JOIN domain_shared.channel_process_threads t ON t.thread_id=a.thread_id WHERE t.tenant_id IN (:a,:b)"), params).scalar_one()
        return rows, audit


def test_committed_preparation_survives_new_session_with_actor_audit(engine):
    with Session(engine) as db:
        first = prepare(db)
        db.commit()
    with Session(engine) as db:
        saved = service.get_outbox(A, db=db)
        assert len(saved) == 1
        assert saved[0]["msg_id"] == first["msg_id"]
        assert saved[0]["status"] == "pending_browser"
        actor = db.execute(text("SELECT payload->>'actor' FROM domain_shared.channel_thread_audit_items WHERE thread_id=:id"), {"id": first["msg_id"]}).scalar_one()
        assert actor == "verified-actor"
    assert counts(engine) == (1, 1)


def test_same_request_replays_original_result_without_second_audit(engine):
    with Session(engine) as db:
        first = prepare(db)
        db.commit()
    with Session(engine) as db:
        second = prepare(db)
        db.commit()
    assert second == first
    assert counts(engine) == (1, 1)


@pytest.mark.parametrize("change", [{"phone": "+491700000002"}, {"doc": "RE-2"}, {"actor": "other-actor"}])
def test_replay_cannot_change_content_or_actor(engine, change):
    with Session(engine) as db:
        original = prepare(db)
        db.commit()
    with Session(engine) as db:
        with pytest.raises(service.WhatsAppReplayConflict):
            prepare(db, **change)
        db.commit()
        assert service.get_outbox(A, db=db)[0]["text"] == original["text"]
    assert counts(engine) == (1, 1)


def test_same_key_in_another_tenant_is_independent_and_reads_are_isolated(engine):
    with Session(engine) as db:
        a = prepare(db)
        b = prepare(db, tenant=B, phone="+491700000002")
        db.commit()
        assert a["msg_id"] != b["msg_id"]
        assert [m["phone"] for m in service.get_outbox(A, db=db)] == ["+491700000001"]
        assert [m["phone"] for m in service.get_outbox(B, db=db)] == ["+491700000002"]


def test_rollback_removes_message_and_audit_and_does_not_consume_key(engine):
    with Session(engine) as db:
        first = prepare(db)
        db.rollback()
    assert counts(engine) == (0, 0)
    with Session(engine) as db:
        second = prepare(db)
        db.commit()
    assert first["msg_id"] == second["msg_id"]
    assert counts(engine) == (1, 1)


def test_audit_failure_rolls_back_insert_without_memory_fallback(engine, monkeypatch):
    with Session(engine) as db:
        original = db.execute

        def execute(statement, *args, **kwargs):
            if "INSERT INTO domain_shared.channel_thread_audit_items" in str(statement):
                raise RuntimeError("Owned audit failure")
            return original(statement, *args, **kwargs)

        monkeypatch.setattr(db, "execute", execute)
        with pytest.raises(RuntimeError, match="Owned audit failure"):
            prepare(db)
        db.commit()
    assert counts(engine) == (0, 0)


def test_two_concurrent_transactions_create_one_message_and_audit(engine):
    barrier = Barrier(2)

    def run():
        with Session(engine) as db:
            barrier.wait(timeout=5)
            result = prepare(db)
            db.commit()
            return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [pool.submit(run) for _ in range(2)]
        a, b = [f.result(timeout=10) for f in results]
    assert a == b
    assert counts(engine) == (1, 1)


def test_different_notification_actions_do_not_collide(engine):
    with Session(engine) as db:
        a = prepare(db)
        b = service.send_lieferankuendigung(A, "+491700000001", None, None, "Weizen", 2, "t", db=db, actor="verified-actor", idempotency_key="request-1")
        db.commit()
        assert a["msg_id"] != b["msg_id"]
    assert counts(engine) == (2, 2)


@pytest.mark.parametrize("key", ["", " ", None])
def test_invalid_key_is_rejected_without_write(engine, key):
    with Session(engine) as db:
        with pytest.raises(ValueError, match="Idempotenz"):
            prepare(db, key=key)
        db.commit()
    assert counts(engine) == (0, 0)


def test_listing_is_bounded_and_copies_do_not_change_durable_recipient(engine):
    with Session(engine) as db:
        prepare(db, key="one")
        prepare(db, key="two")
        db.commit()
        result = service.get_outbox(A, db=db, limit=1)
        assert len(result) == 1
        result[0]["phone"] = "changed"
        assert all(m["phone"] == "+491700000001" for m in service.get_outbox(A, db=db))


def test_generic_process_surfaces_cannot_read_or_replace_notifications(engine):
    import app.infrastructure.models  # register existing shared tenant model for ORM foreign keys
    from app.repositories.channel_thread_repository import PersistentChannelProcessThreadStore
    from app.core.channel_process_actions import ChannelProcessThread
    with Session(engine) as db:
        result = prepare(db)
        db.commit()
        store = PersistentChannelProcessThreadStore(db)
        assert store.get(result["msg_id"]) is None
        assert store.get_audit_trail(result["msg_id"]) is None
        assert store.list_threads(tenant_id=A) == []
        forged = ChannelProcessThread(result["msg_id"], "WHATSAPP", A, "other.process", "OtherCommand", "other", "other", "admin", "employee", "other", None, {}, "pending_approval", {})
        with pytest.raises(ValueError, match="cannot be replaced"):
            store.save(forged)
        forged.thread_id = "other-" + uuid.uuid4().hex
        forged.process_definition_key = service._PROCESS
        with pytest.raises(ValueError, match="dedicated service"):
            store.save(forged)
        normal = ChannelProcessThread("normal-" + uuid.uuid4().hex, "TEAMS", A, "ordinary.process", "OtherCommand", "other", "other", "admin", "employee", "other", None, {}, "accepted", {})
        store.save(normal)
        assert store.get(normal.thread_id).process_definition_key == "ordinary.process"
        assert [t.thread_id for t in store.list_threads(tenant_id=A)] == [normal.thread_id]
    assert counts(engine) == (2, 1)


def test_real_http_commit_replay_conflict_and_token_actor(engine, monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.auth.deps_oidc import oidc
    from app.core.database import get_db
    from app.api.v1.endpoints import whatsapp_notify

    async def verify(token):
        return {"sub": "http-actor", "tenant_id": A, "scope": "crm:read crm:write"}

    def database():
        with Session(engine) as db:
            try:
                yield db
            except Exception:
                db.rollback()
                raise

    monkeypatch.setattr(oidc, "verify", verify)
    app = FastAPI()
    app.include_router(whatsapp_notify.router, prefix="/wa")
    app.dependency_overrides[get_db] = database
    body = {"phone": "+491700000001", "doc_typ": "Rechnung", "doc_nr": "RE-1", "idempotency_key": "http-1", "actor": "forged-actor"}
    headers = {"Authorization": "Bearer test"}
    with TestClient(app) as client:
        first = client.post("/wa/dev/notify/dokument-ready", json=body, headers=headers)
        assert first.status_code == 200
        assert client.post("/wa/dev/notify/dokument-ready", json=body, headers=headers).json() == first.json()
        assert client.post("/wa/dev/notify/dokument-ready", json={**body, "doc_nr": "RE-2"}, headers=headers).status_code == 409
        assert client.post("/wa/dev/notify/dokument-ready", json={**body, "tenant_id": B}, headers=headers).status_code == 403
        for key in ("", " "):
            assert client.post("/wa/dev/notify/dokument-ready", json={**body, "idempotency_key": key}, headers=headers).status_code == 422
        assert client.get("/wa/dev/outbox?limit=0", headers=headers).status_code == 422
        assert client.get("/wa/dev/outbox", headers=headers).json()["messages"][0]["msg_id"] == first.json()["msg_id"]
    with engine.connect() as db:
        actor = db.execute(text("SELECT payload->>'actor' FROM domain_shared.channel_thread_audit_items WHERE thread_id=:id"), {"id": first.json()["msg_id"]}).scalar_one()
        assert actor == "http-actor"
    assert counts(engine) == (1, 1)
