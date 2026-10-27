"""RLS-Domain pricing: Preislisten und ihre Positionen, geprueft als valeo_app.

Alles laeuft auf dem frischen Pruefstand (TEST_DATABASE_URL) in einer Transaktion, die am
Ende zurueckgerollt wird; fehlende Revisionen (auch rls_domain_pricing_20261027) spielt
rls_inventory._pending_upgrade dort ein. Die Engine ist wie die der Anwendung mit
install_tenant_setting ausgestattet: der Mandant kommt aus tenant_scope, nicht aus SQL.

Nur der Pool-Test braucht echte Commits; er nutzt eine temporaere Tabelle derselben
Policy-Form, die mit der Sitzung verschwindet.
"""

from __future__ import annotations

import ast
import asyncio
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.rls_session import install_tenant_setting
from app.core.tenant_context import cross_tenant_scope, tenant_scope

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

URL = os.environ.get("TEST_DATABASE_URL")
A, B, SYSTEM = "rls-pricing-a", "rls-pricing-b", "system"
LISTS, ITEMS = "domain_pricing.price_lists", "domain_pricing.price_list_items"
ENDPOINT = ROOT / "app" / "api" / "v1" / "endpoints" / "price_lists.py"


# --- Vertrag am Quelltext (ohne Datenbank) -------------------------------------------------

@pytest.mark.unit
def test_endpunkte_nehmen_den_mandanten_nur_aus_dem_token():
    source = ENDPOINT.read_text(encoding="utf-8")
    assert "DEFAULT_TENANT" not in source
    assert not re.search(r"Query\([^)]*\)", source), "Mandant nie aus einem Query-Parameter"
    assert "payload.tenant_id" not in source
    routes = [
        node for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.AsyncFunctionDef)
        and any(ast.unparse(d).startswith("router.") for d in node.decorator_list)
    ]
    assert len(routes) == 5
    for route in routes:
        defaults = [ast.unparse(d) for d in route.args.defaults]
        assert "Depends(get_tenant_id)" in defaults, f"{route.name} ohne tokengebundenen Mandanten"


@pytest.mark.unit
def test_jeder_lese_und_schreibweg_filtert_nach_mandant():
    source = ENDPOINT.read_text(encoding="utf-8")
    statements = re.findall(r"(?:SELECT|UPDATE|DELETE)[^\"]*?domain_pricing\.[a-z_]+[^\"]*", source)
    assert statements
    for sql in statements:
        assert "tenant_id = :tid" in sql or "tenant_id = pl.tenant_id" in sql, sql
    for insert in re.findall(r"INSERT INTO domain_pricing\.[a-z_]+\s*\([^)]*\)", source):
        assert "tenant_id" in insert, insert


# --- Pruefstand -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def probe():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    import rls_inventory

    engine = install_tenant_setting(sa.create_engine(URL))
    conn = engine.connect()
    tx = conn.begin()
    try:
        rls_inventory._pending_upgrade(conn)
        for role in ("valeo_app", "valeo_system"):
            conn.execute(sa.text(f"GRANT USAGE ON SCHEMA domain_pricing TO {role}"))
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {LISTS}, {ITEMS} TO {role}"))
        # Testdaten als Eigentuemer (ohne FORCE nicht von RLS betroffen).
        for list_id, tenant in (("rlsp-a1", A), ("rlsp-b1", B), ("rlsp-s1", SYSTEM)):
            conn.execute(sa.text(
                f"INSERT INTO {LISTS} (id, tenant_id, name, currency, is_active) "
                "VALUES (:id, :t, :n, 'EUR', TRUE)"), {"id": list_id, "t": tenant, "n": f"Liste {tenant}"})
            conn.execute(sa.text(
                f"INSERT INTO {ITEMS} (id, price_list_id, tenant_id, article_id, article_number, "
                "unit_price, min_quantity, discount_percent) "
                "VALUES (:id, :pl, :t, 'rlsp-art', 'RLSP-1', :p, 0, 0)"),
                {"id": list_id + "-i", "pl": list_id, "t": tenant, "p": {A: 10, B: 20, SYSTEM: 30}[tenant]})
        conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
        yield conn
    finally:
        tx.rollback()
        conn.close()
        engine.dispose()


