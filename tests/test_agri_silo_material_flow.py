"""Unit-Tests AgriSiloMaterialFlowService (WM-AGRI-SILO-001)."""

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
    if fetchall is not None:
        m.fetchall.return_value = fetchall
    if fetchone is not None:
        m.fetchone.return_value = fetchone
    return m


def make_svc():
    from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

    db = MagicMock()
    return AgriSiloMaterialFlowService(db, "tenant-a", trace_hooks_enabled=False), db


@pytest.mark.unit
def test_list_silo_cells_passes_tenant():
    svc, db = make_svc()
    db.execute.return_value.fetchall.return_value = []
    svc.list_silo_cells("wh-1")
    params = db.execute.call_args[0][1]
    assert params["tid"] == "tenant-a"
    assert params["wid"] == "wh-1"


@pytest.mark.unit
def test_create_silo_cell_commits():
    svc, db = make_svc()
    sys_row = MagicMock()
    sys_row.warehouse_id = "wh-1"
    db.execute.side_effect = [
        _mk_result(fetchone=sys_row),
        MagicMock(),
    ]
    out = svc.create_silo_cell(
        "sys-1",
        "wh-1",
        {
            "cell_code": "Z1",
            "name": "Zelle 1",
            "capacity_kg": Decimal("1000"),
            "qs_status": "frei",
        },
    )
    assert out["cell_code"] == "Z1"
    assert "id" in out
    svc.db.commit.assert_called_once()


@pytest.mark.unit
def test_create_open_edge_rejects_blocked_target_node():
    svc, db = make_svc()
    n_from = _row(
        id="n1",
        warehouse_id="wh-1",
        status="active",
        ref_type=None,
        ref_id=None,
    )
    n_to = _row(
        id="n2",
        warehouse_id="wh-1",
        status="blocked",
        ref_type=None,
        ref_id=None,
    )
    db.execute.side_effect = [
        _mk_result(fetchone=n_from),
        _mk_result(fetchone=n_to),
        _mk_result(fetchone=n_to),
    ]
    with pytest.raises(ValueError, match="open"):
        svc.create_material_flow_edge(
            "wh-1",
            {
                "from_node_id": "n1",
                "to_node_id": "n2",
                "status": "open",
            },
        )
    svc.db.commit.assert_not_called()


@pytest.mark.unit
def test_create_open_edge_rejects_gesperrt_silo_cell_ref():
    svc, db = make_svc()
    n_from = _row(id="n1", warehouse_id="wh-1", status="active", ref_type=None, ref_id=None)
    n_to = _row(
        id="n2",
        warehouse_id="wh-1",
        status="active",
        ref_type="silo_cell",
        ref_id="cell-1",
    )
    cell_qs = MagicMock()
    cell_qs.qs_status = "gesperrt"
    db.execute.side_effect = [
        _mk_result(fetchone=n_from),
        _mk_result(fetchone=n_to),
        _mk_result(fetchone=n_to),
        _mk_result(fetchone=cell_qs),
    ]
    with pytest.raises(ValueError, match="gesperrt"):
        svc.create_material_flow_edge(
            "wh-1",
            {"from_node_id": "n1", "to_node_id": "n2", "status": "open"},
        )


@pytest.mark.unit
def test_patch_silo_cell_updates_qs():
    svc, db = make_svc()
    updated = _row(id="c1", cell_code="Z1", qs_status="in_pruefung", warehouse_id="wh-1")
    db.execute.return_value.fetchone.return_value = updated
    out = svc.patch_silo_cell("c1", "wh-1", {"qs_status": "in_pruefung"})
    assert out["qs_status"] == "in_pruefung"
    svc.db.commit.assert_called_once()
    params = db.execute.call_args[0][1]
    assert params["tid"] == "tenant-a"
    assert params["cid"] == "c1"


@pytest.mark.unit
def test_patch_silo_cell_updates_layout():
    svc, db = make_svc()
    updated = _row(id="c1", cell_code="Z1", layout_x=Decimal("120.5"), layout_y=Decimal("88"), warehouse_id="wh-1")
    db.execute.return_value.fetchone.return_value = updated
    out = svc.patch_silo_cell("c1", "wh-1", {"layout_x": Decimal("120.5"), "layout_y": Decimal("88")})
    assert out["layout_x"] == Decimal("120.5")
    svc.db.commit.assert_called_once()
    params = db.execute.call_args[0][1]
    assert params["layout_x"] == Decimal("120.5")
    assert params["layout_y"] == Decimal("88")


@pytest.mark.unit
def test_patch_silo_cell_rejects_invalid_qs():
    svc, db = make_svc()
    with pytest.raises(ValueError, match="qs_status"):
        svc.patch_silo_cell("c1", "wh-1", {"qs_status": "tot"})
    svc.db.commit.assert_not_called()


@pytest.mark.unit
def test_patch_silo_cell_not_found():
    svc, db = make_svc()
    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(ValueError, match="nicht gefunden"):
        svc.patch_silo_cell("missing", "wh-1", {"name": "Neu"})
    svc.db.commit.assert_not_called()


@pytest.mark.unit
def test_patch_silo_cell_requires_field():
    svc, db = make_svc()
    with pytest.raises(ValueError, match="Keine Felder"):
        svc.patch_silo_cell("c1", "wh-1", {})


@pytest.mark.unit
def test_validate_route_directed_only_follows_from_to():
    """Nur Kante b→a erlaubt keinen Weg a→b (gerichteter Graph)."""
    svc, db = make_svc()
    edge_wrong_way = _row(
        from_node_id="b",
        to_node_id="a",
        contamination_guard_enabled=False,
        flush_required=False,
        status="open",
    )
    db.execute.side_effect = [
        _mk_result(fetchall=[edge_wrong_way]),
    ]
    res = svc.validate_route("wh-1", "a", "b")
    assert res["ok"] is False
    assert "Keine" in res["reason"] or "offene" in res["reason"].lower()


