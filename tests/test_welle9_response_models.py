"""SPEC-P1-06 Welle 9: Ops-Worklists (Produktion, Tank, Fremdware)."""

from datetime import date, datetime

import pytest

from app.api.v1.endpoints import foreign_goods_worklist as fg_module
from app.api.v1.endpoints import production_control as pc_module
from app.api.v1.endpoints import tank_adapter as tank_module
from app.api.v1.schemas import ops_worklist_bundle_schemas as ops

pytestmark = pytest.mark.unit

WELLE9_MODULE = [pc_module, tank_module, fg_module]


def _response_models(module):
    out = {}
    for route in module.router.routes:
        for method in getattr(route, "methods", []) or []:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize("module", WELLE9_MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_kein_endpunkt_mehr_schwach_typisiert(module):
    schwach = []
    for (path, method), model in _response_models(module).items():
        text = str(model)
        if (
            model is None
            or model in (dict, list)
            or "dict[str, Any]" in text
            or "list[dict" in text
        ):
            schwach.append(f"{method} {path}")
    assert not schwach, f"noch schwach typisiert: {schwach}"


def _assert_kein_feldverlust(model, data, label=None):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{label or model.__name__} verliert Felder: {fehlend}"
    return dumped


def test_production_register_page_summary_sync_transition_audit():
    _assert_kein_feldverlust(
        ops.ProductionRegisterOut,
        {"id": "op-1", "status": "queued", "duplicate": False},
    )
    _assert_kein_feldverlust(
        ops.ProductionRegisterOut,
        {"id": "op-1", "status": "running", "duplicate": True},
    )
    row = {
        "id": "op-1",
        "operation_type": "mill_run",
        "status": "queued",
        "source_type": "mischfutterauftrag",
        "source_ref": "src-1",
        "source_number": "CH-1",
        "source_route": "/produktion",
        "work_center": "Muehle-1",
        "article_ref": "A-1",
        "article_name": "Weizen",
        "batch_ref": "B-1",
        "quantity": 12.5,
        "unit": "t",
        "assigned_user": "u1",
        "planned_at": datetime(2026, 9, 1),
        "notes": None,
        "created_at": datetime(2026, 8, 1),
        "updated_at": datetime(2026, 8, 2),
    }
    _assert_kein_feldverlust(
        ops.ProductionOperationPageOut,
        {"items": [row], "total": 1, "page": 1, "page_size": 50},
    )
    _assert_kein_feldverlust(
        ops.ProductionSummaryOut,
        {
            "waiting": 1,
            "running": 0,
            "attention": 0,
            "completed": 2,
            "mill_runs": 1,
        },
    )
    _assert_kein_feldverlust(ops.ProductionSyncOut, {"synchronized": 3})
    _assert_kein_feldverlust(
        ops.ProductionTransitionOut, {"id": "op-1", "status": "released"}
    )
    _assert_kein_feldverlust(
        ops.ProductionAuditOut,
        {
            "action": "status_changed",
            "old_value": "queued",
            "new_value": "released",
            "actor": "u1",
            "reason": "Freigabe",
            "created_at": datetime(2026, 9, 1),
        },
    )


def test_tank_ingest_page_summary_validate_process_retry():
    _assert_kein_feldverlust(
        ops.TankIngestOut,
        {
            "id": "t1",
            "status": "received",
            "payload_hash": "abc",
            "idempotent": False,
        },
    )
    _assert_kein_feldverlust(
        ops.TankIngestOut,
        {"id": "t1", "status": "processed", "idempotent": True},
    )
    intake = {
        "id": "t1",
        "adapter_key": "shell",
        "external_id": "ext-1",
        "payload_hash": "abc",
        "status": "validated",
        "validation_errors": [],
        "rule_result": {"create_delivery_note": False, "reason": "internal_consumption"},
        "zapfung_id": None,
        "delivery_handover_id": None,
        "retry_count": 0,
        "received_at": datetime(2026, 9, 1),
        "processed_at": None,
        "updated_at": datetime(2026, 9, 1),
    }
    _assert_kein_feldverlust(
        ops.TankIntakePageOut,
        {"items": [intake], "total": 1, "page": 1, "page_size": 50},
    )
    _assert_kein_feldverlust(
        ops.TankSummaryOut,
        {
            "received": 1,
            "validated": 2,
            "error": 0,
            "processed": 3,
            "delivery_handover": 1,
        },
    )
    _assert_kein_feldverlust(
        ops.TankValidateOut,
        {
            "id": "t1",
            "status": "validated",
            "validation_errors": [],
            "rule_result": {
                "create_delivery_note": True,
                "reason": "billable_customer",
            },
        },
    )
    _assert_kein_feldverlust(
        ops.TankProcessOut,
        {
            "id": "t1",
            "status": "processed",
            "zapfung_id": "z1",
            "delivery_handover_id": "h1",
            "idempotent": False,
        },
    )
    _assert_kein_feldverlust(
        ops.TankRetryOut,
        {"id": "t1", "status": "received", "payload_hash": "def"},
    )


def test_foreign_goods_page_summary_transfer_complete():
    item = {
        "id": "fg-1",
        "tenant_id": "t1",
        "einlagerungs_nr": "FW-1",
        "eigentuemer_id": "K-1",
        "eigentuemer_name": "Hof Meyer",
        "warehouse_id": "L-1",
        "lagerort": "A-1",
        "artikel_nr": "ART-1",
        "artikel_bezeichnung": "Weizen",
        "charge": "C-1",
        "einlagerungstyp": "fremd",
        "menge_eingelagert": 10.0,
        "menge_aktuell": 8.0,
        "einheit": "t",
        "einlagerungsdatum": date(2026, 8, 1),
        "geplante_auslagerung": date(2026, 10, 1),
        "auslagerungsdatum": None,
        "gebuehr_pro_tag": 1.5,
        "gebuehr_einheit": "EUR",
        "status": "eingelagert",
        "notiz": None,
        "updated_at": datetime(2026, 9, 1),
        "source_route": "/lager/fremdware?focus=fg-1",
    }
    _assert_kein_feldverlust(
        ops.ForeignGoodsPageOut,
        {"items": [item], "total": 1, "page": 1, "page_size": 50},
    )
    _assert_kein_feldverlust(
        ops.ForeignGoodsSummaryOut,
        {
            "stored": 2,
            "partial": 1,
            "completed": 3,
            "owners": 2,
            "warehouses": 1,
        },
    )
    _assert_kein_feldverlust(
        ops.ForeignGoodsTransferOut,
        {
            "id": "fg-1",
            "status": "eingelagert",
            "warehouse_id": "L-2",
            "lagerort": "B-1",
        },
    )
    _assert_kein_feldverlust(
        ops.ForeignGoodsCompleteOut,
        {"id": "fg-1", "status": "ausgelagert", "menge_aktuell": 0.0},
    )
