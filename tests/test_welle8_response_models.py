"""SPEC-P1-06 Welle 8: Inventur/Lots (DOM-INV-004) und Silo/Materialfluss."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.api.v1.endpoints import agri_silo_material_flow as silo_module
from app.api.v1.endpoints import inventory_operations as inv_module
from app.api.v1.schemas import inventory_lot_bundle_schemas as lots
from app.api.v1.schemas import silo_material_flow_schemas as flow

pytestmark = pytest.mark.unit

WELLE8_MODULE = [inv_module, silo_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize("module", WELLE8_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        text = str(model)
        if model in (dict, list) or "dict[str, Any]" in text or "list[dict" in text:
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


# -- Chargen / Lots ---------------------------------------------------------


LOT_ROW = {
    "id": "lot-1",
    "tenant_id": "system",
    "article_id": "art-1",
    "warehouse_id": "wh-1",
    "lot_number": "CH-2026-001",
    "mhd": date(2026, 12, 31),
    "initial_qty": Decimal("1000.000"),
    "current_qty": Decimal("750.000"),
    "unit": "kg",
    "status": "AKTIV",
    "created_at": datetime(2026, 8, 1, 10, 0),
    "herkunft": "Eigenanbau",
    "sperrgrund": None,
    "qs_status": "pending",
    "received_at": date(2026, 8, 1),
}


def test_lot_zeile_deckt_die_volle_ddl_ab():
    """GET /lager/lots liefert SELECT * - alle 15 Spalten muessen durchkommen."""
    dumped = _assert_kein_feldverlust(lots.InventoryLotOut, LOT_ROW)
    assert dumped["qs_status"] == "pending"
    assert dumped["herkunft"] == "Eigenanbau"


def test_lot_anlage_liefert_nur_ihre_teilmenge():
    """POST /lager/lots gibt zehn Felder zurueck; der Rest bleibt leer statt zu kippen."""
    angelegt = {
        "id": "lot-2",
        "tenant_id": "system",
        "article_id": "art-1",
        "warehouse_id": "wh-1",
        "lot_number": "CH-2026-002",
        "mhd": "2026-11-30",
        "initial_qty": 500.0,
        "current_qty": 500.0,
        "unit": "kg",
        "status": "AKTIV",
    }
    dumped = _assert_kein_feldverlust(lots.InventoryLotOut, angelegt, "Lot-Anlage")
    assert dumped["created_at"] is None
    assert dumped["received_at"] is None


def test_lot_verbrauch():
    dumped = _assert_kein_feldverlust(
        lots.LotConsumeOut,
        {"lot_id": "lot-1", "consumed_qty": 250.0, "remaining_qty": 500.0, "status": "AKTIV"},
    )
    assert dumped["remaining_qty"] == 500.0


# -- Inventurdifferenz und Storno -------------------------------------------


def test_inventur_differenz_zaehlt_idempotent_uebersprungene_zeilen():
    dumped = _assert_kein_feldverlust(
        lots.InventurDifferenzOut,
        {
            "count_id": "cnt-1",
            "corrections_created": 2,
            "lines_skipped_idempotent": 3,
            "correction_line_ids": ["l1", "l2"],
        },
    )
    assert dumped["lines_skipped_idempotent"] == 3


def test_storno_neu_und_idempotent_verlieren_kein_feld():
    """Der Endpunkt hat zwei Zweige mit sehr unterschiedlicher Feldmenge."""
    neu = {
        "id": "st-1",
        "storno_ref": "korr-1",
        "tenant_id": "system",
        "article_id": "art-1",
        "warehouse_id": "wh-1",
        "movement_type": "ABGANG",
        "quantity": 120.0,
        "source_document_type": "STORNO",
        "source_document_id": "korr-1",
        "previous_stock": 500.0,
        "new_stock": 380.0,
        "unit": "kg",
        "idempotent": False,
    }
    _assert_kein_feldverlust(lots.StornoKorrekturOut, neu, "Storno(neu)")

    # idempotenter Zweig: komplette Bewegungszeile aus der 35-Spalten-Tabelle
    bestand = dict(neu)
    bestand.update(
        {
            "idempotent": True,
            "unit_cost": Decimal("1.25"),
            "total_cost": Decimal("150.00"),
            "reference_number": "BEL-1",
            "movement_number": "BW-0001",
            "movement_date": date(2026, 8, 2),
            "movement_time": None,
            "notes": "Storno von korr-1",
            "warehouse_location": "H1",
            "charge": "CH-2026-001",
            "bin_id": "B-1",
            "booking_user": "u1",
            "auto_created": True,
            "linked_order_id": None,
            "ownership_type": "owned",
            "owner_partner_id": None,
            "agrar_contract_id": None,
            "weighing_ticket_id": None,
            "storage_fee_relevant": False,
            "storage_fee_start_date": None,
            "storage_fee_monthly_rate": None,
            "storage_fee_last_charged_until": None,
            "created_at": datetime(2026, 8, 2, 9, 0),
            "updated_at": None,
        }
    )
    dumped = _assert_kein_feldverlust(lots.StornoKorrekturOut, bestand, "Storno(idempotent)")
    assert dumped["idempotent"] is True
    assert dumped["ownership_type"] == "owned"


def test_storno_modell_kennt_keine_reference_type_spalte():
    """Regression: die Tabelle hat source_document_type, nicht reference_type."""
    assert "reference_type" not in lots.StornoKorrekturOut.model_fields
    assert "source_document_type" in lots.StornoKorrekturOut.model_fields


# -- Silo und Materialfluss -------------------------------------------------


def test_siloanlage_und_silozelle():
    _assert_kein_feldverlust(
        flow.SiloSystemOut,
        {
            "id": "sys-1",
            "warehouse_id": "wh-1",
            "system_code": "SILO-A",
            "name": "Silo Nord",
            "description": None,
            "tenant_id": "system",
            "is_active": True,
            "created_at": datetime(2026, 8, 1, 8, 0),
        },
    )
    dumped = _assert_kein_feldverlust(
        flow.SiloCellOut,
        {
            "id": "cell-1",
            "silo_system_id": "sys-1",
            "warehouse_id": "wh-1",
            "zone_id": None,
            "aisle_id": None,
            "bin_id": None,
            "cell_code": "A-01",
            "name": "Zelle A1",
            "capacity_kg": Decimal("50000.000"),
            "current_stock_kg": Decimal("12500.000"),
            "current_material_id": "art-1",
            "current_lot_id": "lot-1",
            "qs_status": "frei",
            "contamination_risk_class": "B",
            "tenant_id": "system",
            "is_active": True,
            "layout_x": Decimal("10.5"),
            "layout_y": Decimal("4.0"),
            "legacy_silo_id": "L3-SILO-7",
            "created_at": datetime(2026, 8, 1, 8, 0),
            "updated_at": None,
        },
    )
    assert dumped["legacy_silo_id"] == "L3-SILO-7"
    assert dumped["contamination_risk_class"] == "B"


def test_materialfluss_knoten_und_kante():
    _assert_kein_feldverlust(
        flow.MaterialFlowNodeOut,
        {
            "id": "n-1",
            "warehouse_id": "wh-1",
            "node_type": "silo_cell",
            "ref_type": "silo_cell",
            "ref_id": "cell-1",
            "code": "N-A01",
            "name": "Zelle A1",
            "status": "aktiv",
            "geo_lat": Decimal("53.1234"),
            "geo_lng": Decimal("7.4321"),
            "layout_x": Decimal("10.5"),
            "layout_y": Decimal("4.0"),
            "tenant_id": "system",
            "is_active": True,
            "created_at": datetime(2026, 8, 1, 8, 0),
        },
    )
    dumped = _assert_kein_feldverlust(
        flow.MaterialFlowEdgeOut,
        {
            "id": "e-1",
            "warehouse_id": "wh-1",
            "from_node_id": "n-1",
            "to_node_id": "n-2",
            "conveyor_type": "kettenfoerderer",
            "status": "aktiv",
            "contamination_guard_enabled": True,
            "flush_required": True,
            "max_capacity_kg_h": Decimal("40000.000"),
            "tenant_id": "system",
            "created_at": datetime(2026, 8, 1, 8, 0),
        },
    )
    assert dumped["flush_required"] is True
