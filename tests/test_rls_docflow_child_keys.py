"""Verbund-FKs der docflow-Kinder: kein Verweis auf Koepfe, Positionen, Artefakte, TSE fremder Mandanten.

Migration rls_docflow_child_keys_20261027; Pruefhilfe tests/rls_domain_support.py (valeo_app).
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B

pytestmark = pytest.mark.integration

S = "domain_docflow"
HEADERS, ITEMS, ARTIFACTS, TERMINALS, TSE = (f"{S}.{t}" for t in (
    "document_headers", "document_items", "document_artifacts", "pos_terminals", "pos_tse_devices"))
HEADER_LINKS, LINKS_T, POSTINGS, RETURNS, RECEIPTS, NOTICES = (f"{S}.{t}" for t in (
    "document_header_links", "document_links", "document_postings", "document_return_cases",
    "pos_receipt_compliance", "pos_regulatory_notices"))

# child, column, parent key in rows
REFERENCES = (
    (HEADER_LINKS, "from_header_id", "header"), (HEADER_LINKS, "to_header_id", "header"),
    (LINKS_T, "from_header_id", "header"), (LINKS_T, "to_header_id", "header"),
    (LINKS_T, "from_item_id", "item"), (LINKS_T, "to_item_id", "item"),
    (POSTINGS, "header_id", "header"),
    (RETURNS, "header_id", "header"), (RETURNS, "artifact_id", "artifact"),
    (RECEIPTS, "header_id", "header"), (RECEIPTS, "original_header_id", "header"),
    (NOTICES, "tse_device_id", "tse"),
)


def _child_values(child: str, rows: dict, tenant: str) -> dict:
    h, h2 = rows["header", tenant], rows["header2", tenant]
    return {
        HEADER_LINKS: {"from_header_id": h, "to_header_id": h2},
        LINKS_T: {"from_header_id": h, "to_header_id": h2, "from_item_id": rows["item", tenant],
                  "to_item_id": rows["item", tenant]},
        POSTINGS: {"header_id": h, "posting_type": "post"},
        RETURNS: {"header_id": h, "artifact_id": rows["artifact", tenant], "return_status": "expected",
                  "shipping_status": "not_sent", "subject_type": "customer"},
        RECEIPTS: {"header_id": h, "original_header_id": h2, "transaction_type": "storno", "correction_type": "storno"},
        NOTICES: {"tse_device_id": rows["tse", tenant], "notice_status": "draft", "notice_type": "install"},
    }[child]


@pytest.fixture(scope="module")
def probe():
    tables = (HEADERS, ITEMS, ARTIFACTS, TERMINALS, TSE, HEADER_LINKS, LINKS_T, POSTINGS, RETURNS, RECEIPTS, NOTICES)
    with support.probe(tables) as conn:
        for role in support.APP_ROLES:
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {S} TO {role}"))
        support.ensure_tenants(conn, A, B)
        rows = {}
        for tenant in (A, B):
            rows["header", tenant] = support.insert_row(conn, HEADERS, tenant)
            rows["header2", tenant] = support.insert_row(conn, HEADERS, tenant)
            rows["item", tenant] = support.insert_row(conn, ITEMS, tenant, header_id=rows["header", tenant], line_number=1)
            rows["artifact", tenant] = support.insert_row(conn, ARTIFACTS, tenant, header_id=rows["header", tenant],
                                                          artifact_type="pdf")
            rows["terminal", tenant] = support.insert_row(conn, TERMINALS, tenant)
            rows["tse", tenant] = support.insert_row(conn, TSE, tenant, terminal_id=rows["terminal", tenant], status="active")
            for child in (HEADER_LINKS, LINKS_T, POSTINGS, RETURNS, RECEIPTS, NOTICES):
                rows[child, tenant] = support.insert_row(conn, child, tenant, **_child_values(child, rows, tenant))
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


@pytest.mark.parametrize("child, column, parent", REFERENCES, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in REFERENCES])
def test_kein_verweis_auf_fremde_elternsaetze(db, child, column, parent):
    conn, rows = db
    foreign = rows[parent, B]
    with tenant_scope(A, "test"):
        values = {**_child_values(child, rows, A), column: foreign}
        if child == RECEIPTS and column == "original_header_id":
            values["header_id"] = rows["header2", A]  # UNIQUE (tenant_id, header_id) der Belegpruefung
        message = support.rejected_insert_with(conn, child, A, **values)
        assert f"fk_{child.split('.')[1]}_{column}_tenant" in message, message
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": foreign, "i": rows[child, A]})
        assert f"fk_{child.split('.')[1]}_{column}_tenant" in message, message


def test_set_null_leert_nur_den_verweis(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        assert support.affected(conn, f"DELETE FROM {ITEMS} WHERE id = :i", {"i": rows["item", A]}) == 1
        link = conn.execute(sa.text(f"SELECT from_item_id, to_item_id, tenant_id FROM {LINKS_T} WHERE id = :i"),
                            {"i": rows[LINKS_T, A]}).one()
        assert tuple(link) == (None, None, A)


def test_rueckgabefall_haelt_seinen_kopf(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        message = support.rejected(conn, f"DELETE FROM {HEADERS} WHERE id = :i", {"i": rows["header", A]})
        assert "fk_document_return_cases_header_id_tenant" in message


def test_policies_der_kindtabellen_unveraendert(db):
    conn, _ = db
    for child in (HEADER_LINKS, LINKS_T, POSTINGS, RETURNS, RECEIPTS, NOTICES):
        assert support.shape(conn, child)[0] in ("getrennt", "getrennt_system"), child
