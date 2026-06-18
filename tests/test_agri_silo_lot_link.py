"""Unit-Tests AgriSiloLotLinkService (WM-AGRI-LOT-LINK)."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest


def _row(**kwargs):
    obj = MagicMock()
    obj._mapping = kwargs
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


def _mk_result(*, fetchall=None, fetchone=None):
    m = MagicMock()
    m.fetchall.return_value = fetchall if fetchall is not None else []
    m.fetchone.return_value = fetchone
    return m


@pytest.mark.unit
def test_sync_cell_from_lots_aggregates_active_lots(mocker):
    append = mocker.patch(
        "app.services.agri_silo_lot_link_service.append_material_flow_supply_chain_event",
    )
    mocker.patch(
        "app.services.agri_silo_lot_link_service.store_material_flow_outbox_best_effort",
    )
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    db = MagicMock()
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="A1",
        legacy_silo_id="silo-legacy",
        current_stock_kg=0,
        current_material_id=None,
        current_lot_id=None,
    )
    silo = _row(id="silo-legacy")
    lot_a = _row(
        id="lot-a",
        article_id="art-wheat",
        quantity_tons=Decimal("12.5"),
        virtual_lot_number="VL-001",
        created_at="2026-06-01",
    )
    lot_b = _row(
        id="lot-b",
        article_id="art-wheat",
        quantity_tons=Decimal("2.0"),
        virtual_lot_number="VL-002",
        created_at="2026-06-02",
    )
    db.execute.side_effect = [
        _mk_result(fetchone=cell),
        _mk_result(fetchone=silo),
        _mk_result(fetchall=[lot_a, lot_b]),
        MagicMock(),
    ]

    svc = AgriSiloLotLinkService(db, "tenant-1")
    out = svc.sync_cell_from_lots("cell-1", "wh-1", commit=False)

    assert out["ok"] is True
    assert out["active_lot_count"] == 2
    assert out["current_stock_kg"] == 14500.0
    assert out["current_lot_id"] == "lot-a"
    assert out["current_material_id"] == "art-wheat"
    append.assert_called_once()
    db.commit.assert_not_called()


@pytest.mark.unit
def test_sync_cell_from_lots_requires_legacy_mapping():
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    db = MagicMock()
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="A1",
        legacy_silo_id=None,
        current_stock_kg=0,
        current_material_id=None,
        current_lot_id=None,
    )
    db.execute.return_value = _mk_result(fetchone=cell)
    svc = AgriSiloLotLinkService(db, "tenant-1", trace_hooks_enabled=False)
    with pytest.raises(ValueError, match="legacy_silo_id"):
        svc.sync_cell_from_lots("cell-1", "wh-1")


@pytest.mark.unit
def test_sync_cells_for_legacy_silo_no_mapping_is_noop():
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    db = MagicMock()
    db.execute.return_value = _mk_result(fetchall=[])
    svc = AgriSiloLotLinkService(db, "tenant-1", trace_hooks_enabled=False)
    assert svc.sync_cells_for_legacy_silo("silo-x") == []
    db.commit.assert_not_called()
