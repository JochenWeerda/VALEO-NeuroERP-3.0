"""SPEC-P1-08 — FEFO-Pick berücksichtigt MHD vor Eingangsdatum."""
from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest


def _mock_db_fefo(lots: list[dict]):
    """Return lots on SELECT inventory_lots; support consume updates."""
    db = MagicMock()
    store = {lot["id"]: dict(lot) for lot in lots}

    def side_effect(stmt, params=None):
        sql = str(stmt)
        m = MagicMock()
        if "FROM domain_inventory.inventory_lots" in sql and "ORDER BY" in sql:
            sorted_lots = sorted(
                store.values(),
                key=lambda x: (x.get("mhd") is None, x.get("mhd") or date.max, x.get("created_at") or date.min),
            )
            active = [lot for lot in sorted_lots if lot.get("status") == "AKTIV" and float(lot.get("current_qty", 0)) > 0]
            m.mappings.return_value.all.return_value = active
            return m
        if "FROM domain_inventory.inventory_lots" in sql and "WHERE id" in sql:
            lot_id = (params or {}).get("id")
            lot = store.get(lot_id)
            m.mappings.return_value.first.return_value = lot
            return m
        if "UPDATE domain_inventory.inventory_lots" in sql:
            lot_id = (params or {}).get("id")
            if lot_id in store:
                store[lot_id]["current_qty"] = params.get("qty")
                store[lot_id]["status"] = params.get("status")
            return m
        if "INSERT INTO domain_inventory.inventory_lot_movements" in sql:
            return m
        m.mappings.return_value.first.return_value = None
        m.mappings.return_value.all.return_value = []
        return m

    db.execute.side_effect = side_effect
    return db, store


pytestmark = pytest.mark.unit


class TestSpecP108FefoPick:
    def test_pick_uses_earliest_mhd_first(self):
        from app.services.inventory_lot_trace_service import pick_lots_fefo

        today = date.today()
        lots = [
            {
                "id": "lot-late",
                "tenant_id": "t1",
                "article_id": "art-1",
                "warehouse_id": "wh-1",
                "current_qty": 100.0,
                "mhd": today + timedelta(days=60),
                "status": "AKTIV",
                "created_at": today - timedelta(days=30),
            },
            {
                "id": "lot-early-mhd",
                "tenant_id": "t1",
                "article_id": "art-1",
                "warehouse_id": "wh-1",
                "current_qty": 50.0,
                "mhd": today + timedelta(days=5),
                "status": "AKTIV",
                "created_at": today - timedelta(days=1),
            },
        ]
        db, store = _mock_db_fefo(lots)
        allocations = pick_lots_fefo(db, "t1", "art-1", "wh-1", 40.0)

        assert len(allocations) == 1
        assert allocations[0]["lot_id"] == "lot-early-mhd"
        assert allocations[0]["consumed_qty"] == 40.0

    def test_pick_spans_multiple_lots_in_fefo_order(self):
        from app.services.inventory_lot_trace_service import pick_lots_fefo

        today = date.today()
        lots = [
            {
                "id": "lot-a",
                "tenant_id": "t1",
                "article_id": "art-1",
                "warehouse_id": "wh-1",
                "current_qty": 30.0,
                "mhd": today + timedelta(days=10),
                "status": "AKTIV",
                "created_at": today,
            },
            {
                "id": "lot-b",
                "tenant_id": "t1",
                "article_id": "art-1",
                "warehouse_id": "wh-1",
                "current_qty": 30.0,
                "mhd": today + timedelta(days=20),
                "status": "AKTIV",
                "created_at": today,
            },
        ]
        db, _store = _mock_db_fefo(lots)
        allocations = pick_lots_fefo(db, "t1", "art-1", "wh-1", 50.0)

        assert [a["lot_id"] for a in allocations] == ["lot-a", "lot-b"]
        assert sum(a["consumed_qty"] for a in allocations) == pytest.approx(50.0)

    def test_list_lots_fefo_sql_orders_mhd_before_created_at(self):
        from app.services.inventory_lot_trace_service import list_lots_fefo

        today = date.today()
        lots = [
            {"id": "1", "mhd": today + timedelta(days=30), "created_at": today - timedelta(days=10), "status": "AKTIV", "tenant_id": "t1"},
            {"id": "2", "mhd": today + timedelta(days=5), "created_at": today, "status": "AKTIV", "tenant_id": "t1"},
        ]
        db = MagicMock()

        def side_effect(stmt, params=None):
            m = MagicMock()
            if "ORDER BY mhd ASC NULLS LAST, created_at ASC" in str(stmt):
                sorted_lots = sorted(lots, key=lambda x: (x["mhd"], x["created_at"]))
                m.mappings.return_value.all.return_value = sorted_lots
            else:
                m.mappings.return_value.all.return_value = []
            return m

        db.execute.side_effect = side_effect
        result = list_lots_fefo(db, "t1", article_id="art-1")
        assert [r["id"] for r in result] == ["2", "1"]
