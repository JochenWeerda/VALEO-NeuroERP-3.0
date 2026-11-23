"""Real PostgreSQL/RLS conversion, entirely rolled back, including fixture ACLs.

The owner connection only prepares uncommitted test permissions. All business
statements run as the existing non-owner, non-BYPASSRLS valeo_agent role. This
does not provision live permissions or claim an OIDC/browser acceptance.
"""
from __future__ import annotations

import os
import json
from contextlib import contextmanager
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.rls_session import install_tenant_setting
from app.core.tenant_context import tenant_scope
from app.services.docflow_service import DocflowService

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

_DOC_TABLES = (
    "document_headers", "document_items", "document_links", "document_header_links",
    "document_command_log", "document_status_history", "command_idempotency_keys", "number_series",
)
_SNAPSHOT = (
    "SELECT n.nspname,c.relname,c.relowner,c.relrowsecurity,c.relforcerowsecurity,c.relacl::text "
    "FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
    "WHERE n.nspname IN ('domain_docflow','domain_shared','domain_sales','infrastructure','public') "
    "ORDER BY n.nspname,c.relname"
)


@pytest.fixture
def probe():
    raw = os.environ.get("TEST_DATABASE_URL")
    if not raw:
        if os.environ.get("PYTEST_REQUIRE_DB_STRICT") == "1":
            pytest.fail("Explicit TEST_DATABASE_URL is required for the PostgreSQL conversion contract")
        pytest.skip("Explicit PostgreSQL test connection is not configured")
    url = make_url(raw)
    assert url.get_backend_name() == "postgresql" and url.database == "valeo_probe"
    assert make_url(os.environ.get("DATABASE_URL", "")) == url, "Test and application connections must match"
    engine = install_tenant_setting(create_engine(url, poolclass=NullPool, connect_args={
        "application_name": "agent:codex-docflow-sql", "connect_timeout": 5,
        "options": "-c statement_timeout=15000 -c lock_timeout=3000",
    }))
    tenant, foreign, source, position, foreign_source, foreign_position = [str(uuid4()) for _ in range(6)]
    actor = str(uuid4())
    try:
        with engine.connect() as conn:
            before = conn.execute(text(_SNAPSHOT)).all()
            schema_sql = "SELECT nspname,nspowner,nspacl::text FROM pg_namespace ORDER BY nspname"
            role_sql = "SELECT rolname,rolsuper,rolcreaterole,rolbypassrls FROM pg_roles ORDER BY rolname"
            before_schemas = conn.execute(text(schema_sql)).all()
            before_roles = conn.execute(text(role_sql)).all()
            conn.rollback()
            outer = conn.begin()
            db = None
            try:
                assert conn.execute(text("SELECT current_database()")).scalar_one() == "valeo_probe"
                # Existing test-role fixture pattern: grants are invisible to other
                # sessions and never committed, including when service.commit() runs.
                conn.execute(text("GRANT USAGE ON SCHEMA domain_docflow, domain_shared, domain_sales, infrastructure TO valeo_agent"))
                for table in _DOC_TABLES:
                    conn.execute(text(f"GRANT SELECT, INSERT, UPDATE ON domain_docflow.{table} TO valeo_agent"))  # nosec B608 -- fixed fixture table names
                conn.execute(text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA domain_docflow TO valeo_agent"))
                conn.execute(text("GRANT SELECT ON domain_docflow.pos_receipt_compliance TO valeo_agent"))
                conn.execute(text("GRANT SELECT, INSERT ON domain_shared.tenants TO valeo_agent"))
                conn.execute(text("GRANT SELECT, INSERT ON public.outbox_events TO valeo_agent"))
                conn.execute(text("GRANT INSERT ON infrastructure.audit_log TO valeo_agent"))
                conn.execute(text("SET LOCAL ROLE valeo_agent"))
                role = conn.execute(text("SELECT current_user,rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user")).one()
                assert tuple(role) == ("valeo_agent", False, False)
                assert conn.execute(text("SELECT pg_get_userbyid(relowner) <> current_user AND relrowsecurity "
                                         "FROM pg_class WHERE oid='domain_docflow.document_headers'::regclass")).scalar_one()
                assert not conn.execute(text("SELECT has_schema_privilege(current_user,'domain_docflow','CREATE')")).scalar_one()
                db = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
                for tid, sid, pid in ((tenant, source, position), (foreign, foreign_source, foreign_position)):
                    with tenant_scope(tid, "isolated DocFlow SQL fixture"):
                        db.execute(text("INSERT INTO domain_shared.tenants (id,name,domain,is_active) "
                                        "VALUES (:t,'Synthetic SQL conversion fixture',:domain,true)"),
                                   {"t": tid, "domain": f"{tid}.invalid"})
                        db.execute(text("INSERT INTO domain_docflow.document_headers "
                                        "(id,tenant_id,doc_type,doc_number,status,currency,document_date,version,total_net,total_tax,total_gross) "
                                        "VALUES (:id,:t,'sales_order',:number,'open','EUR',NOW(),1,20,0,20)"),
                                   {"id": sid, "t": tid, "number": f"SYNTH-SQL-{sid}"})
                        db.execute(text("INSERT INTO domain_docflow.document_items "
                                        "(id,tenant_id,header_id,line_number,article_number,description,quantity,unit,unit_price,"
                                        "discount_percent,tax_rate,line_total_net,line_total_tax,line_total_gross) "
                                        "VALUES (:id,:t,:header,1,'SYNTHETIC','Synthetic conversion source',10,'kg',2,0,0,20,0,20)"),
                                   {"id": pid, "t": tid, "header": sid})
                        db.commit()  # releases only the fixture savepoint
                        assert outer.is_active
                yield {"db": db, "conn": conn, "outer": outer, "tenant": tenant, "foreign": foreign,
                       "source": source, "position": position, "foreign_position": foreign_position, "actor": actor}
            finally:
                if db is not None:
                    db.close()
                outer.rollback()
            # Read-only owner checks after rollback prove the fixture left neither
            # business data nor broadened ACLs behind.
            assert conn.execute(text(_SNAPSHOT)).all() == before
            assert conn.execute(text(schema_sql)).all() == before_schemas
            assert conn.execute(text(role_sql)).all() == before_roles
            assert conn.execute(text("SELECT count(*) FROM domain_shared.tenants WHERE id IN (:a,:b)"),
                                {"a": tenant, "b": foreign}).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM domain_docflow.document_headers WHERE tenant_id IN (:a,:b)"),
                                {"a": tenant, "b": foreign}).scalar_one() == 0
            assert conn.execute(text("SELECT count(*) FROM public.outbox_events WHERE tenant_id IN (:a,:b)"),
                                {"a": tenant, "b": foreign}).scalar_one() == 0
            conn.rollback()
    finally:
        engine.dispose()


