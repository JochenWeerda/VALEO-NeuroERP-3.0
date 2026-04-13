from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import dunning
from app.core.database import get_db


class _FakeResult:
    def __init__(self, *, fetchone=None, fetchall=None):
        self._fetchone = fetchone
        self._fetchall = list(fetchall or [])

    def fetchone(self):
        return self._fetchone

    def fetchall(self):
        return list(self._fetchall)


class FakeDb:
    def __init__(self):
        now = datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc)
        self.commit_count = 0
        self.rollback_count = 0
        self.rules = {
            "rule-1": {
                "id": "rule-1",
                "tenant_id": "system",
                "level": 1,
                "days_overdue_min": 14,
                "days_overdue_max": 29,
                "fee_amount": Decimal("5.00"),
                "fee_percentage": Decimal("0.00"),
                "interest_rate": Decimal("9.00"),
                "payment_deadline_days": 14,
                "block_customer": False,
                "escalate_to_collection": False,
                "description_template": "Mahnung Stufe 1",
                "active": True,
                "created_at": now,
                "updated_at": now,
            }
        }
        self.notices = {}

    def _rule_tuple(self, rule):
        return (
            rule["id"],
            rule["level"],
            rule["days_overdue_min"],
            rule["days_overdue_max"],
            rule["fee_amount"],
            rule["fee_percentage"],
            rule["interest_rate"],
            rule["payment_deadline_days"],
            rule["block_customer"],
            rule["escalate_to_collection"],
            rule["description_template"],
            rule["active"],
            rule["created_at"],
            rule["updated_at"],
        )

    def _notice_tuple(self, notice):
        return (
            notice["id"],
            notice["op_id"],
            notice["debtor_id"],
            notice["dunning_level"],
            notice["dunning_date"],
            notice["due_date"],
            notice["open_amount"],
            notice["dunning_fee"],
            notice["interest"],
            notice["total_amount"],
            notice["payment_deadline"],
            notice["status"],
            notice["sent_date"],
            notice["payment_date"],
            notice["notes"],
            notice["created_at"],
            notice["updated_at"],
        )

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "FROM domain_erp.dunning_rules WHERE tenant_id = :tenant_id" in sql and "ORDER BY level" in sql:
            rows = [rule for rule in self.rules.values() if rule["tenant_id"] == params["tenant_id"]]
            if "AND active = true" in sql:
                rows = [rule for rule in rows if rule["active"]]
            rows.sort(key=lambda rule: rule["level"])
            return _FakeResult(fetchall=[self._rule_tuple(rule) for rule in rows])

        if "SELECT id FROM domain_erp.dunning_rules" in sql:
            existing = next(
                (
                    rule
                    for rule in self.rules.values()
                    if rule["tenant_id"] == params["tenant_id"]
                    and rule["level"] == params["level"]
                    and rule["active"]
                ),
                None,
            )
            return _FakeResult(fetchone=((existing["id"],) if existing else None))

        if "INSERT INTO domain_erp.dunning_rules" in sql:
            rule = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "level": params["level"],
                "days_overdue_min": params["days_overdue_min"],
                "days_overdue_max": params["days_overdue_max"],
                "fee_amount": params["fee_amount"],
                "fee_percentage": params["fee_percentage"],
                "interest_rate": params["interest_rate"],
                "payment_deadline_days": params["payment_deadline_days"],
                "block_customer": params["block_customer"],
                "escalate_to_collection": params["escalate_to_collection"],
                "description_template": params["description_template"],
                "active": params["active"],
                "created_at": self.rules["rule-1"]["created_at"],
                "updated_at": self.rules["rule-1"]["updated_at"],
            }
            self.rules[rule["id"]] = rule
            return _FakeResult(fetchone=self._rule_tuple(rule))

        if "SELECT fee_amount, fee_percentage, interest_rate, payment_deadline_days, description_template FROM domain_erp.dunning_rules" in sql:
            rule = next(
                (
                    rule
                    for rule in self.rules.values()
                    if rule["tenant_id"] == params["tenant_id"]
                    and rule["level"] == params["level"]
                    and rule["active"]
                ),
                None,
            )
            if not rule:
                return _FakeResult(fetchone=None)
            return _FakeResult(
                fetchone=(
                    rule["fee_amount"],
                    rule["fee_percentage"],
                    rule["interest_rate"],
                    rule["payment_deadline_days"],
                    rule["description_template"],
                )
            )

        if "INSERT INTO domain_erp.dunning_notices" in sql:
            notice = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "op_id": params["op_id"],
                "debtor_id": params["debtor_id"],
                "dunning_level": params["dunning_level"],
                "dunning_date": params["dunning_date"],
                "due_date": params["due_date"],
                "open_amount": params["open_amount"],
                "dunning_fee": params["dunning_fee"],
                "interest": params["interest"],
                "total_amount": params["total_amount"],
                "payment_deadline": params["payment_deadline"],
                "status": params["status"],
                "sent_date": None,
                "payment_date": None,
                "notes": params["notes"],
                "created_at": self.rules["rule-1"]["created_at"],
                "updated_at": self.rules["rule-1"]["updated_at"],
            }
            self.notices[notice["id"]] = notice
            return _FakeResult(fetchone=self._notice_tuple(notice))

        if "UPDATE domain_erp.offene_posten SET dunning_level = :dunning_level" in sql:
            return _FakeResult()

        if "FROM domain_erp.dunning_notices WHERE tenant_id = :tenant_id" in sql and "ORDER BY dunning_date DESC" in sql:
            rows = [notice for notice in self.notices.values() if notice["tenant_id"] == params["tenant_id"]]
            return _FakeResult(fetchall=[self._notice_tuple(notice) for notice in rows])

        if "UPDATE domain_erp.dunning_notices SET status = 'sent'" in sql:
            notice = self.notices.get(params["dunning_id"])
            if not notice or notice["tenant_id"] != params["tenant_id"]:
                return _FakeResult(fetchone=None)
            notice["status"] = "sent"
            notice["sent_date"] = date(2026, 4, 13)
            return _FakeResult(fetchone=self._notice_tuple(notice))

        if "UPDATE domain_erp.dunning_notices SET status = 'paid'" in sql:
            notice = self.notices.get(params["dunning_id"])
            if not notice or notice["tenant_id"] != params["tenant_id"]:
                return _FakeResult(fetchone=None)
            notice["status"] = "paid"
            notice["payment_date"] = date(2026, 4, 14)
            return _FakeResult(fetchone=self._notice_tuple(notice))

        if "FROM domain_erp.offene_posten WHERE tenant_id = :tenant_id" in sql:
            return _FakeResult(fetchall=[])

        raise AssertionError(f"Unhandled SQL in dunning test double: {sql}")

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1


