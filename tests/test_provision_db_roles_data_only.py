from __future__ import annotations

from unittest.mock import MagicMock
import sys

import pytest
import sqlalchemy

from scripts import provision_db_roles as provision


def catalog(schemas=('domain_ops',), roles=('valeo_app',)):
    conn = MagicMock()
    conn.execute.side_effect = [ [(name,) for name in schemas], [(name,) for name in roles] ]
    return conn


def test_scoped_plan_verwendet_dieselbe_datenpolitik_wie_vollplan():
    conn = catalog()
    plan = provision.data_only_plan(conn, ['domain_ops'], ['valeo_app'])
    assert plan == provision.data_grant_statements('domain_ops', ['valeo_app'])
    full = provision.grant_statements('probe', ['domain_ops'], [], False)
    assert provision.data_grant_statements('domain_ops', provision.DATA_ROLES) == [s for s in full if 'ALL TABLES' in s or 'ALL SEQUENCES' in s or 'ALL FUNCTIONS' in s or 'USAGE ON SCHEMA "domain_ops"' in s]
    assert len(plan) == 4
    assert all('valeo_app' in s and 'valeo_agent' not in s for s in plan)
    assert not any(word in ' '.join(plan).upper() for word in ('CREATE', 'GRANT OPTION', 'ALTER ', 'PASSWORD', 'BYPASSRLS', 'DEFAULT PRIVILEGES', ' OWNER '))
    assert 'pg_catalog.pg_namespace' in str(conn.execute.call_args_list[0].args[0])
    assert 'pg_catalog.pg_roles' in str(conn.execute.call_args_list[1].args[0])


@pytest.mark.parametrize('schemas,roles', [
    ([], ['valeo_app']), ([''], ['valeo_app']), (['governance'], ['valeo_app']),
    (['information_schema'], ['valeo_app']), (['pg_temp_4'], ['valeo_app']),
    (['PG_CATALOG'], ['valeo_app']), (['domain_ops'], []), (['domain_ops'], ['valeo_owner']),
    (['domain_ops'], ['public']), (['domain_ops', 'domain_ops'], ['valeo_app']),
    (['domain_ops'], ['valeo_app', 'valeo_app']),
])
def test_ungueltige_auswahl_faellt_vor_katalogzugriff(schemas, roles):
    conn = MagicMock()
    with pytest.raises(ValueError):
        provision.data_only_plan(conn, schemas, roles)
    conn.execute.assert_not_called()


@pytest.mark.parametrize('schemas,roles,match', [
    ([], ['valeo_app'], 'Schemas nicht vorhanden'),
    (['domain_ops'], [], 'Datenrollen nicht vorhanden'),
])
def test_unbekannte_katalogobjekte_werden_abgelehnt(schemas, roles, match):
    conn = catalog(schemas, roles)
    with pytest.raises(ValueError, match=match):
        provision.data_only_plan(conn, ['domain_ops'], ['valeo_app'])
    assert conn.execute.call_count == 2


@pytest.mark.parametrize('args', [
    ['--data-only'], ['--data-only', '--schemas', 'domain_ops'],
    ['--data-only', '--data-roles', 'valeo_app'],
    ['--data-only', '--schemas', 'domain_ops', '--data-roles', 'valeo_owner'],
    ['--data-only', '--schemas', 'pg_catalog', '--data-roles', 'valeo_app'],
    ['--data-only', '--schemas', 'domain_ops', '--data-roles', 'valeo_app', '--eigentum'],
    ['--data-only', '--schemas', 'domain_ops', '--data-roles', 'valeo_app', '--waage-only'],
    ['--schemas', 'domain_ops'],
])
def test_cli_verwirft_ungueltige_auswahl_vor_verbindung(monkeypatch, args):
    create = MagicMock()
    monkeypatch.setattr(sqlalchemy, 'create_engine', create)
    monkeypatch.setattr(sys, 'argv', ['provision', '--url', 'postgresql://unused/unused', *args])
    with pytest.raises(SystemExit):
        provision.main()
    create.assert_not_called()


