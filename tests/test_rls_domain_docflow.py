"""RLS-Domain docflow: Belegkoepfe, Positionen, Archivartefakte, E-Rechnungs-XML, TSE als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import asyncio
import hashlib

import pytest
import sqlalchemy as sa
from starlette.requests import Request
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

pytestmark = pytest.mark.integration

S = "domain_docflow"
HEADERS = f"{S}.document_headers"
ITEMS = f"{S}.document_items"
ARTIFACTS = f"{S}.document_artifacts"
XML = f"{S}.invoice_xml_store"
TSE = f"{S}.pos_tse_devices"
TERMINALS = f"{S}.pos_terminals"
ISOLATED = (HEADERS, ITEMS, ARTIFACTS, XML, TSE)
LINKS = ((ITEMS, "header_id", HEADERS), (ARTIFACTS, "header_id", HEADERS), (XML, "header_id", HEADERS),
         (TSE, "terminal_id", TERMINALS))


def _values(table: str, tenant: str, rows: dict, n: int = 0) -> dict:
    if table in (ITEMS, ARTIFACTS, XML):
        values = {"header_id": rows[HEADERS, tenant]}
        if table == ITEMS:
            values["line_number"] = 100 + n
        if table == ARTIFACTS:
            values["artifact_type"] = "pdf"
        if table == XML and n:
            values["header_id"] = rows["header2", tenant]  # UNIQUE (tenant_id, header_id)
        return values
    if table == TSE:
        return {"terminal_id": rows[TERMINALS, tenant], "status": "active"}
    return {}


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (TERMINALS,)) as conn:
        # Trigger schreiben die Statushistorie (P5-Tabelle); live hat valeo_app Rechte am ganzen Schema.
        for role in support.APP_ROLES:
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {S} TO {role}"))
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            rows[HEADERS, tenant] = support.insert_row(conn, HEADERS, tenant)
            rows["header2", tenant] = support.insert_row(conn, HEADERS, tenant)
            rows[TERMINALS, tenant] = support.insert_row(conn, TERMINALS, tenant)
        for table in ISOLATED[1:]:
            for tenant in (A, B, SYSTEM):
                rows[table, tenant] = support.insert_row(conn, table, tenant, **_values(table, tenant, rows))
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_policy_form(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    new_row = None
    if table != HEADERS:
        def new_row(tenant):
            return support.insert_row(conn, table, tenant, **_values(table, tenant, rows, n=1))
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], new_row=new_row)


@pytest.mark.parametrize("child, column, parent", LINKS)
def test_kein_verweis_auf_fremde_elternsaetze(db, child, column, parent):
    conn, rows = db
    foreign = rows["header2" if parent == HEADERS else parent, B] if parent == HEADERS else rows[parent, B]
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, child, A, **{**_values(child, A, rows, n=2), column: foreign})
        assert "_tenant" in message and "foreign key" in message, message
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": foreign, "i": rows[child, A]})
        assert "_tenant" in message and "foreign key" in message, message


def test_kopf_mit_positionen_behaelt_seinen_mandanten(db):
    conn, rows = db
    message = support.as_owner_rejected(conn, f"UPDATE {HEADERS} SET tenant_id = :b WHERE id = :i",
                                        {"b": B, "i": rows[HEADERS, A]})
    assert "_tenant" in message


def test_kontextwechsel_und_savepoint(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, HEADERS, rows[HEADERS, A], rows[HEADERS, B])


def test_hintergrund_nur_mit_ausdruecklichem_kontext(db):
    conn, rows = db
    support.assert_background_needs_explicit_context(conn, ITEMS, rows[ITEMS, A], rows[ITEMS, B])


def test_pool_wiederverwendung():
    support.assert_pool_reuse_keeps_no_tenant()


def _request() -> Request:
    request = Request({"type": "http", "method": "POST", "path": "/gobd", "headers": [], "query_string": b""})
    request.state.token_claims = {"sub": "pruefer", "iss": "test", "tenant_id": A}
    return request


def test_fachkette_e_rechnung_und_archiv(db, monkeypatch):
    from app.api.v1.endpoints import gobd_archiv as ep

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    digest = hashlib.sha256(b"rls").hexdigest()
    try:
        with tenant_scope(A, "test"):
            stored = run(ep.store_invoice_xml(
                ep.InvoiceXmlCreate(header_id=rows["header2", A], content_hash_sha256=digest, storage_key="xml/1"),
                _request(), tenant_id=A, db=session))
            assert stored.tenant_id == A
            assert run(ep.get_invoice_xml(rows["header2", A], tenant_id=A, db=session)).id == stored.id
            checked = run(ep.set_invoice_xml_validation(
                rows["header2", A], ep.InvoiceXmlValidateIn(validation_status="valid"), tenant_id=A, db=session))
            assert checked.validation_status == "valid"
            listed = run(ep.list_document_artifacts(header_id=rows[HEADERS, A], tenant_id=A, db=session))
            assert {a.id for a in listed} == {rows[ARTIFACTS, A]}
        with tenant_scope(B, "test"):
            assert run(ep.get_invoice_xml(rows["header2", A], tenant_id=B, db=session)) is None
            assert run(ep.list_document_artifacts(header_id=rows[HEADERS, A], tenant_id=B, db=session)) == []
            # E-Rechnung zu einem fremden Kopf: der Verbund-FK weist sie ab
            with pytest.raises(Exception):
                run(ep.store_invoice_xml(
                    ep.InvoiceXmlCreate(header_id=rows["header2", A], content_hash_sha256=digest, storage_key="xml/2"),
                    _request(), tenant_id=B, db=session))
    finally:
        session.close()
