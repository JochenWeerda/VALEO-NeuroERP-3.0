"""Public authentication surfaces contain no protected data source or command."""


def build_public_auth_screen(screen_id: str) -> dict:
    if screen_id not in {"auth/login", "auth/callback"}:
        raise ValueError("Not a public authentication surface")
    login = screen_id == "auth/login"
    action = {"key": "login" if login else "back", "label": "Mit SSO anmelden" if login else "Zurueck zur Anmeldung",
              "kind": "primary", "dangerLevel": "safe", "localEffect": "view", "forbiddenForAgents": True}
    if not login:
        action["enabledWhen"] = {"path": "hasError", "equals": True}
    return {"schemaVersion": 1, "id": screen_id, "domain": "identity", "mode": "wizard",
            "title": "VALEO NeuroERP" if login else "Anmeldung",
            "subtitle": "Melden Sie sich mit Ihrem Unternehmens-Account an." if login else "Anmeldung wird abgeschlossen...",
            "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
            "layout": {"floorplan": "wizard", "density": "compact", "contextRail": "workflow"},
            "dataSources": [], "fields": [], "tables": [], "actions": [action],
            "noWorkflowReason": "Oeffentlicher OIDC-Einstieg; State und PKCE bleiben im Authentifizierungsdienst.",
            "noProcessChainReason": "Technischer Identitaetsweg ohne ERP-Fachdaten.",
            "performance": {"initialPayloadBudgetKb": 10, "requiresLazyTabs": False,
                            "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "identity"},
            "agentContract": {"businessPurpose": "Interaktive Unternehmensanmeldung", "examplePrompts": [],
                              "forbiddenAgentTasks": ["Anmeldung oder OIDC-Callback fuer Benutzer ausfuehren"],
                              "sensitiveFields": [], "testSelectors": {"screenRoot": "[data-testid='" + screen_id.replace('/', '-') + "']"}}}
