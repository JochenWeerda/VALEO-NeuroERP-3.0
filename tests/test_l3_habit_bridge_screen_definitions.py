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
    bewegungen = next(tab["tables"][0] for tab in screen["tabs"] if tab["key"] == "bewegungen")
    assert bewegungen["rowRouteTemplate"] == "/lager/stock-movement/{movement_id}"
    _assert_ready(screen)


def test_customer_360_keeps_customer_actions_in_familiar_footer_zones() -> None:
    screen = get_screen_definition("crm/customer-360")
    assert screen is not None
    assert screen["layout"]["stickyHeader"] is True
    assert screen["layout"]["stickyFooter"] is True
    assert _action(screen, "create_activity")["zone"] == "footer"
    # Pflege der Untertabellen in der Akte selbst (09.11.2026): Kopfaktionen statt Sprung "edit".
    assert _action(screen, "anschrift_anlegen")["zone"] == "header"
    _assert_ready(screen)


def _table(screen: dict, tab_key: str, table_key: str) -> dict:
    tab = next(tab for tab in screen["tabs"] if tab["key"] == tab_key)
    return next(table for table in tab["tables"] if table["key"] == table_key)


def test_document_chain_uses_one_page_layout() -> None:
    """Lieferschein, Rechnung und Bestellung lesen sich gleich (Gewohnheits-Prinzip); der Auftrag ist Belegmaske."""
    for screen_id in ("einkauf/purchase-order",):
        screen = get_screen_definition(screen_id)
        assert screen is not None, screen_id
        assert screen["layout"]["sectionNavigation"] == "anchors", screen_id
        _assert_ready(screen)



def test_readiness_rejects_row_detail_without_label_or_duplicates() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    _table(screen, "positionen", "positionen")["rowDetail"]["fields"] = [
        {"key": "line_no", "label": ""},
        {"key": "unit", "label": "Einheit"},
        {"key": "unit", "label": "Einheit"},
    ]
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "table positionen rowDetail field requires key and label" in detail
    assert "table positionen rowDetail field is duplicated: unit" in detail


def test_readiness_rejects_row_detail_that_is_not_an_object() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    _table(screen, "positionen", "positionen")["rowDetail"] = ["line_no"]
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "table positionen rowDetail must be an object" in detail


def test_documents_are_named_by_their_number() -> None:
    """Der h1 eines Belegs ist seine Nummer, nicht der Maskentyp."""
    expected = {
        "einkauf/purchase-order": "bestellnummer",
    }
    for screen_id, identity_field in expected.items():
        screen = get_screen_definition(screen_id)
        assert screen is not None, screen_id
        assert screen["identityField"] == identity_field, screen_id
        kopf = next(tab for tab in screen["tabs"] if tab["key"] == "kopf")
        assert identity_field in {f["key"] for f in kopf["fields"]}, screen_id


def test_readiness_rejects_identity_field_that_the_mask_does_not_show() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    screen["identityField"] = "belegnummer"
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "identityField belegnummer is not a declared field" in detail


def _schema_gate_detail(screen: dict) -> tuple[bool, str]:
    report = _check_readiness(screen)
    gate = next(gate for gate in report["gates"] if gate["gate"] == "schema_valid")
    return gate["passed"], gate["detail"]


def test_readiness_rejects_unknown_section_navigation() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    screen["layout"]["sectionNavigation"] = "accordion"
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "layout.sectionNavigation is invalid: accordion" in detail


def test_readiness_rejects_section_anchors_outside_document_floorplans() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    screen["layout"]["floorplan"] = "worklist"
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "only supported for objectPage and transaction" in detail


def test_readiness_rejects_section_anchors_with_column_split() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    screen["layout"]["floorplan"] = "objectPage"
    screen["layout"]["columnNavigation"] = "listDetail"
    passed, detail = _schema_gate_detail(screen)
    assert passed is False
    assert "requires columnNavigation=single" in detail


def test_readiness_rejects_duplicate_shortcuts_and_unknown_zones() -> None:
    screen = get_screen_definition("einkauf/purchase-order")
    assert screen is not None
    # Erst eine gueltige Aktion mit dem Kuerzel, dann die doppelte (bis 1b trug der alte Lieferscheindruck ctrl+p).
    screen["actions"].append({
        "key": "drucken_kopie", "label": "Drucken", "kind": "secondary", "dangerLevel": "safe",
        "permission": "sales.read", "zone": "footer", "keyboardShortcut": "ctrl+p",
    })
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
    allowed_floorplans = {"worklist", "objectPage", "transaction", "cockpit", "wizard", "analyticalList"}
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
