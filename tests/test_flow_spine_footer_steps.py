"""FSX-022 — Naechste Schritte sind Zielrouten oder sie entfallen.

Vertrag: Beobachtungskarten bleiben Strings. Die Karte „Naechste Schritte"
liefert nur {label, href}, und href muss bereits im selben Workspace als
Aktion, Dokument, Ressource oder verknuepftes Modul stehen. Kein Raten aus
Text, keine neuen Pfade.
"""

from __future__ import annotations

import pytest

from app.core.flow_spine_registry import (
    WORKSPACES,
    _footer_item,
    get_flow_spine_workspace,
    merge_instance_statuses,
)

pytestmark = pytest.mark.unit


def _is_next_steps(title: str) -> bool:
    lowered = title.lower()
    return "schritt" in lowered or "naechste" in lowered


def _workspace_hrefs(workspace: dict) -> set[str]:
    hrefs: set[str] = set()
    for node in workspace.get("nodes") or []:
        for document in node.get("documents") or []:
            if document.get("href"):
                hrefs.add(document["href"])
        for action in node.get("actions") or []:
            if action.get("href"):
                hrefs.add(action["href"])
    right = workspace.get("right_panel") or {}
    for resource in right.get("resources") or []:
        if resource.get("href"):
            hrefs.add(resource["href"])
    for module in right.get("linked_modules") or []:
        if module.get("href"):
            hrefs.add(module["href"])
    return hrefs


def test_next_step_items_are_existing_workspace_routes() -> None:
    for process_key in WORKSPACES:
        workspace = get_flow_spine_workspace(process_key)
        allowed = _workspace_hrefs(workspace)
        next_cards = [card for card in workspace["footer_cards"] if _is_next_steps(card["title"])]
        assert next_cards, f"{process_key}: Karte 'Naechste Schritte' fehlt — dann muss sie bewusst entfallen"
        for card in next_cards:
            assert card["items"], f"{process_key}: leere Naechste Schritte — die Karte muss entfallen"
            for item in card["items"]:
                assert isinstance(item, dict), (
                    f"{process_key}: Schritt ohne Ziel muss entfallen, nicht als Text stehen bleiben: {item!r}"
                )
                assert item["label"].strip()
                href = item["href"]
                assert href.startswith("/"), href
                assert href in allowed, (
                    f"{process_key}: {href} ist keine Aktion/kein Modul dieses Prozesses"
                )


def test_observation_footer_cards_stay_plain_text() -> None:
    for process_key in WORKSPACES:
        workspace = get_flow_spine_workspace(process_key)
        for card in workspace["footer_cards"]:
            if _is_next_steps(card["title"]):
                continue
            for item in card["items"]:
                assert isinstance(item, str), (
                    f"{process_key}/{card['title']}: Feststellung braucht kein href ({item!r})"
                )


def test_next_step_labels_are_definition_not_instance_claims() -> None:
    for process_key in WORKSPACES:
        workspace = get_flow_spine_workspace(process_key)
        for card in workspace["footer_cards"]:
            if not _is_next_steps(card["title"]):
                continue
            for item in card["items"]:
                label = item["label"]
                assert "EUR" not in label
                assert "%" not in label
                assert "SO-" not in label
                assert "PO-" not in label


def test_instance_merge_keeps_footer_step_hrefs() -> None:
    catalog = get_flow_spine_workspace("order-to-cash")
    merged = merge_instance_statuses(
        catalog,
        {
            "instance_id": "11111111-1111-1111-1111-111111111111",
            "case_number": "WF-00042",
            "label": "Testvorgang",
            "node_statuses": {},
        },
    )
    steps = next(card for card in merged["footer_cards"] if _is_next_steps(card["title"]))
    hrefs = {item["href"] for item in steps["items"]}
    assert "/sales/orders/new" in hrefs
    assert "/verladung" in hrefs


def test_footer_item_rejects_external_or_empty_href() -> None:
    with pytest.raises(ValueError, match="in-app path"):
        _footer_item(("Auftrag erfassen", "https://example.invalid/orders"))
    with pytest.raises(ValueError, match="in-app path"):
        _footer_item(("Auftrag erfassen", ""))
