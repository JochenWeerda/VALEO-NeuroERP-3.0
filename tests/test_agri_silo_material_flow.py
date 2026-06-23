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


@pytest.mark.unit
def test_book_flush_charge_writes_movements_and_resets_flush_flag(mocker):
    """WM-AGRI-FLUSH-006: Spülcharge schreibt out+in Bewegungen und setzt flush_required zurueck."""
    mocker.patch("app.services.agri_material_flow_trace_integration.append_material_flow_supply_chain_event")
    mocker.patch("app.services.agri_material_flow_trace_integration.store_material_flow_outbox_best_effort")
    from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

    from_cell = _row(id="cell-a", cell_code="A1", current_stock_kg=0, current_material_id=None, current_lot_id=None)
    to_cell = _row(id="cell-b", cell_code="B1", current_stock_kg=0, current_material_id=None, current_lot_id=None)

    _no_node = MagicMock()
    _no_node.fetchone.return_value = None

    db = MagicMock()
    db.execute.side_effect = [
        _mk_result(fetchone=from_cell),   # from_cell
        _mk_result(fetchone=to_cell),     # to_cell
        _no_node,                         # from_node → None (kein Graph-Knoten)
        _no_node,                         # to_node → None
        MagicMock(),                      # INSERT out movement
        MagicMock(),                      # INSERT in movement
    ]
    db.commit = MagicMock()

    svc = AgriSiloMaterialFlowService(db, "tenant-x", trace_hooks_enabled=False)
    svc.validate_route = MagicMock(return_value={"ok": True, "warnings": [], "flush_required": False})

    result = svc.book_flush_charge(
        warehouse_id="wh-1",
        from_cell_id="cell-a",
        to_cell_id="cell-b",
        flush_material_id="art-flush",
        flush_quantity_kg=Decimal("200"),
        booked_by="operator",
    )

    assert result["ok"] is True
    assert result["flush_material_id"] == "art-flush"
    assert result["flush_quantity_kg"] == 200.0
    assert "move_out_id" in result
    assert "move_in_id" in result
    db.commit.assert_called_once()
    # 4 SELECT + 2 INSERT = mindestens 6 execute-Aufrufe
    assert db.execute.call_count >= 6


@pytest.mark.unit
def test_sync_lots_from_transfer_reduces_source_and_increases_dest():
    """sync_lots_from_transfer reduziert Quell-Lot und erhöht Ziel-Lot."""
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    from_cell = _row(legacy_silo_id="silo-a")
    to_cell = _row(legacy_silo_id="silo-b")
    src_lot = _row(id="lot-src", quantity_tons=Decimal("10"))
    dest_lot = _row(id="lot-dest", quantity_tons=Decimal("5"))

    _no_row = MagicMock()
    _no_row.fetchone.return_value = None

    db = MagicMock()
    db.execute.side_effect = [
        _mk_result(fetchone=from_cell),   # from_cell legacy_silo_id
        _mk_result(fetchone=to_cell),     # to_cell legacy_silo_id
        _mk_result(fetchone=src_lot),     # src lot by lot_id
        MagicMock(),                      # UPDATE src lot
        MagicMock(),                      # INSERT src movement 'out'
        _no_row,                          # dest lot by same lot_id → not found
        _mk_result(fetchone=dest_lot),    # dest lot by article_id
        MagicMock(),                      # UPDATE dest lot
        MagicMock(),                      # INSERT dest movement 'in'
    ]

    svc = AgriSiloLotLinkService(db, "tenant-x", trace_hooks_enabled=False)
    result = svc.sync_lots_from_transfer(
        from_cell_id="cell-a",
        to_cell_id="cell-b",
        quantity_kg=Decimal("2000"),  # 2 t
        lot_id="lot-src",
        article_id="art-1",
    )

    assert result["ok"] is True
    assert len(result["updated"]) == 2
    # Quell-UPDATE: neue Menge = 10 - 2 = 8 t
    src_update_params = db.execute.call_args_list[3][0][1]
    assert src_update_params["qty"] == pytest.approx(8.0)
    assert src_update_params["st"] == "active"
    # Ziel-UPDATE: neue Menge = 5 + 2 = 7 t
    dest_update_params = db.execute.call_args_list[7][0][1]
    assert dest_update_params["qty"] == pytest.approx(7.0)
    db.commit.assert_not_called()


