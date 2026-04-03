from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

warehouse_transfers = importlib.import_module("app.api.v1.endpoints.warehouse_transfers")


class _RecordingQuery:
    def __init__(self, items=None, first_item=None):
        self.items = list(items or [])
        self.first_item = first_item
        self.filters: list[str] = []

    def filter(self, *clauses):
        self.filters.extend(str(clause) for clause in clauses)
        return self

    def count(self):
        return len(self.items)

    def offset(self, _value):
        return self

    def limit(self, _value):
        return self

    def all(self):
        return list(self.items)

    def first(self):
        return self.first_item


class _RecordingDb:
    def __init__(self, query_map):
        self.query_map = query_map
        self.queries = []
        self.added = []
        self.committed = False
        self.refreshed = []

    def query(self, model):
        query = self.query_map.setdefault(model, _RecordingQuery())
        self.queries.append((model, query))
        return query

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed.append(obj)


@pytest.mark.asyncio
async def test_list_transfers_filters_by_context_tenant():
    db = _RecordingDb({warehouse_transfers.WarehouseTransfer: _RecordingQuery(items=[])})

    result = await warehouse_transfers.list_transfers(
        tenant_id="tenant-a",
        skip=0,
        limit=25,
        db=db,
    )

    assert result.total == 0
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)


@pytest.mark.asyncio
async def test_get_transfer_lines_scopes_lines_by_tenant(monkeypatch):
    db = _RecordingDb({warehouse_transfers.WarehouseTransferLine: _RecordingQuery(items=[])})

    monkeypatch.setattr(
        warehouse_transfers,
        "_get_transfer_or_404",
        lambda *_args, **_kwargs: SimpleNamespace(id="tr-1"),
    )

    result = await warehouse_transfers.get_transfer_lines(
        transfer_id="tr-1",
        tenant_id="tenant-a",
        db=db,
    )

    assert result == []
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)


@pytest.mark.asyncio
async def test_create_transfer_line_uses_context_tenant(monkeypatch):
    db = _RecordingDb({})

    monkeypatch.setattr(
        warehouse_transfers,
        "_get_transfer_or_404",
        lambda *_args, **_kwargs: SimpleNamespace(id="tr-1"),
    )
    monkeypatch.setattr("app.core.uuid7.uuid7", lambda: "line-1")

    result = await warehouse_transfers.create_transfer_line(
        transfer_id="tr-1",
        payload=warehouse_transfers.TransferLineCreate(
            article_id="art-1",
            quantity=5,
            batch_number="B-1",
        ),
        tenant_id="tenant-a",
        db=db,
    )

    assert db.added[0].tenant_id == "tenant-a"
    assert result.transfer_id == "tr-1"
    assert db.committed is True
