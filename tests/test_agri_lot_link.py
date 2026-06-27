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
def test_auto_book_lot_link_books_legacy_match_cell():
    """auto_book_lot_link_by_lot_id wählt Zelle mit legacy_silo_id-Match und bucht transaktional."""
    lot = _row(
        id="lot-auto",
        silo_id="silo-auto",
        virtual_lot_number="VL-AUTO",
        source_ticket_id="ticket-auto",
        article_id="art-auto",
        quantity_tons=Decimal("5"),
        status="active",
        silo_number="SA",
    )
    # Zelle mit passendem legacy_silo_id
    cell_match = _row(
        id="cell-match",
        warehouse_id="wh-auto",
        cell_code="M1",
        legacy_silo_id="silo-auto",
        capacity_kg=Decimal("20000"),
        current_stock_kg=Decimal("0"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
    )
    # Wiederverwendung der book_lot_to_cell-Mocks (lot, cell, existing=None, insert, update)
    lot2 = _row(
        id="lot-auto",
        silo_id="silo-auto",
        virtual_lot_number="VL-AUTO",
        source_ticket_id="ticket-auto",
        article_id="art-auto",
        quantity_tons=Decimal("5"),
        status="active",
        silo_number="SA",
    )
    cell2 = _row(
        id="cell-match",
        warehouse_id="wh-auto",
        cell_code="M1",
        capacity_kg=Decimal("20000"),
        current_stock_kg=Decimal("0"),
        current_material_id=None,
        current_lot_id=None,
        qs_status="frei",
        legacy_silo_id="silo-auto",
    )
    db = MagicMock()
    cells_result = MagicMock()
    cells_result.fetchall.return_value = [cell_match]
    # Reihenfolge: lot-resolve, cells-fetchall, dann book_lot_to_cell: lot, cell, existing=None, insert, update
    db.execute.side_effect = [
        _result(lot),
        cells_result,
        _result(lot2),
        _result(cell2),
        _result(None),  # existing movement = None → frische Buchung
        MagicMock(),   # INSERT
        MagicMock(),   # UPDATE cell
    ]

    svc = AgriLotLinkBookingService(db, "tenant-a", trace_hooks_enabled=False)
    out = svc.auto_book_lot_link_by_lot_id(lot_id="lot-auto")

    assert out["ok"] is True
    assert out["auto_booked"] is True
    assert out["cell_id"] == "cell-match"
    assert out["warehouse_id"] == "wh-auto"
    assert out["quantity_kg"] == 5000.0
    db.commit.assert_called_once()


@pytest.mark.unit
def test_auto_book_lot_link_returns_ok_false_when_no_cell_mapping():
    """auto_book_lot_link_by_lot_id gibt ok=False wenn kein legacy_silo_id-Mapping existiert."""
    lot = _row(
        id="lot-x",
        silo_id="silo-x",
        virtual_lot_number="VL-X",
        source_ticket_id=None,
        article_id="art-x",
        quantity_tons=Decimal("3"),
        status="active",
        silo_number="SX",
    )
    db = MagicMock()
    cells_result = MagicMock()
    cells_result.fetchall.return_value = []
    db.execute.side_effect = [_result(lot), cells_result]

    svc = AgriLotLinkBookingService(db, "tenant-a", trace_hooks_enabled=False)
    out = svc.auto_book_lot_link_by_lot_id(lot_id="lot-x")

    assert out["ok"] is False
    assert "reason" in out
    db.commit.assert_not_called()


@pytest.mark.unit
def test_auto_book_lot_link_returns_ok_false_for_missing_lot():
    """auto_book_lot_link_by_lot_id gibt ok=False für unbekanntes/inaktives Lot."""
    db = MagicMock()
    db.execute.return_value = _result(None)

    svc = AgriLotLinkBookingService(db, "tenant-a", trace_hooks_enabled=False)
    out = svc.auto_book_lot_link_by_lot_id(lot_id="lot-missing")

    assert out["ok"] is False
    assert "reason" in out
    db.commit.assert_not_called()


@pytest.mark.unit
def test_score_cell_for_lot_returns_none_for_gesperrt():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "gesperrt", "capacity_kg": "10000", "current_stock_kg": "0"}
    lot = {"id": "l1", "article_id": "art-1"}
    assert Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("100")) is None


def test_score_cell_for_lot_returns_none_for_material_conflict():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "frei", "current_material_id": "art-2", "current_lot_id": None, "capacity_kg": "10000", "current_stock_kg": "0", "legacy_silo_id": None}
    lot = {"id": "l1", "article_id": "art-1"}
    assert Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("100")) is None


def test_score_cell_for_lot_returns_none_for_lot_conflict():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "frei", "current_material_id": None, "current_lot_id": "other-lot", "capacity_kg": "10000", "current_stock_kg": "0", "legacy_silo_id": None}
    lot = {"id": "l1", "article_id": "art-1"}
    assert Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("100")) is None


def test_score_cell_for_lot_returns_none_for_capacity_overflow():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "frei", "current_material_id": None, "current_lot_id": None, "capacity_kg": "1000", "current_stock_kg": "900", "legacy_silo_id": None}
    lot = {"id": "l1", "article_id": "art-1"}
    assert Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("200")) is None


def test_score_cell_for_lot_boosts_legacy_silo_match():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "frei", "current_material_id": None, "current_lot_id": None, "capacity_kg": "10000", "current_stock_kg": "0", "legacy_silo_id": "silo-1"}
    lot = {"id": "l1", "article_id": "art-1"}
    score = Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("100"))
    assert score is not None
    assert score >= 100


def test_score_cell_for_lot_no_legacy_match():
    from app.services.agri_lot_link_booking_service import AgriLotLinkBookingService as Svc
    cell = {"qs_status": "frei", "current_material_id": None, "current_lot_id": None, "capacity_kg": "10000", "current_stock_kg": "0", "legacy_silo_id": "other-silo"}
    lot = {"id": "l1", "article_id": "art-1"}
    score = Svc._score_cell_for_lot(cell, lot, "silo-1", Decimal("100"))
    assert score is not None
    assert score < 100


def test_resolve_active_lot_raises_without_any_ref():
    svc = AgriLotLinkBookingService(MagicMock(), "t1", trace_hooks_enabled=False)
    with pytest.raises(ValueError, match="lot_id"):
        svc._resolve_active_lot(lot_id=None, ticket_ref=None, acceptance_ref=None)


def test_resolve_active_lot_by_lot_id():
    lot = _row(id="l1", silo_id="s1", virtual_lot_number="VL1", source_ticket_id="t1",
               article_id="art1", quantity_tons=Decimal("5"), status="active", silo_number="S1")
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = lot
    svc = AgriLotLinkBookingService(db, "t1", trace_hooks_enabled=False)
    result = svc._resolve_active_lot(lot_id="l1", ticket_ref=None, acceptance_ref=None)
    assert result["id"] == "l1"


def test_resolve_active_lot_not_found_raises():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    svc = AgriLotLinkBookingService(db, "t1", trace_hooks_enabled=False)
    with pytest.raises(ValueError, match="Kein aktives Silo-Lot"):
        svc._resolve_active_lot(lot_id="missing", ticket_ref=None, acceptance_ref=None)


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