@pytest.fixture
def db(probe):
    savepoint = probe.begin_nested()
    yield probe
    if savepoint.is_active:
        savepoint.rollback()


def _ids(conn, table, where="TRUE", params=None):
    return {r[0] for r in conn.execute(sa.text(f"SELECT id FROM {table} WHERE {where}"), params or {})}


def _count(conn, sql, params=None) -> int:
    return conn.execute(sa.text(sql), params or {}).rowcount


def _rejected(conn, sql, params=None) -> str:
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text(sql), params or {})
    except sa.exc.DBAPIError as exc:
        savepoint.rollback()
        return str(exc.orig).splitlines()[0]
    savepoint.rollback()
    pytest.fail(f"nicht abgewiesen: {sql}")


def _as_owner(conn, sql, params=None):
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        return conn.execute(sa.text(sql), params or {}).all()
    finally:
        savepoint.rollback()  # stellt auch SET LOCAL ROLE valeo_app wieder her


@pytest.mark.integration
def test_migration_und_policy_form(db):
    import rls_policy_shape

    assert db.execute(sa.text("SELECT current_user")).scalar() == "valeo_app"
    shapes = rls_policy_shape.shapes(db)
    assert shapes[LISTS] == ("getrennt", "")
    assert shapes[ITEMS] == ("getrennt", "")
    nullable = db.execute(sa.text(
        "SELECT is_nullable FROM information_schema.columns WHERE table_schema = 'domain_pricing' "
        "AND table_name = 'price_list_items' AND column_name = 'tenant_id'")).scalar()
    assert nullable == "NO"


@pytest.mark.integration
def test_eigener_mandant_lesen_anlegen_aendern_loeschen(db):
    with tenant_scope(A, "test"):
        assert _ids(db, LISTS) == {"rlsp-a1"}
        assert _ids(db, ITEMS) == {"rlsp-a1-i"}
        db.execute(sa.text(f"INSERT INTO {LISTS} (id, tenant_id, name, currency, is_active) "
                           "VALUES ('rlsp-a2', :t, 'Neu', 'EUR', TRUE)"), {"t": A})
        # Position ohne tenant_id: der Mandant kommt aus dem Kontext und passt zum Kopf.
        db.execute(sa.text(f"INSERT INTO {ITEMS} (id, price_list_id, article_id, unit_price, "
                           "min_quantity, discount_percent) VALUES ('rlsp-a2-i', 'rlsp-a2', 'x', 1, 0, 0)"))
        assert db.execute(sa.text(f"SELECT tenant_id FROM {ITEMS} WHERE id = 'rlsp-a2-i'")).scalar() == A
        assert _count(db, f"UPDATE {LISTS} SET name = 'Geaendert' WHERE id = 'rlsp-a2'") == 1
        assert _count(db, f"UPDATE {ITEMS} SET unit_price = 2 WHERE id = 'rlsp-a2-i'") == 1
        assert _count(db, f"DELETE FROM {ITEMS} WHERE id = 'rlsp-a2-i'") == 1
        assert _count(db, f"DELETE FROM {LISTS} WHERE id = 'rlsp-a2'") == 1


@pytest.mark.integration
def test_fremder_mandant_select_insert_update_delete_gesperrt(db):
    with tenant_scope(A, "test"):
        assert _ids(db, LISTS, "tenant_id = :t", {"t": B}) == set()
        assert _ids(db, ITEMS, "price_list_id = 'rlsp-b1'") == set()
        assert "row-level security" in _rejected(
            db, f"INSERT INTO {LISTS} (id, tenant_id, name, currency, is_active) "
                "VALUES ('rlsp-x', :t, 'x', 'EUR', TRUE)", {"t": B})
        assert _count(db, f"UPDATE {LISTS} SET name = 'x' WHERE id = 'rlsp-b1'") == 0
        assert _count(db, f"UPDATE {ITEMS} SET unit_price = 0 WHERE id = 'rlsp-b1-i'") == 0
        assert _count(db, f"DELETE FROM {ITEMS} WHERE id = 'rlsp-b1-i'") == 0
        assert _count(db, f"DELETE FROM {LISTS} WHERE id = 'rlsp-b1'") == 0
    with tenant_scope(B, "test"):
        assert _ids(db, LISTS) == {"rlsp-b1"}
        assert db.execute(sa.text(f"SELECT name FROM {LISTS}")).scalar() == f"Liste {B}"


