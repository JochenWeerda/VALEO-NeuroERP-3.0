"""RLS-Plan P3: Pilot domain_finance + Buchungsjournal.

Gegen den frischen Pruefstand in EINER Transaktion, die immer zurueckgerollt wird: fehlende
Revisionen (inkl. rls_pilot_finance_20261026) werden eingespielt, Testdaten als Eigentuemer
angelegt, dann als ``valeo_app`` gelesen und geschrieben – so, wie die Anwendung verbindet.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

URL = os.environ.get("TEST_DATABASE_URL")
A, B = "rls-test-a", "rls-test-b"


def _load_pilot():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rls_pilot", ROOT / "alembic" / "versions" / "rls_pilot_finance_20261026.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PILOT = _load_pilot()


@pytest.fixture(scope="module")
def conn():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    import rls_inventory
    from app.core.rls_session import install_tenant_setting

    engine = install_tenant_setting(sa.create_engine(URL, pool_size=1, max_overflow=0))
    connection = engine.connect()
    tx = connection.begin()
    try:
        rls_inventory._pending_upgrade(connection)
        for schema in ("domain_erp", "domain_finance", "public"):
            connection.execute(sa.text(f"GRANT USAGE ON SCHEMA {schema} TO valeo_app"))
        for table in PILOT.PILOT_TABLES:
            if connection.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar():
                connection.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO valeo_app"))
        for tenant in (A, B):
            connection.execute(sa.text(
                "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true) "
                "ON CONFLICT (id) DO NOTHING"), {"t": tenant})
        for tenant in (A, B, "system"):
            connection.execute(sa.text(
                "INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                "VALUES (:id, :t, :n, 'Test')"), {"id": f"ks-{tenant}", "t": tenant, "n": f"N-{tenant}"})
        for tenant in (A, B):
            connection.execute(sa.text(
                "INSERT INTO domain_erp.journal_entries (id, tenant_id, entry_number, entry_date, posting_date) "
                "VALUES (:id, :t, :n, current_date, current_date)"), {"id": f"je-{tenant}", "t": tenant, "n": f"JE-{tenant}"})
        yield connection
    finally:
        tx.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def as_app(conn):
    """valeo_app im Savepoint; RESET erfolgt durch den Savepoint-Rollback."""
    nested = conn.begin_nested()
    conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
    try:
        yield conn
    finally:
        nested.rollback()


@pytest.fixture
def tenant_a():
    from app.core.tenant_context import tenant_scope
    with tenant_scope(A, "test"):
        yield


def _ids(conn, table: str) -> set[str]:
    return set(conn.execute(sa.text(f"SELECT id FROM {table} WHERE id LIKE 'ks-%' OR id LIKE 'je-%'")).scalars())


def _fails(conn, sql: str, params: dict | None = None) -> bool:
    nested = conn.begin_nested()
    try:
        conn.execute(sa.text(sql), params or {})
    except DBAPIError:
        nested.rollback()
        return True
    nested.rollback()
    return False


def test_alle_pilottabellen_haben_rls_ohne_force(conn):
    rows = conn.execute(sa.text(
        "SELECT c.oid::regclass::text, c.relrowsecurity, c.relforcerowsecurity, "
        "(SELECT count(*) FROM pg_policy p WHERE p.polrelid = c.oid AND p.polname IN ('tenant_isolation_select', 'tenant_isolation_insert', 'tenant_isolation_update', 'tenant_isolation_delete')) "
        "FROM pg_class c WHERE c.oid = ANY(:oids)"),
        {"oids": [conn.execute(sa.text("SELECT to_regclass(:t)::oid"), {"t": t}).scalar()
                  for t in PILOT.PILOT_TABLES if conn.execute(sa.text("SELECT to_regclass(:t)"), {"t": t}).scalar()]}).all()
    assert len(rows) == len(PILOT.PILOT_TABLES)
    assert all(rls and not force and policies == 4 for _, rls, force, policies in rows), rows


def test_lesen_nur_eigener_mandant_und_system(as_app, tenant_a):
    assert _ids(as_app, "domain_finance.kostenstellen") == {f"ks-{A}", "ks-system"}
    assert _ids(as_app, "domain_erp.journal_entries") == {f"je-{A}"}


def test_ohne_mandant_nichts_sichtbar_und_nichts_schreibbar(as_app):
    assert _ids(as_app, "domain_finance.kostenstellen") == set()
    assert _fails(as_app, "INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                          "VALUES ('ks-x', 'system', 'X', 'x')")


def test_schreiben_fuer_fremden_mandanten_scheitert(as_app, tenant_a):
    assert _fails(as_app, "INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                          "VALUES ('ks-x', :b, 'X', 'x')", {"b": B})
    assert _fails(as_app, "INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                          "VALUES ('ks-y', 'system', 'Y', 'y')")
    assert not _fails(as_app, "INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                              "VALUES ('ks-z', :a, 'Z', 'z')", {"a": A})


def test_fremde_zeilen_aendern_und_loeschen_trifft_nichts(as_app, tenant_a):
    assert as_app.execute(sa.text("UPDATE domain_finance.kostenstellen SET bezeichnung = 'x' WHERE tenant_id = :b"), {"b": B}).rowcount == 0
    assert as_app.execute(sa.text("DELETE FROM domain_erp.journal_entries WHERE tenant_id = :b"), {"b": B}).rowcount == 0



def test_system_zeilen_lesbar_aber_nicht_aenderbar(as_app, tenant_a):
    assert "ks-system" in _ids(as_app, "domain_finance.kostenstellen")
    assert as_app.execute(sa.text("UPDATE domain_finance.kostenstellen SET bezeichnung = 'x' WHERE id = 'ks-system'")).rowcount == 0
    assert as_app.execute(sa.text("DELETE FROM domain_finance.kostenstellen WHERE id = 'ks-system'")).rowcount == 0
    assert as_app.execute(sa.text("UPDATE domain_finance.kostenstellen SET tenant_id = :a WHERE id = 'ks-system'"), {"a": A}).rowcount == 0


def test_eigene_zeile_nicht_zu_fremdem_mandanten_verschieben(as_app, tenant_a):
    assert _fails(as_app, "UPDATE domain_finance.kostenstellen SET tenant_id = :b WHERE id = :id", {"b": B, "id": f"ks-{A}"})


def test_ende_zu_ende_ueber_den_app_mechanismus(as_app):
    from app.core.tenant_context import tenant_scope
    with tenant_scope(B, "test"):
        assert _ids(as_app, "domain_finance.kostenstellen") == {f"ks-{B}", "ks-system"}
    with tenant_scope(A, "test"):
        assert _ids(as_app, "domain_erp.journal_entries") == {f"je-{A}"}
