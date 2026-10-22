"""Vertrag: KontrollWorklistParent-Shell fuer die gesamte Worklist-Familie (§2.4)."""

from __future__ import annotations

import pytest

from app.core.kontroll_worklist_parent import (
    KONTROLL_WORKLIST_LAYOUT_KEYS,
    build_document_control_variant,
    build_document_control_worklist,
    build_kontroll_worklist_screen,
    kontroll_queue_table,
)
from app.core.screen_definitions import get_screen_definition
from app.core.screen_definitions_kontrolle import KONTROLL_WORKLIST_SCREEN_IDS
from app.services.made_by_studio_gates import check_gate_b

DOCUMENT_CONTROL_FAMILY = (
    "auswertungen/beleg-kontrolle",
    "auswertungen/auftrags-kontrolle",
    "auswertungen/lieferschein-kontrolle",
    "abrechnung/eb-lieferschein-kontrolle",
)

SANCTIONS_SCREENS = (
    "auswertungen/sanktionspruefung-personal",
    "auswertungen/sanktionspruefung-kunden",
)

VARIANT_EXCEPTION_TYPES = {
    "auswertungen/auftrags-kontrolle": "open_purchase_order",
    "auswertungen/lieferschein-kontrolle": "uninvoiced_delivery_note",
    "abrechnung/eb-lieferschein-kontrolle": "missing_inbound_document",
}

SHARED_ROW_ACTION_KEYS = {"assign_me", "start_work", "resolve", "waive", "open_source"}


def _assert_kontroll_worklist_shell(screen: dict, *, screen_id: str) -> None:
    assert screen["mode"] == "list"
    assert screen["adapter"]["type"] == "native"
    assert screen["adapter"]["temporary"] is False
    assert screen["adapter"]["sourceId"] == screen_id
    layout = screen["layout"]
    assert layout["floorplan"] == KONTROLL_WORKLIST_LAYOUT_KEYS["floorplan"]
    assert layout["density"] == KONTROLL_WORKLIST_LAYOUT_KEYS["density"]
    assert layout["contextRail"] in {"audit", "none", "combined"}
    assert layout["tableProfile"] in {"financial", "audit", "inventory", "standard"}
    assert screen["performance"]["requiresVirtualTables"] is True
    assert screen["performance"]["requiresLazyTabs"] is False
    assert screen["agentContract"]["testSelectors"]["summaryArea"] == "[data-testid='mask-summary']"
    assert "workflow" not in screen or "phases" not in (screen.get("workflow") or {})
    assert "processRibbon" not in layout
    tables = screen["tables"]
    assert tables
    for table in tables:
        assert table.get("virtualized") is True
        assert table.get("rowHeight") == 44
    assert screen.get("noWorkflowReason") or screen.get("workflow")


