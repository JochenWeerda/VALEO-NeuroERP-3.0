"""Real PostgreSQL contracts for atomic CSV payment imports."""
from __future__ import annotations

import os
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import bank_statement_import
from app.core.database import get_db


class ImportSession(Session):
    failure = None
    commits = 0
    rollbacks = 0

    def execute(self, statement, params=None, **kwargs):
        sql = str(statement)
        if (self.failure == "header" and "INSERT INTO domain_erp.bank_statements" in sql) or (
            self.failure == "line" and "INSERT INTO domain_erp.bank_statement_lines" in sql
            and params["line_num"] == 2
        ):
            return super().execute(text("SELECT 1 / 0"))
        return super().execute(statement, params, **kwargs)

    def commit(self):
        self.commits += 1
        if self.failure == "commit":
            super().execute(text("SELECT 1 / 0"))
        return super().commit()

    def rollback(self):
        self.rollbacks += 1
        return super().rollback()


@pytest.fixture
def import_case():
    raw = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw:
        pytest.skip("Migrated PostgreSQL test database required")
    url = make_url(raw)
    if url.database != "valeo_probe" and "test" not in (url.database or "").lower():
        if os.getenv("TEST_DATABASE_URL"):
            pytest.fail("TEST_DATABASE_URL must point to shared valeo_probe or a configured test database")
        pytest.skip("Never seed bank imports into a development database")
    assert url.drivername.startswith("postgresql")
    engine = create_engine(url)
    db = ImportSession(engine)
    tenant = str(uuid4())
    db.execute(text("INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:t,'Import test',:domain,TRUE)"),
               {"t": tenant, "domain": f"{tenant}.test.local"})
    db.execute(text("""
        INSERT INTO domain_erp.bank_accounts (id,tenant_id,account_number,bank_name,iban,currency,is_active)
        VALUES (:id,:t,:id,'Test Bank','DE89370400440532013000',:currency,TRUE)
    """), {"id": f"bank-{tenant}", "t": tenant, "currency": "USD"})
    db.commit()
    db.commits = db.rollbacks = 0
    app = FastAPI()
    app.include_router(bank_statement_import.router)
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, headers={"X-Tenant-ID": tenant}) as client:
        yield db, client, tenant
    db.rollback()
    db.close()
    with engine.begin() as cleanup:
        cleanup.execute(text("DELETE FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.bank_statements WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.bank_accounts WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_shared.tenants WHERE id=:t"), {"t": tenant})
    engine.dispose()


CSV = "date,amount,currency,reference\n2026-09-28,10.00,USD,REF-1\n2026-09-29,20.00,USD,REF-2\n"


def upload(case, csv=CSV):
    _, client, tenant = case
    return client.post("/bank-statements/import", params={"tenant_id": tenant,
        "bank_account_id": f"bank-{tenant}", "format": "CSV", "auto_match": False},
        files={"file": ("statement.csv", csv.encode(), "text/csv")})


def counts(case):
    db, _, tenant = case
    return tuple(db.execute(text(f"SELECT count(*) FROM domain_erp.{table} WHERE tenant_id=:t"),
                            {"t": tenant}).scalar_one()
                 for table in ("bank_statements", "bank_statement_lines"))


def test_valid_csv_preserves_currency_counts_and_balance(import_case):
    db, _, tenant = import_case
    response = upload(import_case)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_lines"] == data["imported_lines"] == 2
    assert data["error_lines"] == 0 and data["import_errors"] is None
    assert Decimal(data["closing_balance"]) == Decimal("30")
    assert [row["currency"] for row in data["lines"]] == ["USD", "USD"]
    rows = db.execute(text("SELECT currency,amount FROM domain_erp.bank_statement_lines WHERE tenant_id=:t ORDER BY line_number"), {"t": tenant}).all()
    assert rows == [("USD", Decimal("10")), ("USD", Decimal("20"))]
    assert counts(import_case) == (1, 2) and db.commits == 1


@pytest.mark.parametrize("failure", ["header", "line", "commit"])
def test_sql_failure_is_never_a_successful_import(import_case, failure):
    db, _, _ = import_case
    db.failure = failure
    response = upload(import_case)
    assert response.status_code == 500, response.text
    assert response.json()["detail"] == "Failed to import bank statement"
    assert db.rollbacks >= 1 and counts(import_case) == (0, 0)


def test_actual_second_line_constraint_rolls_back_whole_statement(import_case):
    response = upload(import_case, CSV.replace("REF-2", "R" * 256))
    assert response.status_code == 500, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize("csv", [
    CSV.replace("USD", "XXX"), CSV.replace("10.00", "10.001"),
    "date,amount,currency,reference\n2026-09-28,10,EUR,REF-1\n2026-09-28,10,EUR,REF-1\n",
])
def test_invalid_input_is_rejected_before_writes(import_case, csv):
    db, _, _ = import_case
    response = upload(import_case, csv)
    assert response.status_code == 422, response.text
    assert db.commits == 0 and counts(import_case) == (0, 0)


def test_two_imports_have_distinct_persistent_ids(import_case):
    first, second = upload(import_case), upload(import_case, CSV.replace("REF-2", "REF-3"))
    assert first.status_code == second.status_code == 200
    assert first.json()["statement_id"] != second.json()["statement_id"]
    assert counts(import_case) == (2, 4)


def test_auto_match_without_candidate_keeps_import_unmatched(import_case):
    db, client, tenant = import_case
    response = client.post("/bank-statements/import", params={"tenant_id": tenant,
        "bank_account_id": f"bank-{tenant}", "format": "CSV", "auto_match": True},
        files={"file": ("statement.csv", CSV.encode(), "text/csv")})
    assert response.status_code == 200, response.text
    assert all(row["status"] == "UNMATCHED" for row in response.json()["lines"])
    assert db.commits == 1 and counts(import_case) == (1, 2)


def test_signed_bank_debit_is_preserved(import_case):
    response = upload(import_case, CSV.replace("10.00", "-10.00"))
    assert response.status_code == 200, response.text
    assert Decimal(response.json()["lines"][0]["amount"]) == Decimal("-10")


def test_response_validation_failure_rolls_back_before_commit(import_case, monkeypatch):
    def invalid_response(**kwargs):
        raise ValueError("invalid response")
    monkeypatch.setattr(bank_statement_import, "BankStatementImportResult", invalid_response)
    db, _, _ = import_case
    response = upload(import_case)
    assert response.status_code == 500, response.text
    assert db.commits == 0 and db.rollbacks >= 1
    assert counts(import_case) == (0, 0)
