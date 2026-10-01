"""Real PostgreSQL contracts for shared bank/payment matching."""
from __future__ import annotations

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import bank_statement_import, payment_matching
from app.documents.repository import DocumentRepository
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
    engine.dispose()


CSV = "date,amount,currency,reference\n2026-09-28,{amount},{currency},{reference}\n"


def seed_op(case, amount="100", direction="debitoren", currency="EUR", number=None, doc=True):
    db, _, tenant = case
    number = number or f"RE-{tenant}"
    op_id = str(uuid4())
    db.info.setdefault("owned_ops", []).append(op_id)
    db.execute(text("""
        INSERT INTO domain_erp.offene_posten
        (id,tenant_id,rechnungsnr,konto_typ,offen,op_status,waehrung,betrag,kunde_id,faelligkeit)
        VALUES (:id,:tenant,:number,:direction,:amount,'offen',:currency,:amount,:tenant,CURRENT_DATE)
    """), {"id": op_id, "tenant": tenant, "number": number, "direction": direction,
            "amount": Decimal(amount), "currency": currency})
    if doc:
        db.info.setdefault("owned_documents", []).append(number)
        DocumentRepository(db).save_document("sales_invoice" if direction == "debitoren" else "ap_invoice",
            number, {"status": "GEBUCHT", "tenantId": tenant})
    else:
        db.commit()
    db.commits = db.rollbacks = 0
    return op_id


def upload(case, amount="100", currency="EUR", reference=None, auto=True):
    _, client, tenant = case
    reference = reference or f"RE-{tenant}"
    csv = CSV.format(amount=amount, currency=currency, reference=reference)
    return client.post("/bank-statements/import", params={"tenant_id": tenant,
        "bank_account_id": "bank-test", "format": "CSV", "auto_match": auto},
        files={"file": ("statement.csv", csv.encode(), "text/csv")})


def op_state(case, op_id):
    return case[0].execute(text("SELECT offen,op_status FROM domain_erp.offene_posten WHERE id=:id"), {"id": op_id}).one()


def line_id(case):
    return case[0].execute(text("SELECT id FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": case[2]}).scalar_one()


def line_state(case):
    return case[0].execute(text("SELECT status,matched_op_id FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": case[2]}).one()


def manual(case, op_id, payment_id=None):
    return case[1].post(f"/payments/match/{payment_id or line_id(case)}", params={"op_id": op_id})


def test_auto_import_fully_settles_real_payment_and_invoice_once(import_case):
    op = seed_op(import_case)
    response = upload(import_case)
    assert response.status_code == 200, response.text
    assert response.json()["lines"][0]["status"] == "MATCHED"
    assert op_state(import_case, op) == (Decimal("0"), "geschlossen")
    assert line_state(import_case) == ("MATCHED", op)
    assert DocumentRepository(import_case[0]).get_document("sales_invoice", f"RE-{import_case[2]}")["status"] == "BEZAHLT"
    assert import_case[0].commits == 1
    repeated = manual(import_case, op)
    assert repeated.status_code == 200, repeated.text
    assert op_state(import_case, op)[0] == 0


def test_partial_payment_keeps_invoice_unpaid(import_case):
    op = seed_op(import_case)
    assert upload(import_case, amount="40").status_code == 200
    assert op_state(import_case, op) == (Decimal("60"), "teilweise")
    assert line_state(import_case) == ("MATCHED", op)
    assert DocumentRepository(import_case[0]).get_document("sales_invoice", f"RE-{import_case[2]}")["status"] == "GEBUCHT"


def test_manual_uses_actual_bank_amount_not_assumed_full_op(import_case):
    op = seed_op(import_case)
    assert upload(import_case, amount="25", auto=False).status_code == 200
    response = manual(import_case, op)
    assert response.status_code == 200, response.text
    assert Decimal(response.json()["matched_amount"]) == 25
    assert response.json()["match_type"] == "PARTIAL"
    assert op_state(import_case, op)[0] == 75


def test_missing_payment_cannot_settle_anything(import_case):
    op = seed_op(import_case)
    response = manual(import_case, op, "missing-payment")
    assert response.status_code == 404, response.text
    assert op_state(import_case, op)[0] == 100


@pytest.mark.parametrize("amount,currency", [("-100", "EUR"), ("100", "USD"), ("101", "EUR")])
def test_wrong_direction_currency_or_overpayment_is_not_auto_matched(import_case, amount, currency):
    op = seed_op(import_case)
    assert upload(import_case, amount=amount, currency=currency).status_code == 200
    assert op_state(import_case, op)[0] == 100
    assert line_state(import_case) == ("UNMATCHED", None)
    response = manual(import_case, op)
    assert response.status_code == 409
    assert op_state(import_case, op)[0] == 100


