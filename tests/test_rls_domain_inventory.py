"""RLS-Domain inventory: Artikel, Lager, Bestaende, Bewegungen, Inventuren und Ruestlisten als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt). Silo-/Materialfluss-
tabellen, agrar_contracts, weighing_tickets und die Tabellen des Inventory-Dienstes gehoeren nicht dazu.
"""

from __future__ import annotations

import asyncio
import importlib

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

INV = "domain_inventory"
ARTICLES, WAREHOUSES = f"{INV}.articles", f"{INV}.warehouses"
ZONES, BINS, AISLES = f"{INV}.warehouse_zones", f"{INV}.warehouse_bins", f"{INV}.warehouse_aisles"
LOCATIONS, MOVEMENTS = f"{INV}.stock_locations", f"{INV}.inventory_stock_movements"
COUNTS, PREP_LISTS = f"{INV}.inventory_counts", f"{INV}.preparation_lists"
DRYING_RULES, HARVEST = f"{INV}.drying_rule_sets", f"{INV}.harvest_acceptances"
PARTNERS = "domain_crm.business_partners"
SELECTIONS, SHIPPING = f"{INV}.article_selections", f"{INV}.shipping_units"

ISOLATED = tuple(f"{INV}.{name}" for name in (
    "articles", "article_batches", "article_documents", "article_selections", "article_suppliers",
    "warehouses", "warehouse_zones", "warehouse_bins", "bin_stock", "stock_locations",
    "stock_item", "stock_movement", "stock_movements", "inventory_stock_movements",
    "inventory_counts", "inventory_count_lines", "inventory_lots", "inventory_lot_movements",
    "preparation_lists", "preparation_list_lines", "shipping_units", "epcis_events",
    "nawaro_print_notifications", "drying_rule_factor_ranges", "drying_rule_lookup_rows",
    "harvest_acceptance_lines", "harvest_acceptance_positions",
))
NEW_TENANT_COLUMN = tuple(f"{INV}.{name}" for name in (
    "article_suppliers", "stock_locations", "drying_rule_factor_ranges", "drying_rule_lookup_rows",
    "harvest_acceptance_lines", "harvest_acceptance_positions",
))
# Eltern in der Reihenfolge, in der sie angelegt werden (spaetere verweisen auf fruehere).
PARENTS = (PARTNERS, ARTICLES, WAREHOUSES, ZONES, AISLES, BINS, LOCATIONS, MOVEMENTS, COUNTS, PREP_LISTS,
           DRYING_RULES, HARVEST)
PARENT_KEY = {PARTNERS: "partner_id"}
# Ein Trigger prueft die Belegart gegen inventory_movement_types.
VALUES = {MOVEMENTS: {"movement_type": "in"}}


def _l(child: str, column: str, parent: str):
    return (child if "." in child else f"{INV}.{child}", column, parent)