@pytest.mark.unit
def test_sync_lots_from_transfer_closes_source_lot_when_empty():
    """sync_lots_from_transfer setzt status='closed' wenn Quell-Lot auf 0 fällt."""
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    from_cell = _row(legacy_silo_id="silo-a")
    to_cell = _row(legacy_silo_id=None)
    src_lot = _row(id="lot-src", quantity_tons=Decimal("2"))

    db = MagicMock()
    db.execute.side_effect = [
        _mk_result(fetchone=from_cell),
        _mk_result(fetchone=to_cell),
        _mk_result(fetchone=src_lot),
        MagicMock(),  # UPDATE
        MagicMock(),  # INSERT movement
    ]

    svc = AgriSiloLotLinkService(db, "tenant-x", trace_hooks_enabled=False)
    result = svc.sync_lots_from_transfer(
        from_cell_id="cell-a",
        to_cell_id="cell-b",
        quantity_kg=Decimal("2000"),
        lot_id="lot-src",
        article_id="art-1",
    )

    assert result["ok"] is True
    update_params = db.execute.call_args_list[3][0][1]
    assert update_params["qty"] == pytest.approx(0.0)
    assert update_params["st"] == "closed"


@pytest.mark.unit
def test_sync_lots_from_transfer_ok_false_without_silo_mapping():
    """sync_lots_from_transfer gibt ok=False wenn keine legacy_silo_id auf beiden Zellen."""
    from app.services.agri_silo_lot_link_service import AgriSiloLotLinkService

    db = MagicMock()
    db.execute.side_effect = [
        _mk_result(fetchone=_row(legacy_silo_id=None)),
        _mk_result(fetchone=_row(legacy_silo_id=None)),
    ]

    svc = AgriSiloLotLinkService(db, "tenant-x", trace_hooks_enabled=False)
    result = svc.sync_lots_from_transfer(
        from_cell_id="cell-a",
        to_cell_id="cell-b",
        quantity_kg=Decimal("500"),
        lot_id=None,
        article_id="art-1",
    )

    assert result["ok"] is False
    assert "reason" in result
    db.commit.assert_not_called()


@pytest.mark.unit
def test_transfer_commits_after_trace_hooks(mocker):
    """WMS-FLOW-001: Supply-Chain-Hooks müssen vor commit in derselben Transaktion landen."""
    append = mocker.patch(
        "app.services.agri_material_flow_trace_integration.append_material_flow_supply_chain_event",
    )
    mocker.patch(
        "app.services.agri_material_flow_trace_integration.store_material_flow_outbox_best_effort",
    )
    from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

    db = MagicMock()
    call_order: list[str] = []

    def _commit() -> None:
        call_order.append("commit")

    db.commit = _commit

    from_cell = _row(
        id="cell-a",
        cell_code="A1",
        current_stock_kg=500,
        current_material_id="art-1",
        current_lot_id="lot-1",
    )
    to_cell = _row(
        id="cell-b",
        cell_code="B1",
        current_stock_kg=0,
        current_material_id=None,
        current_lot_id=None,
    )
    db.execute.side_effect = [
        _mk_result(fetchone=from_cell),
        _mk_result(fetchone=to_cell),
        _mk_result(fetchone=None),
        _mk_result(fetchone=None),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]

    svc = AgriSiloMaterialFlowService(db, "tenant-x", trace_hooks_enabled=True)
    svc.validate_route = MagicMock(return_value={"ok": True, "warnings": [], "path": []})
    out = svc.book_material_transfer(
        warehouse_id="wh-1",
        from_cell_id="cell-a",
        to_cell_id="cell-b",
        quantity_kg=Decimal("100"),
        article_id="art-1",
        lot_id="lot-1",
    )
    assert out["ok"] is True
    append.assert_called_once()
    assert call_order == ["commit"]
