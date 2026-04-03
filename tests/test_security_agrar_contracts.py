from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

agrar_contracts = importlib.import_module("app.api.v1.endpoints.agrar_contracts")


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

    def order_by(self, *_args, **_kwargs):
        return self

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
async def test_list_agrar_contracts_filters_by_context_tenant():
    db = _RecordingDb({agrar_contracts.AgrarContract: _RecordingQuery(items=[])})

    result = await agrar_contracts.list_agrar_contracts(
        status=None,
        pricing_model=None,
        skip=0,
        limit=25,
        db=db,
        tenant_id="tenant-a",
    )

    assert result.total == 0
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)


def test_get_contract_helper_scopes_lookup_by_tenant():
    db = _RecordingDb({agrar_contracts.AgrarContract: _RecordingQuery(first_item=None)})

    with pytest.raises(agrar_contracts.HTTPException) as exc:
        agrar_contracts._get_contract_or_404(db, "contract-1", "tenant-a")

    assert exc.value.status_code == 404
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)


@pytest.mark.asyncio
async def test_list_contract_allocations_filters_allocation_by_tenant(monkeypatch):
    contract = SimpleNamespace(id="contract-1")
    db = _RecordingDb({agrar_contracts.AgrarContractAllocation: _RecordingQuery(items=[])})

    monkeypatch.setattr(
        agrar_contracts,
        "_get_contract_or_404",
        lambda *_args, **_kwargs: contract,
    )

    result = await agrar_contracts.list_contract_allocations(
        contract_id="contract-1",
        tenant_id="tenant-a",
        db=db,
    )

    assert result == []
    _, query = db.queries[0]
    assert any("tenant_id" in clause for clause in query.filters)
