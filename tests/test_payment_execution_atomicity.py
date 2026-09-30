"""Payment execution against a migrated PostgreSQL test database.

Use TEST_DATABASE_URL, or CI's DATABASE_URL pointing to a test database.
Every fixture owns unique records; never reset a shared database.
"""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import payment_runs
from app.core.database import get_db
from app.documents.repository import DocumentRepository


class ObservedSession(Session):
    commits = 0
    rollbacks = 0
    fail_document = False
    fail_op = False
    fail_response = False
    response_reads = 0

    def commit(self):
        self.commits += 1
        super().commit()

    def rollback(self):
        self.rollbacks += 1
        super().rollback()

    def execute(self, statement, *args, **kwargs):
        sql = str(statement)
        if "SELECT id, run_number" in sql:
            self.response_reads += 1
            if self.fail_response and self.response_reads == 2:
                return super().execute(text("SELECT 1 / 0"))
        if (self.fail_document and "UPDATE documents" in sql) or (
            self.fail_op and "UPDATE domain_erp.offene_posten" in sql
        ):
            # A real PostgreSQL error poisons the transaction until rollback.
            return super().execute(text("SELECT 1 / 0"))
        return super().execute(statement, *args, **kwargs)


@pytest.fixture
def execution_case():
    raw_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not raw_url:
        pytest.skip("Explicit migrated PostgreSQL test database required")
    url = make_url(raw_url)
    if "test" not in (url.database or "").lower():
        if os.getenv("TEST_DATABASE_URL"):
            pytest.fail("TEST_DATABASE_URL must name a test database")
        pytest.skip("Never seed payment tests into a development database")
    if not url.drivername.startswith("postgresql"):
        pytest.fail("PostgreSQL required to verify failed-transaction semantics")
    engine = create_engine(url)
    db = ObservedSession(engine)
    suffix = uuid4().hex
    ids = {key: f"{key}-{suffix}" for key in ("run", "op", "invoice", "item", "tenant")}
    db.execute(text("""
        INSERT INTO domain_erp.payment_runs
          (id,tenant_id,run_number,execution_date,initiator_name,initiator_iban,
           initiator_bic,total_amount,payment_count,status)
        VALUES (:run,:tenant,:run,CURRENT_DATE,'Test','DE89370400440532013000',
          'COBADEFFXXX',500,1,'approved')
    """), ids)
    db.execute(text("""
        INSERT INTO domain_erp.offene_posten
          (id,tenant_id,rechnungsnr,konto_typ,offen,op_status)
        VALUES (:op,:tenant,:invoice,'kreditoren',500,'offen')
    """), ids)
    db.execute(text("""
        INSERT INTO domain_erp.payment_run_items
          (id,tenant_id,payment_run_id,creditor_id,creditor_name,iban,bic,
           amount,purpose,op_id,invoice_number)
        VALUES (:item,:tenant,:run,'TEST','Test','DE27100777770209299700',
          'DEUTDEFF',500,'Test',:op,:invoice)
    """), ids)
    DocumentRepository(db).save_document("ap_invoice", ids["invoice"], {
        "status": "GEBUCHT", "tenantId": ids["tenant"],
    })
    db.commits = db.rollbacks = 0
    app = FastAPI()
    app.include_router(payment_runs.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield db, client, ids
    db.rollback()
    db.close()
    with engine.begin() as cleanup:
        cleanup.execute(text("DELETE FROM domain_erp.payment_run_items WHERE payment_run_id=:run"), ids)
        cleanup.execute(text("DELETE FROM domain_erp.payment_runs WHERE id=:run"), ids)
        cleanup.execute(text("DELETE FROM domain_erp.offene_posten WHERE id=:op"), ids)
        cleanup.execute(text("DELETE FROM documents WHERE doc_type='ap_invoice' AND doc_number=:invoice"), ids)
    engine.dispose()


def execute(case):
    _, client, ids = case
    return client.post(f"/finance/payment-runs/{ids['run']}/execute",
                       params={"tenant_id": ids["tenant"]}, json={"executed_by": "test"})


def state(db, ids):
    return (
        db.execute(text("SELECT status FROM domain_erp.payment_runs WHERE id=:run"), ids).scalar_one(),
        db.execute(text("SELECT offen FROM domain_erp.offene_posten WHERE id=:op"), ids).scalar_one(),
        DocumentRepository(db).get_document("ap_invoice", ids["invoice"])["status"],
    )


def test_full_settlement_commits_once_and_repetition_cannot_debit(execution_case):
    db, _, ids = execution_case
    assert execute(execution_case).status_code == 200
    assert db.commits == 1
    assert state(db, ids) == ("executed", Decimal("0"), "BEZAHLT")
    assert execute(execution_case).status_code == 400
    assert db.commits == 1
    assert state(db, ids) == ("executed", Decimal("0"), "BEZAHLT")


def test_partial_settlement_preserves_invoice(execution_case):
    db, _, ids = execution_case
    db.execute(text("UPDATE domain_erp.offene_posten SET offen=750 WHERE id=:op"), ids)
    db.commit()
    db.commits = 0
    assert execute(execution_case).status_code == 200
    assert db.commits == 1
    assert state(db, ids) == ("executed", Decimal("250"), "GEBUCHT")


@pytest.mark.parametrize("failure", ["fail_document", "fail_op", "fail_response"])
def test_real_sql_failure_rolls_back_every_write(execution_case, failure):
    db, _, ids = execution_case
    setattr(db, failure, True)
    response = execute(execution_case)
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to execute payment run"
    assert db.commits == 0
    assert db.rollbacks >= 1
    assert state(db, ids) == ("approved", Decimal("500"), "GEBUCHT")
    assert db.execute(text("SELECT status FROM domain_erp.payment_run_items WHERE id=:item"), ids).scalar_one() == "pending"


@pytest.mark.parametrize("condition", ["missing", "insufficient", "wrong_tenant", "debtor"])
def test_invalid_open_item_blocks_execution(execution_case, condition):
    db, _, ids = execution_case
    mutations = {
        "missing": "UPDATE domain_erp.payment_run_items SET op_id='missing' WHERE id=:item",
        "insufficient": "UPDATE domain_erp.offene_posten SET offen=100 WHERE id=:op",
        "wrong_tenant": "UPDATE domain_erp.offene_posten SET tenant_id='other' WHERE id=:op",
        "debtor": "UPDATE domain_erp.offene_posten SET konto_typ='debitoren' WHERE id=:op",
    }
    db.execute(text(mutations[condition]), ids)
    db.commit()
    db.commits = 0
    assert execute(execution_case).status_code == 409
    assert db.commits == 0
    assert state(db, ids)[0::2] == ("approved", "GEBUCHT")


@pytest.mark.parametrize("invalid_doc", [{"status": "STORNIERT"}, {"tenantId": "other"}])
def test_invalid_invoice_rolls_back_open_item(execution_case, invalid_doc):
    db, _, ids = execution_case
    doc = DocumentRepository(db).get_document("ap_invoice", ids["invoice"])
    doc.update(invalid_doc)
    DocumentRepository(db).save_document("ap_invoice", ids["invoice"], doc)
    db.commits = 0
    assert execute(execution_case).status_code == 409
    assert db.commits == 0
    assert state(db, ids)[:2] == ("approved", Decimal("500"))


def test_document_default_commit_is_backwards_compatible(execution_case):
    db, _, ids = execution_case
    repo = DocumentRepository(db)
    doc = repo.get_document("ap_invoice", ids["invoice"])
    doc["status"] = "DRAFT"
    repo.save_document("ap_invoice", ids["invoice"], doc, commit=False)
    assert db.commits == 0
    db.rollback()
    assert repo.get_document("ap_invoice", ids["invoice"])["status"] == "GEBUCHT"
    repo.save_document("ap_invoice", ids["invoice"], doc)
    assert db.commits == 1
    assert repo.get_document("ap_invoice", ids["invoice"])["status"] == "DRAFT"


@pytest.mark.parametrize("mutation", [
    "UPDATE domain_erp.payment_run_items SET tenant_id='other' WHERE id=:item",
    "UPDATE domain_erp.payment_runs SET total_amount=501 WHERE id=:run",
    "UPDATE domain_erp.payment_run_items SET status='executed' WHERE id=:item",
    "UPDATE domain_erp.payment_run_items SET invoice_number='other' WHERE id=:item",
])
def test_contradictory_run_blocks_settlement(execution_case, mutation):
    db, _, ids = execution_case
    db.execute(text(mutation), ids)
    db.commit()
    db.commits = 0
    assert execute(execution_case).status_code == 409
    assert db.commits == 0
    assert state(db, ids) == ("approved", Decimal("500"), "GEBUCHT")


def test_concurrent_requests_only_execute_once(execution_case):
    db, _, ids = execution_case
    engine = db.get_bind()

    def request():
        with ObservedSession(engine) as own_db:
            app = FastAPI()
            app.include_router(payment_runs.router, prefix="/finance")
            app.dependency_overrides[get_db] = lambda: own_db
            with TestClient(app) as client:
                response = client.post(f"/finance/payment-runs/{ids['run']}/execute",
                                       params={"tenant_id": ids["tenant"]},
                                       json={"executed_by": "test"})
            return response.status_code, own_db.commits

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = list(workers.map(lambda _: request(), range(2)))
    assert sorted(status for status, _ in results) == [200, 400]
    assert sum(commits for _, commits in results) == 1
    assert state(db, ids) == ("executed", Decimal("0"), "BEZAHLT")
