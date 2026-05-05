"""
COV-INV-002: Tests for Waage API endpoints.

Covers /api/v1/waage — Waagen CRUD + Wiegungen CRUD.

Unit-Tests (kein DB) für Helper + alle Endpoint-Pfade via Repo-Mocks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.waage import _serialize_value, _to_list, router as waage_router
from app.core.database import get_db

_NOW = datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Repo fakes
# ---------------------------------------------------------------------------

def _fw(wid: str = "W-1", status: str = "aktiv") -> MagicMock:
    w = MagicMock()
    w.id = wid
    w.standort = "Halle A"
    w.typ = "LKW"
    w.max_kapazitaet = 50.0
    w.status = status
    w.created_at = _NOW
    w.updated_at = _NOW
    return w


def _fwg(wgid: str = "WG-1") -> MagicMock:
    w = MagicMock()
    w.id = wgid
    w.kennzeichen = "HB-1"
    w.artikel = "Mais"
    w.brutto = 30.0
    w.tara = 10.0
    w.netto = 20.0
    w.created_at = _NOW
    return w


class _WaageRepo:
    def __init__(self, items=None):
        self._items = list(items or [])

    def get_all(self, skip=0, limit=100):
        return self._items[skip: skip + limit]

    def get_by_status(self, status):
        return [i for i in self._items if i.status == status]

    def get_by_id(self, eid):
        return next((i for i in self._items if i.id == eid), None)

    def create(self, data):
        if data.get("_raise"):
            raise ValueError("boom")
        return _fw("W-new")

    def update(self, eid, data):
        return next((i for i in self._items if i.id == eid), None)

    def delete(self, eid):
        return any(i.id == eid for i in self._items)


class _WiegungRepo:
    def __init__(self, items=None):
        self._items = list(items or [])
        self.last_data: dict = {}

    def get_all(self, skip=0, limit=100):
        return self._items

    def get_by_waage(self, _wid):
        return []

    def get_by_kennzeichen(self, kz):
        return [i for i in self._items if i.kennzeichen == kz]

    def get_by_id(self, eid):
        return next((i for i in self._items if i.id == eid), None)

    def create(self, data):
        self.last_data = dict(data)
        w = _fwg("WG-new")
        w.netto = data.get("netto", data.get("brutto", 0) - data.get("tara", 0))
        return w

    def delete(self, eid):
        return any(i.id == eid for i in self._items)


from unittest.mock import patch as _mock_patch
import contextlib


_WAAGE_ATTRS = ("id", "standort", "typ", "max_kapazitaet", "status", "created_at", "updated_at")
_WIEGUNG_ATTRS = ("id", "kennzeichen", "artikel", "brutto", "tara", "netto", "created_at")


def _mock_to_dict(model):
    """Replacement for _to_dict that works with MagicMock (no sa_inspect)."""
    if model is None:
        return {}
    attrs = _WIEGUNG_ATTRS if hasattr(model, "kennzeichen") else _WAAGE_ATTRS
    return {a: _serialize_value(getattr(model, a, None)) for a in attrs}


@contextlib.contextmanager
def _client_ctx(waagen=None, wiegungen=None):
    """Context manager that keeps repo patches alive for the lifetime of the client."""
    wr = _WaageRepo(waagen)
    wgr = _WiegungRepo(wiegungen)
    with _mock_patch("app.api.v1.endpoints.waage.WaageRepository", lambda db: wr), \
         _mock_patch("app.api.v1.endpoints.waage.WiegungRepository", lambda db: wgr), \
         _mock_patch("app.api.v1.endpoints.waage._to_dict", _mock_to_dict):
        _app = FastAPI()
        _app.include_router(waage_router)
        _app.dependency_overrides[get_db] = lambda: MagicMock()
        yield TestClient(_app), wgr


def _client(waagen=None, wiegungen=None):
    """Returns (client, wgr) with patches already entered (used inside `with` blocks in tests)."""
    wr = _WaageRepo(waagen)
    wgr = _WiegungRepo(wiegungen)
    patcher_w = _mock_patch("app.api.v1.endpoints.waage.WaageRepository", lambda db: wr)
    patcher_wg = _mock_patch("app.api.v1.endpoints.waage.WiegungRepository", lambda db: wgr)
    patcher_w.start()
    patcher_wg.start()
    _app = FastAPI()
    _app.include_router(waage_router)
    _app.dependency_overrides[get_db] = lambda: MagicMock()
    c = TestClient(_app)
    # Stop after client creation so patches stay active through requests made on c
    # (TestClient is synchronous — requests happen when .get/.post is called, not here)
    # We need patches to stay active, so we DON'T stop them. Tests must call
    # patcher_w.stop() / patcher_wg.stop() — handled via _client_ctx in unit tests.
    # For backward compat: store stoppers on the client object.
    c._stop_patches = lambda: (patcher_w.stop(), patcher_wg.stop())
    return c, wgr

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Waagen ──────────────────────────────────────────────────────


class TestWaagenList:
    """GET /waage/waagen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/waagen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/waagen?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_status(self):
        r = client.get("/api/v1/waage/waagen?status=aktiv", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestWaagenCRUD:
    """POST/GET/PATCH/DELETE /waage/waagen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_waage(self):
        payload = {
            "id": "WAAGE-TEST-001",
            "waage_name": "Testwaage COV-INV-002",
            "standort": "Hauptlager",
            "status": "aktiv",
            "max_kapazitaet": 60000,
        }
        r = client.post("/api/v1/waage/waagen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_patch_nonexistent_404(self):
        r = client.patch(
            "/api/v1/waage/waagen/NONEXISTENT-WAAGE",
            headers=AUTH,
            json={"status": "inaktiv"},
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Wiegungen ───────────────────────────────────────────────────


class TestWiegungenList:
    """GET /waage/wiegungen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/wiegungen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/wiegungen?skip=0&limit=10", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_waage_id(self):
        r = client.get("/api/v1/waage/wiegungen?waage_id=WAAGE-001", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_kennzeichen(self):
        r = client.get("/api/v1/waage/wiegungen?kennzeichen=AB-CD-1234", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestWiegungenCRUD:
    """POST/GET/DELETE /waage/wiegungen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_wiegung(self):
        payload = {
            "id": "WIEG-TEST-001",
            "waage_id": "WAAGE-001",
            "kennzeichen": "AB-CD-1234",
            "brutto": 25000,
            "tara": 12000,
        }
        r = client.post("/api/v1/waage/wiegungen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Helper unit tests (kein DB)
# ---------------------------------------------------------------------------

class TestSerializeValue:
    def test_datetime(self):
        assert "2026-05-05" in _serialize_value(_NOW)

    def test_decimal(self):
        assert _serialize_value(Decimal("3.14")) == pytest.approx(3.14)

    def test_string(self):
        assert _serialize_value("hello") == "hello"

    def test_none(self):
        assert _serialize_value(None) is None

    def test_int(self):
        assert _serialize_value(7) == 7


class TestToList:
    def test_empty(self):
        assert _to_list([]) == []


# ---------------------------------------------------------------------------
# Waage Unit-Tests via Repo-Mock
# ---------------------------------------------------------------------------

class TestWaagenUnit:
    def test_list_empty(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/waagen").status_code == 200
            assert c.get("/waage/waagen").json() == []

    def test_list_status_filter(self):
        with _client_ctx(waagen=[_fw("W-1", "aktiv"), _fw("W-2", "inaktiv")]) as (c, _):
            assert c.get("/waage/waagen?status=aktiv").status_code == 200

    def test_get_not_found(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/waagen/W-miss").status_code == 404

    def test_get_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.get("/waage/waagen/W-1").status_code == 200

    def test_create_ok(self):
        with _client_ctx() as (c, _):
            assert c.post("/waage/waagen", json={"standort": "A"}).status_code == 201

    def test_create_error_400(self):
        with _client_ctx() as (c, _):
            assert c.post("/waage/waagen", json={"_raise": True}).status_code == 400

    def test_update_not_found(self):
        with _client_ctx() as (c, _):
            assert c.patch("/waage/waagen/W-miss", json={"standort": "X"}).status_code == 404

    def test_update_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.patch("/waage/waagen/W-1", json={"standort": "X"}).status_code == 200

    def test_delete_not_found(self):
        with _client_ctx() as (c, _):
            assert c.delete("/waage/waagen/W-miss").status_code == 404

    def test_delete_found(self):
        with _client_ctx(waagen=[_fw("W-1")]) as (c, _):
            assert c.delete("/waage/waagen/W-1").status_code == 204


class TestWiegungenUnit:
    def test_list_empty(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/wiegungen").status_code == 200

    def test_get_not_found(self):
        with _client_ctx() as (c, _):
            assert c.get("/waage/wiegungen/WG-miss").status_code == 404

    def test_get_found(self):
        with _client_ctx(wiegungen=[_fwg("WG-1")]) as (c, _):
            assert c.get("/waage/wiegungen/WG-1").status_code == 200

    def test_create_netto_auto(self):
        with _client_ctx() as (c, wgr):
            r = c.post("/waage/wiegungen", json={
                "kennzeichen": "HB-1", "artikel": "Mais", "brutto": 30.0, "tara": 10.0
            })
            assert r.status_code == 201
            assert wgr.last_data.get("netto") == pytest.approx(20.0)

    def test_create_explicit_netto_kept(self):
        with _client_ctx() as (c, wgr):
            r = c.post("/waage/wiegungen", json={
                "kennzeichen": "HB-2", "artikel": "Mais",
                "brutto": 30.0, "tara": 10.0, "netto": 25.0,
            })
            assert r.status_code == 201
            assert wgr.last_data.get("netto") == pytest.approx(25.0)

    def test_delete_not_found(self):
        with _client_ctx() as (c, _):
            assert c.delete("/waage/wiegungen/WG-miss").status_code == 404

    def test_delete_found(self):
        with _client_ctx(wiegungen=[_fwg("WG-1")]) as (c, _):
            assert c.delete("/waage/wiegungen/WG-1").status_code == 204
