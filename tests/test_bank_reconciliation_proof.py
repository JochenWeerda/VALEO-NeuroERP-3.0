"""Real PostgreSQL contract in an owned schema on the existing shared database."""
import importlib.util
import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.endpoints import bank_accounts, bank_reconciliation
from app.core.database import get_db


@pytest.fixture(scope="module")
def schema():
    raw = os.getenv("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("Existing shared test PostgreSQL required")
    url = make_url(raw)
    assert url.database == "valeo_probe" or "test" in url.database.lower()
    engine = create_engine(url)
    name = "bankproof_" + uuid4().hex
    tables = ("bank_accounts", "chart_of_accounts", "bank_statements", "bank_statement_lines",
              "journal_entries", "journal_entry_lines", "offene_posten")
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{name}"'))
        for table in tables:
            conn.execute(text(f'CREATE TABLE "{name}".{table} (LIKE domain_erp.{table} INCLUDING ALL)'))
    path = Path("alembic/versions/bank_gl_binding_20261001.py")
    spec = importlib.util.spec_from_file_location("bank_gl_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        with engine.begin() as conn:
            class Bind:
                def execute(self, statement):
                    return conn.execute(text(str(statement).replace("domain_erp.", f'"{name}".')))
            previous = module.op.get_bind
            module.op.get_bind = lambda: Bind()
            try:
                module.upgrade()
            finally:
                module.op.get_bind = previous
        yield engine, name
    finally:
        # UUID-derived identifier, confined to this fixture's one owned schema.
        assert name.startswith("bankproof_") and len(name) == 42
        with engine.begin() as conn:
            conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))
        engine.dispose()


@pytest.fixture
def case(schema, request):
    engine, name = schema
    class SchemaSession(Session):
        failure = False
        commits = 0
        reads = 0

        def execute(self, statement, params=None, **kwargs):
            sql = str(statement).replace("domain_erp.", f'"{name}".')
            if sql.startswith("\nWITH statement"):
                self.reads += 1
                if self.failure:
                    sql = "SELECT 1/0"
            return super().execute(text(sql), params, **kwargs)

        def commit(self):
            self.commits += 1
            return super().commit()

    db = SchemaSession(engine)
    request.addfinalizer(db.close)
    tenant, other = str(uuid4()), str(uuid4())
    bank, gl, contra, statement = (str(uuid4()) for _ in range(4))
    for account, typ in ((gl, "ASSET"), (contra, "LIABILITY")):
        db.execute(text("""INSERT INTO domain_erp.chart_of_accounts
            (id,tenant_id,account_number,account_name,account_type,category,is_active,is_summary)
            VALUES (:id,:t,:number,'Proof account',:typ,'bank',TRUE,FALSE)"""), {"id": account, "t": tenant, "typ": typ, "number": uuid4().hex[:20]})
    db.execute(text("""INSERT INTO domain_erp.bank_accounts
        (id,tenant_id,account_number,bank_name,iban,currency,is_active,gl_account_id)
        VALUES (:id,:t,:id,'Proof bank','DE89370400440532013000','EUR',TRUE,:gl)"""),
        {"id": bank, "t": tenant, "gl": gl})
    db.execute(text("""INSERT INTO domain_erp.bank_statements
        (id,tenant_id,bank_account_id,account_iban,statement_date,opening_balance,closing_balance,format,total_lines,imported_lines,status)
        VALUES (:id,:t,:bank,'DE89370400440532013000','2026-09-28',0,25,'MT940',1,1,'imported')"""),
        {"id": statement, "t": tenant, "bank": bank})
    line = str(uuid4())
    db.execute(text("""INSERT INTO domain_erp.bank_statement_lines
        (id,tenant_id,statement_id,line_number,booking_date,value_date,amount,currency,reference,status)
        VALUES (:id,:t,:s,1,'2026-09-28','2026-09-28',25,'EUR','REF-1','UNMATCHED')"""),
        {"id": line, "t": tenant, "s": statement})
    db.commit()
    app = FastAPI()
    app.include_router(bank_accounts.router)
    app.include_router(bank_reconciliation.router)
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app, headers={"X-Tenant-ID": tenant}, raise_server_exceptions=False) as client:
        yield db, client, tenant, other, bank, gl, contra, statement, line
    db.rollback()
    # Only this case's rows; foreign/shared schemas and database revisions untouched.
    for table in ("journal_entry_lines", "journal_entries", "bank_statement_lines", "bank_statements", "bank_accounts", "chart_of_accounts", "offene_posten"):
        db.execute(text(f"DELETE FROM domain_erp.{table} WHERE tenant_id IN (:t,:o)"), {"t": tenant, "o": other})
    db.commit()
    db.close()


