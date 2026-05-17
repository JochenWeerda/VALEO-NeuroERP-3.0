"""
WMS FEFO-Picking + Lagerplatz-Hierarchie Tests
"""
from __future__ import annotations
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch, call
from datetime import date


# ── Helpers ────────────────────────────────────────────────────────────────

def make_service():
    from app.services.warehouse_service import WarehouseService
    db = MagicMock()
    return WarehouseService(db, "tenant-test")


def _row(**kwargs):
    """Einfache Namespace-Row für fetchall()-Mocks."""
    obj = MagicMock()
    obj._mapping = kwargs
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ── Zone + Bin CRUD ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_list_zones_filters_by_tenant():
    svc = make_service()
    svc.db.execute.return_value.fetchall.return_value = []
    result = svc.list_zones("wh-1")
    assert result == []
    call_args = svc.db.execute.call_args[0][1]
    assert call_args["tid"] == "tenant-test"
    assert call_args["wid"] == "wh-1"


@pytest.mark.unit
def test_create_zone_returns_id_and_payload():
    svc = make_service()
    result = svc.create_zone("wh-1", {"zone_code": "A", "name": "Zone A"})
    assert result["zone_code"] == "A"
    assert "id" in result
    svc.db.commit.assert_called_once()


@pytest.mark.unit
def test_create_bin_returns_id():
    svc = make_service()
    result = svc.create_bin("zone-1", "wh-1", {"bin_code": "A-01"})
    assert result["bin_code"] == "A-01"
    assert result["zone_id"] == "zone-1"
    assert result["warehouse_id"] == "wh-1"


# ── FEFO-Picking ───────────────────────────────────────────────────────────

@pytest.mark.unit
def test_fefo_pick_suggestion_respects_fefo_order():
    """FEFO: frühestes MHD zuerst."""
    svc = make_service()
    rows = [
        _row(bin_id="b1", bin_code="A-01", batch_number="CH1",
             best_before_date=date(2026, 6, 1), quantity_kg=Decimal("50")),
        _row(bin_id="b2", bin_code="A-02", batch_number="CH2",
             best_before_date=date(2026, 8, 1), quantity_kg=Decimal("100")),
    ]
    svc.db.execute.return_value.fetchall.return_value = rows

    result = svc.fefo_pick_suggestion("wh-1", "art-1", Decimal("70"))

    assert len(result) == 2
    assert result[0]["bin_id"] == "b1"
    assert result[0]["pick_kg"] == 50.0
    assert result[1]["bin_id"] == "b2"
    assert result[1]["pick_kg"] == 20.0


@pytest.mark.unit
def test_fefo_pick_suggestion_partial_coverage():
    """Wenn Gesamtbestand < Bedarf, liefert Teilmengen."""
    svc = make_service()
    rows = [
        _row(bin_id="b1", bin_code="A-01", batch_number=None,
             best_before_date=date(2026, 5, 1), quantity_kg=Decimal("30")),
    ]
    svc.db.execute.return_value.fetchall.return_value = rows

    result = svc.fefo_pick_suggestion("wh-1", "art-1", Decimal("100"))
    assert len(result) == 1
    assert result[0]["pick_kg"] == 30.0  # nur was da ist


@pytest.mark.unit
def test_fefo_pick_suggestion_exact_coverage():
    svc = make_service()
    rows = [
        _row(bin_id="b1", bin_code="A-01", batch_number="B1",
             best_before_date=date(2026, 7, 1), quantity_kg=Decimal("100")),
    ]
    svc.db.execute.return_value.fetchall.return_value = rows

    result = svc.fefo_pick_suggestion("wh-1", "art-1", Decimal("100"))
    assert result[0]["pick_kg"] == 100.0


# ── Bestandsbuchung ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_book_stock_movement_insert_new_position():
    svc = make_service()
    # kein bestehender Bestand
    svc.db.execute.return_value.fetchone.return_value = None

    mv_id = svc.book_stock_movement(
        bin_id="b1", article_id="art-1", batch_number="CH1",
        best_before_date=None, quantity_kg=Decimal("50"),
        unit_cost=Decimal("1.20"), movement_type="inbound",
    )
    assert mv_id is not None
    svc.db.commit.assert_called_once()


