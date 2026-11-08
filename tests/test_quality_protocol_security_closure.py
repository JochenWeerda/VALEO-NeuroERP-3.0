"""Quality protocol tenant, actor, and finalization invariants."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import quality_protocols as api
from modules.agrar.repositories import quality_protocol_repo as repository


class Query:
    def __init__(self, row):
        self.row = row
        self.filters = []
        self.locks = []

    def filter(self, *conditions):
        self.filters.extend(str(condition) for condition in conditions)
        return self

    def with_for_update(self, **options):
        self.locks.append(options)
        return self

    def populate_existing(self):
        self.refreshed_identity = True
        return self

    def first(self):
        return self.row


class Db:
    def __init__(self, row):
        self.row = row
        self.queries = []
        self.flushes = 0
        self.commits = 0

    def query(self, model):
        query = Query(self.row)
        self.queries.append(query)
        return query

    def flush(self):
        self.flushes += 1

    def refresh(self, row):
        pass

    def commit(self):
        self.commits += 1


def test_repository_requires_tenant_and_parent_ownership():
    with pytest.raises(ValueError, match="Tenant context"):
        repository.QualityProtocolRepositoryImpl(Db(None), "")
    db = Db(None)
    repo = repository.QualityProtocolRepositoryImpl(db, "tenant-a")
    with pytest.raises(repository.AcceptanceNotOwnedError):
        repo.ensure_acceptance_owned("acceptance-b")
    assert db.queries[-1].locks == []
    assert any("tenant_id" in clause for clause in db.queries[-1].filters)
    assert db.commits == 0


def test_finalize_checks_state_under_row_lock_and_defers_commit():
    row = SimpleNamespace(is_final=False, approved_by=None, approved_at=None, updated_at=None)
    db = Db(row)
    repo = repository.QualityProtocolRepositoryImpl(db, "tenant-a")
    repo._to_service = lambda value: value
    result = repo.finalize("protocol-a", "verified-sub")
    assert result.is_final is True
    assert result.approved_by == "verified-sub"
    assert db.queries[-1].locks == [{}]
    assert db.queries[-1].refreshed_identity is True
    assert any("tenant_id" in clause for clause in db.queries[-1].filters)
    assert db.flushes == 1 and db.commits == 0
    with pytest.raises(ValueError, match="already finalized"):
        repo.finalize("protocol-a", "another-sub")
    assert row.approved_by == "verified-sub"


def test_update_rejects_finalized_row_after_acquiring_lock():
    db = Db(SimpleNamespace(is_final=True))
    repo = repository.QualityProtocolRepositoryImpl(db, "tenant-a")
    with pytest.raises(ValueError, match="cannot be updated"):
        repo.update("protocol-a", SimpleNamespace(moisture_pct=12))
    assert db.queries[-1].locks == [{}]
    assert db.queries[-1].refreshed_identity is True
    assert db.commits == 0


def test_finalization_uses_verified_actor_and_stores_outbox_without_early_mirror(monkeypatch):
    protocol = SimpleNamespace(id="protocol-a", tenant_id="tenant-a", harvest_acceptance_id="acceptance-a", is_final=False)
    captured = {}

    class Repo:
        def __init__(self, db, tenant_id):
            assert tenant_id == "tenant-a"

        def get_by_id(self, protocol_id):
            return protocol

    class Outbox:
        def __init__(self, db, publisher):
            pass

        async def store_event(self, event, **kwargs):
            captured["event"] = event
            captured["kwargs"] = kwargs

    db = Db(None)
    monkeypatch.setattr(api, "QualityProtocolRepositoryImpl", Repo)
    monkeypatch.setattr(api, "finalize_quality_protocol", lambda repo, protocol_id, actor: (captured.update(actor=actor) or protocol))
    monkeypatch.setattr(api, "OutboxPublisher", Outbox)
    monkeypatch.setattr(api, "get_event_publisher", lambda: object())
    monkeypatch.setattr(api, "_to_out", lambda value: value)
    asyncio.run(api.finalize_protocol("protocol-a", db=db, tenant_id="tenant-a", user={"sub": "verified-sub"}))
    assert captured["actor"] == "verified-sub"
    assert captured["event"].payload["approved_by"] == "verified-sub"
    assert captured["kwargs"] == {"tenant_id": "tenant-a", "mirror_on_store": False}
    assert db.commits == 1
    with pytest.raises(HTTPException) as exc:
        asyncio.run(api.finalize_protocol("protocol-a", db=db, tenant_id="tenant-a", user={"sub": ""}))
    assert exc.value.status_code == 403
