from __future__ import annotations

import pytest

from app.api.v1.endpoints import admin_mobile


class _FakeMappings:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return _FakeMappings(self._rows)


class _CapturingDb:
    def __init__(self, rows=None):
        self.rows = list(rows or [])
        self.calls: list[tuple[str, dict]] = []

    def execute(self, statement, params=None):
        self.calls.append((str(statement), dict(params or {})))
        rows = self.rows.pop(0) if self.rows else []
        return _FakeResult(rows)


def test_list_rows_rejects_unknown_table():
    db = _CapturingDb()

    with pytest.raises(ValueError):
        admin_mobile._list_rows(
            db,
            "domain_shared.admin_stations; DROP TABLE users; --",
            "tenant-a",
            "id",
        )


def test_list_rows_falls_back_to_safe_default_order_clause():
    db = _CapturingDb(rows=[[{"id": "row-1", "tenant_id": "tenant-a"}]])

    rows = admin_mobile._list_rows(
        db,
        "domain_shared.admin_stations",
        "tenant-a",
        "id; DROP TABLE users; --",
    )

    assert rows == [{"id": "row-1", "tenant_id": "tenant-a"}]
    statement, params = db.calls[0]
    assert "ORDER BY id LIMIT :limit" in statement
    assert params["tenant_id"] == "tenant-a"
