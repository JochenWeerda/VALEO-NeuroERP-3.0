"""Gemeinsame Pruefhilfe der RLS-Domain-Slices (kein Testmodul).

Alles laeuft auf dem frischen Pruefstand (TEST_DATABASE_URL) in einer Transaktion, die am
Ende zurueckgerollt wird. Fehlende Revisionen spielt rls_inventory._pending_upgrade ein.
Die Engine ist wie die der Anwendung mit install_tenant_setting ausgestattet: der Mandant
kommt aus tenant_scope, nicht aus SQL. Testdaten legt der Eigentuemer an (ohne FORCE nicht
von RLS betroffen), geprueft wird danach als valeo_app.
"""

from __future__ import annotations

import os
import re
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest
import sqlalchemy as sa

from app.core.rls_session import install_tenant_setting
from app.core.tenant_context import cross_tenant_scope, tenant_scope

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

URL = os.environ.get("TEST_DATABASE_URL")
A, B, SYSTEM = "rls-domain-a", "rls-domain-b", "system"
APP_ROLES = ("valeo_app", "valeo_system")


@contextmanager
def probe(tables: tuple[str, ...]):
    """Connection with all migrations applied (rolled back at the end) and grants on ``tables``."""
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    import rls_inventory

    engine = install_tenant_setting(sa.create_engine(URL))
    conn = engine.connect()
    tx = conn.begin()
    try:
        rls_inventory._pending_upgrade(conn)
        for role in APP_ROLES:
            for schema in sorted({t.split(".")[0] for t in tables}):
                conn.execute(sa.text(f"GRANT USAGE ON SCHEMA {schema} TO {role}"))
            present = [t for t in tables if exists(conn, t)]
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {', '.join(present)} TO {role}"))
        yield conn
    finally:
        tx.rollback()
        conn.close()
        engine.dispose()


def as_app(conn) -> None:
    conn.execute(sa.text("SET LOCAL ROLE valeo_app"))


def exists(conn, table: str) -> bool:
    return conn.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


# --- Zeilen ---------------------------------------------------------------------------------

COLUMNS_SQL = """
SELECT a.attname, format_type(a.atttypid, a.atttypmod), t.typtype, a.atttypid,
       a.attnotnull, a.atthasdef OR a.attidentity <> '' OR a.attgenerated <> ''
  FROM pg_attribute a JOIN pg_type t ON t.oid = a.atttypid
 WHERE a.attrelid = to_regclass(:t) AND a.attnum > 0 AND NOT a.attisdropped
 ORDER BY a.attnum
"""


def _value(conn, type_name: str, typtype: str, typid: int):
    if typtype == "e":
        return conn.execute(sa.text(
            "SELECT enumlabel FROM pg_enum WHERE enumtypid = :o ORDER BY enumsortorder LIMIT 1"), {"o": typid}).scalar()
    if type_name.endswith("[]"):
        return "{}"
    if type_name == "uuid":
        return str(uuid.uuid4())
    if type_name.startswith(("character", "text", "citext")):
        size = type_name[type_name.find("(") + 1:-1] if "(" in type_name else None
        value = f"rls-{uuid.uuid4().hex[:12]}"
        return value[: int(size)] if size and size.isdigit() else value
    if type_name in ("integer", "bigint", "smallint", "real", "double precision") or type_name.startswith("numeric"):
        return 1
    if type_name == "boolean":
        return False
    if type_name == "date":
        return "2026-01-01"
    if type_name.startswith("timestamp") or type_name.startswith("time"):
        return "2026-01-01 00:00:00"
    if type_name in ("json", "jsonb"):
        return "{}"
    raise AssertionError(f"kein Testwert fuer Typ {type_name}")


FKS_SQL = """
SELECT k.conname, array_agg(a.attname ORDER BY u.ord), k.confrelid::regclass::text,
       array_agg(af.attname ORDER BY u.ord)
  FROM pg_constraint k
  CROSS JOIN LATERAL unnest(k.conkey, k.confkey) WITH ORDINALITY AS u(ck, fk, ord)
  JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = u.ck
  JOIN pg_attribute af ON af.attrelid = k.confrelid AND af.attnum = u.fk
 WHERE k.contype = 'f' AND k.conrelid = to_regclass(:t)
 GROUP BY k.conname, k.confrelid
"""
CHECK_CHOICE = re.compile(r"\(\(?(\w+)\)?(?:::\w+(?: \w+)?)? = ANY \(\(?ARRAY\['([^']*)'")
UNIQUE_COLUMNS_SQL = """
SELECT DISTINCT a.attname FROM pg_index i
  JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
 WHERE i.indrelid = to_regclass(:t) AND i.indisunique
"""


