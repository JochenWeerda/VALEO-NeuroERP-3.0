"""One active bank model; development-only legacy removed without side effects."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
REVISION = ROOT / 'alembic/versions/bank_legacy_retirement_20261001.py'


def migration():
    spec = importlib.util.spec_from_file_location('bank_retirement', REVISION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_no_shadow_bank_module_or_dtos():
    assert not (ROOT / 'app/api/v1/endpoints/bank_import.py').exists()
    schemas = (ROOT / 'app/api/v1/schemas/finance_controlling_bundle_schemas.py').read_text(encoding='utf-8')
    for name in ('BankStatementImportOut', 'BankMatchOut', 'BankStatementListOut', 'BankStatementItemOut'):
        assert f'class {name}' not in schemas


def test_no_live_code_uses_retired_bank_model():
    for path in (ROOT / 'app').rglob('*.py'):
        assert 'domain_finance.bank_statement' not in path.read_text(encoding='utf-8'), path


def test_actual_router_uses_only_canonical_bank_paths():
    from app.api.v1.api import api_router

    paths = {route.path for route in api_router.routes}
    assert not any(path.startswith('/bank/') for path in paths)
    assert '/finance/bank-statements/import' in paths
    assert '/finance/payments/auto-match' in paths


@pytest.fixture(scope='module')
def retirement_db():
    raw = os.getenv('TEST_DATABASE_URL')
    if not raw:
        pytest.skip('Shared migrated PostgreSQL required')
    url = make_url(raw)
    assert url.database == 'valeo_probe', 'Only existing shared probe; never create databases'
    engine = create_engine(url)
    schema = 'bank_retirement_contract_' + uuid4().hex
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA {schema}'))
    try:
        yield engine, schema
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA {schema} CASCADE'))
        engine.dispose()


@pytest.fixture
def historical(retirement_db):
    engine, schema = retirement_db
    with engine.connect() as conn:
        transaction = conn.begin()
        conn.execute(text(f'CREATE TABLE {schema}.bank_statements (id text PRIMARY KEY)'))
        conn.execute(text(f'''CREATE TABLE {schema}.bank_statement_lines (
            id text PRIMARY KEY, statement_id text REFERENCES {schema}.bank_statements(id), amount numeric(18,4))'''))
        conn.execute(text(f"INSERT INTO {schema}.bank_statements VALUES ('legacy')"))
        conn.execute(text(f"INSERT INTO {schema}.bank_statement_lines VALUES ('old-line', 'legacy',25.1234)"))
        conn.execute(text(f'CREATE TABLE {schema}.canonical_bank_statements (id text PRIMARY KEY)'))
        conn.execute(text(f'CREATE TABLE {schema}.canonical_bank_statement_lines (id text PRIMARY KEY)'))
        conn.execute(text(f"INSERT INTO {schema}.canonical_bank_statements VALUES ('canonical')"))
        conn.execute(text(f"INSERT INTO {schema}.canonical_bank_statement_lines VALUES ('canonical-line')"))
        conn.execute(text(f'CREATE TABLE {schema}.offene_posten (id text PRIMARY KEY, offen numeric(18,4))'))
        conn.execute(text(f"INSERT INTO {schema}.offene_posten VALUES ('real-op',25.1234)"))
        try:
            yield conn, schema
        finally:
            transaction.rollback()


def retire(conn, schema):
    for statement in migration().UPGRADE_SQL:
        statement = statement.replace('domain_finance', schema)
        statement = statement.replace('domain_erp.bank_statement', f'{schema}.canonical_bank_statement')
        conn.execute(text(statement))


@pytest.mark.parametrize('populated', [True, False])
def test_legacy_removed_without_touching_canonical_payments(historical, populated):
    conn, schema = historical
    if not populated:
        conn.execute(text(f'DELETE FROM {schema}.bank_statement_lines'))
        conn.execute(text(f'DELETE FROM {schema}.bank_statements'))
    retire(conn, schema)
    for table in ('bank_statements', 'bank_statement_lines'):
        assert conn.execute(text('SELECT to_regclass(:t)'), {'t': f'{schema}.{table}'}).scalar() is None
    assert conn.execute(text(f'SELECT id FROM {schema}.canonical_bank_statements')).scalar_one() == 'canonical'
    assert conn.execute(text(f'SELECT id FROM {schema}.canonical_bank_statement_lines')).scalar_one() == 'canonical-line'
    assert str(conn.execute(text(f'SELECT offen FROM {schema}.offene_posten')).scalar_one()) == '25.1234'
    assert not conn.execute(text('SELECT tablename FROM pg_tables WHERE schemaname=:s AND tablename LIKE :p'),
                            {'s': schema, 'p': '%archive%'}).all()


@pytest.mark.parametrize('missing', ['bank_statement_lines', 'canonical_bank_statement_lines'])
def test_incomplete_schema_aborts_before_deleting(historical, missing):
    conn, schema = historical
    conn.execute(text(f'DROP TABLE {schema}.{missing}'))
    with conn.begin_nested() as savepoint:
        with pytest.raises(Exception, match='bank .*required'):
            retire(conn, schema)
        savepoint.rollback()
    assert conn.execute(text(f'SELECT id FROM {schema}.bank_statements')).scalar_one() == 'legacy'


def test_unknown_dependency_aborts_transaction_without_cascade(historical):
    conn, schema = historical
    conn.execute(text(f'CREATE TABLE {schema}.unexpected_dependency (id text REFERENCES {schema}.bank_statements(id))'))
    with conn.begin_nested() as savepoint:
        with pytest.raises(Exception, match='depend on it'):
            retire(conn, schema)
        savepoint.rollback()
    assert conn.execute(text(f'SELECT id FROM {schema}.bank_statement_lines')).scalar_one() == 'old-line'
    assert conn.execute(text(f'SELECT id FROM {schema}.bank_statements')).scalar_one() == 'legacy'


def test_downgrade_does_not_fabricate_deleted_history():
    with pytest.raises(RuntimeError, match='irreversible'):
        migration().downgrade()
