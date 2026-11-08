"""RLS-Domain KI: Agentenvorschlaege, Werkzeugausfuehrungen, Wissensversionen als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

pytestmark = pytest.mark.integration

PROPOSALS = "public.agent_proposals"
EXECUTIONS = "public.mcp_tool_executions"
OBJECTS = "domain_shared.knowledge_objects"
VERSIONS = "domain_shared.knowledge_versions"
KEYS = {PROPOSALS: "proposal_id", EXECUTIONS: "idempotency_key", VERSIONS: "id"}


def _proposal(conn, tenant):
    return support.insert_row(conn, PROPOSALS, tenant, key="proposal_id", action_type="sales_credit_note_booking",
                              risk_level="high")


def _execution(conn, tenant):
    return support.insert_row(conn, EXECUTIONS, tenant, key="idempotency_key", result="{}")


def _version(conn, tenant, rows, n=1):
    return support.insert_row(conn, VERSIONS, tenant, knowledge_id=rows[OBJECTS, tenant], version=n,
                              format="MARKDOWN", inhalt="x")


@pytest.fixture(scope="module")
def probe():
    with support.probe((PROPOSALS, EXECUTIONS, OBJECTS, VERSIONS)) as conn:
        for role in support.APP_ROLES:
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA domain_shared TO {role}"))
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            rows[OBJECTS, tenant] = support.insert_row(conn, OBJECTS, tenant, key="knowledge_id", titel="W",
                                                       typ="SOP", status="FREIGEGEBEN")
            rows["object2", tenant] = support.insert_row(conn, OBJECTS, tenant, key="knowledge_id", titel="W2",
                                                         typ="SOP", status="FREIGEGEBEN")
            rows[PROPOSALS, tenant] = _proposal(conn, tenant)
            rows[EXECUTIONS, tenant] = _execution(conn, tenant)
            rows[VERSIONS, tenant] = _version(conn, tenant, rows)
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
    assert support.shape(conn, PROPOSALS) == ("getrennt", "")
    assert support.shape(conn, EXECUTIONS) == ("getrennt", "")
    assert support.shape(conn, VERSIONS) == ("getrennt_system", "")


@pytest.mark.parametrize("table, make", [(PROPOSALS, _proposal), (EXECUTIONS, _execution)], ids=["proposals", "executions"])
def test_mandantengrenze_mandanteneigene_tabellen(db, table, make):
    conn, rows = db
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM],
                                    key=KEYS[table], new_row=lambda tenant: make(conn, tenant))


def test_versionen_gemeinsam_lesbar_nur_eigene_schreibbar(db):
    conn, rows = db
    with tenant_scope(A, "test"):
        visible = support.keys(conn, VERSIONS)
        assert {rows[VERSIONS, A], rows[VERSIONS, SYSTEM]} <= visible and rows[VERSIONS, B] not in visible
        for other in (rows[VERSIONS, B], rows[VERSIONS, SYSTEM]):
            assert support.affected(conn, f"UPDATE {VERSIONS} SET inhalt = 'x' WHERE id = :i", {"i": other}) == 0
            assert support.affected(conn, f"DELETE FROM {VERSIONS} WHERE id = :i", {"i": other}) == 0
        # Version an gemeinsamem oder fremdem Objekt: Policy bzw. Verbund-FK weisen ab.
        assert "row-level security" in support.rejected_insert_with(
            conn, VERSIONS, SYSTEM, knowledge_id=rows[OBJECTS, SYSTEM], version=9, format="MARKDOWN", inhalt="x")
        message = support.rejected_insert_with(conn, VERSIONS, A, knowledge_id=rows[OBJECTS, B], version=9,
                                               format="MARKDOWN", inhalt="x")
        assert "fk_knowledge_versions_knowledge_tenant" in message, message
        message = support.rejected(conn, f"UPDATE {VERSIONS} SET knowledge_id = :k, version = 99 WHERE id = :i",
                                   {"k": rows[OBJECTS, B], "i": rows[VERSIONS, A]})
        assert "fk_knowledge_versions_knowledge_tenant" in message, message
        # Version ohne tenant_id erbt den Mandanten aus dem Kontext
        conn.execute(sa.text(f"INSERT INTO {VERSIONS} (id, knowledge_id, version, format, inhalt) "
                             "VALUES ('rls-ki-v', :k, 7, 'MARKDOWN', 'x')"), {"k": rows["object2", A]})
        assert conn.execute(sa.text(f"SELECT tenant_id FROM {VERSIONS} WHERE id = 'rls-ki-v'")).scalar() == A
    assert support.keys(conn, VERSIONS) == set()


def test_objekt_mit_versionen_behaelt_seinen_mandanten(db):
    conn, rows = db
    message = support.as_owner_rejected(conn, f"UPDATE {OBJECTS} SET tenant_id = :b WHERE knowledge_id = :k",
                                        {"b": B, "k": rows[OBJECTS, A]})
    assert "fk_knowledge_versions_knowledge_tenant" in message


def test_kontextwechsel_savepoint_hintergrund_pool(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, PROPOSALS, rows[PROPOSALS, A], rows[PROPOSALS, B], key="proposal_id")
    support.assert_background_needs_explicit_context(conn, EXECUTIONS, rows[EXECUTIONS, A], rows[EXECUTIONS, B],
                                                     key="idempotency_key")
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_wissensversionen(db):
    import app.infrastructure.models  # noqa: F401  # ORM-Fremdschluessel auf domain_shared.tenants
    from sqlalchemy.orm import Session

    from app.repositories.knowledge_repository import KnowledgeRepository, SharedKnowledgeReadOnly

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        repo = KnowledgeRepository(session)
        with tenant_scope(A, "test"):
            record = repo.add_version(rows["object2", A], {"format": "MARKDOWN", "inhalt": "neu"})
            assert {v.tenant_id for v in record.versionen} == {A}
            with pytest.raises(SharedKnowledgeReadOnly):
                repo.add_version(rows[OBJECTS, SYSTEM], {"format": "MARKDOWN", "inhalt": "fremd"})
            created = repo.create_object(knowledge_id="rls-ki-neu", titel="Neu", typ="SOP", status="ENTWURF",
                                         tenant_id=A, version_payload={"format": "MARKDOWN", "inhalt": "x"})
            assert {v.tenant_id for v in created.versionen} == {A}
    finally:
        session.close()
