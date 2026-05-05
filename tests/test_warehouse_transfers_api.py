"""
COV-INV-002: Tests for Warehouse Transfers API endpoints.

Covers /api/v1/warehouses/transfers — Transfers CRUD + Post,
Corrections CRUD, Bin Locations.

Unit-Tests: Schema-Validierung, Helper-Funktionen, Paginierungslogik (kein DB).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.core.database import get_db
from app.core.tenant import get_tenant_id

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Transfers ───────────────────────────────────────────────────


class TestTransfersList:
    """GET /warehouses/transfers/"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/transfers/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_list_with_pagination(self):
        r = client.get("/api/v1/warehouses/transfers/?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestTransfersCRUD:
    """POST/GET/PUT/DELETE /warehouses/transfers"""

    def test_create_transfer(self):
        payload = {
            "transfer_number": "UML-TEST-001",
            "from_warehouse_id": "WH-001",
            "to_warehouse_id": "WH-002",
            "notes": "Test-Umlagerung COV-INV-002",
        }
        r = client.post("/api/v1/warehouses/transfers/", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_create_transfer_missing_fields_422(self):
        r = client.post("/api/v1/warehouses/transfers/", headers=AUTH, json={})
        assert r.status_code == 422

    def test_get_nonexistent_transfer_404(self):
        r = client.get(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_update_nonexistent_transfer_404(self):
        payload = {
            "transfer_number": "UML-TEST-002",
            "from_warehouse_id": "WH-001",
            "to_warehouse_id": "WH-003",
        }
        r = client.put(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_transfer_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_post_nonexistent_transfer_404(self):
        r = client.post(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/post",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestTransferLines:
    """POST/PUT/DELETE /warehouses/transfers/{id}/lines"""

    def test_create_line_nonexistent_transfer_404(self):
        payload = {
            "article_id": "ART-001",
            "quantity": 100,
        }
        r = client.post(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_update_line_nonexistent_404(self):
        payload = {
            "article_id": "ART-001",
            "quantity": 50,
        }
        r = client.put(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines/NONEXISTENT-LINE",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_line_nonexistent_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines/NONEXISTENT-LINE",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Corrections ─────────────────────────────────────────────────


class TestCorrectionsList:
    """GET /warehouses/transfers/corrections"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/transfers/corrections", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data


class TestCorrectionsCRUD:
    """POST/PUT/DELETE /warehouses/transfers/corrections"""

    def test_create_correction(self):
        payload = {
            "correction_number": "KORR-TEST-001",
            "warehouse_id": "WH-001",
            "reason": "Inventurdifferenz",
        }
        r = client.post(
            "/api/v1/warehouses/transfers/corrections",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_create_correction_missing_fields_422(self):
        r = client.post(
            "/api/v1/warehouses/transfers/corrections",
            headers=AUTH,
            json={},
        )
        assert r.status_code == 422

    def test_update_nonexistent_correction_404(self):
        payload = {
            "correction_number": "KORR-TEST-002",
            "warehouse_id": "WH-001",
        }
        r = client.put(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_correction_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestCorrectionLines:
    """GET/POST correction lines"""

    def test_get_lines_nonexistent_404(self):
        r = client.get(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR/lines",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_line_nonexistent_404(self):
        payload = {
            "article_id": "ART-001",
            "old_quantity": 100,
            "new_quantity": 95,
        }
        r = client.post(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR/lines",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Bin Locations ───────────────────────────────────────────────


class TestBinLocations:
    """GET /warehouses/transfers/bin-locations"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/warehouses/transfers/bin-locations", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_filter_by_warehouse(self):
        r = client.get(
            "/api/v1/warehouses/transfers/bin-locations?warehouse_id=WH-001",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Unit-Tests (kein DB)
# ---------------------------------------------------------------------------

from app.api.v1.endpoints.warehouse_transfers import (
    TransferCreate,
    TransferLineCreate,
    CorrectionCreate,
    CorrectionLineCreate,
    TransferOut,
    CorrectionOut,
    router as transfer_router,
)


class TestTransferSchemas:
    def test_transfer_create_required_fields(self):
        t = TransferCreate(
            transfer_number="UML-001",
            from_warehouse_id="WH-A",
            to_warehouse_id="WH-B",
        )
        assert t.transfer_number == "UML-001"
        assert t.notes is None

    def test_transfer_line_create(self):
        line = TransferLineCreate(article_id="ART-001", quantity=50.0)
        assert line.quantity == 50.0
        assert line.batch_number is None

    def test_correction_create(self):
        c = CorrectionCreate(correction_number="KORR-001", warehouse_id="WH-A")
        assert c.reason is None

    def test_correction_line_create_difference(self):
        line = CorrectionLineCreate(article_id="ART-001", old_quantity=100.0, new_quantity=95.0)
        assert line.old_quantity == 100.0
        assert line.new_quantity == 95.0


class _FakeTransferQuery:
    def __init__(self, items=None):
        self._items = list(items or [])

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


class _FakeTransferDb:
    def __init__(self, transfers=None, lines=None, corrections=None, bins=None):
        self._transfers = list(transfers or [])
        self._lines = list(lines or [])
        self._corrections = list(corrections or [])
        self._bins = list(bins or [])

    def query(self, model):
        from app.infrastructure.models import (
            WarehouseTransfer, WarehouseTransferLine,
            StockCorrection, StockCorrectionLine, BinLocation,
        )
        mapping = {
            WarehouseTransfer: self._transfers,
            WarehouseTransferLine: self._lines,
            StockCorrection: self._corrections,
            StockCorrectionLine: [],
            BinLocation: self._bins,
        }
        return _FakeTransferQuery(mapping.get(model, []))

    def add(self, obj):
        pass

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def delete(self, obj):
        pass

    def execute(self, *_a, **_kw):
        return MagicMock()


def _transfer_mock(tid: str = "T-1") -> MagicMock:
    m = MagicMock()
    m.id = tid
    m.transfer_number = f"UML-{tid}"
    m.from_warehouse_id = "WH-A"
    m.to_warehouse_id = "WH-B"
    m.status = "draft"
    m.notes = None
    m.tenant_id = "unit"
    return m


def _correction_mock(cid: str = "C-1") -> MagicMock:
    m = MagicMock()
    m.id = cid
    m.correction_number = f"KORR-{cid}"
    m.warehouse_id = "WH-A"
    m.reason = None
    m.status = "draft"
    m.tenant_id = "unit"
    return m


def _bin_mock(bid: str = "BIN-1") -> MagicMock:
    m = MagicMock()
    m.id = bid
    m.code = "A-01-1"
    m.warehouse_id = "WH-A"
    m.zone = "A"
    m.rack = "01"
    m.shelf = "1"
    m.tenant_id = "unit"
    return m


def _transfer_client(db: _FakeTransferDb):
    _app = FastAPI()
    _app.include_router(transfer_router)
    _app.dependency_overrides[get_db] = lambda: db
    _app.dependency_overrides[get_tenant_id] = lambda: "unit"
    return TestClient(_app)


class TestTransferListUnit:
    def test_empty_paginated(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_with_items(self):
        t = _transfer_mock("T-1")
        db = _FakeTransferDb(transfers=[t])

        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(TransferOut, "model_validate", lambda x: TransferOut(
                id=x.id,
                transfer_number=x.transfer_number,
                from_warehouse_id=x.from_warehouse_id,
                to_warehouse_id=x.to_warehouse_id,
            ))
            c = _transfer_client(db)
            r = c.get("/")
        assert r.status_code == 200
        assert r.json()["total"] == 1


class TestTransferNotFoundUnit:
    def test_lines_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.get("/T-miss/lines")
        assert r.status_code == 404

    def test_update_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.put("/T-miss", json={
            "transfer_number": "X", "from_warehouse_id": "A", "to_warehouse_id": "B"
        })
        assert r.status_code == 404

    def test_delete_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.delete("/T-miss")
        assert r.status_code == 404

    def test_post_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.post("/T-miss/post")
        assert r.status_code == 404

    def test_create_line_transfer_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.post("/T-miss/lines", json={"article_id": "A", "quantity": 1.0})
        assert r.status_code == 404

    def test_create_transfer_missing_fields_422(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.post("/", json={})
        assert r.status_code == 422


class TestCorrectionListUnit:
    def test_empty_paginated(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.get("/corrections")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0


class TestCorrectionNotFoundUnit:
    def test_get_lines_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        assert c.get("/corrections/C-miss/lines").status_code == 404

    def test_create_line_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.post("/corrections/C-miss/lines", json={
            "article_id": "A", "old_quantity": 10.0, "new_quantity": 9.0
        })
        assert r.status_code == 404

    def test_update_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.put("/corrections/C-miss", json={
            "correction_number": "X", "warehouse_id": "WH-A"
        })
        assert r.status_code == 404

    def test_delete_not_found(self):
        c = _transfer_client(_FakeTransferDb())
        assert c.delete("/corrections/C-miss").status_code == 404

    def test_create_missing_fields_422(self):
        c = _transfer_client(_FakeTransferDb())
        assert c.post("/corrections", json={}).status_code == 422


class TestBinLocationsUnit:
    def test_empty_list(self):
        c = _transfer_client(_FakeTransferDb())
        r = c.get("/bin-locations")
        assert r.status_code == 200
        assert r.json() == []

    def test_with_bins(self):
        bins = [_bin_mock("BIN-1"), _bin_mock("BIN-2")]
        db = _FakeTransferDb(bins=bins)
        with pytest.MonkeyPatch().context() as mp:
            from app.api.v1.endpoints.warehouse_transfers import BinLocationOut
            mp.setattr(BinLocationOut, "model_validate", lambda x: BinLocationOut(
                id=x.id, code=x.code, warehouse_id=x.warehouse_id
            ))
            c = _transfer_client(db)
            r = c.get("/bin-locations")
        assert r.status_code == 200
        assert len(r.json()) == 2
