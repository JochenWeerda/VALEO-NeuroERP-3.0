from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import payment_runs
from app.core.database import get_db


class _FakeResult:
    def __init__(self, *, fetchone=None, fetchall=None, rowcount: int = 0):
        self._fetchone = fetchone
        self._fetchall = list(fetchall or [])
        self.rowcount = rowcount

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return list(self._fetchall)


class FakeDb:
    def __init__(self):
        now = datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc)
        self.commit_count = 0
        self.rollback_count = 0
        self.runs = {
            "run-1": {
                "id": "run-1",
                "tenant_id": "system",
                "run_number": "ZL-0001",
                "execution_date": date(2026, 4, 20),
                "initiator_name": "VALEO Test GmbH",
                "initiator_iban": "DE89370400440532013000",
                "initiator_bic": "COBADEFFXXX",
                "total_amount": Decimal("500.00"),
                "payment_count": 1,
                "status": "approved",
                "approved_at": now,
                "approved_by": "controller",
                "executed_at": None,
                "sepa_file_id": None,
                "notes": None,
                "created_at": now,
                "updated_at": now,
            }
        }
        self.items = {
            "run-1": [
                {
                    "id": "pay-1",
                    "tenant_id": "system",
                    "payment_run_id": "run-1",
                    "creditor_id": "KRED-001",
                    "creditor_name": "Lieferant A",
                    "iban": "DE27100777770209299700",
                    "bic": "DEUTDEFF",
                    "amount": Decimal("500.00"),
                    "purpose": "RE-1",
                    "op_id": "OP-1",
                    "invoice_number": "RE-1",
                    "discount_used": False,
                    "discount_amount": Decimal("0.00"),
                    "end_to_end_id": "E2E-1",
                    "status": "pending",
                }
            ]
        }
        self.returns = []

    def _run_tuple(self, run):
        return (
            run["id"],
            run["run_number"],
            run["execution_date"],
            run["initiator_name"],
            run["initiator_iban"],
            run["initiator_bic"],
            run["total_amount"],
            run["payment_count"],
            run["status"],
            run["approved_at"],
            run["approved_by"],
            run["executed_at"],
            run["sepa_file_id"],
            run["notes"],
            run["created_at"],
            run["updated_at"],
        )

    def _item_tuple(self, item):
        return (
            item["creditor_id"],
            item["creditor_name"],
            item["iban"],
            item["bic"],
            item["amount"],
            item["purpose"],
            item["op_id"],
            item["invoice_number"],
            item["discount_used"],
            item["discount_amount"],
            item["end_to_end_id"],
            item["status"],
        )

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "FROM domain_erp.offene_posten WHERE tenant_id = :tenant_id AND konto_typ = 'kreditoren' AND offen > 0" in sql:
            return _FakeResult(fetchall=[("op-1", "KRED-001", "Lieferant A", Decimal("500.00"), "RE-1", "EUR")])

        if "INSERT INTO domain_erp.payment_runs" in sql:
            run = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "run_number": params["run_number"],
                "execution_date": params["execution_date"],
                "initiator_name": params["initiator_name"],
                "initiator_iban": params["initiator_iban"],
                "initiator_bic": params["initiator_bic"],
                "total_amount": params["total_amount"],
                "payment_count": params["payment_count"],
                "status": params["status"],
                "approved_at": None,
                "approved_by": None,
                "executed_at": None,
                "sepa_file_id": None,
                "notes": params["notes"],
                "created_at": self.runs["run-1"]["created_at"],
                "updated_at": self.runs["run-1"]["updated_at"],
            }
            self.runs[run["id"]] = run
            self.items[run["id"]] = []
            return _FakeResult(fetchone=self._run_tuple(run))

        if "INSERT INTO domain_erp.payment_run_items" in sql:
            item = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "payment_run_id": params["payment_run_id"],
                "creditor_id": params["creditor_id"],
                "creditor_name": params["creditor_name"],
                "iban": params["iban"],
                "bic": params["bic"],
                "amount": params["amount"],
                "purpose": params["purpose"],
                "op_id": params["op_id"],
                "invoice_number": params["invoice_number"],
                "discount_used": params["discount_used"],
                "discount_amount": params["discount_amount"],
                "end_to_end_id": params["end_to_end_id"],
                "status": "pending",
            }
            self.items[item["payment_run_id"]].append(item)
            return _FakeResult()

        if "FROM domain_erp.payment_runs WHERE tenant_id = :tenant_id" in sql and "ORDER BY created_at DESC" in sql:
            rows = [run for run in self.runs.values() if run["tenant_id"] == params["tenant_id"]]
            if "AND status = :status" in sql:
                rows = [run for run in rows if run["status"] == params["status"]]
            return _FakeResult(fetchall=[self._run_tuple(run) for run in rows])

        if "FROM domain_erp.payment_runs WHERE id = :run_id AND tenant_id = :tenant_id" in sql:
            run = self.runs.get(params["run_id"])
            if run and run["tenant_id"] == params["tenant_id"]:
                return _FakeResult(fetchone=self._run_tuple(run))
            return _FakeResult(fetchone=None)

        if "FROM domain_erp.payment_run_items WHERE payment_run_id = :payment_run_id" in sql:
            rows = self.items.get(params["payment_run_id"], [])
            return _FakeResult(fetchall=[self._item_tuple(item) for item in rows])

        if "UPDATE domain_erp.payment_runs SET status = 'approved'" in sql:
            run = self.runs.get(params["run_id"])
            if not run or run["tenant_id"] != params["tenant_id"] or run["status"] != "draft":
                return _FakeResult(fetchone=None)
            run["status"] = "approved"
            run["approved_by"] = params["approved_by"]
            run["approved_at"] = self.runs["run-1"]["created_at"]
            return _FakeResult(fetchone=(run["id"],))

        if "UPDATE domain_erp.payment_runs SET status = 'executed'" in sql:
            run = self.runs.get(params["run_id"])
            run["status"] = "executed"
            run["sepa_file_id"] = params["sepa_file_id"]
            run["executed_at"] = self.runs["run-1"]["created_at"]
            return _FakeResult()

        if "UPDATE domain_erp.payment_run_items SET status = 'executed'" in sql:
            for item in self.items.get(params["payment_run_id"], []):
                item["status"] = "executed"
            return _FakeResult()

        if "UPDATE domain_erp.offene_posten SET offen = offen - :amount" in sql:
            return _FakeResult()

        if "UPDATE domain_erp.offene_posten SET offen = 0" in sql:
            return _FakeResult()

        if "SELECT id, payment_run_id, op_id, amount, creditor_id FROM domain_erp.payment_run_items" in sql:
            for run_items in self.items.values():
                for item in run_items:
                    if item["id"] == params["payment_id"] and item["tenant_id"] == params["tenant_id"]:
                        return _FakeResult(
                            fetchone=(item["id"], item["payment_run_id"], item["op_id"], item["amount"], item["creditor_id"])
                        )
            return _FakeResult(fetchone=None)

        if "UPDATE domain_erp.payment_run_items SET status = 'returned'" in sql:
            return _FakeResult()

        if "UPDATE domain_erp.offene_posten SET offen = offen + :amount" in sql:
            self.returns.append(params["amount"])
            return _FakeResult()

        if "INSERT INTO domain_erp.payment_returns" in sql:
            self.returns.append(params["id"])
            return _FakeResult()

        raise AssertionError(f"Unhandled SQL in payment_runs test double: {sql}")

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1


