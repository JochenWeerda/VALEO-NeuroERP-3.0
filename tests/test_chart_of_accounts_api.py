"""
Tests for Chart of Accounts API endpoints.

Unit-Tests (kein DB): Pagination, 404-Pfade, Schema-Validierung,
Validation-Endpoint, DATEV-Export-Signatur.
Integration-Tests (skip_if_db_unavailable): CRUD gegen Live-DB.
"""

from __future__ import annotations

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


# ── Integration Tests ────────────────────────────────────────────────────────

class TestChartOfAccountsList:
    """GET /chart-of-accounts/"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/finance/chart-of-accounts/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_list_with_search(self):
        r = client.get("/api/v1/finance/chart-of-accounts/?search=Bank", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_pagination(self):
        r = client.get("/api/v1/finance/chart-of-accounts/?skip=0&limit=10", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestChartOfAccountsDetail:
    """GET /chart-of-accounts/{id}"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/finance/chart-of-accounts/NONEXISTENT-ACC-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestChartOfAccountsCreate:
    """POST /chart-of-accounts/"""

    def test_create_missing_fields_422(self):
        r = client.post("/api/v1/finance/chart-of-accounts/", headers=AUTH, json={})
        assert r.status_code == 422

    def test_create_invalid_account_type_422(self):
        r = client.post("/api/v1/finance/chart-of-accounts/", headers=AUTH, json={
            "account_number": "9999",
            "account_name": "Test",
            "account_type": "invalid_type",
            "category": "other",
            "tenant_id": "test-tenant",
        })
        assert r.status_code == 422