# (Kind, Spalte, Eltern); P5-Tabellen behalten ihre Policies und bekommen nur den Schluessel.
LINKS = (
    _l("article_suppliers", "article_id", ARTICLES), _l("article_suppliers", "partner_id", PARTNERS),
    _l("stock_locations", "warehouse_id", WAREHOUSES),
    _l("drying_rule_factor_ranges", "rule_set_id", DRYING_RULES),
    _l("drying_rule_lookup_rows", "rule_set_id", DRYING_RULES),
    _l("harvest_acceptance_lines", "harvest_acceptance_id", HARVEST),
    _l("harvest_acceptance_positions", "harvest_acceptance_id", HARVEST),
    _l("harvest_acceptance_positions", "article_id", ARTICLES),
    _l("article_batches", "article_id", ARTICLES), _l("article_batches", "warehouse_id", WAREHOUSES),
    _l("article_documents", "article_id", ARTICLES), _l("article_selections", "article_id", ARTICLES),
    _l("warehouse_zones", "warehouse_id", WAREHOUSES),
    _l("warehouse_bins", "warehouse_id", WAREHOUSES), _l("warehouse_bins", "zone_id", ZONES),
    _l("warehouse_bins", "aisle_id", AISLES), _l("bin_stock", "bin_id", BINS),
    _l("stock_movements", "article_id", ARTICLES), _l("stock_movements", "location_id", LOCATIONS),
    _l("stock_movements", "warehouse_id", WAREHOUSES),
    _l("inventory_stock_movements", "article_id", ARTICLES), _l("inventory_stock_movements", "bin_id", BINS),
    _l("inventory_stock_movements", "warehouse_id", WAREHOUSES),
    _l("inventory_counts", "warehouse_id", WAREHOUSES),
    _l("inventory_count_lines", "inventory_count_id", COUNTS), _l("inventory_count_lines", "article_id", ARTICLES),
    _l("inventory_count_lines", "warehouse_id", WAREHOUSES),
    _l("preparation_lists", "warehouse_id", WAREHOUSES),
    _l("preparation_list_lines", "list_id", PREP_LISTS), _l("preparation_list_lines", "article_id", ARTICLES),
    _l("article_price_thresholds", "article_id", ARTICLES), _l("daily_prices", "article_id", ARTICLES),
    _l("price_adjustment_rules", "article_id", ARTICLES), _l("weighing_ticket_lines", "article_id", ARTICLES),
    _l("warehouse_transfer_lines", "article_id", ARTICLES), _l("stock_correction_lines", "article_id", ARTICLES),
    _l("pick_list_lines", "article_id", ARTICLES), _l("pick_list_lines", "bin_id", BINS),
    _l("lkw_annahme_queue", "article_id", ARTICLES), _l("nawaro_raps_profiles", "article_id", ARTICLES),
    _l("harvest_acceptances", "article_id", ARTICLES), _l("harvest_acceptances", "warehouse_id", WAREHOUSES),
    _l("harvest_acceptances", "stock_movement_id", MOVEMENTS),
    _l("harvest_acceptances", "forwarder_id", PARTNERS), _l("harvest_acceptances", "intermediate_dealer_id", PARTNERS),
    _l("bin_locations", "warehouse_id", WAREHOUSES),
    _l("warehouse_aisles", "warehouse_id", WAREHOUSES), _l("warehouse_aisles", "zone_id", ZONES),
    _l("warehouse_transfers", "from_warehouse_id", WAREHOUSES), _l("warehouse_transfers", "to_warehouse_id", WAREHOUSES),
    _l("stock_corrections", "warehouse_id", WAREHOUSES),
    _l("charge_lineage_links", "source_movement_id", MOVEMENTS),
    _l("charge_lineage_links", "target_movement_id", MOVEMENTS),
    _l("domain_sales.delivery_note_positions", "artikel_id", ARTICLES),
)
CHILDREN = tuple(dict.fromkeys(child for child, _, _ in LINKS))
# Eltern, deren Pflicht-Eltern seed_row selbst anlegt (FK-Pruefungen umgehen RLS, aber valeo_app braucht Rechte).
AUXILIARY = ("domain_crm.customers", "domain_shared.branches", "domain_sales.delivery_notes",
             f"{INV}.pick_lists", f"{INV}.warehouse_transfers", f"{INV}.stock_corrections", f"{INV}.weighing_tickets",
             f"{INV}.agrar_contracts", "domain_finance.self_billing_invoices", "domain_shared.users",
             "domain_agrar.nutrient_compositions", f"{INV}.inventory_movement_types")


def _key(conn, table: str) -> str:
    return support.primary_key(conn, table)


def _parent_key(parent: str) -> str:
    return PARENT_KEY.get(parent, "id")


def _links_of(table: str):
    return [(column, parent) for child, column, parent in LINKS if child == table]


@pytest.fixture(scope="module")
def probe():
    tables = tuple(dict.fromkeys(ISOLATED + PARENTS + CHILDREN + AUXILIARY))
    with support.probe(tables) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            # Eltern zuerst; jede Zeile verweist auf die Eltern desselben Mandanten.
            for table in tuple(dict.fromkeys(PARENTS + ISOLATED + CHILDREN)):
                links = {column: rows[parent, tenant] for column, parent in _links_of(table) if (parent, tenant) in rows}
                full = support.seed_row(conn, table, tenant, **links, **VALUES.get(table, {}))
                rows["full", table, tenant] = full
                key = _parent_key(table) if table in PARENTS else _key(conn, table)
                rows[table, tenant] = str(full[key])
        for parent in PARENTS:
            rows["spare", parent] = str(support.seed_row(conn, parent, B, **VALUES.get(parent, {}))[_parent_key(parent)])
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_policy_formen(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    key = _key(conn, table)
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], key=key,
                                    values=VALUES.get(table))


