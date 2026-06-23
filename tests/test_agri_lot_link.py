"""Unit tests for WM-AGRI-LOT-LINK-001."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService


def _row(**kwargs):
    row = MagicMock()
    row._mapping = kwargs
    for key, value in kwargs.items():
        setattr(row, key, value)
    return row


def _result(row=None):
    result = MagicMock()
    result.fetchone.return_value = row
    return result


def _result_all(rows=None):
    result = MagicMock()
    result.fetchall.return_value = rows or []
    return result


def _svc_with_rows(*rows):
    db = MagicMock()
    db.execute.side_effect = [_result(row) for row in rows]
    return AgriLotLinkBookingService(db, "tenant-a", trace_hooks_enabled=False), db


@pytest.mark.unit
def test_book_lot_to_cell_updates_cell_and_writes_stock_movement():
    lot = _row(
        id="lot-1",
        silo_id="silo-1",
        virtual_lot_number="VL-1",
        source_ticket_id="ticket-1",
        article_id="art-1",
        quantity_tons=Decimal("12.5"),
        status="active",
        silo_number="S1",
    )
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="Z1",
        capacity_kg=Decimal("20000"),
        current_stock_kg=Decimal("1000"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
        legacy_silo_id=None,
    )
    svc, db = _svc_with_rows(lot, cell, None, None, None)

    out = svc.book_lot_to_cell(
        lot_id="lot-1",
        target_cell_id="cell-1",
        warehouse_id="wh-1",
        quantity_kg=Decimal("2500"),
        booked_by="waage",
        reference="WE-4711",
    )

    assert out["ok"] is True
    assert out["cell_stock_kg"] == 3500.0
    assert out["source_ticket_id"] == "ticket-1"
    assert db.execute.call_count == 5
    insert_params = db.execute.call_args_list[3][0][1]
    assert insert_params["article_id"] == "art-1"
    assert insert_params["quantity"] == 2500.0
    assert insert_params["weighing_ticket_id"] == "ticket-1"
    update_params = db.execute.call_args_list[4][0][1]
    assert update_params["stock"] == 3500.0
    assert update_params["legacy_silo_id"] == "silo-1"
    db.commit.assert_called_once()


@pytest.mark.unit
def test_book_lot_to_cell_rejects_capacity_overflow():
    lot = _row(
        id="lot-1",
        silo_id="silo-1",
        virtual_lot_number="VL-1",
        source_ticket_id=None,
        article_id="art-1",
        quantity_tons=Decimal("5"),
        status="active",
        silo_number="S1",
    )
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="Z1",
        capacity_kg=Decimal("1000"),
        current_stock_kg=Decimal("900"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
        legacy_silo_id=None,
    )
    svc, db = _svc_with_rows(lot, cell)

    with pytest.raises(ValueError, match="Kapazitaet"):
        svc.book_lot_to_cell(
            lot_id="lot-1",
            target_cell_id="cell-1",
            warehouse_id="wh-1",
            quantity_kg=Decimal("200"),
        )
    db.commit.assert_not_called()


@pytest.mark.unit
def test_book_lot_to_cell_rejects_material_conflict():
    lot = _row(
        id="lot-1",
        silo_id="silo-1",
        virtual_lot_number="VL-1",
        source_ticket_id=None,
        article_id="art-new",
        quantity_tons=Decimal("1"),
        status="active",
        silo_number="S1",
    )
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="Z1",
        capacity_kg=Decimal("10000"),
        current_stock_kg=Decimal("500"),
        current_material_id="art-old",
        current_lot_id=None,
        qs_status="frei",
        legacy_silo_id=None,
    )
    svc, db = _svc_with_rows(lot, cell)

    with pytest.raises(ValueError, match="Materialkonflikt"):
        svc.book_lot_to_cell(lot_id="lot-1", target_cell_id="cell-1", warehouse_id="wh-1")
    db.commit.assert_not_called()


@pytest.mark.unit
def test_book_lot_to_cell_is_idempotent_for_existing_reference():
    lot = _row(
        id="lot-1",
        silo_id="silo-1",
        virtual_lot_number="VL-1",
        source_ticket_id=None,
        article_id="art-1",
        quantity_tons=Decimal("1"),
        status="active",
        silo_number="S1",
    )
    cell = _row(
        id="cell-1",
        warehouse_id="wh-1",
        cell_code="Z1",
        capacity_kg=Decimal("10000"),
        current_stock_kg=Decimal("1000"),
        current_material_id="art-1",
        current_lot_id="lot-1",
        qs_status="frei",
        legacy_silo_id="silo-1",
    )
    existing = _row(id="mov-1")
    svc, db = _svc_with_rows(lot, cell, existing)

    out = svc.book_lot_to_cell(
        lot_id="lot-1",
        target_cell_id="cell-1",
        warehouse_id="wh-1",
        reference="WE-4711",
    )

    assert out["idempotent"] is True
    assert out["movement_id"] == "mov-1"
    assert db.execute.call_count == 3
    db.commit.assert_not_called()


@pytest.mark.unit
def test_suggest_lot_link_prefers_legacy_silo_match():
    lot = _row(
        id="lot-1",
        silo_id="silo-1",
        virtual_lot_number="VL-1",
        source_ticket_id="ticket-1",
        article_id="art-1",
        quantity_tons=Decimal("10"),
        status="active",
        silo_number="S1",
    )
    cell_legacy = _row(
        id="cell-a",
        cell_code="A1",
        legacy_silo_id="silo-1",
        capacity_kg=Decimal("50000"),
        current_stock_kg=Decimal("0"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
    )
    cell_other = _row(
        id="cell-b",
        cell_code="B1",
        legacy_silo_id=None,
        capacity_kg=Decimal("50000"),
        current_stock_kg=Decimal("0"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
    )
    db = MagicMock()
    cells_result = MagicMock()
    cells_result.fetchall.return_value = [cell_other, cell_legacy]
    db.execute.side_effect = [_result(lot), cells_result]

    svc = AgriLotLinkBookingService(db, "tenant-a", trace_hooks_enabled=False)
    out = svc.suggest_lot_link(warehouse_id="wh-1", lot_id="lot-1")

    assert out["ok"] is True
    assert out["suggested_cell_id"] == "cell-a"
    assert out["quantity_kg_available"] == 10000.0
    assert out["candidate_cells"][0]["cell_id"] == "cell-a"
    assert out["candidate_cells"][0]["legacy_match"] is True
