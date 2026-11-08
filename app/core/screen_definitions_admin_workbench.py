"""Admin workbench contracts, fields and guarded human actions."""
from typing import Any


def build_webhooks_workbench() -> dict[str, Any]:
    """Declarative list and guarded actions; no private administrative React surface."""
    from app.core.stamm_list_parent import build_stamm_list_screen
    definition = build_stamm_list_screen(
        screen_id="admin/webhooks-liste", domain="admin", title="Webhook-Verwaltung",
        subtitle="Registrierungen und Zustellversuche", endpoint="/api/v1/webhooks", row_route=None,
        columns=[
            {"key": "nr", "label": "Nummer", "numeric": True, "sortable": True, "priority": "primary"},
            {"key": "bereich", "label": "Ereignis", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "url", "label": "Ziel-URL", "filterable": True, "priority": "primary"},
            {"key": "is_active", "label": "Aktiv", "renderKind": "boolean"},
            {"key": "signiert", "label": "Signiert", "renderKind": "boolean"},
            {"key": "erstellt_am", "label": "Erstellt", "renderKind": "datetime"},
            {"key": "letzte_auslosung_am", "label": "Letzter Versuch", "renderKind": "datetime"},
            {"key": "fehler_count", "label": "Fehlversuche", "numeric": True, "renderKind": "number"},
        ],
        actions=[{
            "key": "register", "label": "Neuer Webhook", "kind": "primary", "dangerLevel": "moderate",
            "permission": "studio.admin-webhooks.register", "commandEndpoint": "/api/v1/webhooks/",
            "method": "POST", "forbiddenForAgents": True, "requiresConfirmation": True,
            "inputFields": [
                {"key": "event_area", "label": "Ereignis", "type": "select", "required": True,
                 "optionsSource": {"endpoint": "/api/v1/webhooks/areas", "valueKey": "name", "labelKey": "name"}},
                {"key": "url", "label": "Ziel-URL", "type": "text", "required": True},
                {"key": "secret", "label": "Signiergeheimnis (optional)", "type": "password"},
            ],
        }],
        row_actions=[
            {"key": "history", "label": "Zustellversuche", "dangerLevel": "safe", "localEffect": "view",
             "readView": {"endpoint": "/api/v1/webhooks/{id}/zustellversuche", "columns": [
                 {"key": "versucht_am", "label": "Zeitpunkt", "renderKind": "datetime"},
                 {"key": "erfolgreich", "label": "Erfolg", "renderKind": "boolean"},
                 {"key": "status_code", "label": "HTTP-Status", "renderKind": "number"},
                 {"key": "dauer_ms", "label": "Dauer (ms)", "renderKind": "number"},
                 {"key": "fehler", "label": "Fehler"},
             ]}},
            {"key": "unregister", "label": "Abmelden", "dangerLevel": "moderate", "method": "DELETE",
             "commandEndpoint": "/api/v1/webhooks/{entity_id}", "requiresConfirmation": True,
             "permission": "studio.admin-webhooks.unregister", "forbiddenForAgents": True},
        ],
        purpose="Webhook-Registrierungen und echte Zustellversuche im angemeldeten Mandanten verwalten.",
        prompts=["Welche Webhooks sind registriert?", "Zeige die Zustellversuche dieser Registrierung."],
        bundle="admin", table_profile="audit", no_workflow="Administrativer Stammdatenprozess ohne eigenen Belegablauf.",
    )
    definition["agentContract"]["sensitiveFields"] = ["secret"]
    definition["agentContract"]["forbiddenAgentTasks"] = ["Webhooks registrieren oder abmelden"]
    return definition


def build_control_center_workbench() -> dict[str, Any]:
    screen_id = "admin/control-center"
    names = [("tenant_id", "Mandant"), ("incident_id", "Vorfall"), ("source", "Quelle"),
             ("severity", "Schwere"), ("status", "Status"), ("title", "Titel"),
             ("owner", "Verantwortlich"), ("recommended_action", "Naechster Schritt"),
             ("scheduled_for", "Planungszeit"), ("plan_id", "Plan"), ("kind", "Art"),
             ("calendar_window", "Planungsfenster"), ("open_quarantine_count", "Quarantaene"),
             ("journal_error_count", "Journalfehler")]
    fields = [{"key": key, "label": label, "type": "text", "readOnly": key != "scheduled_for"} for key, label in names]
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "admin", "mode": "cockpit",
        "title": "Admin Kontrollzentrum", "subtitle": "Agenten, Integrationen, Vorfaelle und Planung",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "compact", "contextRail": "audit", "tableProfile": "audit"},
        "fields": fields,
        "actions": [
            {"key": "plan", "label": "Planungseintrag anlegen", "kind": "primary", "dangerLevel": "safe", "forbiddenForAgents": True,
             "permission": "studio.admin-control-center.plan", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/agents/neuroassist/ops/planning/items", "method": "POST"}},
            {"key": "escalate", "label": "Vorfall eskalieren", "kind": "secondary", "dangerLevel": "moderate", "forbiddenForAgents": True,
             "permission": "studio.admin-control-center.escalate", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/agents/neuroassist/ops/incidents/{incident_id}/actions", "method": "POST"}, "surfaceOnly": True},
            {"key": "resolve", "label": "Vorfall erledigen", "kind": "secondary", "dangerLevel": "moderate", "forbiddenForAgents": True,
             "permission": "studio.admin-control-center.resolve", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/agents/neuroassist/ops/incidents/{incident_id}/actions", "method": "POST"}, "surfaceOnly": True},
            {"key": "retry", "label": "Erneut versuchen", "kind": "secondary", "dangerLevel": "moderate", "forbiddenForAgents": True,
             "permission": "studio.admin-control-center.retry", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/agents/neuroassist/ops/incidents/{incident_id}/actions", "method": "POST"}, "surfaceOnly": True},
        ],
        "dataSources": [], "specialized": {"type": "admin_workbench", "id": screen_id},
        "workflow": {"processKey": "admin-control-center", "status": "operator-workspace", "auditRequired": True},
        "performance": {"initialPayloadBudgetKb": 100, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "admin"},
        "agentContract": {"businessPurpose": "Administrative Vorfaelle und Planung im verifizierten Mandanten steuern", "examplePrompts": ["Welche Vorfaelle sind offen?"], "forbiddenAgentTasks": ["Vorfaelle mutieren"], "testSelectors": {"screenRoot": "[data-testid='native-cockpit-admin-control-center']"}},
    }
