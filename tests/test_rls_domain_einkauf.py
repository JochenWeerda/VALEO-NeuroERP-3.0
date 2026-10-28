"""RLS-Domain einkauf: Bestellungen, Lieferanten, Positionen, Waren- und Rechnungseingaenge als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import importlib

import pytest
import sqlalchemy as sa

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

EK = "domain_einkauf"
ORDERS, SUPPLIERS, CONTRACTS = f"{EK}.bestellungen", f"{EK}.lieferanten", f"{EK}.kontrakte"
PROPOSALS, CONTRACT_POSITIONS, RFQS = f"{EK}.bestellvorschlaege", f"{EK}.kontrakt_positionen", f"{EK}.rfq_requests"
INVOICES, RECEIPTS = "public.einkauf_rechnungseingaenge", "public.einkauf_wareneingaenge"
REQUESTS, OFFERS = "public.einkauf_anfragen", "public.einkauf_angebote"
DELIVERY_NOTES, PAYMENT_RUNS = "public.einkauf_lieferscheine", "public.einkauf_zahlungslaeufe"
PROC_ORDERS = "domain_procurement.proc_purchase_orders"

ISOLATED = (
    ORDERS, SUPPLIERS, f"{EK}.ers_invoices", f"{EK}.ers_suppliers", f"{EK}.invoice_verification",
    PROC_ORDERS, DELIVERY_NOTES, "public.zahlungslauf_kreditoren",
    f"{EK}.bestellung_positionen", f"{EK}.bestellvorschlag_positionen", CONTRACT_POSITIONS,
    "public.einkauf_anfragen_positionen", "public.einkauf_angebote_positionen",
    "public.einkauf_lieferschein_positionen", "public.einkauf_zahlungslauf_posten",
    INVOICES, "public.einkauf_rechnungseingang_positionen", RECEIPTS, "public.einkauf_wareneingang_positionen",
    "public.einkauf_abgleich_ergebnisse",
)
NEW_TENANT_COLUMN = (
    f"{EK}.bestellung_positionen", f"{EK}.bestellvorschlag_positionen", CONTRACT_POSITIONS,
    "public.einkauf_anfragen_positionen", "public.einkauf_angebote_positionen",
    "public.einkauf_lieferschein_positionen", "public.einkauf_zahlungslauf_posten",
    "public.einkauf_rechnungseingang_positionen", "public.einkauf_wareneingang_positionen",
)
NEW_TENANT_HEADS = (INVOICES, RECEIPTS, "public.einkauf_abgleich_ergebnisse")
DEFAULT_TO_CONTEXT = tuple(f"public.einkauf_{name}" for name in (
    "angebote", "anlieferavis", "auftragsbestaetigungen", "warengruppen", "zahlungslaeufe"))
# Eltern in der Reihenfolge, in der sie angelegt werden (spaetere verweisen auf fruehere).
PARENTS = (SUPPLIERS, CONTRACTS, PROPOSALS, ORDERS, CONTRACT_POSITIONS, RFQS, REQUESTS, OFFERS,
           DELIVERY_NOTES, PAYMENT_RUNS, INVOICES, RECEIPTS)

# (Kind, Spalte, Eltern); P5-Tabellen behalten ihre Policies und bekommen nur den Schluessel.
LINKS = (
    (f"{EK}.bestellung_positionen", "bestellung_id", ORDERS),
    (f"{EK}.bestellvorschlag_positionen", "vorschlag_id", PROPOSALS),
    (CONTRACT_POSITIONS, "kontrakt_id", CONTRACTS),
    ("public.einkauf_anfragen_positionen", "anfrage_id", REQUESTS),
    ("public.einkauf_angebote_positionen", "angebot_id", OFFERS),
    ("public.einkauf_lieferschein_positionen", "lieferschein_id", DELIVERY_NOTES),
    ("public.einkauf_zahlungslauf_posten", "zahlungslauf_id", PAYMENT_RUNS),
    ("public.einkauf_rechnungseingang_positionen", "rechnungseingang_id", INVOICES),
    ("public.einkauf_wareneingang_positionen", "wareneingang_id", RECEIPTS),
    (f"{EK}.bestellung_positionen", "kontrakt_pos_id", CONTRACT_POSITIONS),
    (ORDERS, "kontrakt_id", CONTRACTS), (ORDERS, "lieferant_id", SUPPLIERS), (ORDERS, "vorschlag_id", PROPOSALS),
    (f"{EK}.bestellvorschlag_positionen", "kontrakt_id", CONTRACTS),
    (f"{EK}.bestellvorschlag_positionen", "lieferant_id", SUPPLIERS),
    (CONTRACTS, "lieferant_id", SUPPLIERS),
    (f"{EK}.artikel_lager_parameter", "std_lieferant_id", SUPPLIERS),
    (f"{EK}.rfq_quotes", "rfq_id", RFQS),
)
CHILDREN = tuple(dict.fromkeys(child for child, _, _ in LINKS))
# Feste Werte: Rechnungen im Pruefstatus, damit die Fachkette pruefen kann.
VALUES = {INVOICES: {"status": "OFFEN"}}
AUXILIARY = ("public.docs_store", "domain_shared.users")


def _key(conn, table: str) -> str:
    return support.primary_key(conn, table)


def _links_of(table: str):
    return [(column, parent) for child, column, parent in LINKS if child == table]


@pytest.fixture(scope="module")
def probe():
    tables = tuple(dict.fromkeys(ISOLATED + PARENTS + CHILDREN + DEFAULT_TO_CONTEXT + AUXILIARY))
    with support.probe(tables) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            # Eltern zuerst; jede Zeile verweist auf die Eltern desselben Mandanten.
            for table in tuple(dict.fromkeys(PARENTS + ISOLATED + CHILDREN)):
                links = {column: rows[parent, tenant] for column, parent in _links_of(table) if (parent, tenant) in rows}
                full = support.seed_row(conn, table, tenant, **links, **VALUES.get(table, {}))
                rows["full", table, tenant] = full
                rows[table, tenant] = str(full[_key(conn, table)])
        for parent in PARENTS:
            rows["spare", parent] = str(support.seed_row(conn, parent, B, **VALUES.get(parent, {}))["id"])
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
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM],
                                    key=_key(conn, table), values=VALUES.get(table))


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


def test_kind_und_beleg_erben_den_mandanten_vom_kontext(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        for table in NEW_TENANT_COLUMN + NEW_TENANT_HEADS:
            links = {column: rows[parent, A] for column, parent in _links_of(table)}
            row = support.seed_row(conn, table, None, **links)
            assert row["tenant_id"] == A, table


def test_p5_vorgabe_ist_der_kontext_nicht_default(db):
    """Fuenf P5-Tabellen setzten tenant_id ohne Angabe auf 'default'."""
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
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE id = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "foreign key constraint" in message and "_tena" in message, (parent, message)


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, ORDERS, rows[ORDERS, A], rows[ORDERS, B])
    support.assert_background_needs_explicit_context(conn, INVOICES, rows[INVOICES, A], rows[INVOICES, B])
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_waren_und_rechnungseingaenge_nur_eigener_mandant(db):
    from sqlalchemy.orm import Session

    from app.core.exceptions import EntityNotFoundError
    from app.services.einkauf_compat_service import EinkaufCompatService

    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))  # ohne RLS: der Code selbst muss filtern (live ist RLS noch aus)
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            service = EinkaufCompatService(session, A)
            assert {r["id"] for r in service.list_goods_receipts()} == {rows[RECEIPTS, A]}
            assert {r["id"] for r in service.list_rechnungseingaenge()} == {rows[INVOICES, A]}
            # Fremde Rechnung: nicht pruefbar, nicht freigebbar (vorher ohne Mandantenfilter)
            for action in (service.pruefen_rechnung, service.freigeben_rechnung, service.verbuchen_rechnung):
                with pytest.raises(EntityNotFoundError):
                    action(rows[INVOICES, B])
    finally:
        session.close()


def test_fachkette_rechnungspruefung_protokolliert_den_angemeldeten_nutzer(db):
    """Das Pruefprotokoll trug einen beliebigen aktiven Nutzer des Mandanten (LIMIT 1), Fehler wurden verschluckt."""
    from fastapi import HTTPException
    from sqlalchemy.orm import Session

    from app.services.einkauf_compat_service import EinkaufCompatService

    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))  # ohne RLS: der Code selbst muss zuordnen
    users = [str(support.seed_row(conn, "domain_shared.users", A, is_active=True)["id"]) for _ in range(2)]
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            with pytest.raises(HTTPException) as caught:
                EinkaufCompatService(session, A).pruefen_rechnung(rows[INVOICES, A])
            assert caught.value.status_code == 403
            session.rollback()
            EinkaufCompatService(session, A, actor=users[1]).pruefen_rechnung(rows[INVOICES, A])
        logged = conn.execute(sa.text(
            "SELECT user_id FROM domain_shared.audit_logs WHERE entity_id = :i AND entity_type = 'rechnungseingang'"),
            {"i": rows[INVOICES, A]}).scalars().all()
        assert logged == [users[1]]
    finally:
        session.close()


def test_fachkette_bestellstatus_nur_eigene_bestellung(db):
    from sqlalchemy.orm import Session

    from app.services.proc_bestellung_lifecycle_service import BestellungLifecycleError, transition_bestellung_status

    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))  # ohne RLS: der Code selbst muss filtern
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            with pytest.raises(BestellungLifecycleError, match="nicht gefunden"):
                transition_bestellung_status(session, rows[PROC_ORDERS, B], A, "STORNIERT", "pruefer")
    finally:
        session.close()


# --- ohne Datenbank -----------------------------------------------------------------------------

ROUTES = ("bestellung_transition_endpoint", "buche_wareneingang_endpoint", "update_we_qs_endpoint",
          "rechnungspruefung_endpoint", "rechnungsfreigabe_endpoint")


@pytest.mark.parametrize("name", ROUTES)
def test_beschaffungswege_nehmen_den_mandanten_aus_dem_token(name):
    """Vorher galt der Kopf X-Tenant-ID, ohne ihn der Mandant "default"."""
    import inspect

    from app.core.tenant import get_tenant_id

    procurement = importlib.import_module("app.api.v1.endpoints.procurement_match")
    parameters = inspect.signature(getattr(procurement, name)).parameters
    assert "x_tenant_id" not in parameters
    assert parameters["tenant_id"].default.dependency is get_tenant_id
