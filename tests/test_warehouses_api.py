"""
COV-INV-002: Tests for Warehouses API endpoints.

Covers /api/v1/warehouses — list, get, 404, Superglue carrier rollout.
Unit-Tests: Paginierungslogik, Superglue-Rollout-Contract (kein DB).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints import warehouses as wh_mod
from app.core.database import get_db

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestWarehousesList:
    """GET /warehouses/"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_list_with_pagination(self):
        r = client.get("/api/v1/warehouses/?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_search(self):
        r = client.get("/api/v1/warehouses/?search=Haupt", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_with_tenant_filter(self):
        r = client.get("/api/v1/warehouses/?tenant_id=test-tenant", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestWarehouseDetail:
    """GET /warehouses/{warehouse_id}"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/warehouses/NONEXISTENT-WH-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestSuperglueCarrierRollout:
    """GET /warehouses/integrations/superglue/carrier-rollout"""

    def test_returns_rollout_structure(self):
        r = client.get(
            "/api/v1/warehouses/integrations/superglue/carrier-rollout",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert data["provider_key"] == "superglue"
        assert data["domain_key"] == "logistics"
        assert "rollout" in data

    def test_with_tenant_param(self):
        r = client.get(
            "/api/v1/warehouses/integrations/superglue/carrier-rollout?tenant_id=test-tenant",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert data["tenant_id"] == "test-tenant"


# ---------------------------------------------------------------------------
# Unit-Tests (kein DB)
# ---------------------------------------------------------------------------

def _make_warehouse_mock(wh_id: str = "WH-1", code: str = "HBL", name: str = "Halle A") -> MagicMock:
    m = MagicMock()
    m.id = wh_id
    m.warehouse_code = code
    m.name = name
    m.tenant_id = "unit"
    m.is_active = True
    m.address = ""
    m.city = "Bremen"
    m.postal_code = "28195"
    m.country = "DE"
    m.contact_person = None
    m.phone = None
    m.email = None
    m.warehouse_type = "standard"
    m.total_capacity = None
    m.used_capacity = 0
    m.created_at = None
    m.updated_at = None
    m.deleted_at = None
    return m


class _FakeQuery:
    def __init__(self, items):
        self._items = list(items)

    def filter(self, *_a, **_kw):
        return self

    def ilike(self, *_a):
        return True

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
    def __init__(self, items=None):
        self._items = list(items or [])

    def query(self, _model):
        return _FakeQuery(self._items)


class TestWarehouseUnitPagination:
    def _client(self, items=None):
        from app.api.v1.endpoints.warehouses import router as wh_router
        from app.api.v1.schemas.inventory import Warehouse

        _app = FastAPI()
        _app.include_router(wh_router, prefix="/warehouses")
        db = _FakeDb(items)
        _app.dependency_overrides[get_db] = lambda: db

        # Patch model_validate to return a minimal Warehouse
        def _mv(item):
            return Warehouse(
                id=item.id,
                tenant_id=item.tenant_id,
                warehouse_code=item.warehouse_code,
                name=item.name,
                used_capacity=0,
            )

        with patch.object(Warehouse, "model_validate", side_effect=_mv):
            return TestClient(_app)

    def test_empty_returns_paginated_zero(self):
        c = self._client()
        r = c.get("/warehouses/")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["pages"] == 1

    def test_pagination_fields(self):
        items = [_make_warehouse_mock(f"WH-{i}") for i in range(3)]
        c = self._client(items)
        r = c.get("/warehouses/?limit=2")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 3
        assert data["size"] == 2

    def test_not_found_404(self):
        c = self._client()
        r = c.get("/warehouses/WH-missing")
        assert r.status_code == 404


class TestSuperglueRolloutUnit:
    def test_rollout_structure_without_db(self):
        from app.api.v1.endpoints.warehouses import router as wh_router

        _app = FastAPI()
        _app.include_router(wh_router, prefix="/warehouses")
        _app.dependency_overrides[get_db] = lambda: _FakeDb()
        c = TestClient(_app)

        r = c.get("/warehouses/integrations/superglue/carrier-rollout")
        assert r.status_code == 200
        data = r.json()
        assert data["provider_key"] == "superglue"
        assert data["domain_key"] == "logistics"
        assert data["schema_version"] == 1
        assert "rollout" in data

    def test_tenant_param_reflected(self):
        from app.api.v1.endpoints.warehouses import router as wh_router

        _app = FastAPI()
        _app.include_router(wh_router, prefix="/warehouses")
        _app.dependency_overrides[get_db] = lambda: _FakeDb()
        c = TestClient(_app)

        r = c.get("/warehouses/integrations/superglue/carrier-rollout?tenant_id=my-tenant")
        assert r.json()["tenant_id"] == "my-tenant"


class TestWarehouseCrudUnit:
    def test_create_update_delete_and_conflict_paths(self):
        import asyncio
        from fastapi import HTTPException
        from app.api.v1.endpoints.warehouses import create_warehouse, delete_warehouse, update_warehouse
        from app.api.v1.schemas.inventory import Warehouse, WarehouseCreate, WarehouseUpdate

        created_items: list = []

        class _CrudDb(_FakeDb):
            def __init__(self, first_item=None):
                super().__init__([first_item] if first_item else [])
                self.added = None
                self.commit_count = 0

            def add(self, item):
                self.added = item
                created_items.append(item)

            def commit(self):
                self.commit_count += 1

            def refresh(self, _item):
                return None

        def _mv(item):
            return Warehouse(
                id=item.id,
                tenant_id=item.tenant_id,
                warehouse_code=item.warehouse_code,
                name=item.name,
                used_capacity=getattr(item, "used_capacity", 0) or 0,
            )

        payload = WarehouseCreate(warehouse_code="WH-NEW", name="Neu", tenant_id="unit")
        with patch.object(Warehouse, "model_validate", side_effect=_mv):
            db = _CrudDb()
            result = asyncio.run(create_warehouse(payload=payload, db=db))
            assert result.warehouse_code == "WH-NEW"
            assert db.commit_count == 1

            existing = _make_warehouse_mock("WH-1", "WH-NEW", "Neu")
            with pytest.raises(HTTPException) as conflict:
                asyncio.run(create_warehouse(payload=payload, db=_CrudDb(existing)))
            assert conflict.value.status_code == 409

            existing.name = "Alt"
            updated = asyncio.run(update_warehouse("WH-1", WarehouseUpdate(name="Aktualisiert"), db=_CrudDb(existing)))
            assert updated.name == "Aktualisiert"

            delete_db = _CrudDb(existing)
            asyncio.run(delete_warehouse("WH-1", db=delete_db))
            assert existing.is_active is False
            assert delete_db.commit_count == 1

            with pytest.raises(HTTPException) as missing:
                asyncio.run(update_warehouse("missing", WarehouseUpdate(name="X"), db=_CrudDb()))
            assert missing.value.status_code == 404
