"""Reporting commands: real transaction effects, no database server."""
import hashlib
import hmac
import json
import re
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import l3_report_catalog, query_center
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services import mask_action_runtime_service as runtime
from app.services.l3_report_catalog_service import L3ReportCatalogService
from app.services.query_center_service import QueryCenterService
from app.services import mcp_execution_service as mcp

KEY = "reporting-regression-test-key"
VALID = {"name": "Offene Rechnungen", "data_product_id": "finance-ap-invoice-cockpit",
         "selected_fields": ["invoice_number", "gross_amount"], "filter_spec": {}, "aggregations": []}
TABLES = {
    "domain_reporting.l3_bonus_runs": "id TEXT PRIMARY KEY,tenant_id TEXT,report_id TEXT,from_date TEXT,to_date TEXT,rate_pct TEXT,status TEXT,total_basis TEXT,total_bonus TEXT,currency TEXT,reason TEXT,actor TEXT",
    "domain_reporting.l3_bonus_run_lines": "id TEXT PRIMARY KEY,tenant_id TEXT,run_id TEXT,line_no INTEGER,dimension_id TEXT,dimension_name TEXT,document_count INTEGER,basis_amount TEXT,bonus_amount TEXT,currency TEXT",
    "domain_reporting.query_definitions": "id TEXT PRIMARY KEY,tenant_id TEXT,owner_id TEXT,name TEXT,data_product_id TEXT,selected_fields TEXT,filter_spec TEXT,aggregations TEXT,is_favorite BOOLEAN,updated_at TEXT",
    "domain_reporting.query_center_audit": "id TEXT PRIMARY KEY,tenant_id TEXT,definition_id TEXT,action TEXT,actor TEXT,reason TEXT,payload_hash TEXT",
    "domain_crm.crm_action_audit_log": "id TEXT PRIMARY KEY,tenant_id TEXT,action_key TEXT,entity_type TEXT,entity_id TEXT,idempotency_key TEXT,audit_reason TEXT,performed_at TEXT,result_summary TEXT",
    "outbox_events": "id TEXT PRIMARY KEY,event_type TEXT,aggregate_id TEXT,payload TEXT,timestamp TEXT,published BOOLEAN,retry_count INTEGER,tenant_id TEXT",
}


def signed(definition):
    payload = {"schema_version": 1, "definition": definition}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return {**payload, "signature": hmac.new(KEY.encode(), canonical.encode(), hashlib.sha256).hexdigest()}


@pytest.fixture
def db():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def setup(connection, _):
        connection.isolation_level = None
        connection.create_function("NOW", 0, lambda: "2026-10-09T12:00:00")
        connection.execute("ATTACH DATABASE ':memory:' AS domain_reporting")
        connection.execute("ATTACH DATABASE ':memory:' AS domain_crm")
        connection.execute("ATTACH DATABASE ':memory:' AS public")
        connection.create_function("pg_advisory_xact_lock", 1, lambda _: 0)

    @event.listens_for(engine, "begin")
    def begin(connection):
        connection.exec_driver_sql("BEGIN")

    # Only PostgreSQL JSON/Decimal representations differ; SQL and transactions are real.
    @event.listens_for(engine, "before_cursor_execute", retval=True)
    def representations(connection, cursor, statement, parameters, context, many):
        statement = re.sub(r"CAST\((\?) AS jsonb\)", r"\1", statement, flags=re.I)
        return statement, tuple(str(v) if isinstance(v, Decimal) else v for v in parameters)

    with engine.begin() as connection:
        for table, columns in TABLES.items():
            connection.exec_driver_sql(f"CREATE TABLE {table} ({columns})")
        connection.exec_driver_sql("CREATE TABLE public.mcp_tool_executions (tenant_id TEXT,tool_name TEXT,idempotency_key TEXT,actor_id TEXT,payload_hash TEXT,result TEXT, UNIQUE(tenant_id,tool_name,idempotency_key))")
    with Session(engine) as session:
        yield session
    engine.dispose()


def client(db):
    app = FastAPI()
    app.include_router(l3_report_catalog.router, prefix="/api/v1")
    app.include_router(query_center.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app)


def command(kind):
    if kind == "bonus":
        return "/api/v1/l3-report-catalog/bonus-runs/actions/calculate", {
            "report_id": "bonus-by-customer", "from_date": "2026-01-01",
            "to_date": "2026-01-31", "rate_pct": "2.5", "reason": "Monatsbonus"}
    return "/api/v1/query-center/actions/import", {"bundle": signed(VALID), "reason": "Import pruefen"}


def counts(db):
    return [db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one() for table in TABLES]


