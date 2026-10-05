"""Tenant-scoped journal identity on a private schema of the shared probe."""
import importlib.util
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from app.infrastructure.models.journal import JournalEntry
from scripts.check_journal_identity import violations

spec = importlib.util.spec_from_file_location("journal_number_migration", Path("alembic/versions/journal_number_tenant_20261005.py"))
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


@pytest.fixture(scope="module")
def store():
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Existing shared PostgreSQL required")
    url = make_url(raw)
    assert url.database == "valeo_probe" or "test" in url.database.lower()
    engine = create_engine(url)
    schema = "journalnumber_" + uuid4().hex
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            conn.execute(text(f'CREATE TABLE "{schema}".journal_entries (LIKE domain_erp.journal_entries INCLUDING ALL)'))
            # Reconstruct the old contract even after the shared probe is upgraded.
            for constraint in inspect(conn).get_unique_constraints("journal_entries", schema=schema):
                if constraint["column_names"] == ["tenant_id", "entry_number"]:
                    conn.execute(text(f'ALTER TABLE "{schema}".journal_entries DROP CONSTRAINT "{constraint["name"]}"'))
            if not any(c["column_names"] == ["entry_number"] for c in inspect(conn).get_unique_constraints("journal_entries", schema=schema)):
                conn.execute(text(f'ALTER TABLE "{schema}".journal_entries ADD CONSTRAINT old_global_number UNIQUE (entry_number)'))
            conn.execute(text(f'ALTER TABLE "{schema}".journal_entries ALTER COLUMN tenant_id DROP NOT NULL'))
            migration.apply_contract(conn, schema)
        yield engine, schema
    finally:
        assert schema.startswith("journalnumber_") and len(schema) == 46
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        engine.dispose()


def insert(conn, schema, tenant, number):
    conn.execute(text(f'''INSERT INTO "{schema}".journal_entries
        (id,tenant_id,entry_number,entry_date,posting_date,status,total_debit,total_credit)
        VALUES (:id,:t,:n,'2026-10-05','2026-10-05','draft',0,0)'''),
        {"id": str(uuid4()), "t": tenant, "n": number})


def test_orm_declares_tenant_scoped_required_identity():
    assert not JournalEntry.__table__.c.tenant_id.nullable
    assert any(c.name == 'uq_journal_tenant_number' and [col.name for col in c.columns] == ['tenant_id', 'entry_number']
               for c in JournalEntry.__table__.constraints)


def test_same_number_in_different_tenants_is_preserved(store):
    engine, schema = store
    number = uuid4().hex
    with engine.begin() as conn:
        tenants = [str(uuid4()), str(uuid4())]
        for tenant in tenants:
            insert(conn, schema, tenant, number)
        assert set(conn.execute(text(f'SELECT tenant_id FROM "{schema}".journal_entries WHERE entry_number=:n'), {"n": number}).scalars().all()) == set(tenants)


def test_same_tenant_duplicate_fails_without_losing_original(store):
    engine, schema = store
    tenant, number = str(uuid4()), uuid4().hex
    with engine.begin() as conn:
        insert(conn, schema, tenant, number)
        with pytest.raises(IntegrityError), conn.begin_nested():
            insert(conn, schema, tenant, number)
        assert conn.execute(text(f'SELECT count(*) FROM "{schema}".journal_entries WHERE tenant_id=:t'), {"t": tenant}).scalar_one() == 1


def test_missing_tenant_cannot_bypass_unique_identity(store):
    engine, schema = store
    with engine.begin() as conn:
        with pytest.raises(IntegrityError), conn.begin_nested():
            insert(conn, schema, None, uuid4().hex)


def test_reapplying_contract_does_not_recreate_global_constraint(store):
    engine, schema = store
    with engine.begin() as conn:
        migration.apply_contract(conn, schema)
        constraints = inspect(conn).get_unique_constraints('journal_entries', schema=schema)
        assert [c['column_names'] for c in constraints] == [['tenant_id', 'entry_number']]


def test_migration_rejects_unknown_tenant_without_partial_changes(store):
    engine, _ = store
    schema = 'journalnumber_' + uuid4().hex
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            conn.execute(text(f'CREATE TABLE "{schema}".journal_entries (LIKE domain_erp.journal_entries INCLUDING ALL)'))
            conn.execute(text(f'ALTER TABLE "{schema}".journal_entries ALTER COLUMN tenant_id DROP NOT NULL'))
            insert(conn, schema, None, uuid4().hex)
        with pytest.raises(IntegrityError), engine.begin() as conn:
            migration.apply_contract(conn, schema)
        with engine.connect() as conn:
            assert conn.execute(text(f'SELECT count(*) FROM "{schema}".journal_entries WHERE tenant_id IS NULL')).scalar_one() == 1
            assert next(c for c in inspect(conn).get_columns('journal_entries', schema=schema) if c['name'] == 'tenant_id')['nullable']
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))


def test_runtime_gate_accepts_migrated_database(store):
    engine, schema = store
    with engine.connect() as conn:
        assert violations(conn, schema) == []


def test_runtime_gate_rejects_old_contract(store):
    engine, _ = store
    schema = 'journalnumber_' + uuid4().hex
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA "{schema}"'))
            conn.execute(text(f'CREATE TABLE "{schema}".journal_entries (id text, tenant_id text, entry_number text NOT NULL UNIQUE)'))
            problems = violations(conn, schema)
            assert len(problems) == 3
            assert any('Global' in problem for problem in problems)
            assert any('NOT NULL' in problem for problem in problems)
            assert any('missing' in problem for problem in problems)
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
