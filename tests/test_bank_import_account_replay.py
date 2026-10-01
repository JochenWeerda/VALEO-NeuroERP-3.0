"""Real PostgreSQL account-binding and byte-identical replay contracts."""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import bank_statement_import, payment_matching
from app.core.database import get_db


class ImportSession(Session):
    failure = None
    fail_match = None
    commits = 0
    rollbacks = 0

    def execute(self, statement, params=None, **kwargs):
        sql = str(statement)
        if self.fail_match and self.fail_match in sql:
            return super().execute(text("SELECT 1 / 0"))
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
    """), {"id": f"bank-{tenant}", "t": tenant, "currency": "EUR"})
    db.commit()
    db.commits = db.rollbacks = 0
    app = FastAPI()
    app.include_router(bank_statement_import.router)
    app.include_router(payment_matching.router, prefix="/payments")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, headers={"X-Tenant-ID": tenant}) as client:
        yield db, client, tenant
    db.rollback()
    db.close()
    with engine.begin() as cleanup:
        cleanup.execute(text("DELETE FROM domain_shared.audit_logs WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.bank_statements WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_erp.offene_posten WHERE id=ANY(:ids)"),
            {"ids": db.info.get("owned_ops", [])})
        cleanup.execute(text("DELETE FROM documents WHERE doc_number=ANY(:numbers)"),
            {"numbers": db.info.get("owned_documents", [])})
        cleanup.execute(text("DELETE FROM domain_erp.bank_accounts WHERE tenant_id=:t"), {"t": tenant})
        cleanup.execute(text("DELETE FROM domain_shared.tenants WHERE id=:t"), {"t": tenant})
    engine.dispose()


CSV = "date,amount,currency,reference\n2026-09-28,25.00,EUR,REF-1\n"


def upload(case, content=CSV, account=None, fmt="CSV", auto=False, route="bank"):
    _, client, tenant = case
    params = {"format": fmt, "bank_account_id": account or f"bank-{tenant}", "auto_match": auto}
    path = "/bank-statements/import"
    if route == "payments":
        path = "/payments/import/csv"
        params = {"bank_account": account or f"bank-{tenant}"}
    return client.post(path, params=params, files={"file": ("statement.dat", content.encode(), "application/octet-stream")})


def counts(case):
    db, _, tenant = case
    return tuple(db.execute(text(f"SELECT count(*) FROM domain_erp.{table} WHERE tenant_id=:t"),
                           {"t": tenant}).scalar_one() for table in ("bank_statements", "bank_statement_lines"))


@pytest.mark.parametrize("route", ["bank", "payments"])
def test_missing_account_never_creates_statement(import_case, route):
    response = upload(import_case, account="missing", route=route)
    assert response.status_code == 404, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize("route", ["bank", "payments"])
def test_inactive_account_never_creates_statement(import_case, route):
    db, _, tenant = import_case
    db.execute(text("UPDATE domain_erp.bank_accounts SET is_active=FALSE WHERE tenant_id=:t"), {"t": tenant})
    db.commit()
    response = upload(import_case, route=route)
    assert response.status_code == 404, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize("route", ["bank", "payments"])
def test_foreign_account_never_creates_statement(import_case, route):
    db, _, tenant = import_case
    foreign = str(uuid4())
    db.execute(text("INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:t,'Foreign',:d,TRUE)"), {"t": foreign, "d": f"{foreign}.test.local"})
    db.execute(text("UPDATE domain_erp.bank_accounts SET tenant_id=:f WHERE id=:id"), {"f": foreign, "id": f"bank-{tenant}"})
    db.commit()
    try:
        response = upload(import_case, route=route)
        assert response.status_code == 404, response.text
        assert counts(import_case) == (0, 0)
    finally:
        db.rollback()
        db.execute(text("UPDATE domain_erp.bank_accounts SET tenant_id=:t WHERE id=:id"), {"t": tenant, "id": f"bank-{tenant}"})
        db.execute(text("DELETE FROM domain_shared.tenants WHERE id=:f"), {"f": foreign})
        db.commit()


@pytest.mark.parametrize("route", ["bank", "payments"])
def test_currency_must_match_selected_bank_account(import_case, route):
    response = upload(import_case, CSV.replace("EUR", "USD"), route=route)
    assert response.status_code == 422, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize("route", ["bank", "payments"])
def test_invalid_bank_iban_is_not_assumed_valid(import_case, route):
    db, _, tenant = import_case
    db.execute(text("UPDATE domain_erp.bank_accounts SET iban='DE00000000000000000000' WHERE tenant_id=:t"), {"t": tenant})
    db.commit()
    response = upload(import_case, route=route)
    assert response.status_code == 409, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize("first_route,second_route", [("bank", "bank"), ("payments", "payments"), ("bank", "payments"), ("payments", "bank")])
def test_identical_bytes_across_import_routes_are_stored_once(import_case, first_route, second_route):
    first = upload(import_case, route=first_route)
    second = upload(import_case, route=second_route)
    assert first.status_code == second.status_code == 200, (first.text, second.text)
    assert counts(import_case) == (1, 1)
    bank = upload(import_case)
    assert bank.json()["total_lines"] == bank.json()["imported_lines"] == 1


def test_replay_does_not_match_payment_or_write_audit_again(import_case):
    db, _, tenant = import_case
    op = str(uuid4())
    db.info.setdefault("owned_ops", []).append(op)
    db.execute(text("INSERT INTO domain_erp.offene_posten (id,tenant_id,rechnungsnr,konto_typ,offen,op_status,waehrung) VALUES (:id,:t,'REF-1','debitoren',100,'offen','EUR')"), {"id": op, "t": tenant})
    db.commit()
    first = upload(import_case, auto=True)
    replay = upload(import_case, auto=True)
    assert first.status_code == replay.status_code == 200, replay.text
    assert first.json()["statement_id"] == replay.json()["statement_id"]
    assert replay.json()["lines"][0]["status"] == "MATCHED"
    assert db.execute(text("SELECT offen FROM domain_erp.offene_posten WHERE id=:id"), {"id": op}).scalar_one() == 75
    assert db.execute(text("SELECT count(*) FROM domain_shared.audit_logs WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 1


def test_failed_first_commit_leaves_import_retryable(import_case):
    db, _, _ = import_case
    db.failure = "commit"
    assert upload(import_case).status_code == 500
    assert counts(import_case) == (0, 0)
    db.failure = None
    assert upload(import_case).status_code == 200
    assert counts(import_case) == (1, 1)


def test_different_bytes_keep_distinct_import_identity(import_case):
    first = upload(import_case)
    second = upload(import_case, CSV.replace("REF-1", "REF-2"))
    assert first.status_code == second.status_code == 200
    assert first.json()["statement_id"] != second.json()["statement_id"]
    assert counts(import_case) == (2, 2)


def test_parallel_cross_route_uploads_store_one_statement(import_case):
    db, _, tenant = import_case
    barrier = Barrier(2)

    def concurrent_upload(route):
        with Session(db.bind) as session:
            session.execute(text("SET statement_timeout='10s'"))
            app = FastAPI()
            app.include_router(bank_statement_import.router)
            app.include_router(payment_matching.router, prefix='/payments')
            app.dependency_overrides[get_db] = lambda: session
            with TestClient(app, headers={'X-Tenant-ID': tenant}) as client:
                barrier.wait(timeout=10)
                return upload((session, client, tenant), route=route)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(concurrent_upload, ['bank', 'payments']))
    assert [result.status_code for result in results] == [200, 200], [r.text for r in results]
    assert counts(import_case) == (1, 1)


CAMT_STMT = '''<Stmt><Acct><Id><IBAN>{iban}</IBAN></Id></Acct>
<Ntry><Amt Ccy="{currency}">25.00</Amt><CdtDbtInd>CRDT</CdtDbtInd>
<BookgDt><Dt>2026-09-28</Dt></BookgDt><Refs><AcctSvcrRef>REF-1</AcctSvcrRef></Refs>
</Ntry></Stmt>'''


def camt(iban='DE89370400440532013000', currency='EUR', count=1):
    return '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"><BkToCstmrStmt>' + (
        CAMT_STMT.format(iban=iban, currency=currency) * count
    ) + '</BkToCstmrStmt></Document>'


@pytest.mark.parametrize('iban', ['', 'DE12500105170648489890'])
def test_camt_missing_or_foreign_iban_rejected(import_case, iban):
    response = upload(import_case, camt(iban), fmt='CAMT')
    assert response.status_code == 422, response.text
    assert counts(import_case) == (0, 0)


def test_camt_normalizes_iban_and_preserves_account_currency(import_case):
    db, _, tenant = import_case
    db.execute(text("UPDATE domain_erp.bank_accounts SET currency='CHF' WHERE tenant_id=:t"), {'t': tenant})
    db.commit()
    response = upload(import_case, camt('de89 3704 0044 0532 0130 00', 'CHF'), fmt='camt')
    assert response.status_code == 200, response.text
    assert response.json()['account_iban'] == 'DE89370400440532013000'
    assert response.json()['lines'][0]['currency'] == 'CHF'


def test_camt_multiple_statements_rejected_before_writes(import_case):
    response = upload(import_case, camt(count=2), fmt='CAMT')
    assert response.status_code == 400, response.text
    assert counts(import_case) == (0, 0)


@pytest.mark.parametrize('route', ['bank', 'payments'])
def test_incomplete_stored_import_rejected_and_transaction_released(import_case, route):
    assert upload(import_case).status_code == 200
    db, _, tenant = import_case
    db.execute(text('DELETE FROM domain_erp.bank_statement_lines WHERE tenant_id=:t'), {'t': tenant})
    db.commit()
    response = upload(import_case, route=route)
    assert response.status_code == 409, response.text
    assert not db.in_transaction()
    assert counts(import_case) == (1, 0)


def test_replay_with_auto_flag_does_not_change_original_manual_import(import_case):
    first = upload(import_case)
    replay = upload(import_case, fmt='csv', auto=True)
    assert first.status_code == replay.status_code == 200
    assert first.json() == replay.json()
    assert counts(import_case) == (1, 1)


@pytest.mark.parametrize('first_route', ['bank', 'payments'])
def test_value_date_and_csv_sum_independent_of_first_route(import_case, first_route):
    content = 'date,value_date,amount,currency,reference\n2026-09-28,2026-09-29,25.00,EUR,REF-1\n'
    assert upload(import_case, content, route=first_route).status_code == 200
    replay = upload(import_case, content)
    assert replay.status_code == 200, replay.text
    assert replay.json()['lines'][0]['value_date'] == '2026-09-29'
    assert float(replay.json()['closing_balance']) == 25
