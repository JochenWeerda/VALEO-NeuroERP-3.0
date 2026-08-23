"""Contracts for the vendor-neutral L3 habit bridge reference screens."""

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition


def _action(screen: dict, key: str) -> dict:
    return next(action for action in screen["actions"] if action["key"] == key)


def _assert_ready(screen: dict) -> None:
    report = _check_readiness(screen)
    assert report["generatorReady"] is True, report["errors"]


def test_article_stock_uses_dense_record_work_pattern() -> None:
    screen = get_screen_definition("lager/article-stock")
    assert screen is not None
    assert screen["layout"] | {
        "floorplan": "objectPage",
        "density": "expertDense",
        "summaryPlacement": "header",
        "stickyHeader": True,
        "stickyFooter": True,
    } == screen["layout"]
    assert screen["interaction"]["enterMovesFocus"] is True
    assert _action(screen, "edit")["zone"] == "commit"
    _assert_ready(screen)


def test_customer_360_keeps_customer_actions_in_familiar_footer_zones() -> None:
    screen = get_screen_definition("crm/customer-360")
    assert screen is not None
    assert screen["layout"]["stickyHeader"] is True
    assert screen["layout"]["stickyFooter"] is True
    assert _action(screen, "create_activity")["zone"] == "footer"
    assert _action(screen, "edit")["zone"] == "commit"
    _assert_ready(screen)


def test_delivery_note_places_totals_after_positions_and_print_in_footer() -> None:
    screen = get_screen_definition("sales/delivery-note")
    assert screen is not None
    assert screen["layout"]["floorplan"] == "transaction"
    assert screen["layout"]["summaryPlacement"] == "footer"
    assert screen["interaction"]["enterMovesFocus"] is True
    assert _action(screen, "drucken") | {
        "zone": "footer",
        "keyboardShortcut": "Ctrl+P",
    } == _action(screen, "drucken")
    _assert_ready(screen)


def test_readiness_rejects_duplicate_shortcuts_and_unknown_zones() -> None:
    screen = get_screen_definition("sales/delivery-note")
    assert screen is not None
    screen["actions"].append({
        "key": "invalid",
        "label": "Invalid",
        "kind": "secondary",
        "dangerLevel": "safe",
        "permission": "sales.read",
        "zone": "sidebar",
        "keyboardShortcut": "ctrl+p",
    })
    report = _check_readiness(screen)
    schema_gate = next(gate for gate in report["gates"] if gate["gate"] == "schema_valid")
    assert schema_gate["passed"] is False
    assert "invalid zone" in schema_gate["detail"]
    assert "duplicated" in schema_gate["detail"]


def test_all_native_screens_use_renderer_supported_layout_vocabulary() -> None:
    allowed_floorplans = {"worklist", "objectPage", "transaction", "cockpit", "wizard"}
    allowed_profiles = {"standard", "financial", "inventory", "audit"}
    allowed_rails = {"none", "audit", "copilot", "workflow", "combined"}
    allowed_danger_levels = {"safe", "moderate", "high", "critical"}

    for screen_id in SCREEN_DEFINITION_BUILDERS:
        screen = get_screen_definition(screen_id)
        assert screen is not None
        if screen.get("adapter", {}).get("temporary"):
            continue
        layout = screen.get("layout", {})
        assert layout.get("floorplan") in allowed_floorplans, screen_id
        assert layout.get("contextRail") in allowed_rails, screen_id
        has_tables = bool(screen.get("tables")) or any(
            tab.get("tables") for tab in screen.get("tabs", [])
        )
        if has_tables:
            assert layout.get("tableProfile") in allowed_profiles, screen_id
        for action in screen.get("actions", []):
            level = action.get("dangerLevel")
            assert level in allowed_danger_levels, (screen_id, action.get("key"), level)
            if level in {"high", "critical"}:
                assert action.get("humanApprovalRequired") is True, (
                    screen_id,
                    action.get("key"),
                )
