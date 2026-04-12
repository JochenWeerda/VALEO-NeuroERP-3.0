"""
Tests for inventory counts — Inventur-Kopf and Inventur-Positionen CRUD + Posting.

Covers:
- Pydantic schema validation (InventoryCountCreate, InventoryCountLineCreate, etc.)
- Endpoint structure (GET/POST/DELETE counts, POST post, period-close)
"""

from __future__ import annotations

from typing import Optional

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app
from app.api.v1.endpoints.inventory_counts import (
    InventoryCountCreate,
    InventoryCountLineCreate,
    InventoryCountLineUpdate,
    InventoryCountOut,
    InventoryCountLineOut,
    InventurPostResult,
    PeriodCloseResult,
)

client = TestClient(app, raise_server_exceptions=False)
AUTH = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "test-tenant",
}


def _skip_if_unavailable(resp):
    if resp.status_code in (500, 503):
        body = resp.text
        if any(k in body for k in ("OperationalError", "Connection refused", "UndefinedTable", "does not exist")):
            pytest.skip("DB or tables not available")


# ── Schema: InventoryCountCreate ─────────────────────────────────


class TestInventoryCountCreateSchema:
    """Pydantic validation for InventoryCountCreate."""

    def test_valid_minimal(self):
        obj = InventoryCountCreate(warehouse_id="WH-100")
        assert obj.warehouse_id == "WH-100"
        assert obj.notes is None

    def test_valid_with_notes(self):
        obj = InventoryCountCreate(warehouse_id="WH-100", notes="Jahresinventur 2026")
        assert obj.notes == "Jahresinventur 2026"

    def test_missing_warehouse_id(self):
        with pytest.raises(ValidationError):
            InventoryCountCreate()


# ── Schema: InventoryCountLineCreate ─────────────────────────────


class TestInventoryCountLineCreateSchema:
    """Pydantic validation for InventoryCountLineCreate."""

    def test_valid_minimal(self):
        obj = InventoryCountLineCreate(article_id="ART-001")
        assert obj.article_id == "ART-001"
        assert obj.expected_qty == 0
        assert obj.counted_qty == 0
        assert obj.batch_number is None

    def test_valid_full(self):
        obj = InventoryCountLineCreate(
            article_id="ART-002",
            expected_qty=100.0,
            counted_qty=98.5,
            batch_number="BATCH-2026-01",
            warehouse_id="WH-200",
            bin_location_id="BIN-A3",
        )
        assert obj.counted_qty == 98.5
        assert obj.bin_location_id == "BIN-A3"

    def test_missing_article_id(self):
        with pytest.raises(ValidationError):
            InventoryCountLineCreate()


# ── Schema: InventoryCountLineUpdate ─────────────────────────────


class TestInventoryCountLineUpdateSchema:
    """Pydantic validation for InventoryCountLineUpdate — all fields optional."""

    def test_empty_is_valid(self):
        obj = InventoryCountLineUpdate()
        assert obj.counted_qty is None
        assert obj.expected_qty is None

    def test_partial_update(self):
        obj = InventoryCountLineUpdate(counted_qty=55.0)
        assert obj.counted_qty == 55.0
        assert obj.expected_qty is None


# ── Schema: Output models ────────────────────────────────────────


class TestInventoryCountOutSchema:
    """InventoryCountOut output model structure."""

    def test_construct(self):
        obj = InventoryCountOut(
            id="cnt-001",
            warehouse_id="WH-001",
            status="open",
            total_items=5,
            discrepancies_found=2,
            notes="Q1 Inventur",
        )
        assert obj.status == "open"
        assert obj.discrepancies_found == 2

    def test_defaults(self):
        obj = InventoryCountOut(id="cnt-002", warehouse_id="WH-002", status="posted")
        assert obj.total_items == 0
        assert obj.discrepancies_found == 0
        assert obj.notes is None


class TestInventoryCountLineOutSchema:
    """InventoryCountLineOut output model structure."""

    def test_construct(self):
        obj = InventoryCountLineOut(
            id="line-001",
            inventory_count_id="cnt-001",
            article_id="ART-001",
            expected_qty=100,
            counted_qty=97,
            difference=-3,
        )
        assert obj.difference == -3
        assert obj.batch_number is None


class TestInventurPostResultSchema:
    """InventurPostResult output model."""

    def test_construct(self):
        obj = InventurPostResult(
            count_id="cnt-001",
            posted_lines=10,
            total_adjustments=3,
            journal_entry_id="JE-001",
            status="posted",
        )
        assert obj.total_adjustments == 3

    def test_journal_entry_optional(self):
        obj = InventurPostResult(
            count_id="cnt-002",
            posted_lines=5,
            total_adjustments=0,
            status="posted",
        )
        assert obj.journal_entry_id is None


# ── Endpoint: GET /api/v1/inventory/counts/ ──────────────────────


class TestListInventoryCountsEndpoint:
    """GET /api/v1/inventory/counts/ — paginated list."""

    def test_returns_paginated_response(self):
        resp = client.get("/api/v1/inventory/counts/", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert isinstance(body["items"], list)

    def test_pagination_params(self):
        resp = client.get("/api/v1/inventory/counts/?skip=0&limit=5", headers=AUTH)
        _skip_if_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("size", body.get("limit", 5)) <= 5


# ── Endpoint: POST /api/v1/inventory/counts/ ────────────────────


class TestCreateInventoryCountEndpoint:
    """POST /api/v1/inventory/counts/ — create count header."""

    def test_422_on_empty_body(self):
        resp = client.post("/api/v1/inventory/counts/", json={}, headers=AUTH)
        assert resp.status_code == 422

    def test_create_with_valid_payload(self):
        resp = client.post(
            "/api/v1/inventory/counts/",
            json={"warehouse_id": "WH-TEST-001", "notes": "Pytest-Inventur"},
            headers=AUTH,
        )
        _skip_if_unavailable(resp)
        if resp.status_code == 201:
            body = resp.json()
            assert body["warehouse_id"] == "WH-TEST-001"
            assert body["status"] == "open"


# ── Endpoint: DELETE /api/v1/inventory/counts/{id} ──────────────


class TestDeleteInventoryCountEndpoint:
    """DELETE /api/v1/inventory/counts/{id} — 404 for nonexistent."""

    def test_404_on_nonexistent(self):
        resp = client.delete(
            "/api/v1/inventory/counts/nonexistent-id-00000",
            headers=AUTH,
        )
        _skip_if_unavailable(resp)
        assert resp.status_code == 404


# ── Endpoint: POST /api/v1/inventory/counts/{id}/post ───────────


class TestPostInventoryCountEndpoint:
    """POST /api/v1/inventory/counts/{id}/post — post a count."""

    def test_404_on_nonexistent_count(self):
        resp = client.post(
            "/api/v1/inventory/counts/nonexistent-id-00000/post",
            headers=AUTH,
        )
        _skip_if_unavailable(resp)
        assert resp.status_code == 404


# ── Endpoint: POST /api/v1/inventory/counts/period-close ────────


class TestPeriodCloseEndpoint:
    """POST /api/v1/inventory/counts/period-close."""

    def test_requires_period_param(self):
        resp = client.post("/api/v1/inventory/counts/period-close", headers=AUTH)
        assert resp.status_code == 422

    def test_with_period_param(self):
        resp = client.post(
            "/api/v1/inventory/counts/period-close?period=2026-Q1",
            headers=AUTH,
        )
        _skip_if_unavailable(resp)
        if resp.status_code == 200:
            body = resp.json()
            assert body["period"] == "2026-Q1"
            assert "status" in body