def _build_client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(dunning.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_list_and_create_dunning_rule():
    db = FakeDb()
    client = _build_client(db)

    listed = client.get("/finance/dunning/rules")
    assert listed.status_code == 200
    assert listed.json()[0]["level"] == 1

    created = client.post(
        "/finance/dunning/rules",
        json={
            "level": 2,
            "days_overdue_min": 30,
            "days_overdue_max": 59,
            "fee_amount": "10.00",
            "fee_percentage": "0.00",
            "interest_rate": "9.00",
            "payment_deadline_days": 10,
            "block_customer": True,
            "escalate_to_collection": False,
            "description_template": "Mahnung Stufe 2",
            "active": True,
        },
    )
    assert created.status_code == 201
    assert db.commit_count == 1

    duplicate = client.post(
        "/finance/dunning/rules",
        json={
            "level": 1,
            "days_overdue_min": 14,
            "days_overdue_max": 29,
            "fee_amount": "5.00",
            "fee_percentage": "0.00",
            "interest_rate": "9.00",
            "payment_deadline_days": 14,
            "block_customer": False,
            "escalate_to_collection": False,
            "description_template": "Mahnung Stufe 1",
            "active": True,
        },
    )
    assert duplicate.status_code == 400


def test_create_list_and_transition_dunning_notice(monkeypatch):
    db = FakeDb()
    client = _build_client(db)
    monkeypatch.setattr(dunning, "register_artifact", lambda *args, **kwargs: None)

    created = client.post(
        "/finance/dunning",
        json={
            "op_id": "OP-1",
            "debtor_id": "DEB-1",
            "dunning_level": 1,
            "dunning_date": "2026-04-13",
            "due_date": "2026-04-01",
            "open_amount": "1250.00",
        },
    )
    assert created.status_code == 201
    created_id = created.json()["id"]
    assert Decimal(created.json()["total_amount"]) == Decimal("1258.70")

    listed = client.get("/finance/dunning")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    sent = client.put(f"/finance/dunning/{created_id}/send")
    assert sent.status_code == 200
    assert sent.json()["status"] == "sent"

    paid = client.put(f"/finance/dunning/{created_id}/paid")
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"


def test_nonexistent_notice_actions_and_run_paths():
    client = _build_client(FakeDb())

    missing_send = client.put("/finance/dunning/missing/send")
    assert missing_send.status_code == 404

    missing_paid = client.put("/finance/dunning/missing/paid")
    assert missing_paid.status_code == 404

    run = client.post("/finance/dunning/run", json={"as_of_date": "2026-04-13", "tenant_id": "system"})
    assert run.status_code == 200
    assert run.json()["notices_created"] == 0

    processed = client.post("/finance/dunning/process", json={"tenant_id": "system", "auto_apply_rules": True})
    assert processed.status_code == 200
    assert processed.json() == []
