"""Read-only regression for real migrated PostgreSQL composite foreign keys."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text

from scripts.generate_table_catalog import _FK_SQL


@pytest.fixture(scope="module")
def physical_foreign_keys():
    url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    assert url, "Use the existing configured test database, never create a new one."
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            yield [tuple(row) for row in connection.execute(text(_FK_SQL))]
    finally:
        engine.dispose()


@pytest.mark.needs_live_db
@pytest.mark.parametrize(
    ("schema", "child", "parent", "source_id", "target_id"),
    [
        ("domain_erp", "bank_accounts", "chart_of_accounts", "gl_account_id", "id"),
        ("domain_hr", "bewerbung_einwilligungen", "bewerbung_einwilligungserklaerungen", "erklaerung_id", "id"),
        ("domain_hr", "hrm_operations_gate_evidence", "hrm_operations_gates", "gate_id", "gate_id"),
        ("domain_hr", "hrm_operations_gate_probes", "hrm_operations_gates", "gate_id", "gate_id"),
    ],
)
def test_composite_fk_preserves_actual_column_pairs(
    physical_foreign_keys, schema, child, parent, source_id, target_id
):
    pairs = [
        (column, foreign_column)
        for source_schema, table, column, foreign_schema, foreign_table, foreign_column
        in physical_foreign_keys
        if (source_schema, table, foreign_schema, foreign_table) == (schema, child, schema, parent)
    ]
    assert sorted(pairs) == sorted([(source_id, target_id), ("tenant_id", "tenant_id")])