def posted(case, *, amount=25, day="2026-09-28", currency="EUR", status="posted"):
    db, _, tenant, _, _, gl, contra, _, _ = case
    entry = str(uuid4())
    db.execute(text("""INSERT INTO domain_erp.journal_entries
        (id,tenant_id,entry_number,entry_date,posting_date,total_debit,total_credit,status,currency,period,source)
        VALUES (:id,:t,:id,:day,:day,:a,:a,:status,:currency,'2026-09','manual')"""),
        {"id": entry, "t": tenant, "day": day, "a": amount, "status": status, "currency": currency})
    for index, account, debit, credit in ((1, gl, amount, 0), (2, contra, 0, amount)):
        db.execute(text("""INSERT INTO domain_erp.journal_entry_lines
            (id,tenant_id,journal_entry_id,account_id,line_number,debit,credit,debit_amount,credit_amount)
            VALUES (:id,:t,:e,:acc,:n,:d,:c,:d,:c)"""),
            {"id": str(uuid4()), "t": tenant, "e": entry, "acc": account, "n": index, "d": debit, "c": credit})
    db.commit()
    return entry


def result(case, path="reconcile", *, tenant=None, bank=None, extra=None):
    _, client, own, _, account, _, _, statement, _ = case
    kwargs = {"params": {"bank_account_id": bank or account, **(extra or {})}}
    if tenant:
        kwargs["headers"] = {"X-Tenant-ID": tenant}
    method = client.post if path == "reconcile" else client.get
    return method(f"/bank-reconciliation/{statement}/{path}", **kwargs)


def test_bank_link_roundtrips_and_never_creates_guessed_ledger(case):
    db, client, tenant, _, _, gl, _, _, _ = case
    response = client.post("/bank-accounts", json={"account_number": str(uuid4()), "bank_name": "Bank", "gl_account_id": gl})
    assert response.status_code == 201, response.text
    account = response.json()["id"]
    assert response.json()["gl_account_id"] == gl
    assert client.get(f"/bank-accounts/{account}").json()["gl_account_id"] == gl
    assert client.put(f"/bank-accounts/{account}", json={"gl_account_id": None}).json()["gl_account_id"] is None
    assert db.execute(text("SELECT count(*) FROM domain_erp.chart_of_accounts WHERE tenant_id=:t"), {"t": tenant}).scalar_one() == 2


def test_retired_gl_number_not_silently_accepted(case):
    _, client, *_ = case
    response = client.post("/bank-accounts", json={"account_number": "123", "bank_name": "Bank", "gl_account_number": "1200"})
    assert response.status_code == 422


def test_draft_template_is_valid_without_pretending_to_be_a_stored_account(case):
    response = case[1].get("/bank-accounts/new")
    assert response.status_code == 200, response.text
    assert response.json()["id"] is None
    assert response.json()["account_number"] == ""
    assert response.json()["gl_account_id"] is None


def test_cross_tenant_gl_link_rejected_by_api_and_database(case):
    db, client, tenant, foreign, bank, gl, *_ = case
    response = client.put(f"/bank-accounts/{bank}", json={"gl_account_id": "foreign-gl"})
    assert response.status_code == 404
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(text("UPDATE domain_erp.bank_accounts SET tenant_id=:foreign WHERE id=:id"), {"foreign": foreign, "id": bank})
    db.rollback()
    assert client.get(f"/bank-accounts/{bank}").json()["gl_account_id"] == gl


