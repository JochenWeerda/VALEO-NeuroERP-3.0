"""Existing route replacements share the canonical definition, never a second model."""
from copy import deepcopy

NATIVE_SCREEN_ALIASES = {"verkauf/rechnungen": "sales/invoices", "crm/kunden-cockpit": "crm/customer-360"}


def build_native_alias(screen_id: str) -> dict:
    from app.core.screen_definitions import get_screen_definition
    target = NATIVE_SCREEN_ALIASES[screen_id]
    definition = get_screen_definition(target)
    if not definition or definition.get("id") != target:
        raise ValueError("Canonical alias target is unavailable")
    result = deepcopy(definition)
    result.update(id=screen_id, nativeAlias={"screenId": target})
    result["adapter"] = {**result["adapter"], "sourceId": screen_id}
    return result