def _other_references(conn, rows, child: str, column: str) -> dict:
    """Die uebrigen Fremdschluessel der A-Zeile, damit nur der gepruefte Verweis fremd ist."""
    full = rows["full", child, A]
    columns = {c for _, cols, parent, _ in conn.execute(sa.text(support.FKS_SQL), {"t": child})
               for c in cols if parent != "domain_shared.tenants"}
    return {c: full[c] for c in columns - {column, "tenant_id"} if full.get(c) is not None}


@pytest.mark.parametrize("child,column,parent", LINKS, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in LINKS])
def test_kein_verweis_auf_fremden_eltern(db, child, column, parent):
    conn, rows = db
    foreign = rows["spare", parent]
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"
    with tenant_scope(A, "test"):
        if child in ISOLATED:
            message = support.rejected_insert_with(conn, child, A, _key(conn, child), **{column: foreign},
                                                   **_other_references(conn, rows, child, column),
                                                   **VALUES.get(child, {}))
            assert constraint in message, message
    # Umhaengen der bestehenden A-Zeile; P5-Tabellen als Eigentuemer, ihre Policies sind nicht Gegenstand.
    sql = f"UPDATE {child} SET {column} = :p WHERE {_key(conn, child)} = :i"
    params = {"p": foreign, "i": rows[child, A]}
    if child in ISOLATED:
        with tenant_scope(A, "test"):
            message = support.rejected(conn, sql, params)
    else:
        message = support.as_owner_rejected(conn, sql, params)
    assert constraint in message, message


def test_kind_erbt_den_mandanten_vom_kontext(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        for child in NEW_TENANT_COLUMN:
            links = {column: rows[parent, A] for column, parent in _links_of(child)}
            row = support.seed_row(conn, child, None, **links)
            assert row["tenant_id"] == A, child


def test_eltern_mit_verweisen_behaelt_seinen_mandanten(db):
    conn, rows = db
    for parent in PARENTS:
        key = _parent_key(parent)
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE {key} = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "_tenant" in message, (parent, message)


SET_NULL = ((f"{INV}.daily_prices", "article_id", ARTICLES), (f"{INV}.lkw_annahme_queue", "article_id", ARTICLES),
            ("domain_sales.delivery_note_positions", "artikel_id", ARTICLES),
            (f"{INV}.charge_lineage_links", "source_movement_id", MOVEMENTS))


@pytest.mark.parametrize("child,column,parent", SET_NULL, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in SET_NULL])
def test_loeschen_leert_nur_den_verweis(db, child, column, parent):
    """ON DELETE SET NULL eines Verbund-FK leert die Verweisspalte, nicht den Mandanten (PG15)."""
    conn, rows = db
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        fresh = support.seed_row(conn, parent, A, **VALUES.get(parent, {}))["id"]
        key = _key(conn, child)
        conn.execute(sa.text(f"UPDATE {child} SET {column} = :p WHERE {key} = :i"), {"p": fresh, "i": rows[child, A]})
        conn.execute(sa.text(f"DELETE FROM {parent} WHERE id = :p"), {"p": fresh})
        ref, tenant = conn.execute(sa.text(f"SELECT {column}, tenant_id FROM {child} WHERE {key} = :i"),
                                   {"i": rows[child, A]}).one()
        assert (ref, tenant) == (None, A)
    finally:
        savepoint.rollback()


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, ARTICLES, rows[ARTICLES, A], rows[ARTICLES, B])
    support.assert_background_needs_explicit_context(conn, WAREHOUSES, rows[WAREHOUSES, A], rows[WAREHOUSES, B])
    support.assert_pool_reuse_keeps_no_tenant()


def _session(conn) -> Session:
    import app.infrastructure.models  # noqa: F401  # ORM-Fremdschluessel

    return Session(bind=conn, join_transaction_mode="create_savepoint")


