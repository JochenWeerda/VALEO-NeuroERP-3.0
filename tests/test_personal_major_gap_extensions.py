from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from app.api.v1.endpoints import personal


class _Result:
    def __init__(self, rows=None, row=None):
        self._rows = rows or []
        self._row = row

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._row


def test_org_subtree_uses_actual_root_parent():
    rows = [
        {"id": "TEAM-1", "parent_id": "DEPT-1", "name": "Innendienst"},
        {"id": "TEAM-1-A", "parent_id": "TEAM-1", "name": "Auftrag"},
    ]

    tree = personal._build_org_tree(rows, rows[0]["parent_id"])

    assert tree[0]["id"] == "TEAM-1"
    assert tree[0]["children"][0]["id"] == "TEAM-1-A"


def test_time_account_uses_canonical_time_entries_columns():
    db = MagicMock()
    executed_sql: list[str] = []

    def execute(statement, params=None):
        sql = str(statement)
        executed_sql.append(sql)
        if "FROM domain_hr.time_entries" in sql:
            return _Result(rows=[("2026-05", 16.0, 2)])
        if "FROM domain_hr.time_account_adjustments" in sql:
            return _Result(row=(1.5,))
        if "FROM domain_hr.schichten" in sql:
            return _Result(row=(15.0,))
        return _Result()

    db.execute.side_effect = execute

    result = asyncio.run(
        personal.get_time_account(employee_ref="EMP-1", tenant_id="tenant-1", db=db)
    )

    time_sql = next(sql for sql in executed_sql if "FROM domain_hr.time_entries" in sql)
    assert "entry_date" in time_sql
    assert "hours" in time_sql
    assert "employee_ref" in time_sql
    assert "datum" not in time_sql
    assert "stunden" not in time_sql
    assert "mitarbeiter" not in time_sql
    assert result["saldo_hours"] == 2.5