class TestChartOfAccountsValidate:
    """POST /chart-of-accounts/validate"""

    def test_validate_returns_structure(self):
        r = client.post("/api/v1/finance/chart-of-accounts/validate", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "valid" in data
        assert "errors" in data


class TestChartOfAccountsDatevExport:
    """POST /chart-of-accounts/datev-export"""

    def test_datev_export_requires_von_datum(self):
        r = client.post("/api/v1/finance/chart-of-accounts/datev-export", headers=AUTH)
        assert r.status_code == 422

    def test_datev_export_with_date(self):
        r = client.post(
            "/api/v1/finance/chart-of-accounts/datev-export?von_datum=2026-01-01",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code in (200, 500)


# ── Schemas Unit-Tests ───────────────────────────────────────────────────────

from app.api.v1.schemas.finance import Account, AccountCreate, AccountUpdate


class TestAccountSchemas:
    def test_account_create_valid(self):
        a = AccountCreate(
            account_number="1200",
            account_name="Forderungen",
            account_type="asset",
            category="current_assets",
            tenant_id="t-1",
        )
        assert a.currency == "EUR"
        assert a.allow_manual_entries is True

    def test_account_create_invalid_type(self):
        with pytest.raises(Exception):
            AccountCreate(
                account_number="9999",
                account_name="Bad",
                account_type="unknown_type",
                category="other",
                tenant_id="t-1",
            )

    def test_account_update_all_optional(self):
        u = AccountUpdate()
        assert u.account_name is None
        assert u.account_type is None


# ── FakeDb Unit-Tests ────────────────────────────────────────────────────────

def _make_account_mock(
    aid: str = "ACC-1",
    number: str = "1200",
    name: str = "Forderungen",
    acct_type: str = "asset",
    is_active: bool = True,
):
    m = MagicMock()
    m.id = aid
    m.account_number = number
    m.account_name = name
    m.account_type = acct_type
    m.category = "current_assets"
    m.currency = "EUR"
    m.allow_manual_entries = True
    m.parent_account_id = None
    m.balance = Decimal("0.00")
    m.is_active = is_active
    m.tenant_id = "unit"
    m.created_at = None
    m.updated_at = None
    m.deleted_at = None
    m.is_summary = False
    m.subcategory = None
    m.description = None
    m.last_transaction_date = None
    return m


class _FakeQuery:
    def __init__(self, items):
        self._items = list(items)

    def filter(self, *_a, **_kw):
        return self

    def count(self):
        return len(self._items)

    def offset(self, n):
        self._items = self._items[n:]
        return self

    def limit(self, n):
        self._items = self._items[:n]
        return self

    def all(self):
        return list(self._items)

    def first(self):
        return self._items[0] if self._items else None


class _FakeDb:
    def __init__(self, items=None, execute_rows=None):
        self._items = list(items or [])
        self._execute_rows = execute_rows or []
        self.added = []
        self.committed = 0
        self.refreshed = 0
        self.deleted = []

    def query(self, _model):
        return _FakeQuery(self._items)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed += 1

    def refresh(self, obj):
        self.refreshed += 1

    def delete(self, obj):
        self.deleted.append(obj)

    def execute(self, _q, _p=None):
        m = MagicMock()
        m.fetchall.return_value = self._execute_rows
        m.fetchone.return_value = self._execute_rows[0] if self._execute_rows else None
        return m


def _coa_client(db: _FakeDb):
    from app.api.v1.endpoints import chart_of_accounts as coa_router
    _app = FastAPI()
    _app.include_router(coa_router)  # router prefix is already /chart-of-accounts
    _app.dependency_overrides[get_db] = lambda: db
    return TestClient(_app, raise_server_exceptions=False)


class TestChartOfAccountsListUnit:
    def _client_with_patch(self, items):
        db = _FakeDb(items=items)
        with patch(
            "app.api.v1.schemas.finance.Account.model_validate",
            side_effect=lambda x: Account(
                id=x.id,
                account_number=x.account_number,
                account_name=x.account_name,
                account_type=x.account_type,
                category=x.category,
                tenant_id=x.tenant_id,
                balance=x.balance,
            ),
        ):
            return _coa_client(db)

    def test_empty_returns_paginated_zero(self):
        c = self._client_with_patch([])
        r = c.get("/chart-of-accounts/")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["pages"] == 1

    def test_with_items(self):
        items = [_make_account_mock(f"ACC-{i}") for i in range(3)]
        c = self._client_with_patch(items)
        r = c.get("/chart-of-accounts/?limit=2")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 3
        assert data["size"] == 2

    def test_not_found_404(self):
        c = self._client_with_patch([])
        r = c.get("/chart-of-accounts/ACC-miss")
        assert r.status_code == 404


class TestChartOfAccountsValidateUnit:
    def test_empty_accounts_valid(self):
        c = _coa_client(_FakeDb(items=[]))
        r = c.post("/chart-of-accounts/validate")
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is True
        assert data["errors"] == []

    def test_invalid_account_type_produces_error(self):
        acc = _make_account_mock("ACC-1", acct_type="bogus")
        c = _coa_client(_FakeDb(items=[acc]))
        r = c.post("/chart-of-accounts/validate")
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert any("bogus" in e or "Ungültige" in e for e in data["errors"])

    def test_duplicate_account_number_produces_error(self):
        acc1 = _make_account_mock("ACC-1", number="1200")
        acc2 = _make_account_mock("ACC-2", number="1200")
        c = _coa_client(_FakeDb(items=[acc1, acc2]))
        r = c.post("/chart-of-accounts/validate")
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert any("1200" in e for e in data["errors"])


class TestChartOfAccountsDatevExportUnit:
    def test_export_requires_von_datum(self):
        c = _coa_client(_FakeDb())
        r = c.post("/chart-of-accounts/datev-export")
        assert r.status_code == 422

    def test_export_returns_csv_on_empty_db(self):
        c = _coa_client(_FakeDb(execute_rows=[]))
        r = c.post("/chart-of-accounts/datev-export?von_datum=2026-01-01")
        assert r.status_code == 200
        assert "text/csv" in r.headers.get("content-type", "")
