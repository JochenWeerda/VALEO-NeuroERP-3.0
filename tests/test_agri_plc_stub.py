"""Tests fuer WM-AGRI-PLC-005 — PLC/OPC-UA Stub."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints.agri_plc_stub import (
    AgriPlcService,
    PlcDataPoint,
    PlcDeviceStatusIn,
    PlcIngestIn,
    PlcSiloLevelIn,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_svc(fetchone_result=None):
    db = MagicMock()
    result = MagicMock()
    result.fetchone.return_value = fetchone_result
    db.execute.return_value = result
    return AgriPlcService(db, "t1"), db


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_ingest_good_quality_counts_processed():
    svc, _ = _make_svc()
    payload = PlcIngestIn(
        device_id="plc-01",
        warehouse_id="wh1",
        data_points=[
            PlcDataPoint(node_id="ns=2;s=Silo1.Fuellstand", tag="silo1.level_pct", value=72.5, quality="good"),
            PlcDataPoint(node_id="ns=2;s=Silo1.Temp", tag="silo1.temp", value=18.3, unit="°C", quality="good"),
        ],
    )
    r = svc.ingest_data_points(payload)
    assert r["ok"] is True
    assert r["processed"] == 2
    assert r["skipped_bad_quality"] == 0


@pytest.mark.unit
def test_ingest_bad_quality_counted_as_skipped():
    svc, _ = _make_svc()
    payload = PlcIngestIn(
        device_id="plc-02",
        data_points=[
            PlcDataPoint(node_id="ns=2;s=X", tag="x.val", value=0.0, quality="bad"),
            PlcDataPoint(node_id="ns=2;s=Y", tag="y.val", value=1.0, quality="good"),
        ],
    )
    r = svc.ingest_data_points(payload)
    assert r["received"] == 2
    assert r["processed"] == 1
    assert r["skipped_bad_quality"] == 1


@pytest.mark.unit
def test_update_silo_level_writes_stock_and_returns_pct():
    cell_row = MagicMock()
    cell_row.capacity_kg = 1000
    cell_row.cell_code = "S-01"
    cell_row.qs_status = "frei"

    svc, db = _make_svc(fetchone_result=cell_row)

    payload = PlcSiloLevelIn(
        warehouse_id="wh1",
        cell_id="cell-abc",
        level_pct=50.0,
    )
    r = svc.update_silo_level(payload)
    assert r["ok"] is True
    assert r["level_pct"] == 50.0
    assert r["estimated_stock_kg"] == 500.0
    assert r["cell_code"] == "S-01"
    db.commit.assert_called_once()


@pytest.mark.unit
def test_update_silo_level_raises_for_unknown_cell():
    svc, _ = _make_svc(fetchone_result=None)
    with pytest.raises(ValueError, match="nicht gefunden"):
        svc.update_silo_level(PlcSiloLevelIn(warehouse_id="wh1", cell_id="unknown", level_pct=10.0))


@pytest.mark.unit
def test_device_status_returns_ok():
    svc, _ = _make_svc()
    payload = PlcDeviceStatusIn(device_id="plc-01", status="online", uptime_seconds=3600)
    r = svc.update_device_status(payload)
    assert r["ok"] is True
    assert r["status"] == "online"