@pytest.mark.unit
def test_book_stock_movement_update_existing():
    svc = make_service()
    existing = MagicMock()
    existing.id = "stock-1"
    existing.quantity_kg = Decimal("100")
    svc.db.execute.return_value.fetchone.return_value = existing

    mv_id = svc.book_stock_movement(
        bin_id="b1", article_id="art-1", batch_number=None,
        best_before_date=None, quantity_kg=Decimal("30"),
        unit_cost=None, movement_type="inbound",
    )
    assert mv_id is not None


@pytest.mark.unit
def test_book_stock_movement_raises_on_understock():
    svc = make_service()
    existing = MagicMock()
    existing.id = "stock-1"
    existing.quantity_kg = Decimal("10")
    svc.db.execute.return_value.fetchone.return_value = existing

    with pytest.raises(ValueError, match="Unterdeckung"):
        svc.book_stock_movement(
            bin_id="b1", article_id="art-1", batch_number=None,
            best_before_date=None, quantity_kg=Decimal("-50"),
            unit_cost=None, movement_type="pick_out",
        )


@pytest.mark.unit
def test_book_stock_movement_raises_on_outbound_without_stock():
    svc = make_service()
    svc.db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError, match="ohne vorhandenen Bestand"):
        svc.book_stock_movement(
            bin_id="b1", article_id="art-1", batch_number=None,
            best_before_date=None, quantity_kg=Decimal("-10"),
            unit_cost=None, movement_type="pick_out",
        )


# ── Pick-Liste ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_confirm_pick_list_raises_if_not_found():
    svc = make_service()
    svc.db.execute.return_value.fetchone.return_value = None

    with pytest.raises(ValueError, match="not found"):
        svc.confirm_pick_list("pl-99", [])


@pytest.mark.unit
def test_confirm_pick_list_raises_if_already_completed():
    svc = make_service()
    pl = MagicMock()
    pl.status = "COMPLETED"
    pl.warehouse_id = "wh-1"
    svc.db.execute.return_value.fetchone.return_value = pl

    with pytest.raises(ValueError, match="bereits abgeschlossen"):
        svc.confirm_pick_list("pl-1", [])


# ── MHD-Ampel ──────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_mhd_alert_classifies_critical_and_warning():
    svc = make_service()
    rows = [
        _row(article_id="art-1", batch_number="B1",
             best_before_date=date(2026, 5, 18), total_qty=Decimal("20"),
             bin_codes="A-01", days_remaining=1),   # critical
        _row(article_id="art-2", batch_number="B2",
             best_before_date=date(2026, 6, 1), total_qty=Decimal("50"),
             bin_codes="B-02", days_remaining=15),  # warning
    ]
    svc.db.execute.return_value.fetchall.return_value = rows

    result = svc.get_mhd_alert("wh-1", days_warning=30, days_critical=7)

    assert result[0]["alert_level"] == "critical"
    assert result[1]["alert_level"] == "warning"


# ── Bin-to-Bin Transfer ────────────────────────────────────────────────────

@pytest.mark.unit
def test_transfer_bin_to_bin_calls_both_movements():
    svc = make_service()
    call_count = 0
    ids = ["mv-out-1", "mv-in-1"]

    def side_effect(*args, **kwargs):
        nonlocal call_count
        result = ids[call_count]
        call_count += 1
        return result

    svc.book_stock_movement = MagicMock(side_effect=side_effect)

    result = svc.transfer_bin_to_bin("b1", "b2", "art-1", None, Decimal("25"))

    assert result["from_movement_id"] == "mv-out-1"
    assert result["to_movement_id"] == "mv-in-1"
    assert result["quantity_kg"] == 25.0
    assert svc.book_stock_movement.call_count == 2


# ── Stock Valuation ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_stock_valuation_aggregates_correctly():
    svc = make_service()
    rows = [
        _row(article_id="art-1", batch_number="B1",
             total_qty=Decimal("100"), total_value=Decimal("120"),
             avg_cost=Decimal("1.20")),
    ]
    svc.db.execute.return_value.fetchall.return_value = rows

    result = svc.get_stock_valuation("wh-1")
    assert len(result) == 1
    assert result[0]["total_value_eur"] == 120.0
    assert result[0]["avg_cost_per_kg"] == 1.20