def _qualified(name: str) -> str:
    return name if "." in name else f"public.{name}"


def seed_row(conn, table: str, tenant: str | None, _depth: int = 0, _parents: bool = True, **values) -> dict:
    """Insert a row with every required column filled, required parents created on the way.

    Parents of NOT NULL foreign keys are seeded for the same tenant; valid values come from
    CHECK constraints of the form ``col = ANY (ARRAY['a', ...])``. Returns the inserted row.
    """
    if _depth > 5:
        raise AssertionError(f"Elternkette zu tief bei {table}")
    columns = list(conn.execute(sa.text(COLUMNS_SQL), {"t": table}))
    names = {c[0] for c in columns}
    required = {c[0] for c in columns if c[4] and not c[5]}
    row = dict(values)
    if tenant is not None and "tenant_id" in names:
        row.setdefault("tenant_id", tenant)
    for _name, cols, parent, pcols in conn.execute(sa.text(FKS_SQL), {"t": table}):
        parent = _qualified(parent)
        if parent == "domain_shared.tenants":
            # Mandanten registriert nur der Eigentuemer (Fixtures); valeo_app darf das nicht.
            if row.get(cols[0]) is not None and conn.execute(sa.text("SELECT current_user")).scalar() != "valeo_app":
                ensure_tenants(conn, row[cols[0]])
            continue
        missing = [c for c in cols if c not in row and c in required]
        if not _parents or not missing or parent == _qualified(table):
            continue
        parent_cols = {c[0] for c in conn.execute(sa.text(COLUMNS_SQL), {"t": parent})}
        parent_tenant = row.get("tenant_id", tenant) if "tenant_id" in parent_cols else None
        given = {pc: row[c] for c, pc in zip(cols, pcols) if c in row}
        parent_row = seed_row(conn, parent, parent_tenant, _depth + 1, **given)
        for c, pc in zip(cols, pcols):
            row.setdefault(c, parent_row[pc])
    checks = conn.execute(sa.text(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = to_regclass(:t) AND contype = 'c'"),
        {"t": table}).scalars().all()
    for definition in checks:
        for column, choice in CHECK_CHOICE.findall(definition):
            if column in required and column not in row:
                row[column] = choice
    unique = set(conn.execute(sa.text(UNIQUE_COLUMNS_SQL), {"t": table}).scalars())
    for name, type_name, typtype, typid, not_null, has_default in columns:
        if name in row or not not_null or has_default:
            continue
        value = _value(conn, type_name, typtype, typid)
        if isinstance(value, int) and not isinstance(value, bool) and name in unique:
            value = uuid.uuid4().int % 900_000_000 + 1000
        row[name] = value
    cols = ", ".join(row)
    placeholders = ", ".join(f":{c}" for c in row)
    return dict(conn.execute(sa.text(f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) RETURNING *"),
                             row).mappings().one())


def primary_key(conn, table: str) -> str:
    return conn.execute(sa.text(
        "SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid "
        "AND a.attnum = i.indkey[0] WHERE i.indrelid = to_regclass(:t) AND i.indisprimary"), {"t": table}).scalar()


def insert_row(conn, table: str, tenant: str | None, key: str = "id", _parents: bool = True, **values) -> str:
    """Insert a row with every required column filled (parents included); returns its key."""
    row = seed_row(conn, table, tenant, _parents=_parents, **values)
    if key not in row:
        key = primary_key(conn, table)
    return str(row[key])


def ensure_tenants(conn, *tenants: str) -> None:
    """Register test tenants where a table references domain_shared.tenants (FK checks bypass RLS)."""
    for tenant in tenants:
        if not keys(conn, "domain_shared.tenants", "id", "id = :t", {"t": tenant}):
            insert_row(conn, "domain_shared.tenants", None, id=tenant)


# --- Pruefungen ------------------------------------------------------------------------------

def keys(conn, table: str, key: str = "id", where: str = "TRUE", params=None) -> set[str]:
    return {str(r[0]) for r in conn.execute(sa.text(f"SELECT {key} FROM {table} WHERE {where}"), params or {})}


def affected(conn, sql: str, params=None) -> int:
    return conn.execute(sa.text(sql), params or {}).rowcount


def rejected(conn, sql: str, params=None) -> str:
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text(sql), params or {})
    except sa.exc.DBAPIError as exc:
        savepoint.rollback()
        return str(exc.orig).splitlines()[0]
    savepoint.rollback()
    pytest.fail(f"nicht abgewiesen: {sql}")


