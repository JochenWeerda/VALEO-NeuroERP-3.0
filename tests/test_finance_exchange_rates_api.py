from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import exchange_rates
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
        self.rows = {
            "rate-1": {
                "id": "rate-1",
                "tenant_id": "system",
                "from_currency": "USD",
                "to_currency": "EUR",
                "rate": Decimal("0.92000000"),
                "rate_date": date(2026, 4, 13),
                "rate_type": "SPOT",
                "source": "ECB",
                "active": True,
                "created_at": now,
                "updated_at": now,
            }
        }

    def _tuple(self, row):
        return (
            row["id"],
            row["from_currency"],
            row["to_currency"],
            row["rate"],
            row["rate_date"],
            row["rate_type"],
            row["source"],
            row["active"],
            row["created_at"],
            row["updated_at"],
        )

    def execute(self, statement, params=None):
        sql = " ".join(str(statement).split())
        params = params or {}

        if "FROM domain_erp.exchange_rates WHERE tenant_id = :tenant_id" in sql and "ORDER BY rate_date DESC" in sql:
            rows = [row for row in self.rows.values() if row["tenant_id"] == params["tenant_id"]]
            if "from_currency = :from_currency" in sql:
                rows = [row for row in rows if row["from_currency"] == params["from_currency"]]
            if "to_currency = :to_currency" in sql:
                rows = [row for row in rows if row["to_currency"] == params["to_currency"]]
            if "rate_date = :rate_date" in sql:
                rows = [row for row in rows if row["rate_date"] == params["rate_date"]]
            if "active = true" in sql:
                rows = [row for row in rows if row["active"]]
            rows.sort(key=lambda row: (row["rate_date"], row["from_currency"], row["to_currency"]), reverse=True)
            return _FakeResult(fetchall=[self._tuple(row) for row in rows])

        if "SELECT id FROM domain_erp.exchange_rates" in sql:
            existing = next(
                (
                    row
                    for row in self.rows.values()
                    if row["tenant_id"] == params["tenant_id"]
                    and row["from_currency"] == params["from_currency"]
                    and row["to_currency"] == params["to_currency"]
                    and row["rate_date"] == params["rate_date"]
                ),
                None,
            )
            return _FakeResult(fetchone=(existing["id"],) if existing else None)

        if "INSERT INTO domain_erp.exchange_rates" in sql:
            row = {
                "id": params["id"],
                "tenant_id": params["tenant_id"],
                "from_currency": params["from_currency"],
                "to_currency": params["to_currency"],
                "rate": params["rate"],
                "rate_date": params["rate_date"],
                "rate_type": params["rate_type"],
                "source": params["source"],
                "active": params["active"],
                "created_at": self.rows["rate-1"]["created_at"],
                "updated_at": self.rows["rate-1"]["updated_at"],
            }
            self.rows[row["id"]] = row
            return _FakeResult(fetchone=self._tuple(row))

        if "WHERE id = :rate_id AND tenant_id = :tenant_id" in sql and "FROM domain_erp.exchange_rates" in sql:
            row = self.rows.get(params["rate_id"])
            if row and row["tenant_id"] == params["tenant_id"]:
                return _FakeResult(fetchone=self._tuple(row))
            return _FakeResult(fetchone=None)

        if "UPDATE domain_erp.exchange_rates SET" in sql:
            row = self.rows.get(params["rate_id"])
            if not row or row["tenant_id"] != params["tenant_id"]:
                return _FakeResult(fetchone=None)
            for field in ("rate", "rate_type", "source", "active"):
                if field in params:
                    row[field] = params[field]
            return _FakeResult(fetchone=self._tuple(row))

        if "FROM domain_erp.exchange_rates" in sql and "LIMIT 1" in sql:
            if "WHERE from_currency = :to_currency" in sql:
                wanted_from = params["to_currency"]
                wanted_to = params["from_currency"]
            else:
                wanted_from = params["from_currency"]
                wanted_to = params["to_currency"]
            rows = [
                row
                for row in self.rows.values()
                if row["tenant_id"] == params["tenant_id"]
                and row["from_currency"] == wanted_from
                and row["to_currency"] == wanted_to
                and row["active"]
            ]
            if "rate_date <= :conversion_date" in sql:
                rows = [row for row in rows if row["rate_date"] <= params["conversion_date"]]
            rows.sort(key=lambda row: row["rate_date"], reverse=True)
            if "SELECT rate, rate_date, rate_type" in sql:
                return _FakeResult(
                    fetchone=((rows[0]["rate"], rows[0]["rate_date"], rows[0]["rate_type"]) if rows else None)
                )
            return _FakeResult(fetchone=(self._tuple(rows[0]) if rows else None))

        raise AssertionError(f"Unhandled SQL in exchange_rates test double: {sql}")

    def commit(self):
        self.commit_count += 1

    def rollback(self):
        self.rollback_count += 1


def _build_client(db: FakeDb) -> TestClient:
    app = FastAPI()
    app.include_router(exchange_rates.router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def test_list_exchange_rates_returns_existing_rows():
    client = _build_client(FakeDb())

    response = client.get("/finance/exchange-rates")

    assert response.status_code == 200
    assert response.json()[0]["from_currency"] == "USD"


def test_create_get_and_update_exchange_rate():
    db = FakeDb()
    client = _build_client(db)

    created = client.post(
        "/finance/exchange-rates",
        json={
            "from_currency": "CHF",
            "to_currency": "EUR",
            "rate": "1.05",
            "rate_date": "2026-04-14",
            "rate_type": "SPOT",
            "source": "MANUAL",
            "active": True,
        },
    )
    assert created.status_code == 201
    created_id = created.json()["id"]
    assert db.commit_count == 1

    fetched = client.get(f"/finance/exchange-rates/{created_id}")
    assert fetched.status_code == 200
    assert fetched.json()["to_currency"] == "EUR"

    updated = client.put(
        f"/finance/exchange-rates/{created_id}",
        json={"rate": "1.08", "source": "TREASURY"},
    )
    assert updated.status_code == 200
    assert Decimal(updated.json()["rate"]) == Decimal("1.08")


def test_create_duplicate_and_get_nonexistent():
    client = _build_client(FakeDb())

    duplicate = client.post(
        "/finance/exchange-rates",
        json={
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": "0.92",
            "rate_date": "2026-04-13",
            "rate_type": "SPOT",
            "source": "ECB",
            "active": True,
        },
    )
    assert duplicate.status_code == 400

    missing = client.get("/finance/exchange-rates/missing")
    assert missing.status_code == 404


def test_convert_and_latest_cover_forward_reverse_and_missing_paths():
    client = _build_client(FakeDb())

    forward = client.post(
        "/finance/exchange-rates/convert",
        json={"amount": "100", "from_currency": "USD", "to_currency": "EUR", "rate_type": "SPOT"},
    )
    assert forward.status_code == 200
    assert Decimal(forward.json()["converted_amount"]) == Decimal("92")

    reverse = client.post(
        "/finance/exchange-rates/convert",
        json={"amount": "100", "from_currency": "EUR", "to_currency": "USD", "rate_type": "SPOT"},
    )
    assert reverse.status_code == 200
    assert Decimal(reverse.json()["exchange_rate"]).quantize(Decimal("0.00000001")) == Decimal("1.08695652")

    latest = client.get("/finance/exchange-rates/latest/USD/EUR")
    assert latest.status_code == 200
    assert latest.json()["rate_type"] == "SPOT"

    missing = client.get("/finance/exchange-rates/latest/XYZ/ABC")
    assert missing.status_code == 404
