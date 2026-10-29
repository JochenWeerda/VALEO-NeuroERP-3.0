"""Finisher ScreenDefinitions for last handgebaut routes."""
from __future__ import annotations
from typing import Any
from app.core.cockpit_overview_parent import (
    build_cockpit_overview_screen,
    cockpit_entity_source,
    cockpit_refresh_action,
    cockpit_summary_table,
)
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action


def build_document_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="document",
        domain="workspace",
        title="Dokument",
        subtitle="workspace",
        business_purpose="Dokument mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Dokument."],
        test_id="document",
        data_sources=[cockpit_entity_source("/api/mcp/documents/analytics/customer-analytics")],
        tables=[cockpit_summary_table(table_key="list", label="Dokument", columns=cols)],
        actions=[cockpit_refresh_action(permission="read")],
        context_rail="combined",
    )


def build_einstellungen_system_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="einstellungen/system",
        domain="admin",
        title="Systemeinstellungen",
        subtitle="admin",
        business_purpose="Systemeinstellungen mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Systemeinstellungen."],
        test_id="einstellungen-system",
        data_sources=[cockpit_entity_source("/api/v1/config/system")],
        tables=[cockpit_summary_table(table_key="list", label="Systemeinstellungen", columns=cols)],
        actions=[cockpit_refresh_action(permission="admin.read")],
        context_rail="combined",
    )


def build_finance_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="finance",
        domain="finance",
        title="Finance",
        subtitle="finance",
        business_purpose="Finance mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Finance."],
        test_id="finance",
        data_sources=[cockpit_entity_source("/api/v1/finance/overview")],
        tables=[cockpit_summary_table(table_key="list", label="Finance", columns=cols)],
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_inventory_adjust_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="inventory/adjust",
        domain="lager",
        title="Bestandskorrektur",
        subtitle="lager",
        endpoint="/api/v1/inventory/adjustments",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bestandskorrektur finden und auswerten.",
        prompts=["Zeige Bestandskorrektur."],
        bundle="lager",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_lager_bestandsuebersicht_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="lager/bestandsuebersicht",
        domain="lager",
        title="Bestandsübersicht",
        subtitle="lager",
        endpoint="/api/v1/inventory/stock",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bestandsübersicht finden und auswerten.",
        prompts=["Zeige Bestandsübersicht."],
        bundle="lager",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_nawaro_vertraege_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="nawaro/vertraege",
        domain="nawaro",
        title="NaWaRo-Verträge",
        subtitle="nawaro",
        endpoint="/api/v1/nawaro/vertraege",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="NaWaRo-Verträge finden und auswerten.",
        prompts=["Zeige NaWaRo-Verträge."],
        bundle="nawaro",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_portal_portal_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="portal/portal",
        domain="portal",
        title="Portal",
        subtitle="portal",
        business_purpose="Portal mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Portal."],
        test_id="portal-portal",
        data_sources=[cockpit_entity_source("/api/v1/portal/overview")],
        tables=[cockpit_summary_table(table_key="list", label="Portal", columns=cols)],
        actions=[cockpit_refresh_action(permission="portal.read")],
        context_rail="combined",
    )


def build_pricing_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="pricing",
        domain="preise",
        title="Preise",
        subtitle="preise",
        business_purpose="Preise mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Preise."],
        test_id="pricing",
        data_sources=[cockpit_entity_source("/api/v1/pricing/overview")],
        tables=[cockpit_summary_table(table_key="list", label="Preise", columns=cols)],
        actions=[cockpit_refresh_action(permission="preise.read")],
        context_rail="combined",
    )


def build_schichtplan_liste_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="schichtplan/liste",
        domain="personal",
        title="Schichtplan",
        subtitle="personal",
        endpoint="/api/v1/personal/schichtplan",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Schichtplan finden und auswerten.",
        prompts=["Zeige Schichtplan."],
        bundle="personal",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_termine_kalender_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="termine/kalender",
        domain="termine",
        title="Kalender",
        subtitle="termine",
        business_purpose="Kalender mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Kalender."],
        test_id="termine-kalender",
        data_sources=[cockpit_entity_source("/api/v1/calendar/events")],
        tables=[cockpit_summary_table(table_key="list", label="Kalender", columns=cols)],
        actions=[cockpit_refresh_action(permission="termine.read")],
        context_rail="combined",
    )


def build_weighing_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="weighing",
        domain="waage",
        title="Wiegung",
        subtitle="waage",
        endpoint="/api/v1/weighing/sessions",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Wiegung finden und auswerten.",
        prompts=["Zeige Wiegung."],
        bundle="waage",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_workflows_approval_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="workflows/approval",
        domain="workflow",
        title="Freigaben",
        subtitle="workflow",
        endpoint="/api/v1/workflows/approvals",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Freigaben finden und auswerten.",
        prompts=["Zeige Freigaben."],
        bundle="workflow",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )


def build_workflows_trigger_screen_definition() -> dict[str, Any]:
    return build_stamm_list_screen(
        screen_id="workflows/trigger",
        domain="workflow",
        title="Workflow-Trigger",
        subtitle="workflow",
        endpoint="/api/v1/workflows/triggers",
        row_route=None,
        columns=[{"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160}],
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Workflow-Trigger finden und auswerten.",
        prompts=["Zeige Workflow-Trigger."],
        bundle="workflow",
        no_workflow="Read-Model-Liste ohne Prozessband.",
    )

FINISHER_SCREEN_BUILDERS: dict[str, Any] = {
    "document": build_document_screen_definition,
    "einstellungen/system": build_einstellungen_system_screen_definition,
    "finance": build_finance_screen_definition,
    "inventory/adjust": build_inventory_adjust_screen_definition,
    "lager/bestandsuebersicht": build_lager_bestandsuebersicht_screen_definition,
    "nawaro/vertraege": build_nawaro_vertraege_screen_definition,
    "portal/portal": build_portal_portal_screen_definition,
    "pricing": build_pricing_screen_definition,
    "schichtplan/liste": build_schichtplan_liste_screen_definition,
    "termine/kalender": build_termine_kalender_screen_definition,
    "weighing": build_weighing_screen_definition,
    "workflows/approval": build_workflows_approval_screen_definition,
    "workflows/trigger": build_workflows_trigger_screen_definition,
}