@contextmanager
def own(probe):
    with tenant_scope(probe["tenant"], "real isolated partial-conversion test"):
        yield DocflowService(probe["db"], probe["tenant"], probe["actor"])


def request(probe, quantity=4, *, version=1, key="synthetic-conversion-key", dry_run=False):
    return DocflowConvertRequest(target_doc_type="sales_delivery", idempotency_key=key, expected_version=version,
                                 quantities_by_source_item_id={probe["position"]: quantity}, dry_run=dry_run, created_by="untrusted-body-actor")


def counts(probe):
    db, tenant = probe["db"], probe["tenant"]
    tables = (*[f"domain_docflow.{table}" for table in _DOC_TABLES], "public.outbox_events")
    return [db.execute(text(f"SELECT count(*) FROM {table} WHERE tenant_id=:t"), {"t": tenant}).scalar_one()  # nosec B608 -- fixed fixture table names
            for table in tables]


def test_preisfreie_optionen_vorschau_und_echte_teilmenge_mit_replay(probe):
    with own(probe) as svc:
        initial = counts(probe)
        options = svc.conversion_options(probe["source"], "sales_delivery")
        assert options["version"] == 1 and options["items"][0]["remaining_quantity"] == 10
        assert options["items"][0]["source_item_id"] == probe["position"]
        assert options["items"][0]["unit"] == "kg"
        assert "unit_price" not in options["items"][0]
        assert counts(probe) == initial
        preview = svc.convert(probe["source"], request(probe, dry_run=True))
        assert preview["status"] == "dry_run" and preview["target_doc_id"] is None
        assert counts(probe) == initial
        result = svc.convert(probe["source"], request(probe))
        assert result["status"] == "ok" and result["target_doc_id"]
        assert probe["outer"].is_active
        target = svc.fetch_header(result["target_doc_id"])
        assert target["doc_type"] == "sales_delivery" and target["source_ref"] == probe["source"]
        assert target["created_by"] == probe["actor"]
        target_items = svc.fetch_items(result["target_doc_id"])
        assert len(target_items) == 1
        assert target_items[0]["source_line_id"] == probe["position"]
        assert target_items[0]["quantity"] == Decimal("4") and target_items[0]["unit"] == "kg"
        options = svc.conversion_options(probe["source"], "sales_delivery")
        assert options["version"] == 2 and options["items"][0]["remaining_quantity"] == 6
        after = counts(probe)
        replay = svc.convert(probe["source"], request(probe))
        assert replay["target_doc_id"] == result["target_doc_id"] and replay["idempotent_hit"] is True
        assert counts(probe) == after
        event = probe["db"].execute(text("SELECT payload FROM public.outbox_events WHERE id=:id AND tenant_id=:t"),
                                     {"id": result["payload"]["outbox_event_id"], "t": probe["tenant"]}).scalar_one()
        if isinstance(event, str):
            event = json.loads(event)
        assert isinstance(event, dict)
        assert event["source_doc_id"] == probe["source"] and event["target_doc_id"] == result["target_doc_id"]
        commands = svc.fetch_command_log(probe["source"])
        assert any(row["command"] == "convert" and row["actor"] == probe["actor"] for row in commands)


