"""Vertrag: CockpitOverviewParent fuer Dashboard-/Cockpit-Familie (UIX-061)."""

from __future__ import annotations

import pytest

from app.core.cockpit_overview_parent import COCKPIT_OVERVIEW_LAYOUT_KEYS, build_cockpit_overview_screen
from app.core.screen_definitions import get_screen_definition
BATCH10_COCKPIT_SCREEN_IDS: tuple[str, ...] = (
    "controlling/benchmark-cockpit",
    "controlling/dashboard-verwaltung",
    "controlling/kpi-verwaltung",
    "controlling/massnahmen",
    "controlling/plan-ist",
    "controlling/timeseries-erfassung",
    "controlling/widget-verwaltung",
    "crm/crm-dashboard",
    "crm/bedarfsdeckung-cockpit",
    "crm/campaign-performance",
    "crm/kunden-cockpit",
    "dashboard/einkauf",
    "dashboard/verkauf",
    "dashboard/customizable",
    "dashboards/geschaeftsfuehrung",
    "admin/compliance-dashboard",
    "admin/qualitaets-cockpit",
    "fibu/abschluss-cockpit",
    "finance/offene-posten-cockpit",
    "fuhrpark/auswertung-kosten",
    "fuhrpark/auswertungen-menu",
    "lager/inventory-dashboard",
    "lager/qs-leitstand",
    "management/executive-dashboard",
    "portal/feldbuch-auswertungen",
    "platform/analytics",
    "subventionen/dashboard",
    "workflow/leitstand",
    "workflow/process-mining",
    "workspace/start-dashboard",
    "workspace/einkauf",
    "workspace/verkauf",
    "workspace/lager",
    "workspace/fibu",
    "workspace/leitung",
)
from app.services.made_by_studio_gates import check_gate_a, check_gate_b, check_gate_c, resolve_layout_kind


def _assert_cockpit_shell(screen: dict, *, screen_id: str) -> None:
    assert screen["mode"] == "cockpit"
    assert screen["adapter"]["type"] == "native"
    assert screen["adapter"]["temporary"] is False
    assert screen["adapter"]["sourceId"] == screen_id
    layout = screen["layout"]
    assert layout["floorplan"] == COCKPIT_OVERVIEW_LAYOUT_KEYS["floorplan"]
    assert layout["density"] == COCKPIT_OVERVIEW_LAYOUT_KEYS["density"]
    assert layout.get("contextRail") in {"audit", "combined", "copilot", "workflow"}
    assert resolve_layout_kind(screen) == "overviewPage"
    has_content = bool(screen.get("tiles")) or bool(screen.get("tables")) or bool(screen.get("calendar")) or bool(
        screen.get("twin")
    )
    assert has_content, screen_id
    assert screen.get("noWorkflowReason") or (screen.get("workflow") or {}).get("processKey")
    assert screen["agentContract"]["testSelectors"]["screenRoot"].startswith("[data-testid='")


@pytest.mark.parametrize("screen_id", BATCH10_COCKPIT_SCREEN_IDS)
def test_cockpit_family_uses_parent_shell(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None, screen_id
    _assert_cockpit_shell(screen, screen_id=screen_id)


@pytest.mark.parametrize("screen_id", BATCH10_COCKPIT_SCREEN_IDS)
def test_cockpit_studio_gates_abc_clean(screen_id: str) -> None:
    screen = get_screen_definition(screen_id)
    assert screen is not None
    assert check_gate_a(screen).passed, check_gate_a(screen).issues
    assert check_gate_b(screen).passed, check_gate_b(screen).issues
    assert check_gate_c(screen, screen_id=screen_id).passed, check_gate_c(screen, screen_id=screen_id).issues


def test_build_cockpit_overview_screen_validates_floorplan() -> None:
    with pytest.raises(ValueError, match="tiles"):
        build_cockpit_overview_screen(
            screen_id="test/empty",
            domain="platform",
            title="T",
            subtitle="S",
            business_purpose="P",
            example_prompts=["?"],
        )