@pytest.mark.parametrize("kind", ["bonus", "query"])
@pytest.mark.parametrize("failure", ["audit", "outbox", "commit", None])
def test_command_persists_everything_or_nothing(db, kind, failure):
    url, body = command(kind)
    write_audit, write_outbox, real_commit = runtime._write_audit, runtime._write_outbox, db.commit

    def audit(*args, **kwargs):
        value = write_audit(*args, **kwargs)
        if failure == "audit":
            raise RuntimeError("audit storage failed")
        return value

    def outbox(*args, **kwargs):
        value = write_outbox(*args, **kwargs)
        if failure == "outbox":
            raise RuntimeError("event storage failed")
        return value

    def commit():
        if failure == "commit":
            raise RuntimeError("commit storage failed")
        return real_commit()

    with patch.object(db, "commit", side_effect=commit), patch.object(L3ReportCatalogService, "run", return_value={"items": [{
        "dimension_id": "c1", "dimension_name": "Kunde", "document_count": 1, "gross_amount": "100", "currency": "EUR",
    }]}), patch.object(query_center, "service", side_effect=lambda session, tenant: QueryCenterService(session, tenant, signing_key=KEY)), patch.object(runtime, "_write_audit", side_effect=audit), patch.object(runtime, "_write_outbox", side_effect=outbox):
        response = client(db).post(url, json=body)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is (failure is None)
    if failure:
        assert counts(db) == [0] * 6, "Fachdaten trotz abgelehnter Command-Einheit"
        assert not result["affectedIds"] and not result["auditEntryId"] and not result["outboxEventId"]
    else:
        assert counts(db) == ([1, 1, 0, 0, 1, 1] if kind == "bonus" else [0, 0, 1, 1, 1, 1])
        table = "domain_reporting.l3_bonus_runs" if kind == "bonus" else "domain_reporting.query_definitions"
        assert db.execute(text(f"SELECT id FROM {table}")).scalar_one() == result["affectedIds"][0]
        assert db.execute(text("SELECT entity_id FROM domain_crm.crm_action_audit_log")).scalar_one() == result["affectedIds"][0]


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose", "execute"])
def test_signed_but_forbidden_definition_is_rejected_in_every_mode(db, mode):
    url, body = command("query")
    body.update(bundle=signed({**VALID, "selected_fields": ["password"]}), _mode=mode)
    with patch.object(query_center, "service", side_effect=lambda db, tenant: QueryCenterService(db, tenant, signing_key=KEY)):
        result = client(db).post(url, json=body).json()
    assert result["success"] is False
    assert "Feldliste" in result["error"]
    assert counts(db) == [0] * 6


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose", "execute"])
@pytest.mark.parametrize("value", ["NaN", "sNaN", "Infinity", "-Infinity"])
def test_non_finite_bonus_rate_is_a_validation_error(db, mode, value):
    url, body = command("bonus")
    body.update(rate_pct=value, _mode=mode)
    response = client(db).post(url, json=body)
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["validationErrors"]
    assert counts(db) == [0] * 6


@pytest.mark.parametrize("kind", ["bonus", "query"])
@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose"])
def test_valid_preview_modes_write_nothing(db, kind, mode):
    url, body = command(kind)
    body["_mode"] = mode
    with patch.object(query_center, "service", side_effect=lambda db, tenant: QueryCenterService(db, tenant, signing_key=KEY)):
        result = client(db).post(url, json=body).json()
    assert result["success"] is True
    assert result["proposedChanges"]
    assert counts(db) == [0] * 6


@pytest.mark.parametrize("kind", ["bonus", "query"])
def test_standalone_rest_explicitly_commits(db, kind):
    url, body = command(kind)
    url = url.replace("/actions/calculate", "").replace("/actions/import", "/import")
    with patch.object(L3ReportCatalogService, "run", return_value={"items": []}), patch.object(query_center, "service", side_effect=lambda db, tenant: QueryCenterService(db, tenant, signing_key=KEY)), patch.object(db, "commit", wraps=db.commit) as commit:
        response = client(db).post(url, json=body)
    assert response.status_code == 201
    commit.assert_called_once()
    assert counts(db) == ([1, 0, 0, 0, 0, 0] if kind == "bonus" else [0, 0, 1, 1, 0, 0])


@pytest.mark.parametrize("kind", ["bonus", "query"])
@pytest.mark.parametrize("failure", ["audit", "replay_store", "commit", None])
def test_mcp_business_audit_and_replay_are_one_transaction(db, kind, failure):
    _, parameters = command(kind)
    request = mcp.ToolExecutionRequest(
        tool_name="reporting.bonus.calculate" if kind == "bonus" else "reporting.query.import_signed",
        parameters=parameters, mode="execute", idempotency_key="report-once",
    )
    handler = mcp._bonus_calculate if kind == "bonus" else mcp._query_import_signed
    real_audit, real_store, real_commit = mcp._write_audit, mcp._store_execution, db.commit

    def audit(*args, **kwargs):
        result = real_audit(*args, **kwargs)
        if failure == "audit":
            raise RuntimeError("audit storage failed")
        return result

    def store(*args, **kwargs):
        real_store(*args, **kwargs)
        if failure == "replay_store":
            raise RuntimeError("replay storage failed")

    def commit():
        if failure == "commit":
            raise RuntimeError("commit storage failed")
        return real_commit()

    from app.core.config import settings
    with patch.object(settings, "SECRET_KEY", KEY), patch.object(L3ReportCatalogService, "run", return_value={"items": [{
        "dimension_id": "c1", "dimension_name": "Kunde", "document_count": 1, "gross_amount": "100",
    }]}), patch.object(mcp, "_write_audit", side_effect=audit), patch.object(mcp, "_store_execution", side_effect=store), patch.object(db, "commit", side_effect=commit):
        if failure:
            with pytest.raises(HTTPException) as rejected:
                handler(db, request, "agent-a", "tenant-a")
            assert rejected.value.status_code == 503
            assert counts(db) == [0] * 6
            assert db.execute(text("SELECT COUNT(*) FROM public.mcp_tool_executions")).scalar_one() == 0
        else:
            result = handler(db, request, "agent-a", "tenant-a")
            before = counts(db)
            assert before == ([1, 1, 0, 0, 1, 0] if kind == "bonus" else [0, 0, 1, 1, 1, 0])
            replayed = handler(db, request, "agent-a", "tenant-a")
            assert replayed == {**result, "replayed": True}
            assert counts(db) == before
            assert db.execute(text("SELECT COUNT(*) FROM public.mcp_tool_executions")).scalar_one() == 1
