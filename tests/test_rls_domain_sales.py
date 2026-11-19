"""RLS-Domain Sales: Angebote und ihre Positionen als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).

Auftraege sind seit BELEG-052 (``docflow_auftraege_uebernahme_20261109``) DocFlow-Belege; ``domain_crm.sales_orders``
war eine Sicht mit ``security_invoker``. Seit S5 (``beleg_altspeicher_entfernen_20261117``) gibt es die alten
Speicher fuer Lieferschein, Gutschrift und Quittung nicht mehr; ihre Mandantentrennung ist die von DocFlow
(``test_rls_domain_docflow``).
"""

from __future__ import annotations

import asyncio

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

pytestmark = pytest.mark.integration

OFFERS, OFFER_ITEMS = "domain_crm.sales_offers", "domain_crm.sales_offer_items"
DOCFLOW = "domain_docflow.document_headers"
ORDERS = DOCFLOW  # Auftraege sind DocFlow-Belege (doc_type sales_order)
PICK_LISTS = "domain_inventory.pick_lists"
CUSTOMERS = "domain_crm.customers"
HEADS = (OFFERS,)
CHILDREN = {OFFER_ITEMS: ("offer_id", OFFERS)}
ISOLATED = HEADS


def _head_values(head: str, rows: dict, tenant: str) -> dict:
    if head == OFFERS:
        return {"customer_id": rows["customer", tenant]}
    return {}


def _child_values(child: str, parent_id: str, n: int) -> dict:
    column, _ = CHILDREN[child]
    values = {column: parent_id}
    values["line_number"] = 100 + n
    return values


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (OFFER_ITEMS, PICK_LISTS, DOCFLOW)) as conn:
        for role in support.APP_ROLES:
            for schema in ("domain_crm", "domain_sales", "domain_inventory"):
                conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {schema} TO {role}"))
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            # Koepfe verweisen im frischen Schema per FK auf den Kundenstamm (Klasse B, zurueckgestellt).
            rows["customer", tenant] = support.insert_row(conn, CUSTOMERS, tenant)
            for head in HEADS:
                rows[head, tenant] = support.insert_row(conn, head, tenant, **_head_values(head, rows, tenant))
            for child, (_column, parent) in CHILDREN.items():
                rows[child, tenant] = support.insert_row(conn, child, tenant,
                                                         **_child_values(child, rows[parent, tenant], 0))
            rows[ORDERS, tenant] = support.insert_row(conn, DOCFLOW, tenant, doc_type="sales_order", status="open",
                                                      customer_id=rows["customer", tenant])
        rows[PICK_LISTS, A] = support.insert_row(conn, PICK_LISTS, A)
        rows[PICK_LISTS, B] = support.insert_row(conn, PICK_LISTS, B)
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
    for table in ISOLATED + (PICK_LISTS,):
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    def new_row(tenant):
        return support.insert_row(conn, table, tenant, **_head_values(table, rows, tenant))
    if table in CHILDREN:
        _column, parent = CHILDREN[table]

        def new_row(tenant):
            return support.insert_row(conn, table, tenant, **_child_values(table, rows[parent, tenant], 1))
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], new_row=new_row)


@pytest.mark.parametrize("child", list(CHILDREN))
def test_keine_position_unter_fremdem_kopf(db, child):
    conn, rows = db
    column, parent = CHILDREN[child]
    foreign = rows[parent, B]
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, child, A, **_child_values(child, foreign, 2))
        assert f"fk_{child.split('.')[1]}_{column}_tenant" in message, message
        extra = ", line_number = 999"
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p{extra} WHERE id = :i",
                                   {"p": foreign, "i": rows[child, A]})
        assert f"fk_{child.split('.')[1]}_{column}_tenant" in message, message


def test_kopf_mit_positionen_behaelt_seinen_mandanten(db):
    conn, rows = db
    for head in (OFFERS,):
        message = support.as_owner_rejected(conn, f"UPDATE {head} SET tenant_id = :b WHERE id = :i",
                                            {"b": B, "i": rows[head, A]})
        assert "_tenant" in message, (head, message)


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, OFFERS, rows[OFFERS, A], rows[OFFERS, B])
    support.assert_background_needs_explicit_context(conn, OFFERS, rows[OFFERS, A], rows[OFFERS, B])
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_pickliste_bucht_nur_eigenen_auftrag(db):
    import app.infrastructure.models  # noqa: F401  # ORM-Fremdschluessel
    from app.api.v1.endpoints import pick_lists as ep

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    try:
        with tenant_scope(A, "test"):
            listed = run(ep.list_pick_lists(tenant_id=A, skip=0, limit=25, db=session))
            assert {p.id for p in listed.items} == {rows[PICK_LISTS, A]}
            for call in (
                lambda: ep.cancel_pick_list(rows[PICK_LISTS, B], tenant_id=A, db=session),
                lambda: ep.book_pick_list_order(rows[PICK_LISTS, A], ep.PickListBooking(order_id=rows[ORDERS, B]),
                                                tenant_id=A, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 404
            booked = run(ep.book_pick_list_order(rows[PICK_LISTS, A], ep.PickListBooking(order_id=rows[ORDERS, A]),
                                                 tenant_id=A, db=session))
            assert booked.status == "booked"
            # Den Auftrag (DocFlow) schreibt die Pickliste nicht um; sein Stand folgt aus den Folgebelegen.
            assert support.keys(conn, ORDERS, "status", "id = :i", {"i": rows[ORDERS, A]}) == {"open"}
        with tenant_scope(B, "test"):
            assert support.keys(conn, ORDERS, "status", "id = :i", {"i": rows[ORDERS, B]}) == {"open"}
    finally:
        session.close()
