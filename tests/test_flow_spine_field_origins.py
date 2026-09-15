"""FSX-001 — operative Felder gegen die deklarierte Herkunft, nicht gegen einen anderen Vorgang."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.core.flow_spine_registry import (
    OPERATIONAL_NODE_FIELDS,
    get_flow_spine_workspace,
    merge_instance_statuses,
)

pytestmark = pytest.mark.unit

ORIGINS_PATH = Path(__file__).resolve().parents[1] / "app/core/flow_spine_field_origins.yaml"
EVENT = {
    "created_at": "2026-09-15T08:11:00+00:00",
    "event_type": "hold_set",
    "actor_id": "user-hold",
    "reason_category": "logistics",
    "reason_code": "delivery_deadline_missed",
    "reason_note": "Spedition blockiert",
}


def _origins() -> dict:
    return yaml.safe_load(ORIGINS_PATH.read_text(encoding="utf-8"))


def _instance(**overrides: object) -> dict:
    base = {
        "instance_id": "11111111-1111-1111-1111-111111111111",
        "case_number": "WF-00042",
        "label": "Testvorgang",
        "entry_mode": "manual",
        "assigned_owner": "Innendienst",
        "business_status": "on_hold",
        "node_statuses": {},
        "process_key": "order-to-cash",
    }
    base.update(overrides)
    return base


def test_origin_map_covers_every_operational_field() -> None:
    origins = _origins()
    defaults = origins["defaults"]
    missing = [field for field in OPERATIONAL_NODE_FIELDS if field not in defaults]
    assert not missing, f"Herkunftskarte ohne Eintrag: {missing}"
    assert defaults["insight"]["undeclared"] is True
    assert defaults["status"]["source"] == "FlowSpineInstance.node_statuses[node_id]"
    assert origins["static_fields"]["footer_cards"] == "process_definition"


def test_timestamp_and_detail_rows_match_declared_event_source() -> None:
    origins = _origins()
    assert origins["defaults"]["timestamp"]["undeclared"] is False
    assert origins["defaults"]["detail_rows"]["undeclared"] is False

    merged = merge_instance_statuses(
        get_flow_spine_workspace("order-to-cash"),
        _instance(),
        node_events={"order": EVENT},
    )
    order = next(node for node in merged["nodes"] if node["id"] == "order")
    delivery = next(node for node in merged["nodes"] if node["id"] == "delivery")

    assert order["timestamp"] == EVENT["created_at"]
    rows = {row["label"]: row["value"] for row in order["detail_rows"]}
    assert rows["Aktion"] == EVENT["event_type"]
    assert rows["Akteur"] == EVENT["actor_id"]
    assert rows["Grundkategorie"] == EVENT["reason_category"]
    assert rows["Grund"] == EVENT["reason_code"]
    assert rows["Hinweis"] == EVENT["reason_note"]
    assert rows["Vorgang"] == "WF-00042"
    assert rows["Bearbeiter"] == "Innendienst"
    assert order["data_state"] == "instance"

    assert delivery["timestamp"] is None
    delivery_rows = {row["label"]: row["value"] for row in delivery["detail_rows"]}
    assert "Aktion" not in delivery_rows
    assert delivery_rows["Vorgang"] == "WF-00042"


@pytest.mark.parametrize("field", ("metric", "submetric", "kpis", "documents", "agent"))
def test_undeclared_fields_stay_empty(field: str) -> None:
    assert _origins()["defaults"][field]["undeclared"] is True
    merged = merge_instance_statuses(
        get_flow_spine_workspace("order-to-cash"),
        _instance(),
        node_events={"order": EVENT},
    )
    order = next(node for node in merged["nodes"] if node["id"] == "order")
    value = order[field]
    assert not value, f"{field} hat keine Quelle und muss im Instanzpfad leer bleiben, war {value!r}"
