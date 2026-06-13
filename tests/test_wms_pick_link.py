"""WMS-PICK-LINK-001 — Lieferschein → Kommissionierliste → Warenausgang.

Prüft:
1. create_pick_list_from_delivery_note schlägt fehl wenn LS nicht posted/printed
2. create_pick_list_from_delivery_note erzeugt Pick-Liste mit DELIVERY_NOTE-Referenz
3. Doppelt anlegen (gleicher LS) → ValueError (offene PL existiert)
4. confirm_pick_list setzt Lieferschein auf shipped wenn alle Linien DONE
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, call, patch

import pytest

from app.services.warehouse_service import WarehouseService

TENANT = "00000000-0000-0000-0000-000000000001"


def _svc(db: MagicMock) -> WarehouseService:
    return WarehouseService(db=db, tenant_id=TENANT)


def _row(**kwargs):
    """Erzeugt ein Mock-Row-Objekt mit Attribut-Zugriff."""
    obj = MagicMock()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ── Unit Tests (no DB) ───────────────────────────────────────────────────────


class TestCreatePickListFromDeliveryNote:
    def _db_with_dn(self, status: str, positions: list[dict] | None = None) -> MagicMock:
        db = MagicMock()
        dn_row = _row(id="LS-001", status=status, delivery_note_number="LS-2026-001")
        no_existing = None

        pos_rows = [
            _row(artikel_id=p["artikel_id"], menge=Decimal(str(p["menge"])), einheit=p.get("einheit", "t"))
            for p in (positions or [{"artikel_id": "ART-1", "menge": 10}])
        ]

        def execute_side(sql, params=None):
            sql_str = str(sql) if not isinstance(sql, str) else sql
            mock_result = MagicMock()
            if "delivery_notes" in sql_str and "SELECT" in sql_str:
                mock_result.fetchone.return_value = dn_row
            elif "pick_lists" in sql_str and "NOT IN" in sql_str:
                mock_result.fetchone.return_value = no_existing
            elif "delivery_note_positions" in sql_str:
                mock_result.fetchall.return_value = pos_rows
            elif "bin_stock" in sql_str:
                mock_result.fetchall.return_value = []
            else:
                mock_result.fetchone.return_value = None
                mock_result.fetchall.return_value = []
            return mock_result

        db.execute.side_effect = execute_side
        return db

    def test_raises_wenn_status_draft(self):
        db = self._db_with_dn("draft")
        svc = _svc(db)
        with pytest.raises(ValueError, match="gebucht oder gedruckt"):
            svc.create_pick_list_from_delivery_note("LS-001")

    def test_erzeugt_picklist_mit_delivery_note_referenz(self):
        db = self._db_with_dn("posted")
        svc = _svc(db)
        result = svc.create_pick_list_from_delivery_note("LS-001")
        assert result["delivery_note_id"] == "LS-001"
        assert result["delivery_note_number"] == "LS-2026-001"
        # Commit wurde aufgerufen
        db.commit.assert_called()

    def test_raises_bei_bereits_offener_picklist(self):
        db = MagicMock()
        dn_row = _row(id="LS-001", status="posted", delivery_note_number="LS-2026-001")
        existing_row = _row(id="PL-EXISTING")

        def execute_side(sql, params=None):
            sql_str = str(sql) if not isinstance(sql, str) else sql
            mock_result = MagicMock()
            if "delivery_notes" in sql_str and "SELECT" in sql_str:
                mock_result.fetchone.return_value = dn_row
            elif "pick_lists" in sql_str and "NOT IN" in sql_str:
                mock_result.fetchone.return_value = existing_row
            else:
                mock_result.fetchone.return_value = None
                mock_result.fetchall.return_value = []
            return mock_result

        db.execute.side_effect = execute_side
        svc = _svc(db)
        with pytest.raises(ValueError, match="existiert bereits"):
            svc.create_pick_list_from_delivery_note("LS-001")

    def test_raises_wenn_keine_artikel_positionen(self):
        db = self._db_with_dn("posted", positions=[])
        # Override positions to empty
        pos_calls = 0

        def execute_side(sql, params=None):
            nonlocal pos_calls
            sql_str = str(sql) if not isinstance(sql, str) else sql
            mock_result = MagicMock()
            if "delivery_notes" in sql_str and "SELECT" in sql_str:
                mock_result.fetchone.return_value = _row(
                    id="LS-001", status="posted", delivery_note_number="LS-2026-001"
                )
            elif "pick_lists" in sql_str and "NOT IN" in sql_str:
                mock_result.fetchone.return_value = None
            elif "delivery_note_positions" in sql_str:
                mock_result.fetchall.return_value = []
            else:
                mock_result.fetchone.return_value = None
                mock_result.fetchall.return_value = []
            return mock_result

        db.execute.side_effect = execute_side
        svc = _svc(db)
        with pytest.raises(ValueError, match="keine Positionen"):
            svc.create_pick_list_from_delivery_note("LS-001")


class TestConfirmPickListShipsDeliveryNote:
    def _db_for_confirm(self, pl_status: str = "OPEN", source_doc_type: str = "DELIVERY_NOTE") -> MagicMock:
        db = MagicMock()
        pl_row = _row(id="PL-001", status=pl_status, warehouse_id="WH-1")
        pl_meta_row = _row(source_doc_ref="LS-001", source_doc_type=source_doc_type)
        line_row = _row(
            id="LINE-1", bin_id="BIN-1", article_id="ART-1",
            batch_number=None, best_before_date=None,
            quantity_required=Decimal("10"), unit="t",
        )

        call_count = [0]

        def execute_side(sql, params=None):
            sql_str = str(sql) if not isinstance(sql, str) else sql
            mock_result = MagicMock()
            if "FROM domain_inventory.pick_lists" in sql_str and "WHERE id" in sql_str and "source_doc" not in sql_str:
                mock_result.fetchone.return_value = pl_row
            elif "source_doc_ref" in sql_str and "FROM domain_inventory.pick_lists" in sql_str:
                mock_result.fetchone.return_value = pl_meta_row
            elif "FROM domain_inventory.pick_list_lines WHERE id" in sql_str:
                mock_result.fetchone.return_value = line_row
            elif "FROM domain_inventory.pick_list_lines WHERE pick_list_id" in sql_str:
                mock_result.fetchall.return_value = [_row(status="DONE")]
            elif "FROM domain_inventory.bin_stock" in sql_str:
                mock_result.fetchone.return_value = _row(quantity_kg=Decimal("100"))
                mock_result.fetchall.return_value = [_row(quantity_kg=Decimal("100"))]
            else:
                mock_result.fetchone.return_value = None
                mock_result.fetchall.return_value = []
            return mock_result

        db.execute.side_effect = execute_side
        return db

    def test_setzt_delivery_note_auf_shipped_wenn_abgeschlossen(self):
        db = self._db_for_confirm()
        svc = _svc(db)
        result = svc.confirm_pick_list("PL-001", [{"line_id": "LINE-1", "quantity_picked": 10}])
        assert result["status"] == "COMPLETED"
        # Prüfen: UPDATE delivery_notes SET status = 'shipped' wurde aufgerufen
        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        assert any("delivery_notes" in s and "shipped" in s for s in update_calls), (
            "Lieferschein wurde nicht auf shipped gesetzt"
        )

    def test_kein_delivery_note_update_bei_anderem_doc_type(self):
        db = self._db_for_confirm(source_doc_type="MANUAL")
        svc = _svc(db)
        svc.confirm_pick_list("PL-001", [{"line_id": "LINE-1", "quantity_picked": 10}])
        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        assert not any("delivery_notes" in s and "shipped" in s for s in update_calls), (
            "MANUAL-PickList darf keine Delivery-Note updaten"
        )
