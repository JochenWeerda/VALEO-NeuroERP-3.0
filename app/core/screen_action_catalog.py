"""Extract voice/MCP/toolbar-compatible actions from native ScreenDefinitions.

Builtin shortcuts in ki-usability keep their IDs. Mask actions are namespaced
as ``mask:{screen_id}:{action_key}`` so they never collide with global shortcuts.
Only actions with a real execution path are exported (commandEndpoint,
navigationRoute, command, or humanForm inputFlow submitEndpoint).
"""

from __future__ import annotations

from typing import Any

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition


def action_has_execution_path(action: dict[str, Any]) -> bool:
    if not isinstance(action, dict):
        return False
    if action.get("commandEndpoint") or action.get("navigationRoute") or action.get("command"):
        return True
    flow = action.get("inputFlow")
    return (
        isinstance(flow, dict)
        and isinstance(flow.get("submitEndpoint"), str)
        and bool(flow["submitEndpoint"])
    )


def mask_action_id(screen_id: str, action_key: str) -> str:
    return f"mask:{screen_id}:{action_key}"


def screen_action_to_catalog_entry(
    screen_id: str,
    domain: str | None,
    action: dict[str, Any],
) -> dict[str, Any] | None:
    key = action.get("key")
    label = action.get("label")
    if not isinstance(key, str) or not key or not isinstance(label, str) or not label:
        return None
    if not action_has_execution_path(action):
        return None

    phrases = [label]
    for extra in (action.get("intentPhrases"), action.get("voicePhrases")):
        if isinstance(extra, list):
            phrases.extend(str(p) for p in extra if p)

    # Stable unique phrases without empties
    seen: set[str] = set()
    intent_phrases: list[str] = []
    for phrase in phrases:
        cleaned = phrase.strip()
        if cleaned and cleaned.casefold() not in seen:
            seen.add(cleaned.casefold())
            intent_phrases.append(cleaned)

    entry: dict[str, Any] = {
        "id": mask_action_id(screen_id, key),
        "label": label,
        "description": action.get("description") or f"{label} ({screen_id})",
        "category": "mask-action",
        "domain": domain,
        "mask": screen_id,
        "intent_phrases": intent_phrases,
        "required_data": ["entity_id"] if "{entity_id}" in str(action.get("commandEndpoint") or "") else [],
        "source": {
            "screenId": screen_id,
            "actionKey": key,
            "commandEndpoint": action.get("commandEndpoint"),
            "navigationRoute": action.get("navigationRoute"),
            "command": action.get("command"),
            "method": action.get("method"),
        },
    }
    return entry


def build_screen_action_catalog(
    *,
    screen_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return catalog entries for all (or selected) screen definitions."""
    ids = screen_ids if screen_ids is not None else sorted(SCREEN_DEFINITION_BUILDERS.keys())
    catalog: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for screen_id in ids:
        sd = get_screen_definition(screen_id)
        domain = sd.get("domain") if isinstance(sd.get("domain"), str) else None
        for action in sd.get("actions") or []:
            if not isinstance(action, dict):
                continue
            entry = screen_action_to_catalog_entry(screen_id, domain, action)
            if entry is None:
                continue
            if entry["id"] in seen_ids:
                continue
            seen_ids.add(entry["id"])
            catalog.append(entry)
    catalog.sort(key=lambda row: row["id"])
    return catalog


def catalog_stats(catalog: list[dict[str, Any]] | None = None) -> dict[str, int]:
    rows = catalog if catalog is not None else build_screen_action_catalog()
    domains = {r.get("domain") for r in rows if r.get("domain")}
    return {
        "actions": len(rows),
        "screens_with_actions": len({r["mask"] for r in rows}),
        "domains": len(domains),
    }
