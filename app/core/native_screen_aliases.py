"""Existing route replacements share the canonical definition, never a second model."""
from copy import deepcopy

# verkauf/rechnungen war bis 08.11.2026 ein Alias der alten Rechnungsliste; die Route rendert seitdem direkt die
# Variante beleg-liste/sales-invoice (DocFlow), ein Alias waere eine zweite Maske.
NATIVE_SCREEN_ALIASES = {"crm/kunden-cockpit": "crm/customer-360"}


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