@pytest.mark.parametrize('flags,grant_count,commit_count', [([], 0, 0), (['--anwenden'], 4, 1), (['--anwenden', '--rollback'], 4, 0)])
def test_cli_plan_anwenden_rollback_ohne_globale_rollenaenderung(monkeypatch, flags, grant_count, commit_count):
    conn = catalog()
    checks = [[("domain_ops",)], [("valeo_app",)], []] if grant_count else []
    conn.execute.side_effect = [[("domain_ops",)], [("valeo_app",)], *([None] * grant_count), *checks]
    trans = conn.begin.return_value
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
    monkeypatch.setattr(sys, 'argv', ['provision', '--url', 'postgresql://unused/unused', '--data-only',
                                    '--schemas', 'domain_ops', '--data-roles', 'valeo_app', *flags])
    assert provision.main() == 0
    assert conn.execute.call_count == 2 + grant_count + (3 if grant_count else 0)
    assert trans.commit.call_count == commit_count
    assert trans.rollback.call_count == (1 - commit_count)
    executed = [str(call.args[0]) for call in conn.execute.call_args_list[2:2 + grant_count]]
    assert all(s.startswith('GRANT ') for s in executed)
    engine.dispose.assert_called_once()


def test_fehlende_einzelrechte_verhindern_commit_und_rollback(monkeypatch):
    conn = catalog()
    conn.execute.side_effect = [[("domain_ops",)], [("valeo_app",)], *([None] * 4),
                                [("domain_ops",)], [("valeo_app",)],
                                [("valeo_app", "domain_ops", "TABLE", "ops_waagen", "DELETE")]]
    trans = conn.begin.return_value
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    monkeypatch.setattr(sqlalchemy, 'create_engine', lambda *args, **kwargs: engine)
    monkeypatch.setattr(sys, 'argv', ['provision', '--url', 'postgresql://unused/unused', '--data-only',
                                    '--schemas', 'domain_ops', '--data-roles', 'valeo_app', '--anwenden'])
    with pytest.raises(SystemExit, match='Datenrechte unvollstaendig.*DELETE'):
        provision.main()
    trans.commit.assert_not_called()
    trans.rollback.assert_called_once()


def test_einzelrechte_werden_separat_im_aktuellen_katalog_geprueft():
    sql = provision._DATA_MISSING_SQL
    assert "('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE')" in sql
    assert "('USAGE'), ('SELECT'), ('UPDATE')" in sql
    assert 'has_schema_privilege' in sql and 'has_table_privilege' in sql
    assert 'has_sequence_privilege' in sql and 'has_function_privilege' in sql
    assert 'pg_catalog.pg_class' in sql and 'pg_catalog.pg_proc' in sql


def test_data_only_uebernimmt_pgappname(monkeypatch):
    conn = catalog()
    engine = MagicMock()
    engine.connect.return_value.__enter__.return_value = conn
    create = MagicMock(return_value=engine)
    monkeypatch.setattr(sqlalchemy, 'create_engine', create)
    monkeypatch.setenv('PGAPPNAME', 'agent:codex')
    monkeypatch.setattr(sys, 'argv', ['provision', '--url', 'postgresql://unused/unused', '--data-only',
                                    '--schemas', 'domain_ops', '--data-roles', 'valeo_app'])
    assert provision.main() == 0
    assert create.call_args.kwargs['connect_args']['application_name'] == 'agent:codex'


@pytest.mark.parametrize("roles", [[], ["other_role"], ["valeo_agent; GRANT ALL ON DATABASE postgres TO PUBLIC"]])
def test_wiederverwendbare_grant_factory_verwirft_fremde_rollen(roles):
    with pytest.raises(ValueError, match="DATA_ROLES"):
        provision.data_grant_statements("domain_docflow", roles)
