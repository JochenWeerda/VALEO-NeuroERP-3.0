"""Listenmasken als ScreenDefinition (MASK-STUDIO-ROLLOUT-20261020, Welle 1).

Die Listen zu den nativen Objektmasken waren handgebaut oder Altmuster-Konfigurationen. Hier sind sie
ScreenDefinitions: Spalten, Zeilenroute zur nativen Objektmaske und alle Aktionen mit ihrem Kommando-Weg. Die Seite
ist ``NativeListPage`` und enthaelt keinen eigenen Code; Maske, CLI und MCP rufen dieselben Wege.
"""
from __future__ import annotations

from typing import Any


def _liste(*, screen_id: str, domain: str, title: str, subtitle: str, endpoint: str, row_route: str,
           columns: list[dict[str, Any]], actions: list[dict[str, Any]], row_actions: list[dict[str, Any]],
           purpose: str, prompts: list[str], dangerous: list[dict[str, str]] | None = None,
           bundle: str, no_workflow: str) -> dict[str, Any]:
    agent: dict[str, Any] = {
        "businessPurpose": purpose,
        "examplePrompts": prompts,
        "sensitiveFields": [],
        "testSelectors": {"screenRoot": f"[data-testid='screen-{screen_id}']"},
    }
    if dangerous:
        agent["dangerousActions"] = dangerous
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "list",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": [{"key": "list", "endpoint": endpoint, "pageSize": 500}],
        "actions": actions,
        "tables": [{
            "key": "list", "label": title, "dataSourceKey": "list", "serverPagination": False, "pageSize": 50,
            "virtualized": True, "rowHeight": 40, "rowRouteTemplate": row_route,
            "columns": columns, "rowActions": row_actions,
        }],
        "noWorkflowReason": no_workflow,
        "agentContract": agent,
        "layout": {"floorplan": "worklist", "preferredMode": "desktopDense", "mobileMode": "mobileStack",
                   "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 60, "requiresLazyTabs": False, "requiresVirtualTables": True,
                        "lookupMinChars": 2, "bundleGroup": bundle},
    }


#: CSV-Export der Liste mit ihren Spalten (NativeListPage, ohne Serverwirkung).
_EXPORT = {"key": "export", "label": "CSV-Export", "kind": "secondary", "dangerLevel": "safe", "zone": "header",
           "localEffect": "download"}


def build_einkauf_anfragen_liste() -> dict[str, Any]:
    """Bedarfsanforderungen: senden, in Bestellung ueberfuehren, Entwurf loeschen."""
    return _liste(
        screen_id="einkauf/anfragen", domain="einkauf", title="Anfragen", subtitle="Bedarfsanforderungen an Lieferanten",
        endpoint="/api/v1/einkauf/anfragen", row_route="/einkauf/anfrage/{id}", bundle="einkauf",
        columns=[
            {"key": "anfrageNummer", "label": "Anfrage-Nr.", "sortable": True, "filterable": True, "priority": "primary"},
            {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "priority": "primary"},
            {"key": "artikel", "label": "Artikel", "filterable": True, "priority": "primary"},
            {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "priority": "secondary"},
            {"key": "anforderer", "label": "Anforderer", "filterable": True, "priority": "secondary"},
            {"key": "prioritaet", "label": "Prioritaet", "filterable": True, "priority": "secondary"},
            {"key": "faelligkeit", "label": "Faellig", "renderKind": "date", "sortable": True, "priority": "tertiary"},
            {"key": "createdAt", "label": "Erstellt", "renderKind": "date", "sortable": True, "priority": "tertiary"},
        ],
        actions=[{"key": "neu", "label": "Neue Anfrage", "kind": "primary", "dangerLevel": "safe", "zone": "header",
                  "navigationRoute": "/einkauf/anfrage-erfassung", "localEffect": "navigation"},
                 _EXPORT],
        row_actions=[
            {"key": "senden", "label": "Senden", "dangerLevel": "moderate", "permission": "einkauf.anfrage.senden",
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/senden", "method": "POST",
             "requiresConfirmation": True, "humanApprovalRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["ENTWURF", "OFFEN", "FREIGEGEBEN", "offen", "entwurf"]},
             "inputFields": [{"key": "lieferanten", "label": "Lieferanten", "type": "multiselect", "required": True,
                              "optionsSource": {"endpoint": "/api/v1/einkauf/lieferanten", "valueKey": "id",
                                                "labelKey": "firmenname"}}]},
            {"key": "in_bestellung", "label": "In Bestellung", "dangerLevel": "moderate",
             "permission": "einkauf.anfrage.bestellen", "requiresConfirmation": True,
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/in_bestellung", "method": "POST",
             "visibleWhen": {"field": "status", "values": ["FREIGEGEBEN", "ANGEBOTSPHASE"]}},
            {"key": "loeschen", "label": "Loeschen", "dangerLevel": "high", "permission": "einkauf.anfrage.loeschen",
             "commandEndpoint": "/api/v1/einkauf/anfragen/{entity_id}/actions/loeschen", "method": "POST",
             "requiresConfirmation": True, "auditReasonRequired": True, "forbiddenForAgents": True,
             "visibleWhen": {"field": "status", "values": ["ENTWURF", "OFFEN", "offen", "entwurf"]}},
        ],
        dangerous=[
            {"key": "senden", "reason": "Versendet E-Mails an Lieferanten im Namen des Hauses; nur Mensch."},
            {"key": "loeschen", "reason": "Entfernt eine Anfrage endgueltig; nur Mensch mit Begruendung."},
        ],
        purpose="Bedarfsanforderungen des Einkaufs finden, an Lieferanten senden und in Bestellungen ueberfuehren.",
        prompts=["Welche Anfragen sind noch im Entwurf?", "Zeige dringende Anfragen."],
        no_workflow="Der Status steht an der Anfrage; die Liste fuehrt keinen eigenen Ablauf.",
    )


LISTEN_SCREEN_BUILDERS = {
    "einkauf/anfragen": build_einkauf_anfragen_liste,
}
LISTEN_ROUTEN = {"einkauf/anfragen": "/einkauf/anfragen"}
LISTEN_SYNONYME = {"einkauf/anfragen": ["anfragen", "bedarfsanforderungen", "banf"]}