def test_negative_bank_debit_settles_creditor_only(import_case):
    op = seed_op(import_case, direction="kreditoren")
    response = upload(import_case, amount="-100")
    assert response.status_code == 200, response.text
    assert op_state(import_case, op)[0] == 0
    assert DocumentRepository(import_case[0]).get_document("ap_invoice", f"RE-{import_case[2]}")["status"] == "BEZAHLT"


def test_ambiguous_reference_is_not_arbitrarily_selected(import_case):
    first = seed_op(import_case)
    second = seed_op(import_case, doc=False)
    assert upload(import_case).status_code == 200
    assert op_state(import_case, first)[0] == op_state(import_case, second)[0] == 100
    assert line_state(import_case) == ("UNMATCHED", None)


def test_reference_prefix_cannot_select_different_invoice(import_case):
    op = seed_op(import_case)
    assert upload(import_case, reference="RE-2026").status_code == 200
    assert op_state(import_case, op)[0] == 100


@pytest.mark.parametrize("failure", ["UPDATE domain_erp.offene_posten", "UPDATE domain_erp.bank_statement_lines", "UPDATE documents", "INSERT INTO domain_shared.audit_logs"])
def test_matching_sql_error_rolls_back_import_op_and_invoice(import_case, failure):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.fail_match = failure
    response = upload(import_case)
    assert response.status_code == 500, response.text
    db.fail_match = None
    assert op_state(import_case, op)[0] == 100
    assert DocumentRepository(db).get_document("sales_invoice", f"RE-{import_case[2]}")["status"] == "GEBUCHT"
    assert db.execute(text("SELECT count(*) FROM domain_erp.bank_statements WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 0


def test_tenant_query_cannot_override_header(import_case):
    op = seed_op(import_case)
    response = upload(import_case, auto=False)
    assert response.status_code == 200
    foreign = str(uuid4())
    response = import_case[1].post(f"/payments/match/{line_id(import_case)}",
        headers={"X-Tenant-ID": foreign}, params={"tenant_id": import_case[2], "op_id": op})
    assert response.status_code == 404
    assert op_state(import_case, op)[0] == 100


def test_full_settlement_rejects_foreign_document(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.execute(text("UPDATE documents SET data=jsonb_set(data,'{tenantId}',to_jsonb(CAST(:t AS text))) WHERE doc_type='sales_invoice' AND doc_number=:nr"), {"t": str(uuid4()), "nr": f"RE-{tenant}"})
    db.commit()
    response = upload(import_case)
    assert response.status_code == 409, response.text
    assert op_state(import_case, op)[0] == 100
    # Restore only the owned fixture document for its cleanup.
    db.execute(text("UPDATE documents SET data=jsonb_set(data,'{tenantId}',to_jsonb(CAST(:t AS text))) WHERE doc_type='sales_invoice' AND doc_number=:nr"), {"t": tenant, "nr": f"RE-{tenant}"})
    db.commit()


def test_batch_endpoint_and_repetition_share_the_same_contract(import_case):
    op = seed_op(import_case)
    assert upload(import_case, amount="30", auto=False).status_code == 200
    response = import_case[1].post("/payments/auto-match")
    assert response.status_code == 200, response.text
    assert response.json()[0]["match_type"] == "PARTIAL"
    assert op_state(import_case, op)[0] == 70
    assert import_case[1].post("/payments/auto-match").json() == []
    assert op_state(import_case, op)[0] == 70


def test_parallel_calls_cannot_allocate_the_same_payment_twice(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    assert upload(import_case, amount="40", auto=False).status_code == 200
    payment = line_id(import_case)
    db.rollback()  # Release the test observation transaction before workers.

    def match_once():
        with Session(db.get_bind()) as worker:
            result = asyncio.run(payment_matching.match_payment(
                payment_id=payment, op_id=op, tenant_id=tenant, db=worker))
            return result.matched_amount

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: match_once(), range(2)))
    assert results == [Decimal("40"), Decimal("40")]
    assert op_state(import_case, op)[0] == 60
    assert line_state(import_case) == ("MATCHED", op)


def test_existing_assignment_cannot_be_redirected(import_case):
    first = seed_op(import_case)
    second = seed_op(import_case, number=f"RE-{import_case[2]}-other", doc=False)
    assert upload(import_case).status_code == 200
    response = manual(import_case, second)
    assert response.status_code == 409
    assert line_state(import_case) == ("MATCHED", first)
    assert op_state(import_case, second)[0] == 100


def test_commit_failure_rolls_back_matching_and_import(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.failure = "commit"
    response = upload(import_case)
    assert response.status_code == 500, response.text
    db.failure = None
    assert op_state(import_case, op)[0] == 100
    assert DocumentRepository(db).get_document("sales_invoice", f"RE-{tenant}")["status"] == "GEBUCHT"
    assert db.execute(text("SELECT count(*) FROM domain_erp.bank_statement_lines WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 0


def test_manual_line_failure_rolls_back_op_and_document(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    assert upload(import_case, auto=False).status_code == 200
    db.fail_match = "UPDATE domain_erp.bank_statement_lines"
    response = manual(import_case, op)
    assert response.status_code == 500, response.text
    db.fail_match = None
    assert op_state(import_case, op)[0] == 100
    assert line_state(import_case) == ("UNMATCHED", None)
    assert DocumentRepository(db).get_document("sales_invoice", f"RE-{tenant}")["status"] == "GEBUCHT"


def test_auto_match_cannot_use_foreign_tenant_open_item(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.execute(text("UPDATE domain_erp.offene_posten SET tenant_id=:foreign WHERE id=:id"),
               {"foreign": str(uuid4()), "id": op})
    db.commit()
    assert upload(import_case).status_code == 200
    assert op_state(import_case, op)[0] == 100
    assert line_state(import_case) == ("UNMATCHED", None)


def test_missing_document_tenant_is_not_assumed_to_be_current_tenant(import_case):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.execute(text("UPDATE documents SET data=data-'tenantId' WHERE doc_type='sales_invoice' AND doc_number=:nr"), {"nr": f"RE-{tenant}"})
    db.commit()
    response = upload(import_case)
    assert response.status_code == 409, response.text
    assert op_state(import_case, op)[0] == 100


def test_matching_has_one_transactional_hash_chained_evidence_record(import_case):
    db, client, tenant = import_case
    op = seed_op(import_case)
    client.headers["X-User-ID"] = "unverified-header-actor"
    assert upload(import_case, amount="40").status_code == 200
    assert manual(import_case, op).status_code == 200
    audit = db.execute(text("SELECT action,changes,hash FROM domain_shared.audit_logs WHERE tenant_id=:t"), {"t": tenant}).all()
    assert len(audit) == 1
    assert audit[0][0] == "match_bank_payment"
    assert Decimal(audit[0][1]["previous_open_amount"]) == 100
    assert Decimal(audit[0][1]["matched_amount"]) == 40
    assert Decimal(audit[0][1]["new_open_amount"]) == 60
    assert len(audit[0][2]) == 64
    actor = db.execute(text("SELECT user_id FROM domain_shared.audit_logs WHERE tenant_id=:t"), {"t": tenant}).scalar_one()
    assert actor != "unverified-header-actor"


def test_open_item_reader_uses_migrated_amount_column(import_case):
    seed_op(import_case)
    response = import_case[1].get(f"/payments/open-items/{import_case[2]}")
    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert Decimal(response.json()[0]["amount"]) == 100


@pytest.mark.parametrize("kind", ["unmatched", "open-items", "statement-lines"])
def test_financial_readers_ignore_foreign_tenant_query(import_case, kind):
    seed_op(import_case)
    response = upload(import_case, auto=False)
    assert response.status_code == 200
    tenant = import_case[2]
    paths = {"unmatched": "/payments/unmatched", "open-items": f"/payments/open-items/{tenant}",
             "statement-lines": f"/bank-statements/{response.json()['statement_id']}/lines"}
    response = import_case[1].get(paths[kind], headers={"X-Tenant-ID": str(uuid4())},
                                  params={"tenant_id": tenant})
    assert response.status_code == 200, response.text
    assert response.json() == []


@pytest.mark.parametrize("status", ["STORNIERT", "GUTGESCHRIEBEN"])
def test_cancelled_or_credited_document_prevents_settlement(import_case, status):
    db, _, tenant = import_case
    op = seed_op(import_case)
    db.execute(text("UPDATE documents SET data=jsonb_set(data,'{status}',to_jsonb(CAST(:status AS text))) WHERE doc_type='sales_invoice' AND doc_number=:nr"),
               {"status": status, "nr": f"RE-{tenant}"})
    db.commit()
    response = upload(import_case)
    assert response.status_code == 409, response.text
    assert op_state(import_case, op)[0] == 100
