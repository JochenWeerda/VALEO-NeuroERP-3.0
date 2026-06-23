"""Unit tests for WM-AGRI-QS-003."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.services.agri_qs_workflow_service import AgriQsWorkflowError, AgriQsWorkflowService


def _result(*, first=None, all_rows=None):
    result = MagicMock()
    result.mappings.return_value.first.return_value = first
    result.mappings.return_value.all.return_value = all_rows or []
    return result


@pytest.mark.unit
def test_qs_release_updates_lot_cells_and_records_event():
    db = MagicMock()
    lot = {
        "id": "lot-1",
        "virtual_lot_number": "VL-1",
        "source_ticket_id": "ticket-1",
        "article_id": "art-1",
        "quantity_tons": Decimal("5"),
        "status": "in_pruefung",
    }
    cell = {"id": "cell-1", "warehouse_id": "wh-1", "cell_code": "Z1"}
    db.execute.side_effect = [
        _result(first=lot),
        MagicMock(),
        MagicMock(),
        _result(all_rows=[cell]),
    ]
    with patch("app.services.agri_qs_workflow_service.SupplyChainEventService") as event_cls:
        event_cls.return_value.record.return_value = {"id": "event-1"}
        out = AgriQsWorkflowService(db, "tenant-a").change_lot_qs_status(
            lot_id="VL-1",
            target_status="frei",
            reason="Laborwerte innerhalb Spezifikation",
            operator="labor-user",
            sample_id="sample-1",
            analysis_id="analysis-1",
            gmp_evidence_id="gmp-1",
            vlog_evidence_id="vlog-1",
        )

    assert out["ok"] is True
    assert out["qs_status"] == "frei"
    assert out["lot_status"] == "active"
    assert out["linked_cell_count"] == 1
    update_lot_params = db.execute.call_args_list[1][0][1]
    assert update_lot_params["target_status"] == "active"
    update_cell_params = db.execute.call_args_list[3][0][1]
    assert update_cell_params["qs_status"] == "frei"
    event_kwargs = event_cls.return_value.record.call_args.kwargs
    assert event_kwargs["event_type"] == "qs_status_changed"
    assert event_kwargs["payload"]["analysis_id"] == "analysis-1"
    assert event_kwargs["payload"]["gmp_evidence_id"] == "gmp-1"
    db.commit.assert_called_once()


@pytest.mark.unit
def test_qs_release_requires_lab_evidence():
    with pytest.raises(AgriQsWorkflowError, match="Probe"):
        AgriQsWorkflowService(MagicMock(), "tenant-a").change_lot_qs_status(
            lot_id="lot-1",
            target_status="frei",
            reason="ok",
            operator="labor-user",
        )


@pytest.mark.unit
def test_qs_transition_rejects_invalid_status():
    with pytest.raises(AgriQsWorkflowError, match="qs_status"):
        AgriQsWorkflowService(MagicMock(), "tenant-a").change_lot_qs_status(
            lot_id="lot-1",
            target_status="unknown",
            reason="ok",
            operator="labor-user",
            sample_id="s",
        )


@pytest.mark.unit
def test_qs_block_requires_reason_and_operator():
    svc = AgriQsWorkflowService(MagicMock(), "tenant-a")
    with pytest.raises(AgriQsWorkflowError, match="Grund"):
        svc.change_lot_qs_status(lot_id="lot-1", target_status="gesperrt", reason="", operator="u")
    with pytest.raises(AgriQsWorkflowError, match="Bediener"):
        svc.change_lot_qs_status(lot_id="lot-1", target_status="gesperrt", reason="Sperre", operator="")


@pytest.mark.unit
def test_qs_worklist_returns_lots_and_cells():
    db = MagicMock()
    db.execute.side_effect = [
        _result(all_rows=[{
            "id": "lot-1",
            "virtual_lot_number": "VL-1",
            "article_id": "art-1",
            "quantity_tons": Decimal("2.5"),
            "status": "in_pruefung",
            "source_ticket_id": "ticket-1",
            "updated_at": None,
            "linked_cell_count": 1,
        }]),
        _result(all_rows=[{
            "id": "cell-1",
            "cell_code": "Z1",
            "name": "Zelle 1",
            "warehouse_id": "wh-1",
            "qs_status": "gesperrt",
            "current_lot_id": "lot-1",
            "current_material_id": "art-1",
            "current_stock_kg": Decimal("1000"),
            "updated_at": None,
            "virtual_lot_number": "VL-1",
        }]),
    ]
    out = AgriQsWorkflowService(db, "tenant-a").list_worklist(limit=10)
    assert out["summary"]["lot_count"] == 1
    assert out["summary"]["cell_count"] == 1
    assert out["lots"][0]["quantity_kg"] == 2500.0
    assert out["cells"][0]["qs_status"] == "gesperrt"


@pytest.mark.unit
def test_qs_release_suggest_with_ticket_and_inline_lab():
    db = MagicMock()
    lot = {
        "id": "lot-1",
        "virtual_lot_number": "VL-1",
        "source_ticket_id": "ticket-1",
        "article_id": "art-1",
        "quantity_tons": Decimal("5"),
        "status": "in_pruefung",
        "moisture_pct": Decimal("14.2"),
        "impurities_pct": Decimal("1.1"),
        "protein_pct": None,
    }
    db.execute.side_effect = [
        _result(first=lot),
        _result(all_rows=[]),
    ]
    out = AgriQsWorkflowService(db, "tenant-a").suggest_release("VL-1")
    assert out["production_release_allowed"] is True
    assert out["suggested"]["sampleId"] == "ticket-1"
    assert out["blockers"] == []


@pytest.mark.unit
def test_qs_release_suggest_blocks_without_evidence():
    db = MagicMock()
    lot = {
        "id": "lot-2",
        "virtual_lot_number": "VL-2",
        "source_ticket_id": None,
        "article_id": "art-2",
        "quantity_tons": Decimal("1"),
        "status": "in_pruefung",
        "moisture_pct": None,
        "impurities_pct": None,
        "protein_pct": None,
    }
    db.execute.side_effect = [
        _result(first=lot),
        _result(all_rows=[]),
    ]
    out = AgriQsWorkflowService(db, "tenant-a").suggest_release("VL-2")
    assert out["production_release_allowed"] is False
    assert any("Wiegeschein" in b for b in out["blockers"])
