"""Contracts for the vendor-neutral L3 habit bridge reference screens."""

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import get_screen_definition


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
