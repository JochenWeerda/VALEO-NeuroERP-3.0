"""Admin workbench contracts, fields and guarded human actions."""
from typing import Any


def build_webhooks_workbench() -> dict[str, Any]:
    screen_id = "admin/webhooks-liste"
    names = [("id", "ID"), ("nr", "Nummer"), ("url", "Ziel-URL"), ("bereich", "Ereignis"), ("is_active", "Aktiv"), ("erstellt_am", "Erstellt"), ("letzte_auslosung_am", "Letzter Versuch"), ("fehler_count", "Fehlversuche"), ("signiert", "Signiert"), ("secret", "Geheimnis"), ("versucht_am", "Zeitpunkt"), ("erfolgreich", "Erfolg"), ("status_code", "Statuscode"), ("dauer_ms", "Dauer"), ("fehler", "Fehler")]
    fields = [{"key": key, "label": label, "type": "text", "readOnly": key not in {"url", "bereich", "secret"}} for key, label in names]
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "admin", "mode": "cockpit",
        "title": "Webhook-Verwaltung", "subtitle": "Ausgehende Webhooks verwalten",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "compact", "contextRail": "audit", "tableProfile": "audit"},
        "fields": fields,
        "actions": [
            {"key": "register", "label": "Neuer Webhook", "kind": "primary", "dangerLevel": "safe", "forbiddenForAgents": True, "permission": "studio.admin-webhooks.register", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/webhooks/bereiche/{bereich}", "method": "POST"}},
            {"key": "history", "label": "Zustellversuche", "kind": "secondary", "dangerLevel": "safe", "forbiddenForAgents": True, "localEffect": "view", "surfaceOnly": True},
            {"key": "unregister", "label": "Abmelden", "kind": "secondary", "dangerLevel": "moderate", "forbiddenForAgents": True, "permission": "studio.admin-webhooks.unregister", "inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/webhooks/abmelden/{nr}", "method": "DELETE"}, "surfaceOnly": True},
        ],
        "dataSources": [], "specialized": {"type": "admin_workbench", "id": screen_id},
        "workflow": {"processKey": "admin-webhooks", "status": "operator-workspace", "auditRequired": True},
        "performance": {"initialPayloadBudgetKb": 100, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "admin"},
        "agentContract": {"businessPurpose": "Webhook-Registrierungen und Zustellversuche verwalten", "examplePrompts": ["Welche Webhooks sind registriert?"], "sensitiveFields": ["secret"], "forbiddenAgentTasks": ["Webhooks ändern"], "testSelectors": {"screenRoot": "[data-testid='native-cockpit-admin-webhooks-liste']"}},
    }


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
