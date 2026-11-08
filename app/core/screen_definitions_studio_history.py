"""Native audit masks for Studio versions and immutable before/after comparisons."""

def build_studio_history(diff=False):
    key = "comparison" if diff else "versions"
    screen_id = "platform/studio-history-diff" if diff else "platform/studio-history"
    columns = ([{"key": "path", "label": "Eigenschaft", "width": 280},
                {"key": "before", "label": "Vorher", "width": 380},
                {"key": "after", "label": "Nachher", "width": 380}] if diff else [
                {"key": "recorded_at", "label": "Zeitpunkt", "renderKind": "datetime", "width": 160},
                {"key": "actor", "label": "Benutzer / Agent", "width": 170},
                {"key": "action", "label": "Aktion", "width": 140},
                {"key": "status", "label": "Status", "width": 140},
                {"key": "revision", "label": "Version", "width": 200},
                {"key": "active", "label": "Aktiv veröffentlicht", "renderKind": "boolean", "width": 150},
                {"key": "simulation_result", "label": "Simulation", "width": 140},
                {"key": "simulation_profile", "label": "Prüfprofil", "width": 140},
                {"key": "simulation_failures", "label": "Offene Prüfungen", "width": 220}])
    table = {"key": key, "label": "Änderungsvergleich" if diff else "Fassungen",
             "columns": columns, "serverPagination": True, "pageSize": 25,
             "virtualized": True, "rowHeight": 44}
    table["dataSourceKey"] = key
    if not diff:
        table["rowActions"] = [{"key": "compare", "label": "Änderungen ansehen"}]
    return {"schemaVersion": 1, "id": screen_id, "domain": "platform", "mode": "list",
            "title": "Änderungsvergleich" if diff else "Studio-Historie",
            "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
            "dataSources": [{"key": key, "endpoint": "/api/v1/studio/history-events/{entity_id}/diff" if diff else "/api/v1/studio/drafts/{entity_id}/history-view"}],
            "tabs": [{"key": key, "label": table["label"], "tables": [table]}],
            "layout": {"floorplan": "worklist", "density": "expertDense", "contextRail": "audit", "tableProfile": "audit"},
            "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True,
                            "lookupMinChars": 2, "bundleGroup": "platform"},
            "noWorkflowReason": "Unveränderliche Studio-Historie; nur lesender Vergleich, keine Belegänderung.",
            "agentContract": {"businessPurpose": "Versionen, Urheber und Änderungen von Studio-Definitionen nachvollziehen.",
                              "sensitiveFields": ["actor", "before", "after"],
                              "forbiddenAgentTasks": ["Historienfassungen verändern oder löschen"]}}


STUDIO_HISTORY_BUILDERS = {
    "platform/studio-history": build_studio_history,
    "platform/studio-history-diff": lambda: build_studio_history(True),
}
