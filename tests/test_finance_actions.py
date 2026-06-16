from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import finance_actions
from app.core.database import get_db
from app.core.tenant import get_tenant_id


class _FakeResult:
    def __init__(self, *, fetchone=None, fetchall=None, first=None, rowcount: int = 0):
        self._fetchone = fetchone
        self._fetchall = list(fetchall or [])
        self._first = first
        self.rowcount = rowcount

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return list(self._fetchall)

    def first(self):
        return self._first

    def mappings(self):
        return self

    def all(self):
        return list(self._fetchall)


class FakeDb:
    def __init__(self):
        self.commit_count = 0
        self.entry_lookup = {"BEL-1": "je-1"}
        self.entry_periods = {"je-1": "2026-04", "je-locked": "2026-03"}
        self.period_status = {"2026-04": "OPEN", "2026-03": "CLOSED"}
        self.post_entry_success = True
        self.cash_row = SimpleNamespace(cnt=3, total_debit=120.0, total_credit=120.0)
        self.direct_debit_ids = [("dd-1",), ("dd-2",)]
        self.credit_limits = [
            {
                "id": "bp-1",
                "partner_name": "Musterkunde",
                "credit_limit": 15000.0,
                "used_credit": 2500.0,
                "currency": "EUR",
            }
        ]
        self.collaterals = [
            {
                "id": "col-1",
                "label": "Getreidesicherheit",
                "tenant_id": "tenant-a",
                "created_at": "2026-04-13T10:00:00+00:00",
            }
        ]
        self.payment_suggestions = [
            {
                "id": "op-1",
                "lieferant": "Mueller Handel",
                "rechnungs_nr": "RE-1",
                "faellig_am": "2026-04-20",
                "betrag": 800.0,
                "waehrung": "EUR",
            }
        ]
        self.buchungsuebergabe_rows = [
            (
                date(2026, 4, 1),
                "JE-1",
                1,
                "8400",
                50.0,
                0.0,
                "Warenverkauf",
                "SV",
                "U19",
                "CC-1",
            ),
            (
                date(2026, 4, 1),
                "JE-1",
                2,
                "1000",
                0.0,
                50.0,
                "Kasse",
                "SV",
                "",
                "",
            ),
        ]
        self.closed_period_updates: list[str] = []
        self.inserted_cash_close = None

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "FROM domain_erp.journal_entries WHERE tenant_id = :tenant_id AND entry_number = :entry_number" in sql:
            entry_id = self.entry_lookup.get(params["entry_number"])
            return _FakeResult(fetchone=(entry_id,) if entry_id else None)

        if "SELECT TO_CHAR(entry_date::date, 'YYYY-MM') AS period FROM domain_erp.journal_entries" in sql:
            period = self.entry_periods.get(params["id"])
            return _FakeResult(fetchone=(period,) if period else None)

        if "FROM finance_accounting_periods WHERE tenant_id = :tenant_id AND period = :period" in sql:
            status = self.period_status.get(params["period"])
            return _FakeResult(fetchone=(status,) if status else None)

        if "FROM domain_erp.journal_entries je WHERE je.tenant_id = :tid AND je.entry_date = :today" in sql:
            return _FakeResult(fetchone=self.cash_row)

        if "INSERT INTO domain_erp.journal_entries" in sql and "source, status, total_debit, total_credit" in sql:
            self.inserted_cash_close = params
            return _FakeResult()

        if "INSERT INTO domain_shared.direct_debit_items" in sql:
            return _FakeResult(fetchall=self.direct_debit_ids)

        if "FROM domain_erp.journal_entries je JOIN domain_erp.journal_entry_lines jl" in sql:
            if params["period"] == "2026-04":
                return _FakeResult(first=(2, 150.0, 150.0))
            raise RuntimeError("period calc failed")

        if "UPDATE domain_erp.accounting_periods SET status = 'closed', closed_at = NOW()" in sql:
            self.closed_period_updates.append(params["period"])
            return _FakeResult()

        if "FROM domain_erp.business_partners WHERE tenant_id=:tid AND credit_limit IS NOT NULL" in sql:
            return _FakeResult(fetchall=self.credit_limits)

        if "SELECT * FROM domain_erp.collaterals WHERE tenant_id=:tid ORDER BY created_at DESC" in sql:
            return _FakeResult(fetchall=self.collaterals)

        if "FROM domain_erp.open_items WHERE tenant_id=:tid AND typ='kreditor' AND offen > 0" in sql:
            return _FakeResult(fetchall=self.payment_suggestions)

        if "FROM domain_erp.journal_entries je JOIN domain_erp.journal_entry_lines jel" in sql:
            return _FakeResult(fetchall=self.buchungsuebergabe_rows)

        raise AssertionError(f"Unhandled SQL in finance_actions test double: {sql}")

    def commit(self):
        self.commit_count += 1