def test_fachkette_ruestlisten_nve_selektionen_nur_eigener_mandant(db):
    conn, rows = db
    prep = importlib.import_module("app.api.v1.endpoints.preparation_lists")
    nve = importlib.import_module("app.api.v1.endpoints.nve")
    ext = importlib.import_module("app.api.v1.endpoints.article_extensions")
    run = asyncio.run
    session = _session(conn)
    try:
        with tenant_scope(A, "test"):
            page = run(prep.list_preparation_lists(skip=0, limit=200, db=session, tenant_id=A))
            assert {i.id for i in page.items} == {rows[PREP_LISTS, A]}
            assert run(prep.get_preparation_list(rows[PREP_LISTS, A], db=session, tenant_id=A)).id == rows[PREP_LISTS, A]
            for call in (prep.get_preparation_list, prep.get_prep_list_lines, prep.delete_preparation_list):
                with pytest.raises(HTTPException) as exc:
                    run(call(rows[PREP_LISTS, B], db=session, tenant_id=A))
                assert exc.value.status_code == 404, call.__name__
            lines = run(prep.get_prep_list_lines(rows[PREP_LISTS, A], db=session, tenant_id=A))
            assert {line.id for line in lines} == {rows[f"{INV}.preparation_list_lines", A]}

            page = run(nve.list_nves(skip=0, limit=200, db=session, tenant_id=A))
            assert {i.id for i in page.items} == {rows[SHIPPING, A]}
            created = run(nve.create_nve(nve.NVECreate(sscc="003401234500000018"), db=session, tenant_id=A))
            assert support.keys(conn, SHIPPING, "tenant_id", "id = :i", {"i": created.id}) == {A}

            assert {s.id for s in run(ext.list_article_selections(db=session, tenant_id=A))} == {rows[SELECTIONS, A]}
            with pytest.raises(HTTPException) as exc:
                run(ext.delete_article_selection(rows[SELECTIONS, B], db=session, tenant_id=A))
            assert exc.value.status_code == 404
            page = run(ext.list_article_batches(article_id=None, skip=0, limit=200, db=session, tenant_id=A))
            assert {i.id for i in page.items} == {rows[f"{INV}.article_batches", A]}
    finally:
        session.close()


def test_fachkette_artikellieferanten_nur_eigener_mandant(db):
    """Das Register filterte nach ArticleSupplier.tenant_id, das Modell kennt die Spalte nicht: jeder Abruf endete mit 500."""
    conn, rows = db
    articles = importlib.import_module("app.api.v1.endpoints.articles")
    suppliers = f"{INV}.article_suppliers"
    savepoint = conn.begin_nested()
    conn.execute(sa.text("RESET ROLE"))  # der Weg zeigt nur aktive Artikel
    conn.execute(sa.text(f"UPDATE {ARTICLES} SET is_active = true, deleted_at = NULL WHERE id = ANY(:a)"),
                 {"a": [rows["full", suppliers, t]["article_id"] for t in (A, B)]})
    support.as_app(conn)
    session = _session(conn)
    try:
        with tenant_scope(A, "test"):
            antwort = asyncio.run(articles.get_article_suppliers(
                rows["full", suppliers, A]["article_id"], tenant_id=A, db=session))
            assert [s["id"] for s in antwort["items"]] == [rows[suppliers, A]]
            with pytest.raises(HTTPException) as exc:
                asyncio.run(articles.get_article_suppliers(rows["full", suppliers, B]["article_id"], tenant_id=A, db=session))
            assert exc.value.status_code == 404
    finally:
        session.close()
        savepoint.rollback()


def test_fachkette_pos_retoure_bucht_nur_im_eigenen_mandanten(db):
    conn, rows = db
    retoure = importlib.import_module("app.api.v1.endpoints.pos_retoure")
    own, foreign = rows["full", ARTICLES, A]["article_number"], rows["full", ARTICLES, B]["article_number"]

    def request(artikelnr):
        return retoure.RetourRequest(kassierer="Kasse 1", gesamt=1.0, positionen=[
            retoure.RetourPosition(artikelnr=artikelnr, bezeichnung="Ware", einzelpreis=1.0, menge=1)])

    session = _session(conn)
    try:
        with tenant_scope(A, "test"):
            antwort = asyncio.run(retoure.create_retoure(request(own), db=session, tenant_id=A))
            assert support.keys(conn, MOVEMENTS, "tenant_id", "source_document_id = :r",
                                {"r": antwort.retoure_id}) == {A}
            # Artikel des fremden Mandanten: kein Erfolg ohne Buchung
            with pytest.raises(HTTPException) as exc:
                asyncio.run(retoure.create_retoure(request(foreign), db=session, tenant_id=A))
            assert exc.value.status_code == 422
    finally:
        session.close()


