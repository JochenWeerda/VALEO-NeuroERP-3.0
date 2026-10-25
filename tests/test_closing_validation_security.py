"""Security regressions against the shared PostgreSQL probe, rollback only."""
import json
from uuid import uuid4
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.v1.endpoints import closing_checklists as routes
from app.auth.deps import get_current_user
from app.core.database import engine, get_db
from app.core.tenant import get_tenant_id
from app.services.closing_checklist_validation import validate_closing_item, verified_closing_actor


@pytest.fixture(autouse=True)
def shared_probe_only():
    assert engine.url.get_backend_name() == "postgresql"
    assert engine.url.database == "valeo_probe" or engine.url.database.startswith("test_")


def test_actor_requires_verified_subject_not_display_name():
    for user in ({}, {"name": "admin"}, {"sub": ""}, {"sub": 12}):
        with pytest.raises(HTTPException) as exc:
            verified_closing_actor(user)
        assert exc.value.status_code == 401
    assert verified_closing_actor({"sub": "verified", "name": "spoof"}) == "verified"


@pytest.mark.integration
def test_registered_tax_check_counts_only_own_tenant_and_period():
    marker = uuid4().hex
    with engine.connect() as conn:
        outer = conn.begin()
        try:
            with Session(bind=conn, join_transaction_mode="create_savepoint") as db:
                tenant = "closing-" + marker
                db.execute(text("INSERT INTO domain_erp.vat_returns (id,tenant_id,period,status) VALUES (:id,:tenant,'2026-10','validated')"), {"id": marker, "tenant": tenant})
                assert validate_closing_item(db, item_code="TAX-001", tenant_id=tenant, period="2026-10") == (True, 1)
                assert validate_closing_item(db, item_code="TAX-001", tenant_id=tenant + "-foreign", period="2026-10") == (False, 0)
                assert validate_closing_item(db, item_code="TAX-001", tenant_id=tenant, period="2026-09") == (False, 0)
                for code in ("GL-001", "AR-001", "AP-001"):
                    assert validate_closing_item(db, item_code=code, tenant_id=tenant, period="2026-10") == (True, 0)
                db.execute(text("INSERT INTO domain_erp.offene_posten (id,tenant_id,debtor_id,creditor_id,offen) VALUES (:id,:tenant,'debtor','creditor',10)"), {"id": marker, "tenant": tenant})
                for code in ("AR-001", "AP-001"):
                    assert validate_closing_item(db, item_code=code, tenant_id=tenant, period="2026-10") == (False, 1)
                    assert validate_closing_item(db, item_code=code, tenant_id=tenant + "-foreign", period="2026-10") == (True, 0)
                with pytest.raises(ValueError):
                    validate_closing_item(db, item_code="SELECT 1", tenant_id=tenant, period="2026-10")
                with pytest.raises(ValueError):
                    validate_closing_item(db, item_code="GL-001", tenant_id=tenant, period="2026-10; DROP TABLE x")
        finally:
            outer.rollback()


@pytest.mark.integration
@pytest.mark.parametrize("operation", ["complete", "approve", "validate"])
def test_http_never_accepts_spoofed_actor_or_executes_template_sql(operation):
    marker = uuid4().hex
    tenant = "close-" + marker
    item = {"item_code": "UNKNOWN", "status": "pending", "required": True, "validation_type": "automatic", "validation_query": "SELECT pg_sleep(30)"}
    with engine.connect() as conn:
        outer = conn.begin()
        try:
            with Session(bind=conn, join_transaction_mode="create_savepoint") as db:
                db.execute(text("INSERT INTO domain_erp.closing_checklists (id,tenant_id,period,closing_type,status,items,period_start,period_end,total_items,required_items) VALUES (:id,:tenant,'2026-10','monthly',:status,CAST(:items AS jsonb),'2026-10-01','2026-10-31',1,1)"), {"id": marker, "tenant": tenant, "status": "completed" if operation == "approve" else "draft", "items": json.dumps([item])})
                db.execute(text("SET LOCAL statement_timeout = 1000"))
                app = FastAPI()
                app.include_router(routes.router)
                app.dependency_overrides[get_db] = lambda: db
                app.dependency_overrides[get_tenant_id] = lambda: tenant
                app.dependency_overrides[get_current_user] = lambda: {"sub": "verified-actor", "roles": ["FINANCE_ADMIN"]}
                client = TestClient(app)
                base = f"/closing-checklists/{marker}"
                if operation == "complete":
                    response = client.post(base + "/items/UNKNOWN/complete", json={"item_code": "UNKNOWN", "status": "completed", "completed_by": "spoofed"})
                else:
                    response = client.post(base + "/" + operation + "?approved_by=spoofed")
                assert response.status_code == 200, response.text
                row = db.execute(text("SELECT completed_by, items FROM domain_erp.closing_checklists WHERE id=:id"), {"id": marker}).one()
                if operation == "validate":
                    assert row.items[0]["status"] == "pending"
                    assert row.items[0]["validation_result"]["passed"] is False
                    assert response.json()["validation_results"][0]["message"] == "Automatic validation unavailable"
                else:
                    assert row.completed_by == "verified-actor"
                    if operation == "complete":
                        assert row.items[0]["completed_by"] == "verified-actor"
        finally:
            outer.rollback()
