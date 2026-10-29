"""RLS-Domain shared: Niederlassungen, Stammdaten, Futtermittel, Nachrichten und Konditionen als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import asyncio
import importlib
import inspect

import pytest
import sqlalchemy as sa
from fastapi import HTTPException

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

SH = "domain_shared"
BRANCHES, SINGLE_FEED, COMPOUND_FEED = f"{SH}.branches", f"{SH}.futtermittel_einzelfutter", f"{SH}.futtermittel_mischfutter"
RECIPES, ANALYSES = f"{SH}.futtermittel_rezepte", f"{SH}.grundfutter_analysen"
SCALES, GROUPS = f"{SH}.vertreter_provisionsstaffeln", f"{SH}.vertreter_provisionsgruppen"
THREADS, JOBS = f"{SH}.channel_process_threads", f"{SH}.jobs"
SURCHARGE_GROUPS, SURCHARGE_CLASSES = f"{SH}.zu_abschlaggruppen", f"{SH}.zu_abschlagklassen"
DISPATCHERS, MASTER_DATA = f"{SH}.dispatchers", f"{SH}.master_data_entries"
MESSAGES, FARMERS = f"{SH}.internal_messages", f"{SH}.farmers"

NEW_TENANT_COLUMN = (
    f"{SH}.channel_thread_audit_items", f"{SH}.futtermittel_rezept_komponenten", f"{SH}.job_artifacts",
    SCALES, f"{SH}.vertreter_staffel_zeilen", f"{SH}.zu_abschlag_konditionen",
)
ISOLATED = (
    f"{SH}.agrar_sorten", f"{SH}.artikel_sperren", BRANCHES, f"{SH}.calendar_items",
    f"{SH}.calendar_team_memberships", f"{SH}.direct_debit_items", DISPATCHERS, FARMERS,
    f"{SH}.feeding_feed_analysis_findings", f"{SH}.feeding_feed_analysis_revisions",
    f"{SH}.feeding_feed_analysis_values", SINGLE_FEED, COMPOUND_FEED, f"{SH}.futtermittel_produktionsauftraege",
    RECIPES, ANALYSES, MESSAGES, f"{SH}.logistik_frachttabellen", MASTER_DATA, f"{SH}.rations_zugang",
    "public.number_series",
) + NEW_TENANT_COLUMN
DEFAULT_TO_CONTEXT = ("public.number_series",)
# Eltern in der Reihenfolge, in der sie angelegt werden (spaetere verweisen auf fruehere).
PARENTS = (SINGLE_FEED, COMPOUND_FEED, RECIPES, ANALYSES, BRANCHES, THREADS, JOBS, GROUPS,
           SURCHARGE_GROUPS, SURCHARGE_CLASSES, SCALES)

# (Kind, Spalte, Eltern); Tabellen anderer Domains behalten ihre Policies und bekommen nur den Schluessel.
LINKS = (
    (f"{SH}.channel_thread_audit_items", "thread_id", THREADS),
    (f"{SH}.futtermittel_rezept_komponenten", "rezept_id", RECIPES),
    (f"{SH}.job_artifacts", "job_id", JOBS),
    (SCALES, "gruppe_id", GROUPS),
    (f"{SH}.vertreter_staffel_zeilen", "staffel_id", SCALES),
    (f"{SH}.zu_abschlag_konditionen", "gruppe_id", SURCHARGE_GROUPS),
    (f"{SH}.zu_abschlag_konditionen", "klasse_id", SURCHARGE_CLASSES),
    (f"{SH}.futtermittel_rezept_komponenten", "einzelfutter_id", SINGLE_FEED),
    (RECIPES, "mischfutter_id", COMPOUND_FEED),
    (f"{SH}.futtermittel_produktionsauftraege", "rezept_id", RECIPES),
    (ANALYSES, "feed_id", SINGLE_FEED),
    (f"{SH}.feeding_feed_analysis_findings", "analysis_id", ANALYSES),
    (f"{SH}.feeding_feed_analysis_revisions", "analysis_id", ANALYSES),
    (f"{SH}.feeding_feed_analysis_values", "analysis_id", ANALYSES),
    ("domain_sales.delivery_notes", "branch_id", BRANCHES),
    ("domain_inventory.harvest_acceptances", "branch_id", BRANCHES),
    ("domain_agrar.feeding_feed_products", "feed_id", SINGLE_FEED),
    ("domain_agrar.feeding_feed_reference_values", "feed_id", SINGLE_FEED),
    ("domain_agrar.feeding_feed_revisions", "feed_id", SINGLE_FEED),
)
CHILDREN = tuple(dict.fromkeys(child for child, _, _ in LINKS))
KEYS = {THREADS: "thread_id"}
# Nur anhaengen: ein Trigger verbietet UPDATE und DELETE. Fuer die Policy-Faelle wird er im
# zurueckgerollten Savepoint als Eigentuemer abgeschaltet; geprueft werden nur die Policies.
APPEND_ONLY = (f"{SH}.feeding_feed_analysis_revisions", "domain_agrar.feeding_feed_revisions")
AUXILIARY = ("domain_shared.users",)


def _key(conn, table: str) -> str:
    return support.primary_key(conn, table)


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
                full = support.seed_row(conn, table, tenant, **links)
                rows["full", table, tenant] = full
                rows[table, tenant] = str(full[_key(conn, table)])
        for parent in PARENTS:
            rows["spare", parent] = str(support.seed_row(conn, parent, B)[KEYS.get(parent, "id")])
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


def _without_append_only_guard(conn, table: str) -> None:
    if table in APPEND_ONLY:
        conn.execute(sa.text("RESET ROLE"))
        conn.execute(sa.text(f"ALTER TABLE {table} DISABLE TRIGGER USER"))
        support.as_app(conn)


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    _without_append_only_guard(conn, table)
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM],
                                    key=_key(conn, table))


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
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"[:63]  # PostgreSQL kuerzt Namen auf 63 Zeichen
    with tenant_scope(A, "test"):
        if child in ISOLATED:
            message = support.rejected_insert_with(conn, child, A, _key(conn, child), **{column: foreign},
                                                   **_other_references(conn, rows, child, column))
            assert constraint in message, message
    # Umhaengen der bestehenden A-Zeile; Tabellen anderer Domains als Eigentuemer, ihre Policies sind nicht Gegenstand.
    _without_append_only_guard(conn, child)
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
        for table in NEW_TENANT_COLUMN:
            links = {column: rows[parent, A] for column, parent in _links_of(table)}
            row = support.seed_row(conn, table, None, **links)
            assert row["tenant_id"] == A, table


def test_nummernkreis_vorgabe_ist_der_kontext_nicht_default(db):
    """public.number_series setzte tenant_id ohne Angabe auf 'default'."""
    conn, _ = db
    for table in DEFAULT_TO_CONTEXT:
        default = conn.execute(sa.text(
            "SELECT pg_get_expr(d.adbin, d.adrelid) FROM pg_attrdef d JOIN pg_attribute a "
            "ON a.attrelid = d.adrelid AND a.attnum = d.adnum WHERE d.adrelid = to_regclass(:t) "
            "AND a.attname = 'tenant_id'"), {"t": table}).scalar()
        assert default == "rls_current_tenant()", (table, default)


def test_eltern_mit_verweisen_behaelt_seinen_mandanten(db):
    conn, rows = db
    for parent in PARENTS:
        key = KEYS.get(parent, "id")
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE {key} = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "foreign key constraint" in message and "_tena" in message, (parent, message)


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, BRANCHES, rows[BRANCHES, A], rows[BRANCHES, B])
    support.assert_background_needs_explicit_context(conn, ANALYSES, rows[ANALYSES, A], rows[ANALYSES, B])
    support.assert_pool_reuse_keeps_no_tenant()


# --- Fachketten: als Eigentuemer ohne RLS, der Code selbst muss filtern (live ist RLS noch aus) ---------

@pytest.fixture
def owner_session(db):
    from sqlalchemy.orm import Session

    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session, rows
    finally:
        session.close()


def _not_found(call) -> None:
    with pytest.raises(HTTPException) as caught:
        asyncio.run(call) if inspect.iscoroutine(call) else call()
    assert caught.value.status_code == 404


def test_fachkette_niederlassungen_nur_eigener_mandant(owner_session):
    from app.api.v1.endpoints import branches

    session, rows = owner_session
    listed = {b.id for b in asyncio.run(branches.list_branches(tenant_id=A, active_only=False, db=session))}
    assert rows[BRANCHES, A] in listed and rows[BRANCHES, B] not in listed
    _not_found(branches.get_branch(rows[BRANCHES, B], tenant_id=A, db=session))
    _not_found(branches.delete_branch(rows[BRANCHES, B], tenant_id=A, db=session))


def test_fachkette_disponenten_und_stammdaten_nur_eigener_mandant(owner_session):
    """Aendern und Loeschen von Disponenten und Kontaktarten filterten vorher nicht nach Mandant."""
    from app.api.v1.endpoints import master_data

    session, rows = owner_session
    listed = {d.id for d in asyncio.run(master_data.list_dispatchers(tenant_id=A, db=session))}
    assert rows[DISPATCHERS, B] not in listed
    entries = asyncio.run(master_data.list_master_data(category=None, tenant_id=A, skip=0, limit=500, db=session))
    assert rows[MASTER_DATA, B] not in {e.id for e in entries.items}
    payload = master_data.DispatcherCreate(name="fremd")
    _not_found(master_data.update_dispatcher(rows[DISPATCHERS, B], payload, tenant_id=A, db=session))
    _not_found(master_data.delete_dispatcher(rows[DISPATCHERS, B], tenant_id=A, db=session))
    _not_found(master_data.delete_contact_type(rows[MASTER_DATA, B], tenant_id=A, db=session))
    remaining = session.execute(sa.text(f"SELECT count(*) FROM {DISPATCHERS} WHERE id = :i AND name <> 'fremd'"),
                                {"i": rows[DISPATCHERS, B]}).scalar()
    assert remaining == 1


def test_fachkette_nachrichten_landwirte_analysen_nur_eigener_mandant(owner_session):
    from app.api.v1.endpoints import agribusiness, grundfutter_analysen, messages

    session, rows = owner_session
    page = asyncio.run(messages.list_messages(recipient_id=None, tenant_id=A, skip=0, limit=200, db=session))
    assert rows[MESSAGES, B] not in {m.id for m in page.items}
    farmers = agribusiness.list_farmers(db=session, tenant_id=A)
    assert {f.id for f in farmers.items} == {rows[FARMERS, A]}
    _not_found(lambda: agribusiness.delete_farmer(rows[FARMERS, B], agribusiness.DeleteFarmerRequest(reason="x"),
                                                  db=session, tenant_id=A))
    analyses = grundfutter_analysen.list_analysen(_Request({"sub": "u1"}), probenart=None, verifiziert=None, limit=200,
                                                  offset=0, db=session, tenant_id=A, x_share_token=None)
    ids = {str(a["id"]) for a in analyses["items"]}
    assert rows[ANALYSES, A] in ids and rows[ANALYSES, B] not in ids


def test_fachkette_pos_rabatte_nur_eigener_mandant(owner_session):
    """Die Rabattbruecken lasen Konditionen aller Mandanten (ohne Filter)."""
    from app.api.v1.endpoints import mask_frontend_bridges as bridges

    session, rows = owner_session
    konditionen = f"{SH}.zu_abschlag_konditionen"
    listed = {r["id"] for r in bridges.list_pos_rabatte(tenant_id=A, db=session)}
    assert rows[konditionen, A] in listed and rows[konditionen, B] not in listed
    assert bridges.preise_konditionen(tenant_id=B, db=session)["id"] in {rows[konditionen, B], "default"}


# --- ohne Datenbank -----------------------------------------------------------------------------

MODULES = ("app.api.v1.endpoints.branches", "app.api.v1.endpoints.master_data", "app.api.v1.endpoints.messages",
           "app.api.v1.endpoints.agribusiness", "app.api.v1.endpoints.grundfutter_analysen",
           "app.domains.agrar.api.psm")


class _Request:
    def __init__(self, claims):
        self.state = type("State", (), {"token_claims": claims})()


def test_nachricht_absender_aus_dem_token():
    """Der Absender stand frei im Rumpf; jetzt ist er der gepruefte Nutzer."""
    from app.api.v1.endpoints import messages

    assert "sender_id" not in messages.MessageCreate.model_fields
    assert "request" in inspect.signature(messages.send_message).parameters


def test_rations_zugang_aufrufer_aus_dem_token():
    """E-Mail und Name kamen aus X-User-Email/X-User-Name, ohne Kopf galt system@valeo.local."""
    from app.api.v1.endpoints import rations_zugang

    with pytest.raises(HTTPException) as caught:
        rations_zugang._caller_info(_Request({"sub": "u1"}))
    assert caught.value.status_code == 403
    with pytest.raises(HTTPException) as unverified:
        rations_zugang._caller_info(_Request({"sub": "u1", "email": "b@hof.de", "email_verified": False}))
    assert unverified.value.status_code == 403
    assert rations_zugang._caller_info(_Request({"sub": "u1", "email": "b@hof.de", "email_verified": True, "name": "B"})) == ("b@hof.de", "B")


@pytest.mark.parametrize("module", MODULES)
def test_wege_nehmen_den_mandanten_aus_dem_token(module):
    """Vorher galt ?tenant_id= (bzw. der Kopf X-Tenant-ID), ohne ihn der Standardmandant."""
    from fastapi.routing import APIRoute

    from app.core.tenant import get_tenant_id

    router = importlib.import_module(module).router
    routes = [r for r in router.routes if isinstance(r, APIRoute)]
    # Jeder Weg mit Datenbankzugriff braucht den Mandanten aus dem Token; Wege ohne db (Stubs) duerfen ohne.
    with_db = [r for r in routes if "db" in inspect.signature(r.endpoint).parameters]
    assert with_db
    for route in routes:
        parameters = inspect.signature(route.endpoint).parameters
        assert "x_tenant_id" not in parameters, route.path
        if "tenant_id" in parameters:
            assert getattr(parameters["tenant_id"].default, "dependency", None) is get_tenant_id, route.path
    assert [r.path for r in with_db if "tenant_id" not in inspect.signature(r.endpoint).parameters] == []