@pytest.mark.integration
def test_ohne_mandantenkontext_fail_closed(db):
    assert _ids(db, LISTS) == set()
    assert _ids(db, ITEMS) == set()
    assert db.execute(sa.text("SELECT public.rls_current_tenant()")).scalar() is None
    _rejected(db, f"INSERT INTO {LISTS} (id, tenant_id, name, currency, is_active) "
                  "VALUES ('rlsp-x', :t, 'x', 'EUR', TRUE)", {"t": A})
    _rejected(db, f"INSERT INTO {ITEMS} (id, price_list_id, article_id, unit_price, min_quantity, "
                  "discount_percent) VALUES ('rlsp-x', 'rlsp-a1', 'x', 1, 0, 0)")
    assert _count(db, f"DELETE FROM {LISTS}") == 0
    with cross_tenant_scope("test: uebergreifend ohne Systemverbindung"):
        assert _ids(db, LISTS) == set()


@pytest.mark.integration
def test_wechsel_von_tenant_id_zum_fremden_mandanten_gesperrt(db):
    with tenant_scope(A, "test"):
        assert "row-level security" in _rejected(db, f"UPDATE {LISTS} SET tenant_id = :t WHERE id = 'rlsp-a1'", {"t": B})
        assert "row-level security" in _rejected(db, f"UPDATE {ITEMS} SET tenant_id = :t WHERE id = 'rlsp-a1-i'", {"t": B})
        _rejected(db, f"UPDATE {LISTS} SET tenant_id = 'system' WHERE id = 'rlsp-a1'")
    assert _as_owner(db, f"SELECT tenant_id FROM {LISTS} WHERE id = 'rlsp-a1'") == [(A,)]


@pytest.mark.integration
def test_system_zeilen_weder_lesbar_noch_aenderbar_loeschbar_oder_uebernehmbar(db):
    # Preislisten sind keine gemeinsamen Referenzdaten: auch Lesen ist gesperrt.
    with tenant_scope(A, "test"):
        assert _ids(db, LISTS, "tenant_id = 'system'") == set()
        assert _count(db, f"UPDATE {LISTS} SET name = 'x' WHERE id = 'rlsp-s1'") == 0
        assert _count(db, f"UPDATE {LISTS} SET tenant_id = :t WHERE id = 'rlsp-s1'", {"t": A}) == 0
        assert _count(db, f"UPDATE {ITEMS} SET tenant_id = :t WHERE id = 'rlsp-s1-i'", {"t": A}) == 0
        assert _count(db, f"DELETE FROM {ITEMS} WHERE id = 'rlsp-s1-i'") == 0
        assert _count(db, f"DELETE FROM {LISTS} WHERE id = 'rlsp-s1'") == 0
        _rejected(db, f"INSERT INTO {LISTS} (id, tenant_id, name, currency, is_active) "
                      "VALUES ('rlsp-x', 'system', 'x', 'EUR', TRUE)")
    assert _as_owner(db, f"SELECT tenant_id, name FROM {LISTS} WHERE id = 'rlsp-s1'") == [(SYSTEM, f"Liste {SYSTEM}")]
    assert _as_owner(db, f"SELECT count(*) FROM {ITEMS} WHERE id = 'rlsp-s1-i'") == [(1,)]


