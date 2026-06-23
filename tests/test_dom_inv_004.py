"""DOM-INV-004 Unit Tests — LotTrace (.2), CountClose (.3), CorrectionStorno (.4)."""
from __future__ import annotations

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock


def _mock_db(sql_map: dict):
    """Dispatch db.execute() on SQL keywords → return values."""
    db = MagicMock()

    def side_effect(stmt, params=None):
        sql = str(stmt)
        m = MagicMock()
        for keyword, value in sql_map.items():
            if keyword in sql:
                if isinstance(value, list):
                    m.mappings.return_value.all.return_value = value
                    m.mappings.return_value.first.return_value = value[0] if value else None
                else:
                    m.mappings.return_value.first.return_value = value
                    m.mappings.return_value.all.return_value = [value] if value is not None else []
                return m
        m.mappings.return_value.first.return_value = None
        m.mappings.return_value.all.return_value = []
        return m

    db.execute.side_effect = side_effect
    return db


# ---------------------------------------------------------------------------
# Lot Trace Service
# ---------------------------------------------------------------------------

class TestLotTraceService:
    def test_create_lot_returns_id(self):
        from app.services.inventory_lot_trace_service import create_lot
        db = _mock_db({})
        result = create_lot(db, "t1", "article-1", "wh-1", "LOT-001", 1000.0)
        assert result["lot_number"] == "LOT-001"
        assert result["current_qty"] == 1000.0
        assert result["status"] == "AKTIV"
        db.commit.assert_called_once()

    def test_consume_lot_ok(self):
        from app.services.inventory_lot_trace_service import consume_lot
        lot_data = {
            "id": "lot-1", "tenant_id": "t1", "current_qty": 500.0,
            "mhd": date.today() + timedelta(days=30), "status": "AKTIV"
        }
        db = _mock_db({"inventory_lots": lot_data})
        result = consume_lot(db, "lot-1", "t1", 200.0)
        assert result["consumed_qty"] == 200.0
        assert result["remaining_qty"] == pytest.approx(300.0)
        assert result["status"] == "AKTIV"

    def test_consume_lot_exhausted(self):
        from app.services.inventory_lot_trace_service import consume_lot
        lot_data = {
            "id": "lot-1", "tenant_id": "t1", "current_qty": 100.0,
            "mhd": None, "status": "AKTIV"
        }
        db = _mock_db({"inventory_lots": lot_data})
        result = consume_lot(db, "lot-1", "t1", 100.0)
        assert result["status"] == "ERSCHÖPFT"

    def test_consume_overdrawn_raises(self):
        from app.services.inventory_lot_trace_service import consume_lot, LotTraceError
        lot_data = {
            "id": "lot-1", "tenant_id": "t1", "current_qty": 50.0,
            "mhd": None, "status": "AKTIV"
        }
        db = _mock_db({"inventory_lots": lot_data})
        with pytest.raises(LotTraceError, match="Unterdeckung"):
            consume_lot(db, "lot-1", "t1", 100.0)

    def test_consume_expired_mhd_raises(self):
        from app.services.inventory_lot_trace_service import consume_lot, LotTraceError
        lot_data = {
            "id": "lot-1", "tenant_id": "t1", "current_qty": 500.0,
            "mhd": date.today() - timedelta(days=1), "status": "AKTIV"
        }
        db = _mock_db({"inventory_lots": lot_data})
        with pytest.raises(LotTraceError, match="abgelaufen"):
            consume_lot(db, "lot-1", "t1", 100.0)

    def test_consume_missing_lot_raises(self):
        from app.services.inventory_lot_trace_service import consume_lot, LotTraceError
        db = _mock_db({"inventory_lots": None})
        with pytest.raises(LotTraceError, match="nicht gefunden"):
            consume_lot(db, "lot-missing", "t1", 50.0)


# ---------------------------------------------------------------------------
# Count Close Service
# ---------------------------------------------------------------------------

