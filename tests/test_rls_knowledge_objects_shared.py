"""Wissensobjekte: eigene plus gemeinsames Produktwissen lesen, nur eigene aendern (valeo_app).

Migration rls_knowledge_objects_shared_20261027; Pruefhilfe tests/rls_domain_support.py.
"""

from __future__ import annotations

import json

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, ROOT, SYSTEM

pytestmark = pytest.mark.integration

TABLE = "domain_shared.knowledge_objects"


def _object(conn, tenant: str, titel: str) -> str:
    return support.insert_row(conn, TABLE, tenant, key="knowledge_id", titel=titel, typ="SOP", status="FREIGEGEBEN")


@pytest.fixture(scope="module")
def probe():
    with support.probe((TABLE,)) as conn:
        for role in support.APP_ROLES:
            conn.execute(sa.text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA domain_shared TO {role}"))
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {tenant: _object(conn, tenant, f"Wissen {tenant}") for tenant in (A, B, SYSTEM)}
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_freigabe_begruendet_und_form(db):
    conn, _ = db
    exceptions = json.loads((ROOT / "docs" / "admin" / "rls-exceptions.json").read_text(encoding="utf-8"))
    assert TABLE in exceptions["system_lesbar"]
    assert support.shape(conn, TABLE) == ("getrennt_system", "")


def test_eigenes_und_gemeinsames_lesen_nur_eigenes_aendern(db):
    conn, rows = db
    key = "knowledge_id"
    with tenant_scope(A, "test"):
        assert support.keys(conn, TABLE, key) >= {rows[A], rows[SYSTEM]}
        assert rows[B] not in support.keys(conn, TABLE, key)
        for other in (rows[B], rows[SYSTEM]):
            assert support.affected(conn, f"UPDATE {TABLE} SET titel = 'x' WHERE knowledge_id = :k", {"k": other}) == 0
            assert support.affected(conn, f"UPDATE {TABLE} SET tenant_id = :a WHERE knowledge_id = :k",
                                    {"k": other, "a": A}) == 0
            assert support.affected(conn, f"DELETE FROM {TABLE} WHERE knowledge_id = :k", {"k": other}) == 0
        assert "row-level security" in support.rejected_insert_with(
            conn, TABLE, SYSTEM, key, titel="neu", typ="SOP", status="ENTWURF")
        assert "row-level security" in support.rejected(
            conn, f"UPDATE {TABLE} SET tenant_id = 'system' WHERE knowledge_id = :k", {"k": rows[A]})
    assert support.keys(conn, TABLE, key) == set()


def test_fachkette_wissens_api(db):
    import app.infrastructure.models  # noqa: F401  # registriert domain_shared.tenants fuer die ORM-Fremdschluessel
    from app.api.v1.endpoints import knowledge_api as ep

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        with tenant_scope(A, "test"):
            listed = {o.knowledge_id for o in ep.list_knowledge(None, None, None, None, 50, 0, db=session, tenant_id=A)}
            assert {rows[A], rows[SYSTEM]} <= listed and rows[B] not in listed
            created = ep.create_knowledge(ep.KnowledgeObjectCreate(titel="Eigen", typ="SOP", initiale_version="x"),
                                          db=session, tenant_id=A)
            assert support.as_owner(conn, f"SELECT tenant_id FROM {TABLE} WHERE knowledge_id = :k",
                                    {"k": created.knowledge_id}) == [(A,)]
            with pytest.raises(HTTPException) as exc:
                ep.update_knowledge(rows[SYSTEM], ep.KnowledgeObjectUpdate(titel="geaendert"), db=session, tenant_id=A)
            assert exc.value.status_code == 403
            assert ep.get_knowledge(rows[SYSTEM], db=session, tenant_id=A).knowledge_id == rows[SYSTEM]
        with tenant_scope(B, "test"):
            with pytest.raises(HTTPException) as exc:
                ep.get_knowledge(created.knowledge_id, db=session, tenant_id=B)
            assert exc.value.status_code == 404
    finally:
        session.close()
