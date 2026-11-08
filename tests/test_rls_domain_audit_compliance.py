"""RLS-Domain audit/compliance: Attestierungen, Loeschantraege, Intrastat, PCN-Verlauf als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

pytestmark = pytest.mark.integration

ATTESTATIONS = "domain_audit.attestations"
PCN_LOG = "domain_compliance.compliance_pcn_status_log"
PCN = "domain_compliance.compliance_pcn_meldungen"
ERASURE = "domain_compliance.data_erasure_requests"
INTRASTAT = "domain_compliance.intrastat_meldungen"
ISOLATED = (ATTESTATIONS, PCN_LOG, ERASURE, INTRASTAT)


def _values(table: str, tenant: str, rows: dict) -> dict:
    """Pflichtwerte, die Pruefbedingungen oder Fremdschluessel erfuellen."""
    if table == ATTESTATIONS:
        return {"action": "print", "created_by": rows["user", tenant]}
    if table == INTRASTAT:
        return {"meldungsart": "EINGANG", "meldezeitraum": "2026-01"}
    if table == PCN_LOG:
        return {"meldung_id": rows[PCN, tenant]}
    return {}


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (PCN,)) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            rows["user", tenant] = support.insert_row(conn, "domain_shared.users", tenant)
            rows[PCN, tenant] = support.insert_row(conn, PCN, tenant)
        for table in ISOLATED:
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


def test_policy_form_und_pflichtmandant(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table
    assert support.as_owner(conn, (
        "SELECT is_nullable FROM information_schema.columns WHERE table_schema = 'domain_compliance' "
        "AND table_name = 'compliance_pcn_status_log' AND column_name = 'tenant_id'")) == [("NO",)]


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db

    def new_row(tenant):
        return support.insert_row(conn, table, tenant, **_values(table, tenant, rows))

    support.assert_tenant_isolation(
        conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], new_row=new_row)


def test_pcn_verlauf_nicht_unter_fremder_meldung(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, PCN_LOG, A, meldung_id=rows[PCN, B])
        assert "fk_compliance_pcn_status_log_meldung_tenant" in message
        message = support.rejected(conn, f"UPDATE {PCN_LOG} SET meldung_id = :m WHERE id = :i",
                                   {"m": rows[PCN, B], "i": rows[PCN_LOG, A]})
        assert "fk_compliance_pcn_status_log_meldung_tenant" in message
    # Eine Meldung mit Verlauf verschwindet auch fuer den Eigentuemer nicht still.
    assert "fk_compliance_pcn_status_log_meldung_tenant" in support.as_owner_rejected(
        conn, f"DELETE FROM {PCN} WHERE id = :i", {"i": rows[PCN, A]})


def test_kontextwechsel_und_savepoint(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, ERASURE, rows[ERASURE, A], rows[ERASURE, B])


def test_hintergrund_nur_mit_ausdruecklichem_kontext(db):
    conn, rows = db
    support.assert_background_needs_explicit_context(conn, INTRASTAT, rows[INTRASTAT, A], rows[INTRASTAT, B])


def test_pool_wiederverwendung():
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_pcn_lebenszyklus(db):
    from app.services import compliance_pcn_lifecycle_service as pcn

    conn, _ = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            created = pcn.create_pcn_meldung(session, A, "art-1", "UFI", operator="pruefer")
            moved = pcn.transition_pcn_status(session, created["id"], A, "VALIDATED", operator="pruefer")
            assert moved["previous_status"] == "DRAFT"
            assert len(support.keys(conn, PCN_LOG, "id", "meldung_id = :m", {"m": created["id"]})) == 2
        with tenant_scope(B, "test"):
            for call in (
                lambda: pcn.transition_pcn_status(session, created["id"], B, "SUBMITTED"),
                lambda: pcn.withdraw_pcn_meldung(session, created["id"], B, "fremd"),
            ):
                with pytest.raises(pcn.PCNError, match="nicht gefunden"):
                    call()
            assert support.keys(conn, PCN_LOG, "id", "meldung_id = :m", {"m": created["id"]}) == set()
        with tenant_scope(A, "test"):
            assert pcn.withdraw_pcn_meldung(session, created["id"], A, "zurueck")["status"] == "WITHDRAWN"
            assert len(support.keys(conn, PCN_LOG, "id", "meldung_id = :m", {"m": created["id"]})) == 3
    finally:
        session.close()


def test_fachkette_intrastat(db):
    from app.api.v1.endpoints import intrastat as ep

    conn, _ = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    payload = ep.IntrastatMeldungCreate(
        meldezeitraum="2026-09", meldungsart="EINGANG", cn8_warennummer="10019900", ursprungsland="FR",
        bestimmungsland="DE", statistischer_wert_eur=1000, nettomasse_kg=500, menge=500,
        mengeneinheit="kg", geschaeftsvorgang_code=11)
    try:
        with tenant_scope(A, "test"):
            created = ep.create_meldung(payload, db=session, tenant_id=A)
            assert created["id"] in {m["id"] for m in ep.list_meldungen(None, None, db=session, tenant_id=A)}
            assert ep.update_meldung(created["id"], ep.IntrastatMeldungUpdate(menge=600), db=session,
                                     tenant_id=A)["status"] == "aktualisiert"
        with tenant_scope(B, "test"):
            assert created["id"] not in {m["id"] for m in ep.list_meldungen(None, None, db=session, tenant_id=B)}
            for call in (
                lambda: ep.update_meldung(created["id"], ep.IntrastatMeldungUpdate(menge=1), db=session, tenant_id=B),
                lambda: ep.delete_meldung(created["id"], db=session, tenant_id=B),
                lambda: ep.validate_meldung(created["id"], db=session, tenant_id=B),
            ):
                with pytest.raises(HTTPException) as exc:
                    call()
                assert exc.value.status_code == 404
        with tenant_scope(A, "test"):
            assert support.keys(conn, INTRASTAT, "menge::int::text", "id = :i", {"i": created["id"]}) == {"600"}
            ep.delete_meldung(created["id"], db=session, tenant_id=A)
            assert support.keys(conn, INTRASTAT, "id", "id = :i", {"i": created["id"]}) == set()
    finally:
        session.close()


def test_fachkette_loeschantrag(db):
    from app.api.v1.endpoints import compliance_dsgvo as ep

    conn, _ = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    try:
        with tenant_scope(A, "test"):
            created = run(ep.create_erasure_request(ep.ErasureRequestIn(
                requester_name="Betroffene", requester_email="b@example.org", subject_id="k-1",
                subject_type="CUSTOMER"), tenant_id=A, db=session))
            assert run(ep.get_erasure_request(created["id"], tenant_id=A, db=session))["status"] == "EINGEGANGEN"
        with tenant_scope(B, "test"):
            assert created["id"] not in {r["id"] for r in run(ep.list_erasure_requests(None, tenant_id=B, db=session))}
            for call in (
                lambda: ep.get_erasure_request(created["id"], tenant_id=B, db=session),
                lambda: ep.reject_erasure_request(created["id"], ep.ErasureRejectIn(reason="fremd"), tenant_id=B, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 404
        with tenant_scope(A, "test"):
            run(ep.reject_erasure_request(created["id"], ep.ErasureRejectIn(reason="Aufbewahrungspflicht"),
                                          tenant_id=A, db=session))
            assert run(ep.get_erasure_request(created["id"], tenant_id=A, db=session))["status"] == "ABGELEHNT"
    finally:
        session.close()
