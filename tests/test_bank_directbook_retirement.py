"""Retired reconciliation posting must never write or imply journal approval."""
import asyncio
import inspect

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import text

from app.api.v1.endpoints import bank_reconciliation as reconciliation
from app.core.database import get_db
from test_bank_reconciliation_proof import schema as bank_schema_fixture, case as bank_case_fixture

schema = bank_schema_fixture
import_case = bank_case_fixture


class NoAccess:
    def execute(self, *args, **kwargs):
        pytest.fail("Retired auto-book must be rejected before database access")

    def commit(self):
        pytest.fail("Reconciliation must not commit")


@pytest.mark.parametrize("value", [True, object()])
def test_direct_booking_rejected_before_database_access(value):
    with pytest.raises(HTTPException) as error:
        asyncio.run(reconciliation.reconcile_bank_statement(
            "statement", "bank", "tenant", auto_book=value, db=NoAccess()))
    assert error.value.status_code == 409


def test_internal_default_is_plain_false():
    assert inspect.signature(reconciliation.reconcile_bank_statement).parameters["auto_book"].default is False


def test_http_direct_booking_rejected():
    app = FastAPI()
    app.include_router(reconciliation.router)
    app.dependency_overrides[get_db] = lambda: NoAccess()
    with TestClient(app) as client:
        response = client.post("/bank-reconciliation/stmt/reconcile", params={
            "bank_account_id": "bank", "auto_book": True})
    assert response.status_code == 409
    assert "retired" in response.json()["detail"]


def test_response_cannot_claim_booking_permission():
    with pytest.raises(ValidationError) as error:
        reconciliation.ReconciliationResult.model_validate({"can_be_booked": True})
    assert any(e["loc"] == ("can_be_booked",) for e in error.value.errors())


@pytest.mark.parametrize("mode", ["http", "internal", "summary"])
def test_comparison_is_read_only_and_does_not_guess_accounts(import_case, mode):
    db, _, tenant, _, bank, _, _, statement, _ = import_case
    before = db.execute(text("""
        SELECT id,status,amount,matched_op_id FROM domain_erp.bank_statement_lines
        WHERE tenant_id=:t ORDER BY id
    """), {"t": tenant}).all()
    commits = db.commits
    if mode == "internal":
        # This is how finance_actions calls the endpoint: auto_book is omitted.
        result = asyncio.run(reconciliation.reconcile_bank_statement(
            statement, bank, tenant, db=db)).model_dump()
    else:
        app = FastAPI()
        app.include_router(reconciliation.router)
        app.dependency_overrides[get_db] = lambda: db
        with TestClient(app, headers={"X-Tenant-ID": tenant}) as client:
            params = {"bank_account_id": bank, "tenant_id": tenant}
            if mode == "summary":
                response = client.get(f"/bank-reconciliation/{statement}/summary", params=params)
            else:
                response = client.post(f"/bank-reconciliation/{statement}/reconcile", params=params)
            assert response.status_code == 200, response.text
            result = response.json()
    assert result["can_be_booked"] is False
    assert "booking_suggestions" not in result
    if mode != "summary":
        assert result["total_differences"] == 1
        assert result["differences"][0]["suggested_account"] is None
        assert result["differences"][0]["suggested_action"] == "INVESTIGATE"
    assert db.commits == commits
    assert db.execute(text("""
        SELECT id,status,amount,matched_op_id FROM domain_erp.bank_statement_lines
        WHERE tenant_id=:t ORDER BY id
    """), {"t": tenant}).all() == before
    assert db.execute(text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id=:t"),
                      {"t": tenant}).scalar_one() == 0