@pytest.mark.parametrize("path", ["reconcile", "summary", "differences", "balance-comparison"])
def test_header_tenant_and_account_binding(case, path):
    assert result(case, path, bank="wrong").status_code == 404
    assert result(case, path, tenant=case[3], extra={"tenant_id": case[2]}).status_code == 404


def test_no_journals_is_unknown_not_zero(case):
    response = result(case)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["balance_comparison"]["accounting_state"] == "NO_POSTED_ENTRIES"
    assert data["balance_comparison"]["accounting_balance"] is None
    assert data["balance_comparison"]["difference"] is None
    assert data["comparison_state"] == "INCOMPLETE"


def test_proven_posted_balance_and_canonical_summary(case):
    db = case[0]
    posted(case)
    commits, reads = db.commits, db.reads
    response = result(case)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["balance_comparison"]["accounting_balance"] == "25.00"
    assert data["balance_comparison"]["difference"] == "0.00"
    assert data["balance_comparison"]["is_balanced"] is True
    assert data["comparison_state"] == "DIFFERENCES"  # OP match still open.
    assert db.reads == reads+1 and db.commits == commits
    assert result(case, "summary").json() == data


def test_csv_never_claims_bank_provided_balance(case):
    posted(case)
    case[0].execute(text("UPDATE domain_erp.bank_statements SET format='CSV' WHERE id=:id"), {"id": case[7]})
    case[0].commit()
    data = result(case).json()
    assert data["balance_comparison"]["bank_statement_balance"] is None
    assert data["balance_comparison"]["bank_balance_state"] == "CSV_SYNTHETIC"
    assert data["balance_comparison"]["is_balanced"] is False


@pytest.mark.parametrize("status", ["PARTIAL", "UNKNOWN"])
def test_unresolved_states_cannot_disappear(case, status):
    case[0].execute(text("UPDATE domain_erp.bank_statement_lines SET status=:status WHERE id=:id"), {"id": case[8], "status": status})
    case[0].commit()
    data = result(case).json()
    assert data["line_counts"]["partial" if status == "PARTIAL" else "unknown"] == 1
    assert data["total_differences"] == 1 and len(data["differences"]) == 1
    assert data["comparison_state"] == "INCOMPLETE"


@pytest.mark.parametrize("damage", ["amount_alias", "unbalanced_header", "currency", "foreign_leg", "statement_count", "statement_balance"])
def test_corrupt_evidence_is_not_success(case, damage):
    db, _, tenant, foreign, _, _, _, statement, _ = case
    entry = posted(case)
    sql = {
        "amount_alias": "UPDATE domain_erp.journal_entry_lines SET debit=debit+1 WHERE journal_entry_id=:id AND debit>0",
        "unbalanced_header": "UPDATE domain_erp.journal_entries SET total_debit=26 WHERE id=:id",
        "currency": "UPDATE domain_erp.journal_entries SET currency='USD' WHERE id=:id",
        "foreign_leg": "UPDATE domain_erp.journal_entry_lines SET tenant_id=:foreign WHERE journal_entry_id=:id AND debit>0",
        "statement_count": "UPDATE domain_erp.bank_statements SET total_lines=2 WHERE id=:s",
        "statement_balance": "UPDATE domain_erp.bank_statements SET closing_balance=26 WHERE id=:s",
    }[damage]
    db.execute(text(sql), {"id": entry, "s": statement, "foreign": foreign})
    db.commit()
    assert result(case).status_code == 409


@pytest.mark.parametrize("path", ["reconcile", "summary", "differences", "balance-comparison"])
def test_read_failure_visible_without_sql_leak(case, path):
    case[0].failure = True
    response = result(case, path)
    assert response.status_code == 500
    assert "SELECT" not in response.text and "division" not in response.text
    case[0].failure = False
    case[0].rollback()


