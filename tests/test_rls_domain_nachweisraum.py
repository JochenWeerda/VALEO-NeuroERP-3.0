"""RLS-Domain nachweisraum: Nachweisdokumente und GoBD-Exporte als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

DOCUMENTS = "domain_nachweisraum.nachweisraum_dokumente"
EXPORTS = "domain_nachweisraum.gobd_exporte"
AUDIT = "domain_nachweisraum.nachweisraum_audit_log"
ISOLATED = (DOCUMENTS, EXPORTS)
ENDPOINT = Path(support.ROOT) / "app" / "api" / "v1" / "endpoints" / "doc_nachweisraum_actions.py"


@pytest.mark.unit
def test_endpunkte_nehmen_den_mandanten_nur_aus_dem_token():
    tree = ast.parse(ENDPOINT.read_text(encoding="utf-8"))
    routes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
              and any(ast.unparse(d).startswith("router.") for d in n.decorator_list)]
    assert len(routes) == 4
    for route in routes:
        defaults = [ast.unparse(d) for d in route.args.defaults]
        assert "Depends(get_tenant_id)" in defaults, route.name
        assert not any(d.startswith("Header(") for d in defaults), route.name


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (AUDIT,)) as conn:
        rows = {}
        for table in ISOLATED:
            for tenant in (A, B, SYSTEM):
                rows[table, tenant] = support.insert_row(conn, table, tenant)
        for tenant in (A, B):
            rows[AUDIT, tenant] = support.insert_row(conn, AUDIT, tenant, dokument_id=rows[DOCUMENTS, tenant])
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


@pytest.mark.integration
def test_policy_form(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.integration
@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM])


@pytest.mark.integration
def test_pruefprotokoll_nicht_unter_fremdem_dokument(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, AUDIT, A, dokument_id=rows[DOCUMENTS, B])
        assert "fk_nachweisraum_audit_log_dokument_tenant" in message
        message = support.rejected(conn, f"UPDATE {AUDIT} SET dokument_id = :d WHERE id = :i",
                                   {"d": rows[DOCUMENTS, B], "i": rows[AUDIT, A]})
        assert "fk_nachweisraum_audit_log_dokument_tenant" in message
    # Ein Dokument mit Pruefprotokoll verschwindet auch fuer den Eigentuemer nicht still.
    assert "fk_nachweisraum_audit_log_dokument_tenant" in support.as_owner_rejected(
        conn, f"DELETE FROM {DOCUMENTS} WHERE id = :i", {"i": rows[DOCUMENTS, A]})


@pytest.mark.integration
def test_kontextwechsel_und_savepoint(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, DOCUMENTS, rows[DOCUMENTS, A], rows[DOCUMENTS, B])


@pytest.mark.integration
def test_hintergrund_nur_mit_ausdruecklichem_kontext(db):
    conn, rows = db
    support.assert_background_needs_explicit_context(conn, EXPORTS, rows[EXPORTS, A], rows[EXPORTS, B])


@pytest.mark.integration
def test_pool_wiederverwendung():
    support.assert_pool_reuse_keeps_no_tenant()


@pytest.mark.integration
def test_fachkette_dokument_und_gobd_export(db):
    from app.services import doc_nachweisraum_lifecycle_service as svc

    conn, _ = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            dokument = svc.create_dokument(session, A, "LIEFERSCHEIN", "LS 1", "ls-1", "delivery_note",
                                           "/nachweise/ls-1.pdf", operator="pruefer")
            geprueft = svc.transition_dokument(session, str(dokument["id"]), "IN_PRUEFUNG", A, "pruefer")
            assert geprueft["status"] == "IN_PRUEFUNG"
            assert len(support.keys(conn, AUDIT, "id", "dokument_id = :d", {"d": dokument["id"]})) == 1
            export = svc.create_gobd_export(session, A, "2026-09", ["ls-1"], operator="pruefer")
            assert svc.transition_gobd_export(session, str(export["id"]), "IN_ERSTELLUNG", A, "pruefer")[
                "status"] == "IN_ERSTELLUNG"
        with tenant_scope(B, "test"):
            for call in (
                lambda: svc.transition_dokument(session, str(dokument["id"]), "FREIGEGEBEN", B, "fremd"),
                lambda: svc.transition_gobd_export(session, str(export["id"]), "EXPORTIERT", B, "fremd"),
            ):
                with pytest.raises(svc.NachweisraumError, match="nicht gefunden"):
                    call()
            assert support.keys(conn, AUDIT, "id", "dokument_id = :d", {"d": dokument["id"]}) == set()
        with tenant_scope(A, "test"):
            assert svc.transition_dokument(session, str(dokument["id"]), "FREIGEGEBEN", A, "pruefer")[
                "status"] == "FREIGEGEBEN"
            assert support.keys(conn, EXPORTS, "status", "id = :i", {"i": export["id"]}) == {"IN_ERSTELLUNG"}
    finally:
        session.close()
