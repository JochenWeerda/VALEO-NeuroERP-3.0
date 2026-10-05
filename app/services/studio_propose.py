"""Deterministic ScreenDefinition proposals for humans and agents."""

from __future__ import annotations

import re
from typing import Any

from app.services.studio_validation import load_studio_catalog

_SLUG = re.compile(r"[^a-z0-9]+")


def _slug(value: str) -> str:
    return _SLUG.sub("-", value.lower()).strip("-") or "maske"


def propose_studio_draft(intent: str) -> dict[str, Any]:
    """Turns a short German or English intent into a tenant worklist draft."""

    catalog = load_studio_catalog()
    text = (intent or "").lower()
    sources = {item["key"]: item for item in catalog["data_sources"]}
    if any(token in text for token in ("kunde", "customer", "crm")):
        source = sources["customers"]
        title = "Kunden-Arbeitsliste"
        domain = "crm"
        columns = [("kunden_nr", "Nr"), ("name", "Name"), ("ort", "Ort")]
        action_key = "create_activity"
    elif any(token in text for token in ("posten", "mahn", "op", "finance")):
        source = sources["open_items"]
        title = "Offene Posten"
        domain = "finance"
        columns = [("nr", "Nr"), ("kunde", "Kunde"), ("betrag", "Betrag")]
        action_key = "mahnen"
    elif any(token in text for token in ("artikel", "article", "lager")):
        source = sources["articles"]
        title = "Artikel-Arbeitsliste"
        domain = "lager"
        columns = [("artikel_nr", "Nr"), ("bezeichnung", "Bezeichnung"), ("bestand", "Bestand")]
        action_key = "create_activity"
    else:
        source = sources["suppliers"]
        title = "Lieferanten-Bewertung"
        domain = "einkauf"
        columns = [("lieferantennummer", "Nr"), ("firmenname", "Name"), ("bewertung", "Bewertung"), ("ort", "Ort")]
        action_key = "create_activity"

    action = catalog["actions"][action_key]
    slug = _slug(title)
    return {
        "schemaVersion": 1,
        "id": f"tenant/{slug}",
        "domain": domain,
        "mode": "list",
        "title": title,
        "subtitle": (intent or "").strip() or title,
        "adapter": {"type": "native", "sourceId": f"tenant/{slug}", "temporary": True},
        "dataSources": [{"key": source["key"], "endpoint": source["endpoint"], "pageSize": 50}],
        "layout": {
            "floorplan": "worklist",
            "columnNavigation": "listDetail",
            "density": "compact",
            "contextRail": "none",
            "tableProfile": "financial" if domain == "finance" else "standard",
        },
        "tables": [{
            "key": "list",
            "label": title,
            "dataSourceKey": source["key"],
            "serverPagination": True,
            "pageSize": 25,
            "virtualized": True,
            "rowHeight": 44,
            "columns": [
                {"key": key, "label": label, "sortable": True, "filterable": True, "numeric": key == "betrag"}
                for key, label in columns
            ],
        }],
        "actions": [{
            "key": action_key,
            "label": action.get("label", action_key),
            "dangerLevel": action["dangerLevel"],
            "commandEndpoint": action.get("commandEndpoint"),
            "forbiddenForAgents": action.get("forbiddenForAgents", False),
            "permission": "studio.draft.execute",
        }],
        "noWorkflowReason": "Studio-Worklist priorisiert Auswahl; Statuswechsel bleiben auf der ObjectPage.",
        "agentContract": {
            "screenId": f"tenant/{slug}",
            "domain": domain,
            "schemaVersion": 1,
            "contractVersion": 1,
            "businessPurpose": title,
            "primaryEntity": slug,
            "readableFields": [key for key, _label in columns],
            "editableFields": [key for key, _label in columns],
            "sensitiveFields": [],
            "availableActions": [{
                "key": action_key,
                "label": action.get("label", action_key),
                "dangerLevel": action["dangerLevel"],
                "requiresHumanApproval": False,
                "requiresConfirmation": False,
                "permission": "studio.draft.execute",
            }],
            "validationRules": [],
            "workflowRules": [],
            "auditRequirements": [],
            "recommendedAgentTasks": [f"{title} filtern und bewerten"],
            "forbiddenAgentTasks": [],
            "testSelectors": {
                "screenRoot": f"[data-testid='screen-tenant/{slug}']",
                "submitButton": "[data-testid='form-submit-btn']",
                "workflowPanel": "[data-testid='workflow-panel']",
            },
            "examplePrompts": [intent.strip() or title],
        },
    }