def test_negative_kommandos_hinterlassen_keinen_folgebeleg(probe):
    with own(probe) as svc:
        svc.convert(probe["source"], request(probe))
        after = counts(probe)
        attempts = [
            (request(probe, 7, version=2, key="too-much-quantity"), ValidationFailedError),
            (request(probe, 1, version=1, key="stale-source-version"), ConflictError),
            (request(probe, 5, version=2), ConflictError),
            (request(probe, 0, version=2, key="zero-selected-quantity"), ValidationFailedError),
        ]
        foreign = request(probe, version=2, key="foreign-position-key")
        foreign.quantities_by_source_item_id[probe["foreign_position"]] = 1
        attempts.append((foreign, ValidationFailedError))
        for command, error in attempts:
            with pytest.raises(error):
                svc.convert(probe["source"], command)
            probe["db"].rollback()  # only this command's savepoint
            assert probe["outer"].is_active and counts(probe) == after


def test_fremder_mandantenkontext_sperrt_auch_manipulierten_servicefilter(probe):
    with tenant_scope(probe["foreign"], "negative cross-tenant RLS conversion test"):
        # Deliberately forged service tenant: RLS still binds the actual context.
        forged = DocflowService(probe["db"], probe["tenant"], probe["actor"])
        assert forged.fetch_header(probe["source"]) is None
        assert not probe["db"].execute(text("SELECT id FROM domain_docflow.document_headers WHERE id=:id"),
                                       {"id": probe["source"]}).first()
        with pytest.raises(EntityNotFoundError):
            forged.conversion_options(probe["source"], "sales_delivery")
        with pytest.raises(EntityNotFoundError):
            forged.convert(probe["source"], request(probe))
        probe["db"].rollback()
        changed = probe["db"].execute(text("UPDATE domain_docflow.document_headers SET version=version+1 WHERE id=:id"),
                                       {"id": probe["source"]})
        assert changed.rowcount == 0
        probe["db"].rollback()
    with own(probe) as svc:
        assert svc.fetch_header(probe["source"])["version"] == 1
        assert svc.conversion_options(probe["source"], "sales_delivery")["items"][0]["remaining_quantity"] == 10
