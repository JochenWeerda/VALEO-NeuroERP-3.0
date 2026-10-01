"""Real PostgreSQL contracts for atomic CSV payment imports."""
from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import payment_matching
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
    tenant = f"import-test-{uuid4().hex}"
    app = FastAPI()
    app.include_router(payment_matching.router, prefix="/payments")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield db, client, tenant
    db.rollback()
    db.close()
    with engine.begin() as cleanup:
        cleanup.execute(text("DELETE FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.bank_statements WHERE tenant_id=:t"), {"t": tenant})
    engine.dispose()


CSV = "date,amount,currency,reference\n2026-09-28,10.00,USD,REF-1\n2026-09-29,20.00,CHF,REF-2\n"


def upload(case, csv=CSV):
    _, client, tenant = case
    return client.post("/payments/import/csv", params={"tenant_id": tenant, "bank_account": "bank-test"},
                       files={"file": ("payments.csv", csv.encode(), "text/csv")})


def counts(case):
    db, _, tenant = case
    return tuple(db.execute(text(f"SELECT count(*) FROM domain_erp.{table} WHERE tenant_id=:t"),
                            {"t": tenant}).scalar_one()
                 for table in ("bank_statements", "bank_statement_lines"))


def test_currency_and_success_counts_match_persisted_rows(import_case):
    db, _, tenant = import_case
    response = upload(import_case)
    assert response.status_code == 200, response.text
    assert [row["currency"] for row in response.json()] == ["USD", "CHF"]
    rows = db.execute(text("""
        SELECT currency,amount FROM domain_erp.bank_statement_lines
        WHERE tenant_id=:t ORDER BY line_number
    """), {"t": tenant}).all()
    assert rows == [("USD", Decimal("10")), ("CHF", Decimal("20"))]
    assert counts(import_case) == (1, 2)
    assert db.commits == 1


@pytest.mark.parametrize("failure", ["header", "line", "commit"])
def test_real_sql_error_never_leaves_partial_import(import_case, failure):
    db, _, _ = import_case
    db.failure = failure
    response = upload(import_case)
    assert response.status_code == 500, response.text
    assert response.json()["detail"] == "Failed to import CSV"
    assert db.rollbacks >= 1
    assert counts(import_case) == (0, 0)


def test_database_constraint_on_second_line_rolls_back_first_line(import_case):
    csv = CSV.replace("REF-2", "R" * 256)
    response = upload(import_case, csv)
    assert response.status_code == 500
    assert counts(import_case) == (0, 0)


def test_imports_in_same_second_have_distinct_ids(import_case, monkeypatch):
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 30, 12, 0, 0)

    monkeypatch.setattr(payment_matching, "datetime", FrozenDatetime)
    first, second = upload(import_case), upload(import_case)
    assert first.status_code == second.status_code == 200
    assert len(first.json()) == len(second.json()) == 2
    assert set(row["id"] for row in first.json()).isdisjoint(row["id"] for row in second.json())
    assert counts(import_case) == (2, 4)


@pytest.mark.parametrize("csv", [
    "date,amount,currency,reference\n2026-09-28,10.00,XXX,REF-1\n",
    "date,amount,currency,reference\n2026-09-28,10.001,EUR,REF-1\n",
    "date,amount,currency,reference\n2026-09-28,10,EUR,REF-1\n2026-09-29,-5,EUR,REF-2\n",
])
def test_invalid_input_is_rejected_before_any_write(import_case, csv):
    db, _, _ = import_case
    response = upload(import_case, csv)
    assert response.status_code == 422, response.text
    assert db.commits == 0
    assert counts(import_case) == (0, 0)


def test_empty_file_does_not_create_header(import_case):
    response = upload(import_case, "date,amount,currency,reference\n")
    assert response.status_code == 200
    assert response.json() == []
    assert counts(import_case) == (0, 0)