def as_owner(conn, sql: str, params=None):
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        return conn.execute(sa.text(sql), params or {}).all()
    finally:
        savepoint.rollback()  # stellt auch SET LOCAL ROLE valeo_app wieder her


def assert_tenant_isolation(conn, table: str, own: str, foreign: str, shared: str | None,
                            key: str = "id", new_row=None) -> None:
    """Die Abnahmefaelle fuer eine Tabelle ohne system-Lesefreigabe.

    own/foreign/shared: Schluessel von Zeilen der Mandanten A, B und 'system'.
    new_row: callable(tenant) -> Schluessel einer neu angelegten Zeile (als valeo_app).
    """
    by_key = f"{key} = :k"
    with tenant_scope(A, "test"):
        assert keys(conn, table, key) >= {own}
        assert not keys(conn, table, key) & {foreign, shared}
        # eigener Mandant: anlegen, aendern, loeschen
        created = (new_row or (lambda t: insert_row(conn, table, t, key)))(A)
        assert affected(conn, f"UPDATE {table} SET tenant_id = tenant_id WHERE {by_key}", {"k": created}) == 1
        assert affected(conn, f"DELETE FROM {table} WHERE {by_key}", {"k": created}) == 1
        # fremder Mandant und system: nicht sichtbar, nicht aenderbar, nicht loeschbar
        for other in filter(None, (foreign, shared)):
            assert affected(conn, f"UPDATE {table} SET tenant_id = tenant_id WHERE {by_key}", {"k": other}) == 0
            assert affected(conn, f"UPDATE {table} SET tenant_id = :t WHERE {by_key}", {"k": other, "t": A}) == 0
            assert affected(conn, f"DELETE FROM {table} WHERE {by_key}", {"k": other}) == 0
        # anlegen fuer fremden Mandanten oder system
        for tenant in (B, SYSTEM):
            assert "row-level security" in rejected_insert(conn, table, tenant, key)
        # tenant_id-Wechsel der eigenen Zeile
        for tenant in (B, SYSTEM):
            assert "row-level security" in rejected(
                conn, f"UPDATE {table} SET tenant_id = :t WHERE {by_key}", {"k": own, "t": tenant})
    # ohne Kontext: nichts sichtbar, nichts schreibbar
    assert keys(conn, table, key) == set()
    assert affected(conn, f"DELETE FROM {table}") == 0
    rejected_insert(conn, table, A, key)
    with cross_tenant_scope("test: ohne Systemverbindung"):
        assert keys(conn, table, key) == set()
    # der Eigentuemer sieht alles unveraendert
    expected = {own, foreign} | ({shared} if shared else set())
    assert {str(r[0]) for r in as_owner(conn, f"SELECT {key} FROM {table} WHERE {key}::text = ANY(:ks)",
                                         {"ks": list(expected)})} == expected


def rejected_insert(conn, table: str, tenant: str, key: str = "id") -> str:
    return rejected_insert_with(conn, table, tenant, key)


def rejected_insert_with(conn, table: str, tenant: str, key: str = "id", **values) -> str:
    savepoint = conn.begin_nested()
    try:
        # Ohne Elternsaetze: RLS prueft vor den Fremdschluesseln, Eltern anlegen waere hier selbst gesperrt.
        insert_row(conn, table, tenant, key, _parents=False, **values)
    except sa.exc.DBAPIError as exc:
        savepoint.rollback()
        return str(exc.orig).splitlines()[0]
    savepoint.rollback()
    pytest.fail(f"{table}: Anlage fuer {tenant} {values} nicht abgewiesen")


