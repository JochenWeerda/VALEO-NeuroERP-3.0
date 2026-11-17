"""PostgreSQL behavior of the exact directory SQL, using rollback-only fixtures.

The filtering test executes the production statement in the SAME transaction as
uncommitted fixtures. A separate test runs the service with an injected real
system-role session and an unknown synthetic subject. Neither test exercises the
HTTP identity binding or cross-connection visibility of fixture data. No database,
container, migration, or DDL is created here.
"""
from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.services.portal_tenant_directory import _DIRECTORY_ROLES, _QUERY
from app.services import portal_tenant_directory as directory

pytestmark = pytest.mark.integration


@pytest.fixture
def connection():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL ist nicht konfiguriert")
    engine = create_engine(url, poolclass=NullPool,
                           connect_args={"application_name": "agent:portal-directory-test", "connect_timeout": 5})
    try:
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                role = conn.execute(text(
                    "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
                )).one()
                if not (role[0] or role[1]):
                    pytest.skip("SQL-Verhaltenstest benoetigt eine im Pruefstand mandantenuebergreifend lesende Rolle")
                yield conn
            finally:
                transaction.rollback()
    finally:
        engine.dispose()


def test_nur_eigene_gueltige_zuordnungen_aktiver_haeuser(connection):
    suffix = uuid.uuid4().hex[:16]
    subject = f"portal-directory-{suffix}"
    cases = ("own-a", "own-b", "foreign", "expired", "revoked", "deleted", "inactive", "staff")
    tenant = {case: f"pd-{suffix}-{case}" for case in cases}

    for case in cases:
        customer = f"{tenant[case]}-customer"
        connection.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, domain, is_active) VALUES (:id, :id, :id, :active)"
        ), {"id": tenant[case], "active": case != "inactive"})
        connection.execute(text(
            "INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id, deleted_at) "
            "VALUES (:customer, :customer, :customer, :tenant, CASE WHEN :deleted THEN now() ELSE NULL END)"
        ), {"customer": customer, "tenant": tenant[case], "deleted": case == "deleted"})
        connection.execute(text("""
            INSERT INTO domain_portal.kundenzugaenge
              (id, tenant_id, subject, customer_id, rolle, angelegt_von, gueltig_bis, widerrufen_am, widerrufen_von)
            VALUES (:id, :tenant, :subject, :customer, :role, 'test',
                    CASE WHEN :expired THEN now() - interval '1 second' ELSE NULL END,
                    CASE WHEN :revoked THEN now() ELSE NULL END,
                    CASE WHEN :revoked THEN 'test' ELSE NULL END)
        """), {"id": str(uuid.uuid4()), "tenant": tenant[case],
               "subject": f"{subject}-other" if case == "foreign" else subject,
               "customer": customer, "role": "aussendienst" if case == "staff" else "inhaber",
               "expired": case == "expired", "revoked": case == "revoked"})

    # A second eligible customer belongs to the same house and must increase its count only.
    extra = f"{tenant['own-a']}-second"
    connection.execute(text(
        "INSERT INTO domain_crm.customers (id, customer_number, company_name, tenant_id) "
        "VALUES (:customer, :customer, :customer, :tenant)"
    ), {"customer": extra, "tenant": tenant["own-a"]})
    connection.execute(text(
        "INSERT INTO domain_portal.kundenzugaenge (id, tenant_id, subject, customer_id, rolle, angelegt_von) "
        "VALUES (:id, :tenant, :subject, :customer, 'inhaber', 'test')"
    ), {"id": str(uuid.uuid4()), "tenant": tenant["own-a"], "subject": subject, "customer": extra})

    rows = connection.execute(_QUERY, {"subject": subject, "roles": _DIRECTORY_ROLES, "limit": 101}).all()
    assert [(row[0], row[2]) for row in rows] == [(tenant["own-a"], 2), (tenant["own-b"], 1)]
    assert connection.execute(_QUERY, {"subject": subject + "-unknown", "roles": _DIRECTORY_ROLES,
                                       "limit": 101}).all() == []


def test_service_nutzt_systemrolle_und_readonly_transaktion(monkeypatch):
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL ist nicht konfiguriert")
    engine = create_engine(url, poolclass=NullPool, connect_args={
        "application_name": "agent:portal-directory-system-test", "connect_timeout": 5,
        "options": "-c role=valeo_system",
    })
    statements: list[str] = []
    readonly: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def record_statement(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement.strip())

    class InspectSession(Session):
        def rollback(self):
            try:
                if self.in_transaction():
                    readonly.append(self.execute(text("SHOW transaction_read_only")).scalar_one())
            finally:
                super().rollback()

    monkeypatch.setattr(directory.settings, "SYSTEM_DATABASE_URL", "configured-for-test")
    monkeypatch.setattr(directory, "system_session", lambda: InspectSession(bind=engine))
    subject = f"portal-directory-unknown-{uuid.uuid4().hex}"
    user = {"sub": subject, "raw": {"sub": subject, "tenant_id": "synthetic-tenant"}}
    try:
        assert directory.eigene_handelspartner(user) == []
        assert statements[0].upper() == "SET TRANSACTION READ ONLY"
        assert "current_user" in statements[1]
        assert "domain_portal.kundenzugaenge" in statements[2]
        assert statements[3].upper() == "SHOW TRANSACTION_READ_ONLY"
        assert readonly == ["on"]
    finally:
        engine.dispose()
