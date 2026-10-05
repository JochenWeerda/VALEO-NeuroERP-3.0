from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy.sql import visitors
from sqlalchemy.sql.elements import BindParameter

from app.api.v1.endpoints import portal_shop


pytestmark = pytest.mark.unit


class _Query:
    def __init__(self, *, all_result=None, count_result=0, scalar_result=0):
        self.all_result = [] if all_result is None else all_result
        self.count_result = count_result
        self.scalar_result = scalar_result
        self.filters = []

    def filter(self, *criteria):
        self.filters.extend(criteria)
        return self

    def group_by(self, *_args):
        return self

    def correlate(self, *_args):
        return self

    def scalar_subquery(self):
        return portal_shop.CustomerOrderItem.id

    def all(self):
        return self.all_result

    def count(self):
        return self.count_result

    def scalar(self):
        return self.scalar_result


class _Db:
    def __init__(self):
        self.queries = [_Query(), _Query(), _Query(), _Query(), _Query()]

    def query(self, *_args):
        return self.queries.pop(0)


@pytest.mark.asyncio
async def test_orders_observability_uses_configured_business_day(monkeypatch):
    local_day = date(2026, 10, 1)
    monkeypatch.setattr(portal_shop, "business_today", lambda: local_day)
    db = _Db()
    today_query = db.queries[1]

    result = await portal_shop.get_orders_observability(tenant_id="tenant-a", db=db)

    bind_values = [
        node.value
        for criterion in today_query.filters
        for node in visitors.iterate(criterion)
        if isinstance(node, BindParameter)
    ]
    assert local_day in bind_values
    assert result["today"] == 0