def test_future_and_draft_entries_do_not_enter_cutoff(case):
    posted(case)
    posted(case, amount=100, day="2026-09-29")
    posted(case, amount=100, status="draft")
    response = result(case)
    assert response.status_code == 200, response.text
    assert response.json()["balance_comparison"]["accounting_balance"] == "25.00"


def test_missing_link_requires_mapping(case):
    case[0].execute(text("UPDATE domain_erp.bank_accounts SET gl_account_id=NULL WHERE id=:id"), {"id": case[4]})
    case[0].commit()
    data = result(case).json()
    assert data["balance_comparison"]["accounting_state"] == "MAPPING_REQUIRED"
    assert data["balance_comparison"]["accounting_balance"] is None


def test_database_cannot_bind_a_ledger_without_a_tenant(case):
    with pytest.raises(IntegrityError), case[0].begin_nested():
        case[0].execute(text("UPDATE domain_erp.bank_accounts SET tenant_id=NULL WHERE id=:id"), {"id": case[4]})
    case[0].rollback()


def test_ledger_options_are_own_bookable_accounts(case):
    response = case[1].get("/bank-accounts/ledger-options", params={"tenant_id": case[3]})
    assert response.status_code == 200
    assert [account["id"] for account in response.json()] == [case[5]]
    denied = case[1].put(f"/bank-accounts/{case[4]}", json={"gl_account_id": case[6]})
    assert denied.status_code == 409


def test_balance_discrepancy_has_a_typed_difference(case):
    posted(case, amount=20)
    data = result(case).json()
    assert data["balance_comparison"]["difference"] == "5.00"
    assert data["total_differences"] == 2
    assert data["differences"][-1]["item_type"] == "BALANCE_MISMATCH"


def test_matched_without_op_proof_is_corrupt(case):
    posted(case)
    case[0].execute(text("UPDATE domain_erp.bank_statement_lines SET status='MATCHED' WHERE id=:id"), {"id": case[8]})
    case[0].commit()
    assert result(case).status_code == 409


def test_balances_equal_requires_persisted_matching_proof(case):
    posted(case)
    db, _, tenant, _, _, _, _, _, line = case
    op = str(uuid4())
    db.execute(text("""INSERT INTO domain_erp.offene_posten
        (id,tenant_id,rechnungsnr,konto_typ,offen,waehrung) VALUES (:id,:t,'REF-1','debitoren',0,'EUR')"""),
        {"id": op, "t": tenant})
    db.execute(text("UPDATE domain_erp.bank_statement_lines SET status='MATCHED',matched_op_id=:op WHERE id=:id"),
               {"id": line, "op": op})
    db.commit()
    data = result(case).json()
    assert data["comparison_state"] == "BALANCES_EQUAL"
    assert data["can_be_booked"] is False


def test_unresolved_page_is_bounded_and_count_is_total(case):
    db, _, tenant, _, _, _, _, statement, _ = case
    for number in range(2, 142):
        db.execute(text("""INSERT INTO domain_erp.bank_statement_lines
            (id,tenant_id,statement_id,line_number,booking_date,value_date,amount,currency,status)
            VALUES (:id,:t,:s,:n,'2026-09-28','2026-09-28',1,'EUR','UNMATCHED')"""),
            {"id": str(uuid4()), "t": tenant, "s": statement, "n": number})
    db.execute(text("UPDATE domain_erp.bank_statements SET total_lines=141,imported_lines=141,closing_balance=165 WHERE id=:id"), {"id": statement})
    db.commit()
    data = result(case).json()
    assert data["total_differences"] == 141 and len(data["differences"]) == 100
    response = result(case, "differences", extra={"offset": 100, "limit": 100})
    assert len(response.json()) == 41
    assert not set(item["statement_line_id"] for item in data["differences"]) & set(item["statement_line_id"] for item in response.json())
    assert result(case, "differences", extra={"limit": 101}).status_code == 422
