"""Signed HTTP import against the shared probe; every change rolls back."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.core.database import engine
from app.api.v1.endpoints import sales_offers
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]
HEADER = "offer_number;subject;customer_id;total_amount;currency;valid_until\n"


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


@pytest.fixture
def imports(subject_data, monkeypatch):
    raw = os.environ.get("TEST_DATABASE_URL")
    assert raw and make_url(raw) == engine.url and engine.url.database == "valeo_probe"
    client, db, provider, tenant, foreign, *_ = subject_data
    import importlib.util
    from pathlib import Path
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    path = Path(__file__).resolve().parents[1] / "alembic/versions/sales_offer_number_tenant_20261031.py"
    spec = importlib.util.spec_from_file_location("offer_number_scope", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    db.execute(text("SET LOCAL lock_timeout='5s'"))
    db.execute(text("SET LOCAL statement_timeout='30s'"))
    with Operations.context(MigrationContext.configure(db.connection())):
        migration.upgrade()
    customers = {tid: str(uuid4()) for tid in (tenant, foreign)}
    for tid, customer in customers.items():
        db.execute(text("INSERT INTO domain_crm.customers "
                        "(id,tenant_id,customer_number,company_name,is_active) "
                        "VALUES (:id,:tenant,:number,'Synthetic import customer',TRUE)"),
                   {"id": customer, "tenant": tid, "number": "IMP-" + customer[:16]})
    client.app.include_router(sales_offers.router, prefix="/api/v1/sales/offers")
    from app.services import sales_offer_import
    original = sales_offer_import.import_offers
    failures = []
    def observed(*args, **kwargs):
        try:
            return original(*args, **kwargs)
        except Exception as error:
            failures.append(error.__cause__)
            raise
    monkeypatch.setattr(sales_offer_import, "import_offers", observed)
    def send(content, key, *, selected=tenant, roles=None, actor="human-a"):
        content = content.replace("__CUSTOMER__", customers[selected])
        token = provider.token(selected, changes={"roles": roles or ["SALES_BEARBEITEN"],
                                                 "identity_type": "human", "sub": actor})
        response = client.post("/api/v1/sales/offers/actions/import-csv",
                           headers={"Authorization": "Bearer " + token},
                           json={"csv_content": content, "_idempotencyKey": key})
        assert response.status_code != 503, repr(failures[-1]) if failures else response.text
        return response
    return db, send, tenant, foreign


def test_atomic_import_replay_tenant_and_role_boundaries(imports):
    db, send, tenant, foreign = imports
    number, key = "SQL-" + uuid4().hex[:18], uuid4().hex
    content = HEADER + f"{number};Synthetic import;__CUSTOMER__;12.50;EUR;\n"
    result = send(content, key)
    assert result.status_code == 200, result.text
    first = result.json()
    assert first["count"] == 1
    assert send(content, key).json()["offer_ids"] == first["offer_ids"]
    assert send(content.replace("12.50", "13.50"), key).status_code == 409
    assert send(content, key, actor="synthetic-other").status_code == 409
    assert send(content, uuid4().hex, roles=["SALES_LESEN"]).status_code == 403
    # The same number/key in another tenant creates a separate business record.
    other = send(content, key, selected=foreign)
    assert other.status_code == 200, other.text
    assert other.json()["offer_ids"] != first["offer_ids"]
    assert db.execute(text("SELECT count(*) FROM domain_crm.sales_offers WHERE offer_number=:n"), {"n": number}).scalar() == 2
    assert db.execute(text("SELECT count(*) FROM outbox_events WHERE tenant_id=:t AND event_type=:e"),
                      {"t": tenant, "e": "sales.offer.import_csv.v1"}).scalar() == 1


def test_second_duplicate_rolls_back_first_offer_and_execution_receipt(imports):
    db, send, tenant, _ = imports
    prefix, key = "SQL-" + uuid4().hex[:16], uuid4().hex
    duplicate = prefix + "-B"
    assert send(HEADER + f"{duplicate};Existing;__CUSTOMER__;1;EUR;\n", uuid4().hex).status_code == 200
    response = send(HEADER + f"{prefix}-A;First;__CUSTOMER__;1;EUR;\n{duplicate};Duplicate;__CUSTOMER__;2;EUR;\n", key)
    assert response.status_code == 409, response.text
    assert db.execute(text("SELECT count(*) FROM domain_crm.sales_offers WHERE tenant_id=:t AND offer_number=:n"),
                      {"t": tenant, "n": prefix + "-A"}).scalar() == 0
    assert db.execute(text("SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:t AND idempotency_key=:k"),
                      {"t": tenant, "k": key}).scalar() == 0
