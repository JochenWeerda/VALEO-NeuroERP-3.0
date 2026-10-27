"""Exercise the actual migration policy as valeo_app, with only rolled-back own data.

No migration replay, database reset or new database. Both migration implementations and
both tenant column types must preserve the distinction between visible and writable rows.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import sqlalchemy as sa

from app.core.rls_session import install_tenant_setting
from app.core.tenant_context import tenant_scope

ROOT = Path(__file__).resolve().parents[1]
A = "2d33acc9-34cf-4af2-8aad-37b63f1bed7a"
B = "da396efb-dc34-40cb-b4e6-3716d281fa54"
TABLE = "public.codex_rls_shared_guard_probe"
pytestmark = pytest.mark.integration


@pytest.fixture(params=[(phase, kind) for phase in ("pilot_finance", "rollout", "system_role", "verified_agrar") for kind in ("text", "uuid")])
def policy_db(request, monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail("TEST_DATABASE_URL must identify the shared PostgreSQL test stand")
    assert sa.engine.make_url(url).get_backend_name() == "postgresql"
    phase, kind = request.param
    date = "20261027" if phase == "verified_agrar" else "20261026"
    path = ROOT / "alembic/versions" / f"rls_{phase}_{date}.py"
    spec = importlib.util.spec_from_file_location(f"policy_{phase}", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = install_tenant_setting(sa.create_engine(url, pool_size=1, max_overflow=0))
    try:
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                assert conn.scalar(sa.text("SELECT to_regclass(:t)"), {"t": TABLE}) is None, "Own probe table already exists; do not delete it"
                assert conn.scalar(sa.text("SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='valeo_app')"))
                if conn.scalar(sa.text("SELECT to_regprocedure('public.rls_current_tenant()')")) is None:
                    conn.execute(sa.text("CREATE FUNCTION public.rls_current_tenant() RETURNS text LANGUAGE sql STABLE AS $$ SELECT NULLIF(current_setting('app.tenant_id', true), '') $$"))
                conn.execute(sa.text(f"CREATE TABLE {TABLE} (id text PRIMARY KEY, tenant_id {kind} NOT NULL, label text NOT NULL)"))
                conn.execute(sa.text(f"INSERT INTO {TABLE} VALUES ('own', :a, 'own'), ('foreign', :b, 'foreign')"), {"a": A, "b": B})
                if kind == "text":
                    conn.execute(sa.text(f"INSERT INTO {TABLE} VALUES ('shared', 'system', 'shared')"))
                conn.execute(sa.text(f"CREATE POLICY tenant_isolation ON {TABLE} USING (true) WITH CHECK (true)"))
                monkeypatch.setattr(migration, "op", SimpleNamespace(execute=lambda sql: conn.execute(sa.text(sql))))
                assert migration.enable_tenant_isolation(conn, TABLE)
                assert migration.enable_tenant_isolation(conn, TABLE), "Policy installation must be repeatable"
                assert dict(conn.execute(sa.text("SELECT polname, polcmd FROM pg_policy WHERE polrelid=to_regclass(:t)"), {"t": TABLE}).all()) == {
                    f"tenant_isolation_{name}": command
                    for name, command in (("select", "r"), ("insert", "a"), ("update", "w"), ("delete", "d"))
                }
                conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {TABLE} TO valeo_app"))
                conn.execute(sa.text("GRANT EXECUTE ON FUNCTION public.rls_current_tenant() TO valeo_app"))
                conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
                role = conn.execute(sa.text("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname=current_user")).one()
                assert tuple(role) == ("valeo_app", False, False)
                conn.info["shared_reference_read"] = phase != "verified_agrar"
                with tenant_scope(A, "RLS shared-row regression"):
                    yield conn, kind
            finally:
                transaction.rollback()
    finally:
        engine.dispose()


def reject(conn, statement, parameters):
    with pytest.raises(sa.exc.DBAPIError), conn.begin_nested():
        conn.execute(sa.text(statement), parameters)


def test_reads_preserve_tenant_and_shared_visibility(policy_db):
    conn, kind = policy_db
    shared_read = kind == "text" and conn.info["shared_reference_read"]
    assert set(conn.scalars(sa.text(f"SELECT id FROM {TABLE}"))) == ({"own", "shared"} if shared_read else {"own"})


@pytest.mark.parametrize("mutation", ("delete", "edit", "takeover"))
def test_shared_rows_cannot_be_deleted_edited_or_taken_over(policy_db, mutation):
    conn, _kind = policy_db
    sql, params = {
        "delete": (f"DELETE FROM {TABLE} WHERE id='shared'", {}),
        "edit": (f"UPDATE {TABLE} SET label='changed' WHERE id='shared'", {}),
        "takeover": (f"UPDATE {TABLE} SET tenant_id=:a WHERE id='shared'", {"a": A}),
    }[mutation]
    assert conn.execute(sa.text(sql), params).rowcount == 0
    assert conn.scalar(sa.text(f"SELECT label FROM {TABLE} WHERE id='shared'")) in ("shared", None)


def test_foreign_rows_cannot_be_mutated_or_inserted(policy_db):
    conn, _kind = policy_db
    assert conn.execute(sa.text(f"DELETE FROM {TABLE} WHERE id='foreign'")).rowcount == 0
    assert conn.execute(sa.text(f"UPDATE {TABLE} SET tenant_id=:a WHERE id='foreign'"), {"a": A}).rowcount == 0
    reject(conn, f"INSERT INTO {TABLE} VALUES ('foreign-new', :b, 'x')", {"b": B})


def test_own_rows_remain_writable_but_cannot_change_owner(policy_db):
    conn, kind = policy_db
    assert conn.execute(sa.text(f"UPDATE {TABLE} SET label='edited' WHERE id='own'")).rowcount == 1
    reject(conn, f"UPDATE {TABLE} SET tenant_id=:b WHERE id='own'", {"b": B})
    if kind == "text":
        reject(conn, f"UPDATE {TABLE} SET tenant_id='system' WHERE id='own'", {})
        reject(conn, f"INSERT INTO {TABLE} VALUES ('shared-new', 'system', 'x')", {})
    conn.execute(sa.text(f"INSERT INTO {TABLE} VALUES ('own-new', :a, 'x')"), {"a": A})
    assert conn.execute(sa.text(f"DELETE FROM {TABLE} WHERE id='own-new'")).rowcount == 1


def test_missing_context_cannot_see_or_write_rows(policy_db):
    from app.core.tenant_context import cross_tenant_scope
    conn, _kind = policy_db
    with cross_tenant_scope("RLS negative no-tenant check on application role"):
        assert list(conn.scalars(sa.text(f"SELECT id FROM {TABLE}"))) == []
        assert conn.execute(sa.text(f"DELETE FROM {TABLE}")).rowcount == 0
        reject(conn, f"INSERT INTO {TABLE} VALUES ('no-context', :a, 'x')", {"a": A})
    assert conn.scalar(sa.text(f"SELECT label FROM {TABLE} WHERE id='own'")) == "own"
