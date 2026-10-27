"""RLS-Domain hr: Schulungen, Onboarding, Dienstplan, Person/Beschaeftigung als valeo_app.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.tenant_context import tenant_scope
import rls_domain_support as support
from rls_domain_support import A, B, SYSTEM

pytestmark = pytest.mark.integration

ISOLATED = (
    "domain_hr.onboarding_checklists",
    "domain_hr.training_courses",
    "domain_hr.work_plan_assignments",
    "domain_hr.person",
    "domain_hr.employment",
)
CHILDREN = ("domain_hr.onboarding_runs", "domain_hr.training_assignments")
# child, column, parent, parent key
LINKS = (
    ("domain_hr.onboarding_runs", "checklist_id", "domain_hr.onboarding_checklists", "id"),
    ("domain_hr.training_assignments", "course_id", "domain_hr.training_courses", "id"),
    ("domain_hr.employment", "person_id", "domain_hr.person", "person_id"),
)


def _person_id(tenant: str) -> str:
    return f"rls-person-{tenant}"


def _seed(conn, table: str, tenant: str) -> str:
    if table == "domain_hr.person":
        return support.insert_row(conn, table, tenant, person_id=_person_id(tenant))
    if table == "domain_hr.employment":
        return support.insert_row(conn, table, tenant, person_id=_person_id(tenant))
    return support.insert_row(conn, table, tenant)


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + CHILDREN) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for table in ISOLATED:
            for tenant in (A, B, SYSTEM):
                rows[table, tenant] = _seed(conn, table, tenant)
        for child, column, parent, _key in LINKS[:2]:
            for tenant in (A, B):
                rows[child, tenant] = support.insert_row(conn, child, tenant, **{column: rows[parent, tenant]})
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
    nullable = support.as_owner(conn, (
        "SELECT table_name FROM information_schema.columns WHERE table_schema = 'domain_hr' "
        "AND column_name = 'tenant_id' AND is_nullable = 'YES' AND table_name IN ('person', 'employment')"))
    assert nullable == []


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    new_row = None
    if table == "domain_hr.employment":
        def new_row(tenant):
            return support.insert_row(conn, table, tenant, person_id=_person_id(tenant))
    elif table == "domain_hr.person":
        def new_row(tenant):
            return support.insert_row(conn, table, tenant, person_id=f"rls-neu-{tenant}")
    support.assert_tenant_isolation(
        conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], new_row=new_row)


@pytest.mark.parametrize("child, column, parent, key", LINKS)
def test_kein_verweis_auf_fremde_elternsaetze(db, child, column, parent, key):
    conn, rows = db
    foreign_parent = support.as_owner(conn, f"SELECT {key} FROM {parent} WHERE id = :i", {"i": rows[parent, B]})[0][0]
    own_parent = support.as_owner(conn, f"SELECT {key} FROM {parent} WHERE id = :i", {"i": rows[parent, A]})[0][0]
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, child, A, **{column: foreign_parent})
        assert "_tenant" in message and "foreign key" in message, message
        own_child = support.insert_row(conn, child, A, **{column: own_parent})
        # Umhaengen an den Elternsatz eines anderen Mandanten
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": foreign_parent, "i": own_child})
        assert "_tenant" in message and "foreign key" in message, message


def test_elternsatz_kann_den_mandanten_nicht_mitnehmen(db):
    conn, rows = db
    # Kurs mit Zuweisung: auch der Eigentuemer kann den Mandanten nicht wechseln (Verbund-FK).
    message = support.as_owner_rejected(
        conn, "UPDATE domain_hr.training_courses SET tenant_id = :t WHERE id = :i",
        {"t": B, "i": rows["domain_hr.training_courses", A]})
    assert "fk_hr_training_assignments_course_tenant" in message


def test_kontextwechsel_und_savepoint(db):
    conn, rows = db
    table = "domain_hr.training_courses"
    support.assert_context_switch_and_savepoint(conn, table, rows[table, A], rows[table, B])


def test_hintergrund_nur_mit_ausdruecklichem_kontext(db):
    conn, rows = db
    table = "domain_hr.onboarding_checklists"
    support.assert_background_needs_explicit_context(conn, table, rows[table, A], rows[table, B])


def test_pool_wiederverwendung():
    support.assert_pool_reuse_keeps_no_tenant()


def test_fachkette_schulung_und_onboarding(db):
    from app.api.v1.endpoints import training as ep

    conn, rows = db
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    run = asyncio.run
    try:
        with tenant_scope(A, "test"):
            course = run(ep.create_course(ep.Payload(data={"course_code": "RLS-K1", "title": "Kurs"}), tenant_id=A, db=session))
            assert course["id"] in {c["id"] for c in run(ep.list_courses(include_inactive=False, tenant_id=A, db=session))}
            changed = run(ep.update_course(course["id"], ep.Payload(data={"course_code": "RLS-K1", "title": "Kurs 2"}),
                                           tenant_id=A, db=session))
            assert changed["title"] == "Kurs 2"
            assignment = run(ep.create_assignment(ep.Payload(data={"course_id": course["id"], "employee_ref": "MA-1"}),
                                                  tenant_id=A, db=session))
            listed = run(ep.list_assignments(employee_ref=None, status=None, tenant_id=A, db=session))
            assert assignment["id"] in {a["id"] for a in listed}
            checklist = run(ep.create_checklist(ep.Payload(data={"checklist_code": "RLS-C1", "title": "Liste"}),
                                                tenant_id=A, db=session))
            onboarding = run(ep.create_run(ep.Payload(data={"checklist_id": checklist["id"], "employee_ref": "MA-1"}),
                                           tenant_id=A, db=session))
            assert onboarding["checklist_id"] == checklist["id"]
        with tenant_scope(B, "test"):
            assert course["id"] not in {c["id"] for c in run(ep.list_courses(include_inactive=True, tenant_id=B, db=session))}
            for call in (
                lambda: ep.update_course(course["id"], ep.Payload(data={"course_code": "X", "title": "fremd"}), tenant_id=B, db=session),
                lambda: ep.delete_course(course["id"], tenant_id=B, db=session),
                lambda: ep.create_assignment(ep.Payload(data={"course_id": course["id"], "employee_ref": "MA-2"}), tenant_id=B, db=session),
                lambda: ep.create_run(ep.Payload(data={"checklist_id": checklist["id"], "employee_ref": "MA-2"}), tenant_id=B, db=session),
            ):
                with pytest.raises(HTTPException) as exc:
                    run(call())
                assert exc.value.status_code == 404
        with tenant_scope(A, "test"):
            assert run(ep.list_courses(include_inactive=True, tenant_id=A, db=session))
            run(ep.delete_course(course["id"], tenant_id=A, db=session))  # Zuweisung faellt per CASCADE
            assert assignment["id"] not in {a["id"] for a in run(ep.list_assignments(
                employee_ref=None, status=None, tenant_id=A, db=session))}
    finally:
        session.close()