def test_fachkette_bvl_umsaetze_nur_eigener_mandant(db):
    conn, rows = db
    compliance = importlib.import_module("app.api.v1.endpoints.compliance")
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        for tenant in (A, B):
            conn.execute(sa.text(
                f"UPDATE {ARTICLES} SET pflanzenschutzmittel = true, name = :n WHERE id = :a"),
                {"n": f"Wirkstoff {tenant}", "a": rows[ARTICLES, tenant]})
            conn.execute(sa.text(
                f"UPDATE {MOVEMENTS} SET movement_type = 'out', article_id = :a, "
                "movement_date = make_date(EXTRACT(YEAR FROM CURRENT_DATE)::int - 1, 6, 1) WHERE id = :m"),
                {"a": rows[ARTICLES, tenant], "m": rows[MOVEMENTS, tenant]})
        support.as_app(conn)
        session = _session(conn)
        try:
            with tenant_scope(A, "test"):
                umsaetze = asyncio.run(compliance.get_bvl_umsaetze(db=session, tenant_id=A))
            assert [u["wirkstoff"] for u in umsaetze] == [f"Wirkstoff {A}"]
        finally:
            session.close()
    finally:
        savepoint.rollback()


# --- ohne Datenbank -----------------------------------------------------------------------------

ROUTES = (
    ("app.api.v1.endpoints.preparation_lists", "/preparation-lists", "get", "/preparation-lists/"),
    ("app.api.v1.endpoints.nve", "/nve", "get", "/nve/"),
    ("app.api.v1.endpoints.article_extensions", "/articles", "get", "/articles/selections"),
    ("app.api.v1.endpoints.compliance", "", "get", "/compliance/bvl-umsaetze"),
    ("app.api.v1.endpoints.compliance", "", "get", "/compliance/ustva"),
)


@pytest.mark.parametrize("module,prefix,method,path", ROUTES, ids=[r[3] for r in ROUTES])
def test_lagerwege_nehmen_den_mandanten_aus_dem_token(module, prefix, method, path):
    endpoints = importlib.import_module(module)
    app = FastAPI()
    app.include_router(endpoints.router, prefix=f"/api/v1{prefix}")
    app.dependency_overrides[endpoints.get_db] = lambda: None
    # Vorher galt ?tenant_id=, ohne ihn der Standardmandant.
    antwort = getattr(TestClient(app), method)(f"/api/v1{path}", params={"tenant_id": B})
    assert antwort.status_code in (401, 403), antwort.text


def test_pos_retoure_ignoriert_den_mandanten_im_rumpf():
    retoure = importlib.import_module("app.api.v1.endpoints.pos_retoure")
    assert "tenant_id" not in retoure.RetourRequest.model_fields
    app = FastAPI()
    app.include_router(retoure.router, prefix="/api/v1/pos")
    app.dependency_overrides[retoure.get_db] = lambda: None
    antwort = TestClient(app).post("/api/v1/pos/retoure", json={
        "kassierer": "Kasse 1", "gesamt": 1, "tenant_id": B, "positionen": []})
    assert antwort.status_code in (401, 403), antwort.text


def test_pos_retoure_meldet_keinen_schein_erfolg():
    retoure = importlib.import_module("app.api.v1.endpoints.pos_retoure")

    class Kaputt:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("Datenbank nicht erreichbar")

        def rollback(self):
            pass

    request = retoure.RetourRequest(kassierer="Kasse 1", gesamt=1.0, positionen=[
        retoure.RetourPosition(artikelnr="4711", bezeichnung="Ware", einzelpreis=1.0, menge=1)])
    with pytest.raises(HTTPException) as exc:
        asyncio.run(retoure.create_retoure(request, db=Kaputt(), tenant_id=A))
    assert exc.value.status_code == 500
