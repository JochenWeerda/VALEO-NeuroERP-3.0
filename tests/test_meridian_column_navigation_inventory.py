"""Meridian column-navigation inventory across native screen definitions."""

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

ALLOWED = {"single", "listDetail", "listDetailDetail"}
FORBIDDEN = {"transaction", "cockpit", "wizard"}
LIST_PLANS = {"worklist", "analyticalList"}


def _has_tables(screen: dict) -> bool:
    if screen.get("tables"):
        return True
    return any(tab.get("tables") for tab in screen.get("tabs") or [])


def test_every_native_screen_declares_column_navigation() -> None:
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        screen = get_screen_definition(screen_id)
        assert screen is not None
        if screen.get("adapter", {}).get("temporary"):
            continue
        layout = screen.get("layout") or {}
        nav = layout.get("columnNavigation")
        floorplan = layout.get("floorplan")
        assert nav in ALLOWED, (screen_id, nav)
        if floorplan in FORBIDDEN:
            assert nav == "single", screen_id
        if floorplan in LIST_PLANS and _has_tables(screen):
            assert nav == "listDetail", (screen_id, nav)


def test_futtermittel_analysen_is_list_detail_worklist() -> None:
    screen = get_screen_definition("futtermittel/analysen")
    assert screen is not None
    assert screen["layout"]["floorplan"] == "worklist"
    assert screen["layout"]["columnNavigation"] == "listDetail"
    assert screen["layout"]["contextRail"] == "none"