@pytest.mark.integration
def test_keine_position_unter_fremdem_elternbeleg(db):
    with tenant_scope(A, "test"):
        assert "fk_pli_price_list_tenant" in _rejected(
            db, f"INSERT INTO {ITEMS} (id, price_list_id, article_id, unit_price, min_quantity, "
                "discount_percent) VALUES ('rlsp-x', 'rlsp-b1', 'x', 1, 0, 0)")
        assert "row-level security" in _rejected(
            db, f"INSERT INTO {ITEMS} (id, price_list_id, tenant_id, article_id, unit_price, "
                "min_quantity, discount_percent) VALUES ('rlsp-x', 'rlsp-b1', :t, 'x', 1, 0, 0)", {"t": B})
        # Umhaengen an einen fremden Kopf
        assert "fk_pli_price_list_tenant" in _rejected(
            db, f"UPDATE {ITEMS} SET price_list_id = 'rlsp-b1' WHERE id = 'rlsp-a1-i'")
        assert "fk_pli_price_list_tenant" in _rejected(
            db, f"UPDATE {ITEMS} SET price_list_id = 'rlsp-s1' WHERE id = 'rlsp-a1-i'")


@pytest.mark.integration
def test_kontextwechsel_und_savepoint_rollback_ohne_mandantenuebertrag(db):
    with tenant_scope(A, "test"):
        assert _ids(db, LISTS) == {"rlsp-a1"}
        with tenant_scope(B, "test"):
            assert _ids(db, LISTS) == {"rlsp-b1"}
            inner = db.begin_nested()
            with tenant_scope(A, "test"):
                assert _ids(db, LISTS) == {"rlsp-a1"}  # setzt A innerhalb des Savepoints
            inner.rollback()  # Datenbank faellt auf B zurueck, der Cache wird verworfen
            assert _ids(db, LISTS) == {"rlsp-b1"}
            inner = db.begin_nested()
            assert _ids(db, LISTS) == {"rlsp-b1"}
            inner.rollback()
        assert _ids(db, LISTS) == {"rlsp-a1"}
    assert _ids(db, LISTS) == set()


@pytest.mark.integration
def test_hintergrundverarbeitung_nur_mit_ausdruecklichem_kontext(db):
    seen = {}
    for tenant in (A, B):
        with tenant_scope(tenant, "test: Preislisten-Job je Mandant"):
            seen[tenant] = _ids(db, LISTS)
    assert seen == {A: {"rlsp-a1"}, B: {"rlsp-b1"}}
    with cross_tenant_scope("test: Auswertung ueber alle Mandanten"):
        assert _ids(db, LISTS) == set()  # valeo_app ohne BYPASSRLS
        savepoint = db.begin_nested()
        try:
            db.execute(sa.text("SET LOCAL ROLE valeo_system"))  # wie system_session()
            assert {"rlsp-a1", "rlsp-b1", "rlsp-s1"} <= _ids(db, LISTS)
        finally:
            savepoint.rollback()
    assert db.execute(sa.text("SELECT current_user")).scalar() == "valeo_app"