class TestCountCloseService:
    def test_differenz_buchen_creates_corrections(self):
        from app.services.inventory_count_close_service import differenz_buchen
        count_data = {"id": "cnt-1", "tenant_id": "t1", "status": "posted", "warehouse_id": "wh-1"}
        lines = [
            {"id": "line-1", "article_id": "art-1", "expected_quantity": 100.0, "counted_quantity": 90.0},
            {"id": "line-2", "article_id": "art-2", "expected_quantity": 50.0, "counted_quantity": 50.0},
        ]
        db = _mock_db({"inventory_counts": count_data, "inventory_count_lines": lines})
        result = differenz_buchen(db, "cnt-1", "t1")
        assert result["corrections_created"] == 1
        assert result["lines_skipped_idempotent"] == 0

    def test_differenz_buchen_wrong_status_raises(self):
        from app.services.inventory_count_close_service import differenz_buchen, CountCloseError
        count_data = {"id": "cnt-1", "tenant_id": "t1", "status": "draft", "warehouse_id": "wh-1"}
        db = _mock_db({"inventory_counts": count_data})
        with pytest.raises(CountCloseError, match="posted"):
            differenz_buchen(db, "cnt-1", "t1")

    def test_differenz_buchen_missing_count_raises(self):
        from app.services.inventory_count_close_service import differenz_buchen, CountCloseError
        db = _mock_db({"inventory_counts": None})
        with pytest.raises(CountCloseError, match="nicht gefunden"):
            differenz_buchen(db, "cnt-missing", "t1")


# ---------------------------------------------------------------------------
# Correction Storno Service
# ---------------------------------------------------------------------------

class TestCorrectionStornoService:
    def test_storno_creates_reversal(self):
        from app.services.inventory_correction_service import storno_korrektur
        orig = {
            "id": "corr-1", "tenant_id": "t1",
            "article_id": "art-1", "warehouse_id": "wh-1",
            "movement_type": "ABGANG", "quantity": 100.0, "unit": "kg",
            "reference_type": "KORREKTUR",
        }
        # differentiate SELECT by id vs SELECT by storno_ref
        db = MagicMock()
        def side_effect(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "storno_ref" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = None  # no existing storno
            elif "inventory_stock_movements" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = orig
            else:
                m.mappings.return_value.first.return_value = None
            return m
        db.execute.side_effect = side_effect
        result = storno_korrektur(db, "corr-1", "t1")
        assert result["movement_type"] == "ZUGANG"
        assert result["quantity"] == 100.0
        assert result["reference_type"] == "STORNO"
        assert result["idempotent"] is False

    def test_storno_idempotent(self):
        from app.services.inventory_correction_service import storno_korrektur
        orig = {
            "id": "corr-1", "tenant_id": "t1",
            "article_id": "art-1", "warehouse_id": "wh-1",
            "movement_type": "ABGANG", "quantity": 100.0, "unit": "kg",
            "reference_type": "KORREKTUR",
        }
        existing_storno = {
            "id": "storno-1", "storno_ref": "corr-1",
            "movement_type": "ZUGANG", "quantity": 100.0,
            "reference_type": "STORNO",
        }
        # First call returns orig, second (storno check) returns existing_storno
        call_count = [0]
        db = MagicMock()

        def side_effect(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            call_count[0] += 1
            if "WHERE id = :id" in sql and "storno_ref" not in sql:
                m.mappings.return_value.first.return_value = orig
            elif "storno_ref" in sql:
                m.mappings.return_value.first.return_value = existing_storno
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = side_effect
        result = storno_korrektur(db, "corr-1", "t1")
        assert result["idempotent"] is True
        assert result["id"] == "storno-1"
        db.commit.assert_not_called()

    def test_storno_of_storno_raises(self):
        from app.services.inventory_correction_service import storno_korrektur, CorrectionError
        storno_data = {
            "id": "storno-1", "tenant_id": "t1",
            "article_id": "art-1", "warehouse_id": "wh-1",
            "movement_type": "ZUGANG", "quantity": 100.0, "unit": "kg",
            "reference_type": "STORNO",
        }
        db = _mock_db({"inventory_stock_movements": storno_data})
        with pytest.raises(CorrectionError, match="selbst ein Storno"):
            storno_korrektur(db, "storno-1", "t1")
