"""Vertrag: StammListenParent-Shell fuer Listen-ScreenDefinitions (UIX-STAMM-LISTEN-PARENT)."""

from __future__ import annotations

import pytest

from app.core.screen_definitions_listen import LISTEN_SCREEN_BUILDERS
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_neu_action

PILOT_LIST_SCREENS = (
    "agrar/saatgut-liste",
    "agrar/duenger-liste",
    "einkauf/lieferanten",
    "einkauf/bestellungen",
    "finance/debitoren-liste",
    "finance/kreditoren-liste",
    "futtermittel/mischfuttermittel-liste",
    "crm/opportunities-liste",
)

SHARED_LAYOUT_KEYS = {
    "floorplan": "worklist",
    "preferredMode": "desktopDense",
    "mobileMode": "mobileStack",
    "touchTargetPx": 44,
    "tableProfile": "standard",
}

ROW_ROUTE_BY_SCREEN = {
    "agrar/saatgut-liste": "/agrar/saatgut/{id}",
    "agrar/duenger-liste": "/agrar/duenger/{id}",
    "einkauf/lieferanten": "/einkauf/lieferanten/{id}",
    "einkauf/bestellungen": "/einkauf/bestellung/{id}",
    "finance/debitoren-liste": "/finance/debitor/{id}",
    "finance/kreditoren-liste": "/finance/kreditor/{id}",
    "futtermittel/mischfuttermittel-liste": "/futtermittel/mischfuttermittel/{id}",
    "crm/opportunities-liste": "/crm/opportunity/{id}",
}

TABLE_PROFILE_BY_SCREEN = {
    "finance/debitoren-liste": "financial",
    "finance/kreditoren-liste": "financial",
}


@pytest.mark.parametrize("screen_id", PILOT_LIST_SCREENS)
def test_pilot_listen_children_share_stamm_list_shell(screen_id: str) -> None:
    builder = LISTEN_SCREEN_BUILDERS[screen_id]
    screen = builder()
    assert screen["mode"] == "list"
    assert screen["adapter"]["type"] == "native"
    assert screen["adapter"]["temporary"] is False
    assert len(screen["dataSources"]) == 1
    assert screen["dataSources"][0]["key"] == "list"
    table = screen["tables"][0]
    assert table["key"] == "list"
    assert table["virtualized"] is True
    assert table.get("rowRouteTemplate") == ROW_ROUTE_BY_SCREEN[screen_id]
    layout = screen["layout"]
    for key, value in SHARED_LAYOUT_KEYS.items():
        expected = TABLE_PROFILE_BY_SCREEN.get(screen_id, value) if key == "tableProfile" else value
        assert layout[key] == expected, f"{screen_id}.layout.{key}"
    assert screen["agentContract"]["testSelectors"]["screenRoot"] == f"[data-testid='screen-{screen_id}']"
    assert screen.get("noWorkflowReason")
    assert any(action.get("key") == "export" for action in screen["actions"])


def test_build_stamm_list_screen_validates_row_route_template() -> None:
    with pytest.raises(ValueError, match="Platzhalter"):
        build_stamm_list_screen(
            screen_id="demo/liste",
            domain="demo",
            title="Demo",
            subtitle="Demo",
            endpoint="/api/v1/demo",
            row_route="/demo/detail",
            columns=[{"key": "name", "label": "Name"}],
            actions=[stamm_list_neu_action("Neu", "/demo/neu")],
            row_actions=[],
            purpose="Demo",
            prompts=["Demo?"],
            bundle="demo",
            no_workflow="Kein Ablauf.",
        )


def test_all_listen_builders_use_parent_factory() -> None:
    for screen_id, builder in LISTEN_SCREEN_BUILDERS.items():
        screen = builder()
        assert screen["id"] == screen_id
        assert screen["layout"]["floorplan"] == "worklist"
        assert screen["tables"][0]["virtualized"] is True


def test_beleg_listen_zeilen_navigation_gate_c() -> None:
    """Gate C: kanonische Beleg-Detailrouten fuer Listen-Zeilenklicks."""
    from app.core.screen_definitions import build_sales_invoices_worklist_screen_definition

    bestellungen = LISTEN_SCREEN_BUILDERS["einkauf/bestellungen"]()
    assert bestellungen["tables"][0]["rowRouteTemplate"] == "/einkauf/bestellung/{id}"

    rechnungen = build_sales_invoices_worklist_screen_definition()
    table = rechnungen["tabs"][0]["tables"][0]
    assert table["rowRouteTemplate"] == "/belege/sales_invoice/{id}"