class FakeEntryRepo:
    def __init__(self, success: bool):
        self.success = success
        self.calls: list[tuple[str, str]] = []

    async def post_entry(self, entry_id: str, tenant_id: str) -> bool:
        self.calls.append((entry_id, tenant_id))
        return self.success


class FakeContainer:
    def __init__(self, repo: FakeEntryRepo):
        self.repo = repo

    def resolve(self, _cls):
        return self.repo


def _build_client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(finance_actions.router, prefix="/finance")
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_bank_reconciliation_requires_statement_id():
    db = FakeDb()
    client = _build_client(db)

    response = client.post("/finance/bank-reconciliation/run", json={"bank_account_id": "bank-1"})

    assert response.status_code == 200
    assert response.json()["success"] is False


def test_bank_reconciliation_success_and_failure(monkeypatch):
    db = FakeDb()
    client = _build_client(db)

    async def _ok(**kwargs):
        return SimpleNamespace(matched_count=4)

    async def _fail(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.api.v1.endpoints.bank_reconciliation.reconcile_bank_statement", _ok)
    response = client.post(
        "/finance/bank-reconciliation/run",
        json={"bank_account_id": "bank-1", "statement_id": "stmt-1"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "4 Zuordnung" in response.json()["message"]

    monkeypatch.setattr("app.api.v1.endpoints.bank_reconciliation.reconcile_bank_statement", _fail)
    failed = client.post(
        "/finance/bank-reconciliation/run",
        json={"bank_account_id": "bank-1", "statement_id": "stmt-1"},
    )
    assert failed.status_code == 200
    assert failed.json()["success"] is False


def test_post_journal_entry_handles_lookup_period_lock_success_and_repo_failure(monkeypatch):
    db = FakeDb()
    repo = FakeEntryRepo(success=True)
    monkeypatch.setattr(finance_actions, "container", FakeContainer(repo))
    client = _build_client(db)

    missing = client.post("/finance/journal-entries/post", json={})
    assert missing.status_code == 200
    assert missing.json()["success"] is False

    not_found = client.post("/finance/journal-entries/post", json={"journal_entry_id": "missing"})
    assert not_found.status_code == 200
    assert not_found.json()["message"] == "Buchung nicht gefunden."

    locked = client.post("/finance/journal-entries/post", json={"journal_entry_id": "je-locked"})
    assert locked.status_code == 200
    assert locked.json()["success"] is False
    assert "gesperrt" in locked.json()["message"]

    via_number = client.post("/finance/journal-entries/post", json={"belegnummer": "BEL-1"})
    assert via_number.status_code == 200
    assert via_number.json()["success"] is True
    assert repo.calls[-1] == ("je-1", "tenant-a")

    repo_fail = FakeEntryRepo(success=False)
    monkeypatch.setattr(finance_actions, "container", FakeContainer(repo_fail))
    failed = client.post("/finance/journal-entries/post", json={"journal_entry_id": "je-1"})
    assert failed.status_code == 200
    assert failed.json()["success"] is False


def test_cash_close_day_and_direct_debit_cover_success_and_empty_run():
    db = FakeDb()
    client = _build_client(db)

    close_day = client.post("/finance/cash/close-day")
    assert close_day.status_code == 200
    assert close_day.json()["success"] is True
    assert db.inserted_cash_close is not None
    assert db.commit_count >= 1

    direct_debit = client.post("/finance/direct-debit/run")
    assert direct_debit.status_code == 200
    assert "2 Lastschrift" in direct_debit.json()["message"]

    db.direct_debit_ids = []
    empty = client.post("/finance/direct-debit/run")
    assert empty.status_code == 200
    assert "Keine faelligen Posten" in empty.json()["message"]


def test_closing_calculate_lock_run_and_approve_paths(monkeypatch):
    db = FakeDb()
    client = _build_client(db)

    calculated = client.post("/finance/closing/calculate", json={"period": "2026-04", "closing_type": "month"})
    assert calculated.status_code == 200
    assert calculated.json()["balance"] == 0.0
    assert calculated.json()["entry_count"] == 2

    fallback = client.post("/finance/closing/calculate", json={"period": "broken", "closing_type": "month"})
    assert fallback.status_code == 200
    assert fallback.json()["entry_count"] == 0

    locked = client.post("/finance/closing/lock", json={"period": "2026-04", "closing_type": "month"})
    assert locked.status_code == 200
    assert locked.json()["success"] is True

    run = client.post("/finance/closing/run", json={"period": "2026-04", "closing_type": "month"})
    assert run.status_code == 200
    assert run.json()["success"] is True
    assert "2026-04" in db.closed_period_updates

    monkeypatch.setattr(finance_actions.endpoint_gateways, "get_closing_workspace_gateway", lambda: None)
    pending = client.post(
        "/finance/closing/approve",
        json={"period": "2026-04", "closing_type": "month", "actor": "controller"},
    )
    assert pending.status_code == 200
    assert pending.json()["approval_status"] == "pending"

    class FakeGateway:
        async def approve(self, request, _db):
            return {
                "status": "approved",
                "approval_status": "approved",
                "period": request.period,
                "actor": request.actor,
            }

    monkeypatch.setattr(finance_actions.endpoint_gateways, "get_closing_workspace_gateway", lambda: FakeGateway())
    approved = client.post(
        "/finance/closing/approve",
        json={"period": "2026-04", "closing_type": "month", "actor": "controller"},
    )
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"


def test_credit_collateral_payment_suggestions_and_close_readiness():
    db = FakeDb()
    client = _build_client(db)

    credit_limits = client.get("/finance/credit-limits")
    assert credit_limits.status_code == 200
    assert credit_limits.json()[0]["partner_name"] == "Musterkunde"

    collaterals = client.get("/finance/collaterals")
    assert collaterals.status_code == 200
    assert collaterals.json()[0]["label"] == "Getreidesicherheit"

    suggestions = client.get("/finance/payment-suggestions?days_ahead=14")
    assert suggestions.status_code == 200
    assert suggestions.json()[0]["lieferant"] == "Mueller Handel"

    readiness = client.get("/finance/close-readiness")
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "IN_PROGRESS"
    assert readiness.json()["blocking_items"]


def test_buchungsuebergabe_export_supports_download_and_summary(monkeypatch):
    db = FakeDb()
    client = _build_client(db)
    artifacts: list[dict] = []

    monkeypatch.setattr(
        finance_actions,
        "register_artifact",
        lambda db_arg, tenant_id, header_id, artifact_type, content_hash, storage_key, **kwargs: artifacts.append(
            {
                "tenant_id": tenant_id,
                "header_id": header_id,
                "artifact_type": artifact_type,
                "storage_key": storage_key,
                "file_name": kwargs.get("file_name"),
            }
        ),
    )

    download = client.post(
        "/finance/buchungsuebergabe-export",
        json={
            "von": "2026-04-01",
            "bis": "2026-04-30",
            "download": True,
            "bediener": "jw",
        },
    )
    assert download.status_code == 200
    assert "attachment;" in download.headers["content-disposition"]
    assert "Warenverkauf" in download.text

    summary = client.post(
        "/finance/buchungsuebergabe-export",
        json={
            "von": "2026-04-01",
            "bis": "2026-04-30",
            "download": False,
            "sortierung": "rechnungsnr",
        },
    )
    assert summary.status_code == 200
    body = summary.json()
    assert body["anzahl_buchungen"] == 2
    assert body["summe_soll"] == 50.0
    assert body["summe_haben"] == 50.0
    assert artifacts
