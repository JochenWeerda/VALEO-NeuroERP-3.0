"""KontrollWorklistParent — gemeinsame Shell fuer Kontroll-/Freigabe-/Pruef-Worklists (UIX-P1).

Taxonomie: ``docs/architecture/uix/maskenfamilien-taxonomie.md`` §2.4.
Queue-Worklists mit Summary-KPIs, virtualisierter Ausnahmetabelle, Audit-Rail und
Zeilenaktionen; kein ProcessRibbon und keine ProcessBand-Phasen (nur Worklist-Workflow-Metadaten).
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

KONTROLL_WORKLIST_LAYOUT_KEYS = {
    "floorplan": "worklist",
    "density": "expertDense",
    "contextRail": "audit",
}

DOCUMENT_CONTROL_SUMMARY: list[dict[str, Any]] = [
    {"key": "open_total", "label": "Offen", "tone": "warning"},
    {"key": "open_purchase_order", "label": "Unerledigte Bestellungen", "tone": "warning"},
    {"key": "missing_inbound_document", "label": "Fehlende Eingangsbelege", "tone": "danger"},
    {"key": "blocked_delivery_note", "label": "Gesperrte Lieferscheine", "tone": "danger"},
    {"key": "uninvoiced_delivery_note", "label": "Nicht fakturiert", "tone": "warning"},
    {"key": "overdue", "label": "Ueberfaellig", "tone": "danger"},
]

DOCUMENT_CONTROL_EXCEPTION_COLUMNS: list[dict[str, Any]] = [
    {"key": "due_at", "label": "Faelligkeit", "renderKind": "datetime", "sortable": True, "width": 150},
    {"key": "exception_type", "label": "Typ", "sortable": True, "filterable": True, "width": 190},
    {"key": "document_number", "label": "Beleg", "sortable": True, "filterable": True, "width": 140},
    {"key": "partner_name", "label": "Partner", "filterable": True, "width": 180},
    {"key": "partner_ref", "label": "Partner-Nr.", "filterable": True, "width": 110},
    {"key": "assigned_user", "label": "Verantwortlich", "sortable": True, "filterable": True, "width": 130},
    {"key": "status", "label": "Status", "renderKind": "status", "sortable": True, "filterable": True, "width": 120},
    {"key": "notes", "label": "Hinweis", "width": 220},
    {"key": "created_at", "label": "Erfasst", "renderKind": "datetime", "sortable": True, "width": 150},
]

DOCUMENT_CONTROL_ROW_ACTIONS: list[dict[str, Any]] = [
    {"key": "assign_me", "label": "Zuweisen", "visibleWhen": {"field": "status", "values": ["open", "assigned", "in_progress"]}},
    {"key": "start_work", "label": "In Arbeit", "visibleWhen": {"field": "status", "values": ["open", "assigned"]}},
    {"key": "resolve", "label": "Erledigt", "visibleWhen": {"field": "status", "values": ["open", "assigned", "in_progress"]}},
    {
        "key": "waive",
        "label": "Verwerfen",
        "dangerLevel": "moderate",
        "permission": "document_control.write",
        "visibleWhen": {"field": "status", "values": ["open", "assigned", "in_progress"]},
    },
    {"key": "open_source", "label": "Zum Beleg"},
]

DOCUMENT_CONTROL_NO_WORKFLOW_REASON = (
    "Statuswechsel werden im append-only Belegkontroll-Audit gefuehrt."
)

DOCUMENT_CONTROL_AGENT_EXAMPLE_PROMPTS = [
    "Zeige nicht fakturierte Lieferscheine.",
    "Welche Bestellungen sind unerledigt?",
    "Welche Belegausnahmen sind ueberfaellig?",
]

DOCUMENT_CONTROL_SENSITIVE_FIELDS = ["partner_name", "partner_ref", "notes"]

DOCUMENT_CONTROL_FORBIDDEN_AGENT_TASKS = ["Ausnahmen ohne menschlichen Audit-Grund erledigen"]


def kontroll_entity_and_queue_sources(
    *,
    summary_endpoint: str,
    queue_endpoint: str,
    queue_key: str = "exceptions",
    page_size: int = 50,
    stale_time_ms: int = 10_000,
) -> list[dict[str, Any]]:
    """Standard-Datenquellen: Lagebild (entity) + paginierte Queue."""
    return [
        {"key": "entity", "endpoint": summary_endpoint, "staleTimeMs": stale_time_ms},
        {"key": queue_key, "endpoint": queue_endpoint, "pageSize": page_size, "staleTimeMs": stale_time_ms},
    ]


def kontroll_queue_table(
    *,
    table_key: str,
    label: str,
    columns: list[dict[str, Any]],
    row_actions: list[dict[str, Any]],
    data_source_key: str | None = None,
    row_route_template: str | None = "{source_route}",
    page_size: int = 50,
) -> dict[str, Any]:
    """Virtualisierte Ausnahme-/Prueftabelle mit konsistenten Queue-Defaults."""
    table: dict[str, Any] = {
        "key": table_key,
        "label": label,
        "dataSourceKey": data_source_key or table_key,
        "serverPagination": True,
        "pageSize": page_size,
        "virtualized": True,
        "rowHeight": 44,
        "columns": columns,
        "rowActions": row_actions,
    }
    if row_route_template:
        table["rowRouteTemplate"] = row_route_template
    return table


def _test_id_from_agent_selectors(screen_id: str, test_selectors: dict[str, Any] | None) -> str:
    root = (test_selectors or {}).get("screenRoot", "")
    if isinstance(root, str) and root.startswith("[data-testid='") and root.endswith("']"):
        inner = root[len("[data-testid='") : -2]
        if inner.startswith("screen-"):
            return inner[len("screen-") :]
        return inner
    return screen_id.replace("/", "-")


def kontroll_from_legacy_definition(legacy: dict[str, Any]) -> dict[str, Any]:
    """Bestehende Queue-Worklist-SD in den KontrollWorklistParent-Vertrag heben."""
    layout = legacy.get("layout") or {}
    perf = legacy.get("performance") or {}
    agent = legacy.get("agentContract") or {}
    return build_kontroll_worklist_screen(
        screen_id=legacy["id"],
        domain=legacy["domain"],
        title=legacy["title"],
        subtitle=legacy["subtitle"],
        data_sources=list(legacy.get("dataSources") or []),
        tables=list(legacy.get("tables") or []),
        summary=legacy.get("summary"),
        actions=legacy.get("actions"),
        workflow=legacy.get("workflow"),
        no_workflow_reason=legacy.get("noWorkflowReason"),
        table_profile=layout.get("tableProfile", "standard"),
        context_rail=layout.get("contextRail", "audit"),
        bundle_group=perf.get("bundleGroup"),
        payload_budget_kb=int(perf.get("initialPayloadBudgetKb") or 48),
        business_purpose=agent.get("businessPurpose") or legacy["subtitle"],
        example_prompts=list(agent.get("examplePrompts") or []),
        sensitive_fields=list(agent.get("sensitiveFields") or []),
        forbidden_agent_tasks=list(agent.get("forbiddenAgentTasks") or []),
        test_id=_test_id_from_agent_selectors(legacy["id"], agent.get("testSelectors")),
    )


def _validate_kontroll_worklist_contract(screen_id: str, definition: dict[str, Any]) -> None:
    workflow = definition.get("workflow")
    if workflow and workflow.get("phases"):
        raise ValueError(f"{screen_id}: KontrollWorklistParent verbietet workflow.phases (ProcessBand)")
    layout = definition.get("layout") or {}
    if layout.get("processRibbon"):
        raise ValueError(f"{screen_id}: KontrollWorklistParent verbietet processRibbon")
    tables = definition.get("tables") or []
    if not tables:
        raise ValueError(f"{screen_id}: KontrollWorklistParent erwartet mindestens eine Tabelle")
    for table in tables:
        if not table.get("virtualized"):
            raise ValueError(f"{screen_id}: Kontroll-Tabellen muessen virtualized sein")
    if not definition.get("noWorkflowReason") and not workflow:
        raise ValueError(f"{screen_id}: KontrollWorklistParent erwartet noWorkflowReason oder workflow")


def build_kontroll_worklist_screen(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    data_sources: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    business_purpose: str,
    example_prompts: list[str],
    test_id: str,
    summary: list[dict[str, Any]] | None = None,
    actions: list[dict[str, Any]] | None = None,
    no_workflow_reason: str | None = None,
    workflow: dict[str, Any] | None = None,
    table_profile: str = "financial",
    context_rail: str = "audit",
    bundle_group: str | None = None,
    payload_budget_kb: int = 48,
    sensitive_fields: list[str] | None = None,
    forbidden_agent_tasks: list[str] | None = None,
) -> dict[str, Any]:
    """Parent-Vertrag: worklist + expertDense + Audit-Rail; Child liefert Queue/Spalten."""
    layout = {
        **KONTROLL_WORKLIST_LAYOUT_KEYS,
        "contextRail": context_rail,
        "tableProfile": table_profile,
    }
    definition: dict[str, Any] = {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "list",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": data_sources,
        "tables": tables,
        "layout": layout,
        "performance": {
            "initialPayloadBudgetKb": payload_budget_kb,
            "requiresLazyTabs": False,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": bundle_group or domain,
        },
        "agentContract": {
            "businessPurpose": business_purpose,
            "examplePrompts": example_prompts,
            "sensitiveFields": list(sensitive_fields or []),
            "forbiddenAgentTasks": list(forbidden_agent_tasks or []),
            "testSelectors": {
                "screenRoot": f"[data-testid='{test_id}']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
    }
    if summary is not None:
        definition["summary"] = summary
    if actions:
        definition["actions"] = actions
    if no_workflow_reason is not None:
        definition["noWorkflowReason"] = no_workflow_reason
    if workflow is not None:
        definition["workflow"] = workflow
    _validate_kontroll_worklist_contract(screen_id, definition)
    return definition


def build_document_control_worklist(
    *,
    screen_id: str,
    title: str,
    subtitle: str,
    exception_type: str | None = None,
) -> dict[str, Any]:
    """Beleg-Kontrolle (Parent oder gefilterte Child-Variante)."""
    summary_endpoint = "/api/v1/document-control/summary"
    queue_endpoint = "/api/v1/document-control/exceptions"
    if exception_type:
        queue_endpoint = f"{queue_endpoint}?exception_type={exception_type}"
    test_id = "beleg-kontrolle" if screen_id == "auswertungen/beleg-kontrolle" else screen_id.replace("/", "-")
    business_purpose = subtitle if exception_type else (
        "Belegausnahmen mandantensicher priorisieren und zum Ursprungsbeleg springen."
    )
    return build_kontroll_worklist_screen(
        screen_id=screen_id,
        domain="finance",
        title=title,
        subtitle=subtitle,
        data_sources=kontroll_entity_and_queue_sources(
            summary_endpoint=summary_endpoint,
            queue_endpoint=queue_endpoint,
        ),
        summary=deepcopy(DOCUMENT_CONTROL_SUMMARY),
        tables=[
            kontroll_queue_table(
                table_key="exceptions",
                label="Ausnahmen",
                columns=deepcopy(DOCUMENT_CONTROL_EXCEPTION_COLUMNS),
                row_actions=deepcopy(DOCUMENT_CONTROL_ROW_ACTIONS),
            ),
        ],
        no_workflow_reason=DOCUMENT_CONTROL_NO_WORKFLOW_REASON,
        table_profile="financial",
        bundle_group="finance",
        business_purpose=business_purpose,
        example_prompts=list(DOCUMENT_CONTROL_AGENT_EXAMPLE_PROMPTS),
        sensitive_fields=list(DOCUMENT_CONTROL_SENSITIVE_FIELDS),
        forbidden_agent_tasks=list(DOCUMENT_CONTROL_FORBIDDEN_AGENT_TASKS),
        test_id=test_id,
    )


def build_document_control_variant(
    *,
    screen_id: str,
    title: str,
    subtitle: str,
    exception_type: str,
) -> dict[str, Any]:
    """Gefilterte L3-Worklist-Ansicht ueber die zentrale Beleg-Kontrolle."""
    return build_document_control_worklist(
        screen_id=screen_id,
        title=title,
        subtitle=subtitle,
        exception_type=exception_type,
    )


def build_sanctions_kontroll_worklist(
    *,
    screen_id: str,
    title: str,
    scope: str,
    subject_label: str,
) -> dict[str, Any]:
    """Terrorschutz-Pruefliste (Schwester-Child mit Primary-Action statt Queue-Zeilenworkflow)."""
    endpoint = f"/api/v1/compliance/sanctions/pruefprotokoll?scope={scope}"
    return build_kontroll_worklist_screen(
        screen_id=screen_id,
        domain="compliance",
        title=title,
        subtitle=f"{subject_label} gegen die freigegebenen Sanktionslisten pruefen und nachweisen",
        data_sources=[{"key": "checks", "endpoint": endpoint, "pageSize": 100, "staleTimeMs": 10_000}],
        tables=[{
            "key": "checks",
            "label": "Pruefprotokoll",
            "dataSourceKey": "checks",
            "serverPagination": False,
            "pageSize": 100,
            "virtualized": True,
            "rowHeight": 44,
            "columns": [
                {"key": "geprueft_am", "label": "Geprueft am", "renderKind": "datetime", "sortable": True, "width": 170},
                {"key": "entity_ref", "label": "Personal-/Kunden-Nr.", "filterable": True, "width": 155},
                {"key": "geprueft_name", "label": "Name", "filterable": True, "width": 250},
                {"key": "status", "label": "Ergebnis", "renderKind": "status", "filterable": True, "width": 135},
                {"key": "checked_by", "label": "Geprueft von", "filterable": True, "width": 180},
            ],
        }],
        actions=[{
            "key": "check",
            "label": f"{subject_label} pruefen",
            "kind": "primary",
            "permission": "compliance.sanctions.check",
            "dangerLevel": "moderate",
            "requiresConfirmation": True,
            "commandEndpoint": f"/api/v1/compliance/sanctions/actions/pruefen/{scope}",
            "method": "POST",
            "inputFields": [
                {"key": "name", "label": "Name", "type": "text", "required": True},
                {"key": "entity_ref", "label": "Personal-/Kunden-Nr.", "type": "text", "required": False},
            ],
        }],
        workflow={
            "processKey": f"sanctions-check-{scope}",
            "status": "audited",
            "nextActionKey": "check",
            "auditRequired": True,
        },
        table_profile="audit",
        bundle_group="compliance",
        payload_budget_kb=35,
        business_purpose=f"Terrorschutzpruefungen fuer {subject_label} getrennt und mandantensicher nachweisen.",
        example_prompts=[
            f"Pruefe {subject_label} gegen die Sanktionsliste.",
            "Zeige verdaechtige Treffer.",
        ],
        sensitive_fields=["geprueft_name", "entity_ref", "checked_by"],
        forbidden_agent_tasks=["Treffer automatisch freigeben oder Pruefprotokolle veraendern"],
        test_id=f"{scope}-sanctions-check",
    )


def _default_test_id(screen_id: str) -> str:
    return screen_id.replace("/", "-")


def build_queue_kontroll_screen(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    queue_endpoint: str,
    columns: list[dict[str, Any]],
    business_purpose: str,
    example_prompts: list[str],
    queue_key: str = "items",
    summary_endpoint: str | None = None,
    summary: list[dict[str, Any]] | None = None,
    row_actions: list[dict[str, Any]] | None = None,
    actions: list[dict[str, Any]] | None = None,
    no_workflow_reason: str | None = None,
    table_profile: str = "standard",
    context_rail: str = "audit",
    bundle_group: str | None = None,
    test_id: str | None = None,
    sensitive_fields: list[str] | None = None,
    forbidden_agent_tasks: list[str] | None = None,
    page_size: int = 50,
) -> dict[str, Any]:
    """Kompakter Kontroll-Child: eine Queue (+ optional KPI-Lagebild)."""
    if summary_endpoint:
        data_sources = kontroll_entity_and_queue_sources(
            summary_endpoint=summary_endpoint,
            queue_endpoint=queue_endpoint,
            queue_key=queue_key,
            page_size=page_size,
        )
    else:
        data_sources = [{"key": queue_key, "endpoint": queue_endpoint, "pageSize": page_size, "staleTimeMs": 10_000}]
    return build_kontroll_worklist_screen(
        screen_id=screen_id,
        domain=domain,
        title=title,
        subtitle=subtitle,
        data_sources=data_sources,
        summary=summary,
        tables=[
            kontroll_queue_table(
                table_key=queue_key,
                label=title,
                columns=columns,
                row_actions=row_actions or [{"key": "open_source", "label": "Oeffnen"}],
                data_source_key=queue_key,
                page_size=page_size,
            ),
        ],
        actions=actions,
        no_workflow_reason=no_workflow_reason or "Statuswechsel erfolgen in Fachdialogen oder auditierten Kommandos.",
        table_profile=table_profile,
        context_rail=context_rail,
        bundle_group=bundle_group or domain,
        business_purpose=business_purpose,
        example_prompts=example_prompts,
        sensitive_fields=list(sensitive_fields or []),
        forbidden_agent_tasks=list(forbidden_agent_tasks or []),
        test_id=test_id or _default_test_id(screen_id),
    )
