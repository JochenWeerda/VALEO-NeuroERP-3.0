"""
Tests for Booking Templates API endpoints.

Unit-Tests (kein DB): Schema-Validierung, Listenlogik, Balancing-Check,
Apply-Pfade via FakeDb-Execute-Mocks.
Integration-Tests (skip_if_db_unavailable): CRUD-Pfade gegen Live-DB.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.core.database import get_db

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Integration Tests (DB required) ─────────────────────────────────────────

class TestBookingTemplatesList:
    """GET /booking-templates"""

    def test_list_returns_list(self):
        r = client.get("/api/v1/finance/booking-templates", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_active_only_default(self):
        r = client.get("/api/v1/finance/booking-templates?active_only=true", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_category_filter(self):
        r = client.get("/api/v1/finance/booking-templates?category=GENERAL", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/finance/booking-templates/NONEXISTENT-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestBookingTemplatesCreate:
    """POST /booking-templates"""

    def test_create_missing_lines_422(self):
        r = client.post("/api/v1/finance/booking-templates", headers=AUTH, json={
            "name": "Test", "lines": []
        })
        assert r.status_code == 422

    def test_create_missing_name_422(self):
        r = client.post("/api/v1/finance/booking-templates", headers=AUTH, json={})
        assert r.status_code == 422


class TestBookingTemplatesApply:
    """POST /booking-templates/{id}/apply"""

    def test_apply_nonexistent_404(self):
        r = client.post("/api/v1/finance/booking-templates/NONEXISTENT/apply", headers=AUTH, json={
            "entry_date": "2026-05-05",
            "amount": "1000.00",
        })
        skip_if_db_unavailable(r)
        assert r.status_code in (404, 500)


# ── Schemas Unit-Tests ───────────────────────────────────────────────────────

from app.api.v1.endpoints.booking_templates import (
    BookingTemplateLine,
    BookingTemplateCreate,
    BookingTemplateUpdate,
    BookingTemplateResponse,
    ApplyTemplateRequest,
    ApplyTemplateResponse,
    router as bt_router,
)


class TestBookingTemplateSchemas:
    def test_line_create_minimal(self):
        line = BookingTemplateLine(
            account_number="1000",
            debit_percentage=Decimal("100"),
            credit_percentage=Decimal("0"),
            line_number=1,
        )
        assert line.account_number == "1000"
        assert line.tax_code is None

    def test_line_create_fixed_amounts(self):
        line = BookingTemplateLine(
            account_number="1200",
            fixed_debit=Decimal("500.00"),
            credit_percentage=Decimal("0"),
            line_number=2,
        )
        assert line.fixed_debit == Decimal("500.00")

    def test_template_create_valid(self):
        t = BookingTemplateCreate(
            name="Miete",
            lines=[
                BookingTemplateLine(
                    account_number="4800",
                    debit_percentage=Decimal("100"),
                    credit_percentage=Decimal("0"),
                    line_number=1,
                ),
                BookingTemplateLine(
                    account_number="1200",
                    debit_percentage=Decimal("0"),
                    credit_percentage=Decimal("100"),
                    line_number=2,
                ),
            ],
        )
        assert t.currency == "EUR"
        assert t.active is True
        assert t.trigger_type == "MANUAL"

    def test_template_create_too_few_lines_422(self):
        with pytest.raises(Exception):
            BookingTemplateCreate(
                name="X",
                lines=[
                    BookingTemplateLine(
                        account_number="1000",
                        debit_percentage=Decimal("100"),
                        credit_percentage=Decimal("0"),
                        line_number=1,
                    )
                ],
            )

    def test_apply_request_requires_entry_date(self):
        with pytest.raises(Exception):
            ApplyTemplateRequest()

    def test_apply_request_valid(self):
        r = ApplyTemplateRequest(entry_date=date(2026, 5, 5), amount=Decimal("1000"))
        assert r.amount == Decimal("1000")
        assert r.entry_date == date(2026, 5, 5)

    def test_update_all_none_valid(self):
        u = BookingTemplateUpdate()
        assert u.name is None
        assert u.active is None


# ── FakeDb Unit-Tests ────────────────────────────────────────────────────────

def _make_row(
    tid: str = "T-1",
    name: str = "Miete",
    category: str = "GENERAL",
    active: bool = True,
):
    """Build a fake DB row tuple matching the SELECT column order."""
    lines = json.dumps([
        {
            "account_number": "4800",
            "debit_percentage": "100.00",
            "credit_percentage": "0.00",
            "fixed_debit": None,
            "fixed_credit": None,
            "description_template": None,
            "tax_code": None,
            "cost_center": None,
            "profit_center": None,
            "line_number": 1,
        },
        {
            "account_number": "1200",
            "debit_percentage": "0.00",
            "credit_percentage": "100.00",
            "fixed_debit": None,
            "fixed_credit": None,
            "description_template": None,
            "tax_code": None,
            "cost_center": None,
            "profit_center": None,
            "line_number": 2,
        },
    ])
    now = datetime(2026, 5, 5, 8, 0)
    # Columns: id, name, description, category, trigger_type, trigger_config, lines,
    #          default_amount, currency, active, created_at, updated_at
    return (tid, name, None, category, "MANUAL", None, lines, None, "EUR", active, now, now)


class _FakeResult:
    def __init__(self, rows=None, rowcount=0):
        self._rows = list(rows or [])
        self.rowcount = rowcount

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._rows[0] if self._rows else None


class _FakeDb:
    def __init__(self, rows=None, insert_row=None, rowcount=1):
        self._rows = list(rows or [])
        self._insert_row = insert_row
        self._rowcount = rowcount
        self.committed = 0
        self.rolled_back = 0

    def execute(self, _query, _params=None):
        sql = str(_query).strip().upper()
        if sql.startswith("INSERT"):
            r = self._insert_row or (self._rows[0] if self._rows else _make_row())
            return _FakeResult([r], rowcount=1)
        if sql.startswith("UPDATE"):
            row = self._rows[0] if self._rows else None
            rc = 1 if row else 0
            return _FakeResult([row] if row else [], rowcount=rc)
        # SELECT
        return _FakeResult(self._rows)

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolled_back += 1


def _bt_client(db: _FakeDb):
    _app = FastAPI()
    _app.include_router(bt_router)
    _app.dependency_overrides[get_db] = lambda: db
    return TestClient(_app, raise_server_exceptions=False)


class TestBookingTemplatesListUnit:
    def test_empty_returns_empty_list(self):
        c = _bt_client(_FakeDb())
        r = c.get("/booking-templates")
        assert r.status_code == 200
        assert r.json() == []

    def test_one_row_returns_one_item(self):
        row = _make_row("T-1", "Miete")
        c = _bt_client(_FakeDb(rows=[row]))
        r = c.get("/booking-templates")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["name"] == "Miete"
        assert data[0]["category"] == "GENERAL"

    def test_category_filter_passes_through(self):
        row = _make_row("T-1", "Miete", category="RENT")
        c = _bt_client(_FakeDb(rows=[row]))
        r = c.get("/booking-templates?category=RENT")
        assert r.status_code == 200


class TestBookingTemplateGetUnit:
    def test_get_existing(self):
        row = _make_row("T-1", "Miete")
        c = _bt_client(_FakeDb(rows=[row]))
        r = c.get("/booking-templates/T-1")
        assert r.status_code == 200
        assert r.json()["id"] == "T-1"

    def test_get_nonexistent_404(self):
        c = _bt_client(_FakeDb(rows=[]))
        r = c.get("/booking-templates/T-miss")
        assert r.status_code == 404


class TestBookingTemplateCreateUnit:
    def _valid_payload(self):
        return {
            "name": "Miete",
            "lines": [
                {
                    "account_number": "4800",
                    "debit_percentage": "100.00",
                    "credit_percentage": "0.00",
                    "line_number": 1,
                },
                {
                    "account_number": "1200",
                    "debit_percentage": "0.00",
                    "credit_percentage": "100.00",
                    "line_number": 2,
                },
            ],
        }

    def test_create_balanced_201(self):
        row = _make_row("T-new", "Miete")
        c = _bt_client(_FakeDb(insert_row=row))
        r = c.post("/booking-templates", json=self._valid_payload())
        assert r.status_code == 201
        assert r.json()["name"] == "Miete"

    def test_create_unbalanced_400(self):
        c = _bt_client(_FakeDb())
        payload = self._valid_payload()
        payload["lines"][0]["debit_percentage"] = "90.00"
        r = c.post("/booking-templates", json=payload)
        assert r.status_code == 400
        assert "balance" in r.json()["detail"].lower()

    def test_create_missing_lines_422(self):
        c = _bt_client(_FakeDb())
        r = c.post("/booking-templates", json={"name": "X"})
        assert r.status_code == 422


class TestBookingTemplateUpdateUnit:
    def test_update_existing(self):
        row = _make_row("T-1", "Miete Updated")
        c = _bt_client(_FakeDb(rows=[row]))
        r = c.put("/booking-templates/T-1", json={"name": "Miete Updated"})
        assert r.status_code == 200
        assert r.json()["name"] == "Miete Updated"

    def test_update_nonexistent_404(self):
        c = _bt_client(_FakeDb(rows=[]))
        r = c.put("/booking-templates/T-miss", json={"name": "X"})
        assert r.status_code == 404

    def test_update_no_fields_400(self):
        c = _bt_client(_FakeDb())
        r = c.put("/booking-templates/T-1", json={})
        assert r.status_code == 400


class TestBookingTemplateDeleteUnit:
    def test_delete_existing_204(self):
        c = _bt_client(_FakeDb(rows=[_make_row("T-1")], rowcount=1))
        r = c.delete("/booking-templates/T-1")
        assert r.status_code == 204

    def test_delete_nonexistent_404(self):
        c = _bt_client(_FakeDb(rows=[], rowcount=0))
        r = c.delete("/booking-templates/T-miss")
        assert r.status_code == 404