@pytest.mark.integration
def test_fachkette_preislisten_und_preisfindung(db, monkeypatch):
    from app.api.v1.endpoints import price_lists as ep
    from app.core import read_model_cache
    from app.services import preisfindung_service as preis

    monkeypatch.setattr(read_model_cache, "_get_redis", lambda: None)
    session = Session(bind=db, join_transaction_mode="create_savepoint")
    run = asyncio.run
    item = ep.PriceListItemInput(article_id="rlsp-art2", article_number="RLSP-2", unit_price=Decimal("7.50"))
    try:
        with tenant_scope(A, "test"):
            created = run(ep.create_price_list(
                payload=ep.PriceListCreate(name="Kette", items=[item, item.model_copy(update={"article_id": "y"})]),
                tenant_id=A, db=session))
            assert created.tenant_id == A
            listed = run(ep.list_price_lists(tenant_id=A, is_active=None, db=session))
            assert {pl.id for pl in listed} == {"rlsp-a1", created.id}
            assert run(ep.get_price_list(created.id, tenant_id=A, db=session)).item_count == 2
            updated = run(ep.update_price_list(
                created.id, ep.PriceListUpdate(name="Kette 2", items=[item]), tenant_id=A, db=session))
            assert (updated.name, updated.item_count) == ("Kette 2", 1)
            treffer = preis.preisliste(session, A, {"id": "rlsp-art2", "article_number": "RLSP-2"}, Decimal("1"))
            assert treffer["price_list_id"] == created.id and Decimal(str(treffer["unit_price"])) == Decimal("7.50")
            assert preis.preisliste(session, A, {"id": "rlsp-art", "article_number": "RLSP-1"}, Decimal("1"))[
                "unit_price"] == 10
        with tenant_scope(B, "test"):
            for call in (
                lambda: ep.get_price_list(created.id, tenant_id=B, db=session),
                lambda: ep.update_price_list(created.id, ep.PriceListUpdate(name="fremd"), tenant_id=B, db=session),
                lambda: ep.delete_price_list(created.id, tenant_id=B, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 404
            assert preis.preisliste(session, B, {"id": "rlsp-art2", "article_number": "RLSP-2"}, Decimal("1")) is None
            assert preis.preisliste(session, B, {"id": "rlsp-art", "article_number": "RLSP-1"}, Decimal("1"))[
                "unit_price"] == 20
        with tenant_scope(A, "test"):
            assert run(ep.get_price_list(created.id, tenant_id=A, db=session)).name == "Kette 2"
            run(ep.delete_price_list(created.id, tenant_id=A, db=session))
            with pytest.raises(HTTPException):
                run(ep.get_price_list(created.id, tenant_id=A, db=session))
    finally:
        session.close()


@pytest.mark.integration
def test_pool_wiederverwendung_uebertraegt_keinen_mandanten():
    """Echte Commits auf einer gepoolten Verbindung; Tabelle temporaer, Policy-Form wie oben."""
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    own = "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')"
    engine = install_tenant_setting(sa.create_engine(URL, pool_size=1, max_overflow=0))
    try:
        with engine.connect() as conn:
            pid = conn.execute(sa.text("SELECT pg_backend_pid()")).scalar()
            conn.execute(sa.text("CREATE TEMP TABLE rlsp_pool (tenant_id text NOT NULL, v int)"))
            conn.execute(sa.text("ALTER TABLE rlsp_pool ENABLE ROW LEVEL SECURITY"))
            conn.execute(sa.text(f"CREATE POLICY tenant_isolation_select ON rlsp_pool FOR SELECT USING ({own})"))
            conn.execute(sa.text(f"CREATE POLICY tenant_isolation_insert ON rlsp_pool FOR INSERT WITH CHECK ({own})"))
            conn.execute(sa.text("GRANT SELECT, INSERT ON rlsp_pool TO valeo_app"))
            conn.commit()

        def checkout(scope_tenant):
            with engine.connect() as conn:
                assert conn.execute(sa.text("SELECT pg_backend_pid()")).scalar() == pid
                conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
                if scope_tenant is None:
                    rows = conn.execute(sa.text("SELECT count(*) FROM rlsp_pool")).scalar()
                    setting = conn.execute(sa.text("SELECT current_setting('app.tenant_id', true)")).scalar()
                    conn.commit()
                    return rows, setting
                with tenant_scope(scope_tenant, "test"):
                    rows = conn.execute(sa.text("SELECT count(*) FROM rlsp_pool")).scalar()
                    conn.commit()
                    return rows, scope_tenant

        with engine.connect() as conn, tenant_scope(A, "test"):
            conn.execute(sa.text("SET LOCAL ROLE valeo_app"))
            conn.execute(sa.text("INSERT INTO rlsp_pool VALUES (:t, 1)"), {"t": A})
            conn.commit()
        assert checkout(None) == (0, "")
        assert checkout(B) == (0, B)
        assert checkout(A) == (1, A)
        assert checkout(None)[0] == 0
    finally:
        engine.dispose()  # schliesst die Sitzung, die temporaere Tabelle verschwindet
