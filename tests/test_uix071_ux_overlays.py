from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.ux_overlays import OverlayPut, delete_overlay, get_overlay, put_overlay


NOW = datetime(2026, 7, 7, 10, tzinfo=UTC)


class _Result:
    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self.rows = rows or []

    def mappings(self) -> "_Result":
        return self

    def first(self) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None


class _OverlayDb:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, str], dict[str, Any]] = {}
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        params = params or {}
        key = (params["tenant_id"], params["user_id"], params["screen_id"])
        if "SELECT screen_id, schema_version, overlay, updated_at" in sql:
            row = self.rows.get(key)
            return _Result([row] if row else [])
        if "INSERT INTO domain_shared.user_screen_overlays" in sql:
            overlay = params["overlay"]
            row = {
                "tenant_id": params["tenant_id"],
                "user_id": params["user_id"],
                "screen_id": params["screen_id"],
                "schema_version": params["schema_version"],
                "overlay": json.loads(overlay) if isinstance(overlay, str) else overlay,
                "updated_at": NOW,
            }
            self.rows[key] = row
            return _Result([row])
        if "DELETE FROM domain_shared.user_screen_overlays" in sql:
            self.rows.pop(key, None)
            return _Result([])
        return _Result([])

    def commit(self) -> None:
        self.commits += 1


def _request(user_id: str = "user-a"):
    return SimpleNamespace(headers={"X-User-ID": user_id})


def test_put_sanitizes_and_persists_allowed_overlay() -> None:
    db = _OverlayDb()
    result = asyncio.run(
        put_overlay(
            "finance/ar-open-item",
            OverlayPut(
                schema_version=1,
                overlay={
                    "density": "expertDense",
                    "tables": {
                        "op": {
                            "visibleColumns": ["kunde", "nr"],
                            "columnWidths": {"kunde": 240},
                            "activeVariant": "meine",
                            "customVariants": [{"key": "meine", "label": "Meine Sicht", "filters": {"status": "offen"}}],
                        },
                    },
                    "collapsedSections": ["doku"],
                },
            ),
            _request("user-a"),
            tenant_id="tenant-a",
            db=db,
        )
    )

    assert result.screen_id == "finance/ar-open-item"
    assert result.overlay["density"] == "expertDense"
    assert result.overlay["tables"]["op"]["visibleColumns"] == ["kunde", "nr"]
    assert ("tenant-a", "user-a", "finance/ar-open-item") in db.rows


def test_put_rejects_security_fields() -> None:
    db = _OverlayDb()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            put_overlay(
                "crm/customer-360",
                OverlayPut(
                    schema_version=1,
                    overlay={
                        "density": "compact",
                        "actions": [{"key": "delete"}],
                        "tables": {"t": {"dangerLevel": "safe"}},
                        "contextRailSections": [],
                    },
                ),
                _request("user-a"),
                tenant_id="tenant-a",
                db=db,
            )
        )

    assert exc.value.status_code == 400
    assert "actions" in exc.value.detail["violations"]
    assert "contextRailSections" in exc.value.detail["violations"]
    assert "tables.t.dangerLevel" in exc.value.detail["violations"]
    assert db.rows == {}


def test_get_and_delete_are_tenant_and_user_scoped() -> None:
    db = _OverlayDb()
    db.rows[("tenant-a", "user-a", "crm/customer-360")] = {
        "tenant_id": "tenant-a",
        "user_id": "user-a",
        "screen_id": "crm/customer-360",
        "schema_version": 1,
        "overlay": {"density": "compact"},
        "updated_at": NOW,
    }
    db.rows[("tenant-a", "user-b", "crm/customer-360")] = {
        "tenant_id": "tenant-a",
        "user_id": "user-b",
        "screen_id": "crm/customer-360",
        "schema_version": 1,
        "overlay": {"density": "expertDense"},
        "updated_at": NOW,
    }

    own = asyncio.run(get_overlay("crm/customer-360", _request("user-a"), tenant_id="tenant-a", db=db))
    other_tenant = asyncio.run(get_overlay("crm/customer-360", _request("user-a"), tenant_id="tenant-b", db=db))
    other_user = asyncio.run(get_overlay("crm/customer-360", _request("user-b"), tenant_id="tenant-a", db=db))
    reset = asyncio.run(delete_overlay("crm/customer-360", _request("user-a"), tenant_id="tenant-a", db=db))

    assert own.overlay == {"density": "compact"}
    assert other_tenant.overlay == {}
    assert other_user.overlay == {"density": "expertDense"}
    assert reset.status_code == 204
    assert ("tenant-a", "user-a", "crm/customer-360") not in db.rows
    assert ("tenant-a", "user-b", "crm/customer-360") in db.rows
