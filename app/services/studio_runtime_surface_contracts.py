"""Fixed bindings for domain surfaces rendered inside the universal runtime."""

FLOW_PROCESSES = frozenset({
    "order-to-cash", "procure-to-pay", "inventory-to-settlement", "harvest-to-settlement",
    "contract-to-settlement", "complaint-to-resolution", "service-to-customer",
    "finance-to-close", "compliance-to-report",
})
SPECIALIZED_SCREENS = {
    "finance_workbench": frozenset({"finance/bank-abgleich", "mahnwesen/mahnlauf"}),
    "admin_workbench": frozenset({"admin/webhooks-liste", "admin/control-center"}),
    "intake": frozenset({"annahme/lkw-registrierung", "annahme/qualitaets-check", "annahme/warteschlange"}),
    "weighing": frozenset({"waage/liste", "waage/neu", "waage/waagen-liste", "waage/wiegungen", "waage/wiegungen-liste"}),
    "feed_workbench": frozenset({"futtermittel/rationseditor", "futtermittel/rationsoptimierung", "portal/rationsoptimierung", "futtermittel/fuetterungsdokumentation-mobil"}),
}


def validate_runtime_surface(definition: dict) -> list[str]:
    errors = []
    screen_id = definition.get("id")
    specialized = definition.get("specialized")
    specialized_type = specialized.get("type") if isinstance(specialized, dict) else None
    if not isinstance(specialized_type, str):
        specialized_type = None
    has_surface = "flowSpineWorkspace" in definition or specialized_type in SPECIALIZED_SCREENS
    if has_surface and isinstance(screen_id, str) and screen_id.startswith("tenant/"):
        from app.core.screen_definitions import get_screen_definition
        from app.core.studio_release import definition_hash
        base_id = definition.get("baseScreenId")
        canonical = get_screen_definition(base_id) if isinstance(base_id, str) else None
        baseline = definition.get("nativeBaseline")
        if (not canonical or not isinstance(baseline, dict)
                or baseline.get("sourceHash") != definition_hash(canonical)
                or any(definition.get(key) != canonical.get(key) for key in ("flowSpineWorkspace", "specialized", "mode"))):
            errors.append("fachoberflaechen_basis_ungueltig")
        else:
            screen_id = base_id
    if "flowSpineWorkspace" in definition:
        contract = definition["flowSpineWorkspace"]
        if (not isinstance(contract, dict) or set(contract) != {"processKey"}
                or not isinstance(contract.get("processKey"), str)
                or contract.get("processKey") not in FLOW_PROCESSES
                or screen_id != "workflow/flow-spine-" + str(contract.get("processKey"))
                or definition.get("mode") != "cockpit"):
            errors.append("prozessraum_bindung_ungueltig")
    if specialized_type in SPECIALIZED_SCREENS:
        if (not isinstance(screen_id, str) or screen_id not in SPECIALIZED_SCREENS[specialized_type]
                or specialized.get("id") != screen_id):
            errors.append("fachoberflaechen_bindung_ungueltig")
    for action in definition.get("actions") or []:
        if not isinstance(action, dict):
            continue
        if "surfaceOnly" not in action:
            continue
        if (not isinstance(action["surfaceOnly"], bool)
                or (action["surfaceOnly"] and (
                    not isinstance(specialized, dict)
                    or specialized_type not in SPECIALIZED_SCREENS
                    or not isinstance(screen_id, str)
                    or screen_id not in SPECIALIZED_SCREENS.get(specialized_type, ())
                    or specialized.get("id") != screen_id
                    or action.get("zone", "header") != "header"))):
            errors.append("fachaktion_bindung_ungueltig")
    return errors