def as_owner_rejected(conn, sql: str, params=None) -> str:
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        conn.execute(sa.text(sql), params or {})
    except sa.exc.DBAPIError as exc:
        return str(exc.orig).splitlines()[0]
    finally:
        savepoint.rollback()
    pytest.fail(f"nicht abgewiesen (Eigentuemer): {sql}")


def assert_context_switch_and_savepoint(conn, table: str, own_a: str, own_b: str, key: str = "id") -> None:
    with tenant_scope(A, "test"):
        assert own_a in keys(conn, table, key) and own_b not in keys(conn, table, key)
        with tenant_scope(B, "test"):
            assert own_b in keys(conn, table, key) and own_a not in keys(conn, table, key)
            inner = conn.begin_nested()
            with tenant_scope(A, "test"):
                assert own_a in keys(conn, table, key)  # setzt A innerhalb des Savepoints
            inner.rollback()  # Datenbank faellt auf B zurueck, der Cache wird verworfen
            assert own_b in keys(conn, table, key) and own_a not in keys(conn, table, key)
        assert own_a in keys(conn, table, key) and own_b not in keys(conn, table, key)
    assert keys(conn, table, key) == set()


def assert_background_needs_explicit_context(conn, table: str, own_a: str, own_b: str, key: str = "id") -> None:
    seen = {}
    for tenant in (A, B):
        with tenant_scope(tenant, "test: Job je Mandant"):
            seen[tenant] = keys(conn, table, key) & {own_a, own_b}
    assert seen == {A: {own_a}, B: {own_b}}
    with cross_tenant_scope("test: Auswertung ueber alle Mandanten"):
        assert keys(conn, table, key) == set()  # valeo_app ohne BYPASSRLS
        savepoint = conn.begin_nested()
        try:
            conn.execute(sa.text("SET LOCAL ROLE valeo_system"))  # wie system_session()
            assert {own_a, own_b} <= keys(conn, table, key)
        finally:
            savepoint.rollback()


def assert_pool_reuse_keeps_no_tenant() -> None:
    """Echte Commits auf einer gepoolten Verbindung; temporaere Tabelle derselben Policy-Form."""
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    own = "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')"
    engine = install_tenant_setting(sa.create_engine(URL, pool_size=1, max_overflow=0))
    try:
        with engine.connect() as conn:
            pid = conn.execute(sa.text("SELECT pg_backend_pid()")).scalar()
            conn.execute(sa.text("CREATE TEMP TABLE rls_pool_probe (tenant_id text NOT NULL)"))
            conn.execute(sa.text("ALTER TABLE rls_pool_probe ENABLE ROW LEVEL SECURITY"))
            conn.execute(sa.text(f"CREATE POLICY tenant_isolation_select ON rls_pool_probe FOR SELECT USING ({own})"))
            conn.execute(sa.text(f"CREATE POLICY tenant_isolation_insert ON rls_pool_probe FOR INSERT WITH CHECK ({own})"))
            conn.execute(sa.text("GRANT SELECT, INSERT ON rls_pool_probe TO valeo_app"))
            conn.commit()

        def count(tenant):
            with engine.connect() as conn:
                assert conn.execute(sa.text("SELECT pg_backend_pid()")).scalar() == pid
                as_app(conn)
                if tenant is None:
                    result = conn.execute(sa.text("SELECT count(*) FROM rls_pool_probe")).scalar()
                else:
                    with tenant_scope(tenant, "test"):
                        result = conn.execute(sa.text("SELECT count(*) FROM rls_pool_probe")).scalar()
                conn.commit()
                return result

        with engine.connect() as conn, tenant_scope(A, "test"):
            as_app(conn)
            conn.execute(sa.text("INSERT INTO rls_pool_probe VALUES (:t)"), {"t": A})
            conn.commit()
        assert (count(None), count(B), count(A), count(None)) == (0, 0, 1, 0)
    finally:
        engine.dispose()  # schliesst die Sitzung, die temporaere Tabelle verschwindet


def shape(conn, table: str) -> tuple[str, str]:
    import rls_policy_shape

    # regclass nennt Tabellen im Suchpfad (public) ohne Schema.
    return rls_policy_shape.shapes(conn)[table.removeprefix("public.")]
