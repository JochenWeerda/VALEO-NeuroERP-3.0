"""Vertrag: StammObjectPageParent-Shell fuer Pilot-Children (UIX-STAMM-OBJECTPAGE-PARENT)."""

from __future__ import annotations

import pytest

from app.core.screen_definitions import get_screen_definition
from app.core.stamm_object_page_parent import build_stamm_object_page, stamm_entity_source, stamm_kopf_tab

PILOT_SCREENS = (
    "agrar/duenger",
    "agrar/saatgut",
    "einkauf/supplier",
    "finance/debitor",
    "finance/kreditor",
)

SHARED_LAYOUT_KEYS = {
    "floorplan": "objectPage",
    "sectionNavigation": "anchors",
    "columnNavigation": "single",
    "summaryPlacement": "header",
    "stickyHeader": True,
    "stickyFooter": True,
    "preferredMode": "desktopDense",
    "mobileMode": "mobileStack",
    "touchTargetPx": 44,
}

IDENTITY_BY_SCREEN = {
    "agrar/duenger": "artikelnummer",
    "agrar/saatgut": "artikelnummer",
    "einkauf/supplier": "lieferantennummer",
    "finance/debitor": "debitoren_nr",
    "finance/kreditor": "kreditoren_nr",
}


@pytest.mark.parametrize("screen_id", PILOT_SCREENS)
def test_pilot_children_share_stamm_object_page_shell(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    assert screen["mode"] == "detail"
    assert screen["adapter"]["type"] == "native"
    assert screen["adapter"]["temporary"] is False
    assert screen["identityField"] == IDENTITY_BY_SCREEN[screen_id]
    assert screen["tabs"][0]["key"] == "kopf"
    assert screen["tabs"][0]["lazy"] is False
    assert any(ds["key"] == "entity" for ds in screen["dataSources"])
    edit = next(action for action in screen["actions"] if action["key"] == "edit")
    assert edit["kind"] == "primary"
    assert edit["dangerLevel"] == "safe"
    assert "permission" in edit
    layout = screen["layout"]
    for key, value in SHARED_LAYOUT_KEYS.items():
        assert layout[key] == value, f"{screen_id}.layout.{key}"
    assert layout["density"] in {"compact", "expertDense"}
    assert layout["contextRail"] in {"none", "audit", "combined", "copilot", "workflow"}
    assert any(item.get("kind") == "identity" for item in screen.get("summary") or [])
    assert screen["agentContract"]["testSelectors"]["primaryAction"] == "[data-testid='action-edit']"
    assert screen.get("noWorkflowReason")


def test_supplier_keeps_secondary_bestellung_action() -> None:
    screen = get_screen_definition("einkauf/supplier")
    assert screen is not None
    keys = [action["key"] for action in screen["actions"]]
    assert keys[0] == "edit"
    assert "neue_bestellung" in keys
    assert screen["layout"]["density"] == "expertDense"
    assert screen["layout"]["contextRail"] == "combined"
    assert screen["summaryEndpoint"].endswith("/screen-summary")


def test_finance_children_use_audit_rail() -> None:
    for screen_id in ("finance/debitor", "finance/kreditor"):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        assert screen["layout"]["density"] == "expertDense"
        assert screen["layout"]["contextRail"] == "audit"
        assert screen["performance"]["requiresVirtualTables"] is True


def test_parent_rejects_missing_kopf_tab() -> None:
    with pytest.raises(ValueError, match="kopf"):
        build_stamm_object_page(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            identity_field="id",
            data_sources=[stamm_entity_source("/api/v1/x/{entity_id}")],
            tabs=[{"key": "other", "label": "X", "fields": []}],
            edit_permission="x.update",
            no_workflow_reason="test",
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_parent_rejects_missing_entity_source() -> None:
    with pytest.raises(ValueError, match="entity"):
        build_stamm_object_page(
            screen_id="x/y",
            domain="x",
            title="X",
            subtitle="Y",
            identity_field="id",
            data_sources=[{"key": "list", "endpoint": "/api/v1/x"}],
            tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}])],
            edit_permission="x.update",
            no_workflow_reason="test",
            business_purpose="test",
            example_prompts=["a"],
            test_id="x-y",
        )


def test_duenger_and_saatgut_keep_domain_tabs() -> None:
    duenger = get_screen_definition("agrar/duenger")
    saatgut = get_screen_definition("agrar/saatgut")
    assert duenger is not None and saatgut is not None
    assert [tab["key"] for tab in duenger["tabs"]] == ["kopf", "verwendung", "preise"]
    assert [tab["key"] for tab in saatgut["tabs"]] == ["kopf", "lagerbestaende", "vertraege"]
    assert duenger["layout"]["density"] == "compact"
    assert duenger["layout"]["contextRail"] == "none"