def _build_client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(payment_runs.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_list_and_plan_payment_runs():
    client = _build_client(FakeDb())

    listed = client.get("/finance/payment-runs")
    assert listed.status_code == 200
    assert listed.json()[0]["run_number"] == "ZL-0001"

    planned = client.post("/finance/payment-runs/plan", json={"execution_date": "2026-04-20", "tenant_id": "system"})
    assert planned.status_code == 200
    assert planned.json()["suggested_payments"][0]["creditor_name"] == "Lieferant A"


def test_create_and_fetch_payment_run():
    db = FakeDb()
    client = _build_client(db)

    created = client.post(
        "/finance/payment-runs",
        json={
            "run_number": "ZL-NEW-1",
            "execution_date": "2026-04-21",
            "initiator_name": "VALEO Test GmbH",
            "initiator_iban": "DE89370400440532013000",
            "initiator_bic": "COBADEFFXXX",
            "payments": [
                {
                    "creditor_id": "KRED-002",
                    "creditor_name": "Lieferant B",
                    "iban": "DE27100777770209299700",
                    "amount": "150.00",
                    "purpose": "RE-2",
                    "discount_used": False,
                    "discount_amount": "0.00",
                }
            ],
        },
    )
    assert created.status_code == 201
    created_id = created.json()["id"]
    assert db.commit_count == 1

    fetched = client.get(f"/finance/payment-runs/{created_id}")
    assert fetched.status_code == 200
    assert fetched.json()["payment_count"] == 1


def test_nonexistent_paths_return_404():
    client = _build_client(FakeDb())

    missing = client.get("/finance/payment-runs/missing")
    assert missing.status_code == 404

    approve = client.post("/finance/payment-runs/missing/approve", json={"approved_by": "tester"})
    assert approve.status_code == 404

    execute = client.post("/finance/payment-runs/missing/execute", json={"executed_by": "tester"})
    assert execute.status_code == 404

    sepa = client.get("/finance/payment-runs/missing/sepa-xml")
    assert sepa.status_code == 404


def test_execute_and_return_payment_cover_operator_paths(monkeypatch):
    db = FakeDb()
    client = _build_client(db)

    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(payment_runs, "_store_payment_run_event_in_outbox", _noop)

    executed = client.post("/finance/payment-runs/run-1/execute", json={"executed_by": "treasury"})
    assert executed.status_code == 200
    assert executed.json()["status"] == "executed"

    sepa = client.get("/finance/payment-runs/run-1/sepa-xml")
    assert sepa.status_code == 200
    assert "pain.001.001.03" in sepa.text

    returned = client.post(
        "/finance/payment-runs/run-1/return-payment",
        json={
            "payment_id": "pay-1",
            "return_reason": "ACCOUNT_CLOSED",
            "return_date": "2026-04-22",
        },
    )
    assert returned.status_code == 200
    assert returned.json()["status"] == "ok"
    assert Decimal("500.00") in db.returns