@pytest.mark.unit
def test_validate_route_blocks_silo_cell_gesperrt():
    svc, db = make_svc()
    edge = _row(
        from_node_id="a",
        to_node_id="b",
        contamination_guard_enabled=False,
        flush_required=False,
        status="open",
    )
    na = _row(id="a", warehouse_id="wh-1", status="active", ref_type=None, ref_id=None, code="A")
    nb = _row(
        id="b",
        warehouse_id="wh-1",
        status="active",
        ref_type="silo_cell",
        ref_id="c1",
        code="B",
    )
    cell = MagicMock()
    cell.qs_status = "gesperrt"
    db.execute.side_effect = [
        _mk_result(fetchall=[edge]),
        _mk_result(fetchone=na),
        _mk_result(fetchone=nb),
        _mk_result(fetchone=cell),
    ]
    res = svc.validate_route("wh-1", "a", "b")
    assert res["ok"] is False
    assert "gesperrt" in res["reason"].lower()


@pytest.mark.unit
def test_validate_route_flush_warning_on_material_change_and_guard():
    svc, db = make_svc()
    edge = _row(
        from_node_id="a",
        to_node_id="b",
        contamination_guard_enabled=True,
        flush_required=False,
        status="open",
    )
    na = _row(id="a", warehouse_id="wh-1", status="active", ref_type=None, ref_id=None, code="A")
    nb = _row(id="b", warehouse_id="wh-1", status="active", ref_type=None, ref_id=None, code="B")
    db.execute.side_effect = [
        _mk_result(fetchall=[edge]),
        _mk_result(fetchone=na),
        _mk_result(fetchone=nb),
    ]
    res = svc.validate_route(
        "wh-1",
        "a",
        "b",
        material_id="m-new",
        previous_material_id="m-old",
    )
    assert res["ok"] is True
    assert res["flush_required"] is True
    assert any("Verschleppungsrisiko" in w for w in res["warnings"])


@pytest.mark.unit
def test_patch_material_flow_node_updates_status():
    svc, db = make_svc()
    updated = _row(id="n1", code="X", status="maintenance", warehouse_id="wh-1")
    db.execute.return_value.fetchone.return_value = updated
    out = svc.patch_material_flow_node("n1", "wh-1", {"status": "maintenance"})
    assert out["status"] == "maintenance"
    svc.db.commit.assert_called_once()


@pytest.mark.unit
def test_patch_material_flow_node_invalid_status():
    svc, db = make_svc()
    with pytest.raises(ValueError, match="Knoten-status"):
        svc.patch_material_flow_node("n1", "wh-1", {"status": "kaputt"})


@pytest.mark.unit
def test_patch_material_flow_edge_open_rejected_when_target_node_blocked():
    svc, db = make_svc()
    cur_edge = _row(
        id="e1",
        warehouse_id="wh-1",
        from_node_id="a",
        to_node_id="b",
        status="blocked",
    )
    n_to = _row(
        id="b",
        warehouse_id="wh-1",
        status="blocked",
        ref_type=None,
        ref_id=None,
        code="B",
    )
    db.execute.side_effect = [
        _mk_result(fetchone=cur_edge),
        _mk_result(fetchone=n_to),
    ]
    with pytest.raises(ValueError, match="open"):
        svc.patch_material_flow_edge("e1", "wh-1", {"status": "open"})
    svc.db.commit.assert_not_called()


@pytest.mark.unit
def test_patch_material_flow_edge_flush_only():
    svc, db = make_svc()
    cur_edge = _row(
        id="e1",
        warehouse_id="wh-1",
        from_node_id="a",
        to_node_id="b",
        status="open",
    )
    updated = _row(
        id="e1",
        warehouse_id="wh-1",
        from_node_id="a",
        to_node_id="b",
        status="open",
        flush_required=True,
    )
    db.execute.side_effect = [
        _mk_result(fetchone=cur_edge),
        _mk_result(fetchone=updated),
    ]
    out = svc.patch_material_flow_edge("e1", "wh-1", {"flush_required": True})
    assert out.get("flush_required") is True
    svc.db.commit.assert_called_once()


@pytest.mark.unit
def test_trace_hooks_invoke_integration_on_edge_create(mocker):
    append = mocker.patch(
        "app.services.agri_material_flow_trace_integration.append_material_flow_supply_chain_event",
    )
    outbox = mocker.patch(
        "app.services.agri_material_flow_trace_integration.store_material_flow_outbox_best_effort",
    )
    from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

    db = MagicMock()
    svc = AgriSiloMaterialFlowService(db, "tenant-x", trace_hooks_enabled=True)
    n_from = _row(
        id="n1",
        warehouse_id="wh-1",
        status="active",
        ref_type=None,
        ref_id=None,
    )
    n_to = _row(
        id="n2",
        warehouse_id="wh-1",
        status="active",
        ref_type=None,
        ref_id=None,
    )
    db.execute.side_effect = [
        _mk_result(fetchone=n_from),
        _mk_result(fetchone=n_to),
        _mk_result(fetchone=n_to),
        MagicMock(),
    ]
    svc.create_material_flow_edge(
        "wh-1",
        {"from_node_id": "n1", "to_node_id": "n2", "status": "open"},
    )
    append.assert_called_once()
    outbox.assert_called_once()
    svc.db.commit.assert_called_once()