@pytest.mark.parametrize("screen_id", KONTROLL_WORKLIST_SCREEN_IDS)
def test_kontroll_worklist_family_uses_parent_shell(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    _assert_kontroll_worklist_shell(screen, screen_id=screen_id)


@pytest.mark.parametrize("screen_id", DOCUMENT_CONTROL_FAMILY)
def test_document_control_family_shares_kontroll_shell(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    assert screen["layout"]["tableProfile"] == "financial"
    assert screen["layout"]["contextRail"] == "audit"
    assert screen.get("noWorkflowReason")
    assert "workflow" not in screen
    assert any(ds["key"] == "entity" for ds in screen["dataSources"])
    exceptions_ds = next(ds for ds in screen["dataSources"] if ds["key"] == "exceptions")
    assert "/api/v1/document-control/exceptions" in exceptions_ds["endpoint"]
    table = screen["tables"][0]
    assert table["key"] == "exceptions"
    assert table["rowRouteTemplate"] == "{source_route}"
    row_keys = {action["key"] for action in table["rowActions"]}
    assert row_keys == SHARED_ROW_ACTION_KEYS
    assert len(screen.get("summary") or []) >= 5


@pytest.mark.parametrize("screen_id", DOCUMENT_CONTROL_FAMILY[1:])
def test_document_control_variants_filter_exception_type(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None
    expected = VARIANT_EXCEPTION_TYPES[screen_id]
    exceptions_ds = next(ds for ds in screen["dataSources"] if ds["key"] == "exceptions")
    assert f"exception_type={expected}" in exceptions_ds["endpoint"]
    assert screen["agentContract"]["businessPurpose"] == screen["subtitle"]
    assert screen["agentContract"]["testSelectors"]["screenRoot"] == f"[data-testid='{screen_id.replace('/', '-')}']"


def test_beleg_kontrolle_parent_uses_unfiltered_exceptions_endpoint() -> None:
    screen = get_screen_definition("auswertungen/beleg-kontrolle")
    assert screen is not None
    exceptions_ds = next(ds for ds in screen["dataSources"] if ds["key"] == "exceptions")
    assert exceptions_ds["endpoint"] == "/api/v1/document-control/exceptions"
    assert screen["agentContract"]["testSelectors"]["screenRoot"] == "[data-testid='beleg-kontrolle']"


@pytest.mark.parametrize("screen_id", SANCTIONS_SCREENS)
def test_sanctions_children_use_kontroll_worklist_shell(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None
    assert screen["layout"]["tableProfile"] == "audit"
    assert screen["workflow"]["auditRequired"] is True
    assert screen["actions"][0]["key"] == "check"
    assert "scope=" in screen["dataSources"][0]["endpoint"]


def test_pruefkorb_uses_kontroll_worklist_parent() -> None:
    screen = get_screen_definition("finance/pruefkorb")
    assert screen is not None
    assert screen["layout"]["tableProfile"] == "financial"
    befunde = next(ds for ds in screen["dataSources"] if ds["key"] == "befunde")
    assert befunde["endpoint"] == "/api/v1/kontrolle/pruefkorb"
    table = screen["tables"][0]
    assert table["key"] == "befunde"
    action_keys = [action["key"] for action in table["rowActions"]]
    assert action_keys == ["pruefen", "open_source"]


def test_mde_inbox_lifted_via_kontrolle_registry() -> None:
    screen = get_screen_definition("schnittstelle/mde-inbox")
    assert screen is not None
    assert screen["workflow"]["nextActionKey"] == "process_pending"
    queue = next(ds for ds in screen["dataSources"] if ds["key"] == "queue")
    assert queue["endpoint"] == "/api/v1/mobile/sync-queue"


def test_produktionsleitstand_lifted_via_kontrolle_registry() -> None:
    screen = get_screen_definition("produktion/produktionsleitstand")
    assert screen is not None
    assert screen["layout"]["tableProfile"] == "inventory"
    assert screen["tables"][0]["key"] == "operations"


def test_parent_rejects_process_band_phases() -> None:
    with pytest.raises(ValueError, match="phases"):
        build_kontroll_worklist_screen(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            data_sources=[{"key": "q", "endpoint": "/api/v1/q"}],
            tables=[
                kontroll_queue_table(
                    table_key="q",
                    label="Q",
                    columns=[{"key": "id", "label": "Id", "width": 80}],
                    row_actions=[{"key": "open", "label": "Oeffnen"}],
                )
            ],
            workflow={"processKey": "x", "phases": [{"key": "a", "label": "A"}]},
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_parent_rejects_missing_workflow_metadata() -> None:
    with pytest.raises(ValueError, match="noWorkflowReason"):
        build_kontroll_worklist_screen(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            data_sources=[{"key": "q", "endpoint": "/api/v1/q"}],
            tables=[
                kontroll_queue_table(
                    table_key="q",
                    label="Q",
                    columns=[{"key": "id", "label": "Id", "width": 80}],
                    row_actions=[{"key": "open", "label": "Oeffnen"}],
                )
            ],
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_build_document_control_variant_matches_direct_builder() -> None:
    direct = build_document_control_worklist(
        screen_id="auswertungen/auftrags-kontrolle",
        title="Auftrags-Kontrolle",
        subtitle="Sub",
        exception_type="open_purchase_order",
    )
    via_variant = build_document_control_variant(
        screen_id="auswertungen/auftrags-kontrolle",
        title="Auftrags-Kontrolle",
        subtitle="Sub",
        exception_type="open_purchase_order",
    )
    assert direct == via_variant


def test_kontroll_worklist_screen_id_registry_complete() -> None:
    assert len(KONTROLL_WORKLIST_SCREEN_IDS) == len(set(KONTROLL_WORKLIST_SCREEN_IDS))
    assert len(KONTROLL_WORKLIST_SCREEN_IDS) >= 48  # Batch 8 + Legacy + parallele Batch-12-Erweiterung


@pytest.mark.parametrize("screen_id", KONTROLL_WORKLIST_SCREEN_IDS)
def test_kontroll_worklist_family_passes_gate_b(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    result = check_gate_b(screen)
    assert result.passed, f"{screen_id}: {result.issues}"


@pytest.mark.parametrize("screen_id", DOCUMENT_CONTROL_FAMILY)
def test_document_control_waive_declares_write_permission(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None
    row_actions = {action["key"]: action for action in screen["tables"][0]["rowActions"]}
    assert row_actions["waive"]["permission"] == "document_control.write"
