"""Domain ScreenDefinitions — Batch 15 (einkauf/preisspiegel .. workflow, auto-generated)."""
from __future__ import annotations

from typing import Any

from app.core.cockpit_overview_parent import (
    build_cockpit_overview_screen,
    cockpit_entity_source,
    cockpit_refresh_action,
    cockpit_summary_table,
)
from app.core.kontroll_worklist_parent import (
    build_kontroll_worklist_screen,
    kontroll_entity_and_queue_sources,
    kontroll_queue_table,
)
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action
from app.core.stamm_object_page_parent import (
    build_stamm_object_page,
    stamm_entity_source,
    stamm_kopf_tab,
)


def build_contracts_v2_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="contracts-v2",
        domain="workspace",
        title="Contracts v2",
        subtitle="workspace",
        endpoint="/api/v1/kontrakte",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Contracts v2 im workspace-Bereich finden und auswerten.",
        prompts=["Zeige Contracts v2.", "Filtere die Liste."],
        bundle="workspace",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_rechnung_abgleich_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/rechnung-abgleich",
        domain="einkauf",
        title="Rechnung abgleich",
        subtitle="einkauf",
        endpoint="/api/v1/einkauf/rechnungseingaenge",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rechnung abgleich im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Rechnung abgleich.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_rechnung_eingang_erfassung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/rechnung-eingang-erfassung",
        domain="einkauf",
        title="Rechnung eingang erfassung",
        subtitle="einkauf",
        endpoint="/api/v1/crm/customers/",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rechnung eingang erfassung im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Rechnung eingang erfassung.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_rechnungseingang_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "stammdaten", "label": "Stammdaten", "sortable": True, "filterable": True, "width": 160}, {"key": "betrag", "label": "Betrag", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlung", "label": "Zahlung", "sortable": True, "filterable": True, "width": 160}, {"key": "positionen", "label": "Positionen", "sortable": True, "filterable": True, "width": 160}, {"key": "artikelId", "label": "Artikelid", "sortable": True, "filterable": True, "width": 160}, {"key": "menge", "label": "Menge", "sortable": True, "filterable": True, "width": 160}, {"key": "preis", "label": "Preis", "sortable": True, "filterable": True, "width": 160}, {"key": "steuerSatz", "label": "Steuersatz", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/rechnungseingang/neu",
        domain="einkauf",
        title="Vorgang",
        subtitle="einkauf",
        endpoint="/api/v1/finance/chart-of-accounts/",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Vorgang im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Vorgang.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_reports_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="einkauf/reports",
        domain="einkauf",
        title="Reports",
        subtitle="einkauf",
        business_purpose="Reports mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Reports.", "Aktualisiere die Kennzahlen."],
        test_id="einkauf-reports",
        data_sources=[cockpit_entity_source("/api/v1/einkauf/anfragen")],
        tables=[cockpit_summary_table(table_key="list", label="Reports", columns=cols)],
        actions=[cockpit_refresh_action(permission="einkauf.read")],
        context_rail="combined",
    )


def build_einkauf_retouren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/retouren",
        domain="einkauf",
        title="Retouren",
        subtitle="einkauf",
        endpoint="/api/v1/einkauf/retouren",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Retouren im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Retouren.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_rfq_bids_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/rfq-bids",
        domain="einkauf",
        title="Rfq bids",
        subtitle="einkauf",
        endpoint="/api/v1/einkauf/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rfq bids im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Rfq bids.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_service_entry_sheets_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/service-entry-sheets",
        domain="einkauf",
        title="Service entry sheets",
        subtitle="einkauf",
        endpoint="/api/v1/einkauf/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Service entry sheets im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Service entry sheets.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_wareneingang_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/wareneingang",
        domain="einkauf",
        title="Wareneingang",
        subtitle="einkauf",
        endpoint="/api/v1/purchase-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Wareneingang im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Wareneingang.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_einkauf_wareneingangsabgleich_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="einkauf/wareneingangsabgleich",
        domain="einkauf",
        title="Wareneingangsabgleich",
        subtitle="einkauf",
        endpoint="/api/v1/einkauf/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Wareneingangsabgleich im einkauf-Bereich finden und auswerten.",
        prompts=["Zeige Wareneingangsabgleich.", "Filtere die Liste."],
        bundle="einkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_etiketten_drucken_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="etiketten/drucken",
        domain="etiketten",
        title="Drucken",
        subtitle="etiketten",
        endpoint="/api/v1/etiketten/druckauftrag",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Drucken im etiketten-Bereich finden und auswerten.",
        prompts=["Zeige Drucken.", "Filtere die Liste."],
        bundle="etiketten",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_export_ustva_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="export/ustva",
        domain="export",
        title="Umsatzsteuervoranmeldung",
        subtitle="export",
        endpoint="/api/v1/export/entities",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Umsatzsteuervoranmeldung im export-Bereich finden und auswerten.",
        prompts=["Zeige Umsatzsteuervoranmeldung.", "Filtere die Liste."],
        bundle="export",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_abschluss_checklist_detail_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/abschluss-checklist-detail",
        domain="fibu",
        title="Abschluss checklist detail",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/buchungen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Abschluss checklist detail als Stammblatt pflegen.",
        example_prompts=["Oeffne Abschluss checklist detail.", "Bearbeite Stammdaten."],
        test_id="fibu-abschluss-checklist-detail",
    )


def build_fibu_anlagen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "anlagennr", "label": "Anlagennr", "sortable": True, "filterable": True, "width": 160}, {"key": "bezeichnung", "label": "Bezeichnung", "sortable": True, "filterable": True, "width": 160}, {"key": "anschaffung", "label": "Anschaffung", "sortable": True, "filterable": True, "width": 160}, {"key": "anschaffungswert", "label": "Anschaffungswert", "sortable": True, "filterable": True, "width": 160}, {"key": "afaSatz", "label": "Afasatz", "sortable": True, "filterable": True, "width": 160}, {"key": "kumulierteAfa", "label": "Kumulierteafa", "sortable": True, "filterable": True, "width": 160}, {"key": "buchwert", "label": "Buchwert", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/anlagen",
        domain="fibu",
        title="Anlagen Gesamt",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Anlagen Gesamt im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Anlagen Gesamt.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_anlagen_suite_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/anlagen-suite",
        domain="fibu",
        title="Anlagen suite",
        subtitle="fibu",
        endpoint="/api/v1/finance/asset-ledger-connector/config",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Anlagen suite im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Anlagen suite.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_atlas_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/atlas",
        domain="fibu",
        title="Atlas",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Atlas im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Atlas.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_bilanz_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/bilanz",
        domain="fibu",
        title="Bilanz",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bilanz im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Bilanz.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_buchhaltungsuebersicht_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="fibu/buchhaltungsuebersicht",
        domain="fibu",
        title="Buchhaltungsuebersicht",
        subtitle="fibu",
        business_purpose="Buchhaltungsuebersicht mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Buchhaltungsuebersicht.", "Aktualisiere die Kennzahlen."],
        test_id="fibu-buchhaltungsuebersicht",
        data_sources=[cockpit_entity_source("/api/v1/fibu/anlagen")],
        tables=[cockpit_summary_table(table_key="list", label="Buchhaltungsuebersicht", columns=cols)],
        actions=[cockpit_refresh_action(permission="fibu.read")],
        context_rail="combined",
    )


def build_fibu_buchungsuebernahme_connectors_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/buchungsuebernahme-connectors",
        domain="fibu",
        title="Buchungsuebernahme connectors",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Buchungsuebernahme connectors im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Buchungsuebernahme connectors.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_bwa_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/bwa",
        domain="fibu",
        title="Bwa",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bwa im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Bwa.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_debitoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/debitoren",
        domain="fibu",
        title="Debitoren",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Debitoren im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Debitoren.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_debitoren_api_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/debitoren-api",
        domain="fibu",
        title="Debitoren api",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Debitoren api im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Debitoren api.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_elster_online_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/elster-online",
        domain="fibu",
        title="Elster online",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Elster online im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Elster online.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_erloeskennziffern_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/erloeskennziffern",
        domain="fibu",
        title="Erloeskennziffern",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Erloeskennziffern im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Erloeskennziffern.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_erloeskontenzuordnung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/erloeskontenzuordnung",
        domain="fibu",
        title="Erloeskontenzuordnung",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Erloeskontenzuordnung im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Erloeskontenzuordnung.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_forderungsgruppen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/forderungsgruppen",
        domain="fibu",
        title="Forderungsgruppen",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Forderungsgruppen im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Forderungsgruppen.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_geschaeftsjahre_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/geschaeftsjahre",
        domain="fibu",
        title="Neues Geschäftsjahr [JAHR]",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/geschaeftsjahre/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neues Geschäftsjahr [JAHR] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neues Geschäftsjahr [JAHR].", "Bearbeite Stammdaten."],
        test_id="fibu-geschaeftsjahre",
    )


def build_fibu_guv_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/guv",
        domain="fibu",
        title="Guv",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Guv im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Guv.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_hauptbuch_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/hauptbuch",
        domain="fibu",
        title="Hauptbuch",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Hauptbuch im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Hauptbuch.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_kontenplan_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/kontenplan",
        domain="fibu",
        title="Kontenplan",
        subtitle="fibu",
        endpoint="/api/v1/finance/chart-of-accounts/",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kontenplan im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Kontenplan.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_kostenstellenrechnung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/kostenstellenrechnung",
        domain="fibu",
        title="Kostenstellenrechnung",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kostenstellenrechnung im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Kostenstellenrechnung.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_kreditlinien_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/kreditlinien",
        domain="fibu",
        title="Kreditlinien",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kreditlinien im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Kreditlinien.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_kreditoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/kreditoren",
        domain="fibu",
        title="Kreditoren",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kreditoren im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Kreditoren.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_lohn_connector_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/lohn-connector",
        domain="fibu",
        title="Lohn connector",
        subtitle="fibu",
        endpoint="/api/v1/finance/lohn-connector/runs",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lohn connector im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Lohn connector.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_monatswerte_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/monatswerte",
        domain="fibu",
        title="Monatswerte",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Monatswerte im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Monatswerte.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_op_skonto_auszifferung_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/op-skonto-auszifferung",
        domain="fibu",
        title="Auszifferungen",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/op-auszifferung/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Auszifferungen als Stammblatt pflegen.",
        example_prompts=["Oeffne Auszifferungen.", "Bearbeite Stammdaten."],
        test_id="fibu-op-skonto-auszifferung",
    )


def build_fibu_op_verwaltung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/op-verwaltung",
        domain="fibu",
        title="Op verwaltung",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Op verwaltung im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Op verwaltung.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_periodische_buchungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/periodische-buchungen",
        domain="fibu",
        title="Periodische buchungen",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Periodische buchungen im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Periodische buchungen.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_quadriga_connector_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/quadriga-connector",
        domain="fibu",
        title="Quadriga connector",
        subtitle="fibu",
        endpoint="/api/v1/finance/quadriga-connector/config",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Quadriga connector im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Quadriga connector.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_sachkonto_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/sachkonto",
        domain="fibu",
        title="Sachkonto",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Sachkonto im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Sachkonto.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_schnittstelle_fibu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/schnittstelle-fibu",
        domain="fibu",
        title="Schnittstelle fibu",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Schnittstelle fibu im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Schnittstelle fibu.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_schnittstellen_center_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/schnittstellen-center",
        domain="fibu",
        title="Schnittstellen center",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Schnittstellen center im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Schnittstellen center.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_sicherheiten_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/sicherheiten",
        domain="fibu",
        title="Sicherheiten",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Sicherheiten im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Sicherheiten.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_stammdaten_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/stammdaten",
        domain="fibu",
        title="Neues Zahlungsformular [FIZAF]",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/stammdaten/zahlungsformulare/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neues Zahlungsformular [FIZAF] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neues Zahlungsformular [FIZAF].", "Bearbeite Stammdaten."],
        test_id="fibu-stammdaten",
    )


def build_fibu_verbindlichkeiten_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/verbindlichkeiten",
        domain="fibu",
        title="Verbindlichkeiten",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Verbindlichkeiten im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Verbindlichkeiten.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_zahlungseingaenge_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/zahlungseingaenge",
        domain="fibu",
        title="Zahlungseingaenge",
        subtitle="fibu",
        endpoint="/api/v1/finance/bank-accounts",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zahlungseingaenge im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Zahlungseingaenge.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_zahlungslaeufe_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/zahlungslaeufe",
        domain="fibu",
        title="Zahlungslaeufe",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zahlungslaeufe im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Zahlungslaeufe.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fibu_zahlungsmeldungen_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/zahlungsmeldungen",
        domain="fibu",
        title="Neue Zahlungsmeldung [KASSZAME]",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/zahlungsmeldungen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Zahlungsmeldung [KASSZAME] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Zahlungsmeldung [KASSZAME].", "Bearbeite Stammdaten."],
        test_id="fibu-zahlungsmeldungen",
    )


def build_fibu_zahlungsvorschlaege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fibu/zahlungsvorschlaege",
        domain="fibu",
        title="Zahlungsvorschlaege",
        subtitle="fibu",
        endpoint="/api/v1/fibu/anlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zahlungsvorschlaege im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Zahlungsvorschlaege.", "Filtere die Liste."],
        bundle="fibu",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_abschluss_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "bilanz", "label": "Bilanz", "sortable": True, "filterable": True, "width": 160}, {"key": "guv", "label": "Guv", "sortable": True, "filterable": True, "width": 160}, {"key": "abgrenzungen", "label": "Abgrenzungen", "sortable": True, "filterable": True, "width": 160}, {"key": "abgrenzungen_custom", "label": "Abgrenzungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "rueckstellungen", "label": "Rueckstellungen", "sortable": True, "filterable": True, "width": 160}, {"key": "rueckstellungen_custom", "label": "Rueckstellungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "pruefungen", "label": "Pruefungen", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/abschluss",
        domain="finance",
        title="Monats-/Jahresabschluss",
        subtitle="finance",
        endpoint="/api/v1/finance/closing-checklists",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Monats-/Jahresabschluss im finance-Bereich finden und auswerten.",
        prompts=["Zeige Monats-/Jahresabschluss.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_ap_invoices_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/ap/invoices",
        domain="finance",
        title="Ap invoices list",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Ap invoices list im finance-Bereich finden und auswerten.",
        prompts=["Zeige Ap invoices list.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_ap_invoices_new_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/ap/invoices/new",
        domain="finance",
        title="Ap invoice form",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Ap invoice form im finance-Bereich finden und auswerten.",
        prompts=["Zeige Ap invoice form.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_bank_abgleich_screen_definition() -> dict[str, Any]:
    columns = [{"key": "import", "label": "Import", "sortable": True, "filterable": True, "width": 160}, {"key": "salden", "label": "Salden", "sortable": True, "filterable": True, "width": 160}, {"key": "zuordnung", "label": "Zuordnung", "sortable": True, "filterable": True, "width": 160}, {"key": "zuordnung_custom", "label": "Zuordnung Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "import_protokoll", "label": "Import Protokoll", "sortable": True, "filterable": True, "width": 160}, {"key": "abgleich", "label": "Abgleich", "sortable": True, "filterable": True, "width": 160}, {"key": "validate", "label": "Validate", "sortable": True, "filterable": True, "width": 160}, {"key": "export", "label": "Export", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/bank-abgleich",
        domain="finance",
        title="Objekt",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Objekt im finance-Bereich finden und auswerten.",
        prompts=["Zeige Objekt.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_bank_stamm_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="finance/bank-stamm",
        domain="finance",
        title="Bank stamm",
        subtitle="finance",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/finance/abstimmung/nebenbuch/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="finance.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Bank stamm als Stammblatt pflegen.",
        example_prompts=["Oeffne Bank stamm.", "Bearbeite Stammdaten."],
        test_id="finance-bank-stamm",
    )


def build_finance_bankkonten_stamm_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="finance/bankkonten-stamm",
        domain="finance",
        title="Bankkonten stamm",
        subtitle="finance",
        identity_field="grunddaten",
        data_sources=[stamm_entity_source("/api/v1/finance/bank-accounts/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "grunddaten", "label": "Grunddaten", "type": "text"}, {"key": "save", "label": "Save", "type": "text"}, {"key": "validate", "label": "Validate", "type": "text"}, {"key": "export", "label": "Export", "type": "text"}])],
        edit_permission="finance.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Bankkonten stamm als Stammblatt pflegen.",
        example_prompts=["Oeffne Bankkonten stamm.", "Bearbeite Stammdaten."],
        test_id="finance-bankkonten-stamm",
    )


def build_finance_bookings_new_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/bookings/new",
        domain="finance",
        title="Buchungsjournal",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Buchungsjournal im finance-Bereich finden und auswerten.",
        prompts=["Zeige Buchungsjournal.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_buchungserfassung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "allgemein", "label": "Allgemein", "sortable": True, "filterable": True, "width": 160}, {"key": "buchungszeilen", "label": "Buchungszeilen", "sortable": True, "filterable": True, "width": 160}, {"key": "buchungszeilen_custom", "label": "Buchungszeilen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "summen", "label": "Summen", "sortable": True, "filterable": True, "width": 160}, {"key": "anhaenge", "label": "Anhaenge", "sortable": True, "filterable": True, "width": 160}, {"key": "validate", "label": "Validate", "sortable": True, "filterable": True, "width": 160}, {"key": "save", "label": "Save", "sortable": True, "filterable": True, "width": 160}, {"key": "storno", "label": "Storno", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/buchungserfassung",
        domain="finance",
        title="Vorgang",
        subtitle="finance",
        endpoint="/api/v1/journal-entries",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Vorgang im finance-Bereich finden und auswerten.",
        prompts=["Zeige Vorgang.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_buchungsimport_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/buchungsimport",
        domain="finance",
        title="Buchungsimport",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Buchungsimport im finance-Bereich finden und auswerten.",
        prompts=["Zeige Buchungsimport.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_datev_export_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/datev-export",
        domain="finance",
        title="Datev export",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Datev export im finance-Bereich finden und auswerten.",
        prompts=["Zeige Datev export.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_debitoren_new_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="finance/debitoren/new",
        domain="finance",
        title="Debitoren stamm",
        subtitle="finance",
        identity_field="stammdaten",
        data_sources=[stamm_entity_source("/api/v1/finance/debtors/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "stammdaten", "label": "Stammdaten", "type": "text"}, {"key": "kontakt", "label": "Kontakt", "type": "text"}, {"key": "bankverbindung", "label": "Bankverbindung", "type": "text"}, {"key": "konditionen", "label": "Konditionen", "type": "text"}, {"key": "notizen", "label": "Notizen", "type": "text"}, {"key": "validate", "label": "Validate", "type": "text"}])],
        edit_permission="finance.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Debitoren stamm als Stammblatt pflegen.",
        example_prompts=["Oeffne Debitoren stamm.", "Bearbeite Stammdaten."],
        test_id="finance-debitoren-new",
    )


def build_finance_dunning_editor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "betrag", "label": "Betrag", "sortable": True, "filterable": True, "width": 160}, {"key": "text", "label": "Text", "sortable": True, "filterable": True, "width": 160}, {"key": "versand", "label": "Versand", "sortable": True, "filterable": True, "width": 160}, {"key": "notizen", "label": "Notizen", "sortable": True, "filterable": True, "width": 160}, {"key": "generate", "label": "Generate", "sortable": True, "filterable": True, "width": 160}, {"key": "preview", "label": "Preview", "sortable": True, "filterable": True, "width": 160}, {"key": "send", "label": "Send", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/dunning-editor",
        domain="finance",
        title="Mahnvorgang",
        subtitle="finance",
        endpoint="/api/v1/finance/debtors",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Mahnvorgang im finance-Bereich finden und auswerten.",
        prompts=["Zeige Mahnvorgang.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_invoices_list_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/invoices-list",
        domain="finance",
        title="Invoices list",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Invoices list im finance-Bereich finden und auswerten.",
        prompts=["Zeige Invoices list.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_invoices_new_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/invoices/new",
        domain="finance",
        title="Invoice form",
        subtitle="finance",
        endpoint="/api/v1/finance/invoices",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Invoice form im finance-Bereich finden und auswerten.",
        prompts=["Zeige Invoice form.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_kasse_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "soll", "label": "Soll", "sortable": True, "filterable": True, "width": 160}, {"key": "ist", "label": "Ist", "sortable": True, "filterable": True, "width": 160}, {"key": "bewegungen", "label": "Bewegungen", "sortable": True, "filterable": True, "width": 160}, {"key": "bewegungen_custom", "label": "Bewegungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "kassensturz", "label": "Kassensturz", "sortable": True, "filterable": True, "width": 160}, {"key": "kassensturz_custom", "label": "Kassensturz Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "abschluss", "label": "Abschluss", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/kasse",
        domain="finance",
        title="Kasse",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kasse im finance-Bereich finden und auswerten.",
        prompts=["Zeige Kasse.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_kontenplan_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/kontenplan",
        domain="finance",
        title="Chart of accounts",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Chart of accounts im finance-Bereich finden und auswerten.",
        prompts=["Zeige Chart of accounts.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_kreditoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/kreditoren",
        domain="finance",
        title="Kreditoren liste",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kreditoren liste im finance-Bereich finden und auswerten.",
        prompts=["Zeige Kreditoren liste.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_kreditoren_stamm_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="finance/kreditoren-stamm",
        domain="finance",
        title="Kreditoren stamm",
        subtitle="finance",
        identity_field="stammdaten",
        data_sources=[stamm_entity_source("/api/v1/finance/creditors/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "stammdaten", "label": "Stammdaten", "type": "text"}, {"key": "kontakt", "label": "Kontakt", "type": "text"}, {"key": "bankverbindung", "label": "Bankverbindung", "type": "text"}, {"key": "konditionen", "label": "Konditionen", "type": "text"}, {"key": "compliance", "label": "Compliance", "type": "text"}, {"key": "notizen", "label": "Notizen", "type": "text"}])],
        edit_permission="finance.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kreditoren stamm als Stammblatt pflegen.",
        example_prompts=["Oeffne Kreditoren stamm.", "Bearbeite Stammdaten."],
        test_id="finance-kreditoren-stamm",
    )


def build_finance_lastschriften_debitoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "creditor", "label": "Creditor", "sortable": True, "filterable": True, "width": 160}, {"key": "lastschriften", "label": "Lastschriften", "sortable": True, "filterable": True, "width": 160}, {"key": "lastschriften_custom", "label": "Lastschriften Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "freigabe", "label": "Freigabe", "sortable": True, "filterable": True, "width": 160}, {"key": "notizen", "label": "Notizen", "sortable": True, "filterable": True, "width": 160}, {"key": "preview", "label": "Preview", "sortable": True, "filterable": True, "width": 160}, {"key": "approve", "label": "Approve", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/lastschriften-debitoren",
        domain="finance",
        title="Debitorenlauf",
        subtitle="finance",
        endpoint="/api/v1/finance/direct-debits",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Debitorenlauf im finance-Bereich finden und auswerten.",
        prompts=["Zeige Debitorenlauf.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_nebenbuch_abstimmung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/nebenbuch-abstimmung",
        domain="finance",
        title="Nebenbuch abstimmung",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Nebenbuch abstimmung im finance-Bereich finden und auswerten.",
        prompts=["Zeige Nebenbuch abstimmung.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_offene_posten_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/offene-posten",
        domain="finance",
        title="Offene posten",
        subtitle="finance",
        endpoint="/api/v1/finance/open-items",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Offene posten im finance-Bereich finden und auswerten.",
        prompts=["Zeige Offene posten.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_op_debitoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "betrag", "label": "Betrag", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlungen", "label": "Zahlungen", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlungen_custom", "label": "Zahlungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "mahnwesen", "label": "Mahnwesen", "sortable": True, "filterable": True, "width": 160}, {"key": "ausgleichshistorie", "label": "Ausgleichshistorie", "sortable": True, "filterable": True, "width": 160}, {"key": "notizen", "label": "Notizen", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlung", "label": "Zahlung", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/op-debitoren",
        domain="finance",
        title="OP-Lage",
        subtitle="finance",
        endpoint="/api/v1/finance/dunning",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="OP-Lage im finance-Bereich finden und auswerten.",
        prompts=["Zeige OP-Lage.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_op_kreditoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/op-kreditoren",
        domain="finance",
        title="Op kreditoren",
        subtitle="finance",
        endpoint="/api/v1/finance/open-items",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Op kreditoren im finance-Bereich finden und auswerten.",
        prompts=["Zeige Op kreditoren.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_payments_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/payments",
        domain="finance",
        title="Payment matching",
        subtitle="finance",
        endpoint="/api/v1/finance/payments/unmatched",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Payment matching im finance-Bereich finden und auswerten.",
        prompts=["Zeige Payment matching.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_periodenabschluss_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/periodenabschluss",
        domain="finance",
        title="Periodenabschluss",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Periodenabschluss im finance-Bereich finden und auswerten.",
        prompts=["Zeige Periodenabschluss.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_periods_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/periods",
        domain="finance",
        title="Periods",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Periods im finance-Bereich finden und auswerten.",
        prompts=["Zeige Periods.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_skonto_optimizer_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/skonto-optimizer",
        domain="finance",
        title="Skonto optimizer",
        subtitle="finance",
        endpoint="/api/v1/finance/open-items",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Skonto optimizer im finance-Bereich finden und auswerten.",
        prompts=["Zeige Skonto optimizer.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_umsatz_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="finance/umsatz",
        domain="finance",
        title="Reports",
        subtitle="finance",
        business_purpose="Reports mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Reports.", "Aktualisiere die Kennzahlen."],
        test_id="finance-umsatz",
        data_sources=[cockpit_entity_source("/api/v1/finance/financial-reports/bwa")],
        tables=[cockpit_summary_table(table_key="list", label="Reports", columns=cols)],
        actions=[cockpit_refresh_action(permission="finance.read")],
        context_rail="combined",
    )


def build_finance_ustva_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "umsatz", "label": "Umsatz", "sortable": True, "filterable": True, "width": 160}, {"key": "vorsteuer", "label": "Vorsteuer", "sortable": True, "filterable": True, "width": 160}, {"key": "berechnung", "label": "Berechnung", "sortable": True, "filterable": True, "width": 160}, {"key": "abweichungen", "label": "Abweichungen", "sortable": True, "filterable": True, "width": 160}, {"key": "abweichungen_custom", "label": "Abweichungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "freigabe", "label": "Freigabe", "sortable": True, "filterable": True, "width": 160}, {"key": "notizen", "label": "Notizen", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/ustva",
        domain="finance",
        title="Meldekontext",
        subtitle="finance",
        endpoint="/api/v1/finance/vat-return",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Meldekontext im finance-Bereich finden und auswerten.",
        prompts=["Zeige Meldekontext.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_zahlungseingang_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/zahlungseingang",
        domain="finance",
        title="Zahlungseingang",
        subtitle="finance",
        endpoint="/api/v1/finance/abstimmung/nebenbuch",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zahlungseingang im finance-Bereich finden und auswerten.",
        prompts=["Zeige Zahlungseingang.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_zahlungslauf_kreditoren_screen_definition() -> dict[str, Any]:
    columns = [{"key": "grunddaten", "label": "Grunddaten", "sortable": True, "filterable": True, "width": 160}, {"key": "auftraggeber", "label": "Auftraggeber", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlungen", "label": "Zahlungen", "sortable": True, "filterable": True, "width": 160}, {"key": "zahlungen_custom", "label": "Zahlungen Custom", "sortable": True, "filterable": True, "width": 160}, {"key": "freigabe", "label": "Freigabe", "sortable": True, "filterable": True, "width": 160}, {"key": "notizen", "label": "Notizen", "sortable": True, "filterable": True, "width": 160}, {"key": "approve", "label": "Approve", "sortable": True, "filterable": True, "width": 160}, {"key": "sepaPreview", "label": "Sepapreview", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finance/zahlungslauf-kreditoren",
        domain="finance",
        title="Zahlungslage",
        subtitle="finance",
        endpoint="/api/v1/finance/payment-runs",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zahlungslage im finance-Bereich finden und auswerten.",
        prompts=["Zeige Zahlungslage.", "Filtere die Liste."],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finanzplanung_liquiditaet_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="finanzplanung/liquiditaet",
        domain="finanzplanung",
        title="Liquiditaet",
        subtitle="finanzplanung",
        endpoint="/api/v1/finance/liquidity/overview",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Liquiditaet im finanzplanung-Bereich finden und auswerten.",
        prompts=["Zeige Liquiditaet.", "Filtere die Liste."],
        bundle="finanzplanung",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_foerderung_antrag_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="foerderung/antrag",
        domain="foerderung",
        title="Antrag",
        subtitle="foerderung",
        endpoint="/api/v1/foerderung/antraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Antrag im foerderung-Bereich finden und auswerten.",
        prompts=["Zeige Antrag.", "Filtere die Liste."],
        bundle="foerderung",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_ausgehende_belege_dokumente_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/ausgehende-belege-dokumente",
        domain="fuhrpark",
        title="Ausgehende belege dokumente",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Ausgehende belege dokumente im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Ausgehende belege dokumente.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fahrzeug_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fahrzeug/neu",
        domain="fuhrpark",
        title="Fahrzeug stamm",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fahrzeug stamm im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fahrzeug stamm.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_auswertung_kosten_pro_fahrzeug_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug",
        domain="fuhrpark",
        title="Fuhrpark auswertung kosten pro fahrzeug",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark auswertung kosten pro fahrzeug im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark auswertung kosten pro fahrzeug.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_auswertungen_menu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-auswertungen-menu",
        domain="fuhrpark",
        title="Fuhrpark auswertungen menu",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark auswertungen menu im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark auswertungen menu.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_klassisch_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-klassisch",
        domain="fuhrpark",
        title="Fuhrpark klassisch",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark klassisch im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark klassisch.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_menue_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-menue",
        domain="fuhrpark",
        title="Fuhrpark menue",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark menue im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark menue.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_rechnungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-rechnungen",
        domain="fuhrpark",
        title="Fuhrpark rechnungen",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark rechnungen im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark rechnungen.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_fuhrpark_fuhrpark_stammdaten_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="fuhrpark/fuhrpark-stammdaten",
        domain="fuhrpark",
        title="Fuhrpark stammdaten",
        subtitle="fuhrpark",
        endpoint="/api/v1/fuhrpark/ausgehende-dokumente",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuhrpark stammdaten im fuhrpark-Bereich finden und auswerten.",
        prompts=["Zeige Fuhrpark stammdaten.", "Filtere die Liste."],
        bundle="fuhrpark",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futter_einzel_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futter/einzel/liste",
        domain="futter",
        title="Liste",
        subtitle="futter",
        endpoint="/api/v1/futter/chargen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Liste im futter-Bereich finden und auswerten.",
        prompts=["Zeige Liste.", "Filtere die Liste."],
        bundle="futter",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futter_einzel_stamm_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futter/einzel/stamm/neu",
        domain="futter",
        title="Stamm",
        subtitle="futter",
        endpoint="/api/v1/futter/chargen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Stamm im futter-Bereich finden und auswerten.",
        prompts=["Zeige Stamm.", "Filtere die Liste."],
        bundle="futter",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futter_misch_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futter/misch/liste",
        domain="futter",
        title="Liste",
        subtitle="futter",
        endpoint="/api/v1/futter/chargen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Liste im futter-Bereich finden und auswerten.",
        prompts=["Zeige Liste.", "Filtere die Liste."],
        bundle="futter",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futter_misch_stamm_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futter/misch/stamm/neu",
        domain="futter",
        title="Rezeptur-Komponenten",
        subtitle="futter",
        endpoint="/api/v1/futter/chargen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rezeptur-Komponenten im futter-Bereich finden und auswerten.",
        prompts=["Zeige Rezeptur-Komponenten.", "Filtere die Liste."],
        bundle="futter",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_beratung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/beratung",
        domain="futtermittel",
        title="Beratung",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Beratung im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Beratung.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_chargen_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "chargenNummer", "label": "Chargennummer", "sortable": True, "filterable": True, "width": 160}, {"key": "futtermittel", "label": "Futtermittel", "sortable": True, "filterable": True, "width": 160}, {"key": "menge", "label": "Menge", "sortable": True, "filterable": True, "width": 160}, {"key": "herkunft", "label": "Herkunft", "sortable": True, "filterable": True, "width": 160}, {"key": "produktionsdatum", "label": "Produktionsdatum", "sortable": True, "filterable": True, "width": 160}, {"key": "verfallsdatum", "label": "Verfallsdatum", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "qsZertifikat", "label": "Qszertifikat", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/chargen/neu",
        domain="futtermittel",
        title="Charge-Verfolgung",
        subtitle="futtermittel",
        endpoint="/api/v1/futter/chargen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Charge-Verfolgung im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Charge-Verfolgung.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_einzelfuttermittel_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/einzelfuttermittel/liste",
        domain="futtermittel",
        title="Einzelfuttermittel liste",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Einzelfuttermittel liste im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Einzelfuttermittel liste.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_einzelfuttermittel_stamm_new_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="futtermittel/einzelfuttermittel/stamm/new",
        domain="futtermittel",
        title="Einzelfuttermittel-Stammdaten",
        subtitle="futtermittel",
        identity_field="allgemein",
        data_sources=[stamm_entity_source("/api/v1/futter/einzelfuttermittel/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "allgemein", "label": "Allgemein", "type": "text"}, {"key": "inhaltsstoffe", "label": "Inhaltsstoffe", "type": "text"}, {"key": "qualitaet", "label": "Qualitaet", "type": "text"}, {"key": "lager", "label": "Lager", "type": "text"}, {"key": "validate", "label": "Validate", "type": "text"}, {"key": "save", "label": "Save", "type": "text"}])],
        edit_permission="futtermittel.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Einzelfuttermittel-Stammdaten als Stammblatt pflegen.",
        example_prompts=["Oeffne Einzelfuttermittel-Stammdaten.", "Bearbeite Stammdaten."],
        test_id="futtermittel-einzelfuttermittel-stamm-new",
    )


def build_futtermittel_fuetterungsdokumentation_mobil_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/fuetterungsdokumentation-mobil",
        domain="futtermittel",
        title="Fuetterungsdokumentation mobil",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fuetterungsdokumentation mobil im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Fuetterungsdokumentation mobil.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_futtermittel_bestellung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/futtermittel-bestellung",
        domain="futtermittel",
        title="Futtermittel bestellung",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Futtermittel bestellung im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Futtermittel bestellung.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_futtermittel_statistik_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/futtermittel-statistik",
        domain="futtermittel",
        title="Futtermittel statistik",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Futtermittel statistik im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Futtermittel statistik.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_grundfutteranalysen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/grundfutteranalysen",
        domain="futtermittel",
        title="Grundfutteranalysen native",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Grundfutteranalysen native im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Grundfutteranalysen native.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_integrationsmonitor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/integrationsmonitor",
        domain="futtermittel",
        title="Integrationsmonitor",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Integrationsmonitor im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Integrationsmonitor.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_mischfuttermittel_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/mischfuttermittel/liste",
        domain="futtermittel",
        title="Mischfuttermittel liste",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Mischfuttermittel liste im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Mischfuttermittel liste.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_mischfuttermittel_stamm_new_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="futtermittel/mischfuttermittel/stamm/new",
        domain="futtermittel",
        title="Mischfuttermittel-Stammdaten",
        subtitle="futtermittel",
        identity_field="allgemein",
        data_sources=[stamm_entity_source("/api/v1/futter/mischfuttermittel/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "allgemein", "label": "Allgemein", "type": "text"}, {"key": "zielgruppe", "label": "Zielgruppe", "type": "text"}, {"key": "rezeptur", "label": "Rezeptur", "type": "text"}, {"key": "naehrwerte", "label": "Naehrwerte", "type": "text"}, {"key": "qualitaet", "label": "Qualitaet", "type": "text"}, {"key": "lager", "label": "Lager", "type": "text"}])],
        edit_permission="futtermittel.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Mischfuttermittel-Stammdaten als Stammblatt pflegen.",
        example_prompts=["Oeffne Mischfuttermittel-Stammdaten.", "Bearbeite Stammdaten."],
        test_id="futtermittel-mischfuttermittel-stamm-new",
    )


def build_futtermittel_rations_schnittstellen_import_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/rations-schnittstellen-import",
        domain="futtermittel",
        title="Rations schnittstellen import",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rations schnittstellen import im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Rations schnittstellen import.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_rations_zugang_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/rations-zugang",
        domain="futtermittel",
        title="Rations zugang",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rations zugang im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Rations zugang.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_rationseditor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/rationseditor",
        domain="futtermittel",
        title="Rationseditor",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rationseditor im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Rationseditor.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_rationsoptimierung_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="futtermittel/rationsoptimierung",
        domain="futtermittel",
        title="Rationsoptimierung",
        subtitle="futtermittel",
        business_purpose="Rationsoptimierung mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Rationsoptimierung.", "Aktualisiere die Kennzahlen."],
        test_id="futtermittel-rationsoptimierung",
        data_sources=[cockpit_entity_source("/api/v1/futtermittel/qs/haccp-plaene")],
        tables=[cockpit_summary_table(table_key="list", label="Rationsoptimierung", columns=cols)],
        actions=[cockpit_refresh_action(permission="futtermittel.read")],
        context_rail="combined",
    )


def build_futtermittel_rationsvergleich_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/rationsvergleich",
        domain="futtermittel",
        title="Rationsvergleich",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rationsvergleich im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Rationsvergleich.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_wareneingang_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="futtermittel/wareneingang",
        domain="futtermittel",
        title="Futtermittel wareneingang",
        subtitle="futtermittel",
        endpoint="/api/v1/futtermittel/qs/haccp-plaene",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Futtermittel wareneingang im futtermittel-Bereich finden und auswerten.",
        prompts=["Zeige Futtermittel wareneingang.", "Filtere die Liste."],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_genossenschaft_mitglieder_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="genossenschaft/mitglieder",
        domain="genossenschaft",
        title="Mitglieder",
        subtitle="genossenschaft",
        endpoint="/api/v1/genossenschaft/mitglieder",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Mitglieder im genossenschaft-Bereich finden und auswerten.",
        prompts=["Zeige Mitglieder.", "Filtere die Liste."],
        bundle="genossenschaft",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_inventory_reports_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="inventory-reports",
        domain="workspace",
        title="Inventory reports",
        subtitle="workspace",
        business_purpose="Inventory reports mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Inventory reports.", "Aktualisiere die Kennzahlen."],
        test_id="inventory-reports",
        data_sources=[cockpit_entity_source("/api/v1/inventory/reports/stock-alerts")],
        tables=[cockpit_summary_table(table_key="list", label="Inventory reports", columns=cols)],
        actions=[cockpit_refresh_action(permission="workspace.read")],
        context_rail="combined",
    )


def build_inventory_epcis_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="inventory/epcis",
        domain="inventory",
        title="Index",
        subtitle="inventory",
        endpoint="/api/v1/inventory/articles",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Index im inventory-Bereich finden und auswerten.",
        prompts=["Zeige Index.", "Filtere die Liste."],
        bundle="inventory",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_kasse_tagesabschluss_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="kasse/tagesabschluss",
        domain="kasse",
        title="Tagesabschluss",
        subtitle="kasse",
        endpoint="/api/v1/kasse/tagesabschluss/aktuell",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Tagesabschluss im kasse-Bereich finden und auswerten.",
        prompts=["Zeige Tagesabschluss.", "Filtere die Liste."],
        bundle="kasse",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_kontrakte_frmkontraktprotokoll_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="kontrakte/FrmKontraktProtokoll",
        domain="kontrakte",
        title="FrmKontraktProtokoll",
        subtitle="kontrakte",
        endpoint="/api/v1/kontrakte",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="FrmKontraktProtokoll im kontrakte-Bereich finden und auswerten.",
        prompts=["Zeige FrmKontraktProtokoll.", "Filtere die Liste."],
        bundle="kontrakte",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_kontrakte_kontraktalarmdashboard_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="kontrakte/KontraktAlarmDashboard",
        domain="kontrakte",
        title="KontraktAlarmDashboard",
        subtitle="kontrakte",
        business_purpose="KontraktAlarmDashboard mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige KontraktAlarmDashboard.", "Aktualisiere die Kennzahlen."],
        test_id="kontrakte-KontraktAlarmDashboard",
        data_sources=[cockpit_entity_source("/api/v1/kontrakte")],
        tables=[cockpit_summary_table(table_key="list", label="KontraktAlarmDashboard", columns=cols)],
        actions=[cockpit_refresh_action(permission="kontrakte.read")],
        context_rail="combined",
    )


def build_kontrakte_lstkontraktuebersicht_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="kontrakte/LstKontraktUebersicht",
        domain="kontrakte",
        title="LstKontraktUebersicht",
        subtitle="kontrakte",
        business_purpose="LstKontraktUebersicht mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige LstKontraktUebersicht.", "Aktualisiere die Kennzahlen."],
        test_id="kontrakte-LstKontraktUebersicht",
        data_sources=[cockpit_entity_source("/api/v1/kontrakte")],
        tables=[cockpit_summary_table(table_key="list", label="LstKontraktUebersicht", columns=cols)],
        actions=[cockpit_refresh_action(permission="kontrakte.read")],
        context_rail="combined",
    )


def build_kontrakte_kontraktklassen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="kontrakte/kontraktklassen",
        domain="kontrakte",
        title="Kontraktklassen",
        subtitle="kontrakte",
        endpoint="/api/v1/kontrakt-klassen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kontraktklassen im kontrakte-Bereich finden und auswerten.",
        prompts=["Zeige Kontraktklassen.", "Filtere die Liste."],
        bundle="kontrakte",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_kontrakte_mengenzeitraeume_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="kontrakte/mengenzeitraeume",
        domain="kontrakte",
        title="Kontrakt wählen",
        subtitle="kontrakte",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/kontrakte/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="kontrakte.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kontrakt wählen als Stammblatt pflegen.",
        example_prompts=["Oeffne Kontrakt wählen.", "Bearbeite Stammdaten."],
        test_id="kontrakte-mengenzeitraeume",
    )


def build_kontrakte_positionen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="kontrakte/positionen",
        domain="kontrakte",
        title="KontraktPositionsmonitor",
        subtitle="kontrakte",
        endpoint="/api/v1/kontrakte",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="KontraktPositionsmonitor im kontrakte-Bereich finden und auswerten.",
        prompts=["Zeige KontraktPositionsmonitor.", "Filtere die Liste."],
        bundle="kontrakte",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_auslagerung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/auslagerung",
        domain="lager",
        title="Auslagerung",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Auslagerung im lager-Bereich finden und auswerten.",
        prompts=["Zeige Auslagerung.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_bestandsbewertung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/bestandsbewertung",
        domain="lager",
        title="Bestandsbewertung",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bestandsbewertung im lager-Bereich finden und auswerten.",
        prompts=["Zeige Bestandsbewertung.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_bestandskorrektur_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/bestandskorrektur",
        domain="lager",
        title="Bestandskorrektur",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bestandskorrektur im lager-Bereich finden und auswerten.",
        prompts=["Zeige Bestandskorrektur.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_einlagerung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/einlagerung",
        domain="lager",
        title="Einlagerung",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Einlagerung im lager-Bereich finden und auswerten.",
        prompts=["Zeige Einlagerung.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_gs1_scanner_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/gs1-scanner",
        domain="lager",
        title="Gs1 scanner",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Gs1 scanner im lager-Bereich finden und auswerten.",
        prompts=["Zeige Gs1 scanner.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_inventur_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/inventur",
        domain="lager",
        title="Inventur",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Inventur im lager-Bereich finden und auswerten.",
        prompts=["Zeige Inventur.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_kommissionierung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/kommissionierung",
        domain="lager",
        title="Kommissionierung",
        subtitle="lager",
        endpoint="/api/v1/sales/delivery-notes",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kommissionierung im lager-Bereich finden und auswerten.",
        prompts=["Zeige Kommissionierung.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_lagerplaetze_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/lagerplaetze",
        domain="lager",
        title="Lagerplaetze",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lagerplaetze im lager-Bereich finden und auswerten.",
        prompts=["Zeige Lagerplaetze.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_massebilanz_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="lager/massebilanz",
        domain="lager",
        title="Neue Massebilanz anlegen",
        subtitle="lager",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/lager/bestaende/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="lager.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Massebilanz anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Massebilanz anlegen.", "Bearbeite Stammdaten."],
        test_id="lager-massebilanz",
    )


def build_lager_materialfluss_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/materialfluss",
        domain="lager",
        title="Materialfluss",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Materialfluss im lager-Bereich finden und auswerten.",
        prompts=["Zeige Materialfluss.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_materialfluss_visualisierung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/materialfluss-visualisierung",
        domain="lager",
        title="Materialfluss visualisierung",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Materialfluss visualisierung im lager-Bereich finden und auswerten.",
        prompts=["Zeige Materialfluss visualisierung.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_partiestamm_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/partiestamm",
        domain="lager",
        title="Partiestamm",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Partiestamm im lager-Bereich finden und auswerten.",
        prompts=["Zeige Partiestamm.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_permanente_inventur_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="lager/permanente-inventur",
        domain="lager",
        title="Abschlüsse",
        subtitle="lager",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/lager/bestaende/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="lager.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Abschlüsse als Stammblatt pflegen.",
        example_prompts=["Oeffne Abschlüsse.", "Bearbeite Stammdaten."],
        test_id="lager-permanente-inventur",
    )


def build_lager_rueckverfolgbarkeit_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/rueckverfolgbarkeit",
        domain="lager",
        title="Rueckverfolgbarkeit",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rueckverfolgbarkeit im lager-Bereich finden und auswerten.",
        prompts=["Zeige Rueckverfolgbarkeit.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_silo_mobil_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/silo-mobil",
        domain="lager",
        title="Silo mobil",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Silo mobil im lager-Bereich finden und auswerten.",
        prompts=["Zeige Silo mobil.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_silo_uebersicht_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="lager/silo-uebersicht",
        domain="lager",
        title="Silo uebersicht",
        subtitle="lager",
        business_purpose="Silo uebersicht mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Silo uebersicht.", "Aktualisiere die Kennzahlen."],
        test_id="lager-silo-uebersicht",
        data_sources=[cockpit_entity_source("/api/v1/lager/bestaende")],
        tables=[cockpit_summary_table(table_key="list", label="Silo uebersicht", columns=cols)],
        actions=[cockpit_refresh_action(permission="lager.read")],
        context_rail="combined",
    )


def build_lager_terminal_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/terminal",
        domain="lager",
        title="Terminal",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Terminal im lager-Bereich finden und auswerten.",
        prompts=["Zeige Terminal.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_lager_umlagerung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="lager/umlagerung",
        domain="lager",
        title="Lagerbewegungen",
        subtitle="lager",
        endpoint="/api/v1/lager/bestaende",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lagerbewegungen im lager-Bereich finden und auswerten.",
        prompts=["Zeige Lagerbewegungen.", "Filtere die Liste."],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_logistik_frachtbriefe_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="logistik/frachtbriefe",
        domain="logistik",
        title="Frachtbriefe",
        subtitle="logistik",
        endpoint="/api/v1/logistik/frachtbriefe",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Frachtbriefe im logistik-Bereich finden und auswerten.",
        prompts=["Zeige Frachtbriefe.", "Filtere die Liste."],
        bundle="logistik",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_mahnwesen_mahnlauf_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="mahnwesen/mahnlauf",
        domain="mahnwesen",
        title="Mahnlauf",
        subtitle="mahnwesen",
        endpoint="/api/v1/finance/mahnlauf/candidates",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Mahnlauf im mahnwesen-Bereich finden und auswerten.",
        prompts=["Zeige Mahnlauf.", "Filtere die Liste."],
        bundle="mahnwesen",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_marketing_kampagnen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="marketing/kampagnen",
        domain="marketing",
        title="Kampagnen",
        subtitle="marketing",
        endpoint="/api/v1/marketing/kampagnen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kampagnen im marketing-Bereich finden und auswerten.",
        prompts=["Zeige Kampagnen.", "Filtere die Liste."],
        bundle="marketing",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_mobile_scanner_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="mobile/scanner",
        domain="mobile",
        title="Scanner",
        subtitle="mobile",
        endpoint="/api/v1/mobile/sync-queue",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Scanner im mobile-Bereich finden und auswerten.",
        prompts=["Zeige Scanner.", "Filtere die Liste."],
        bundle="mobile",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_nachhaltigkeit_eudr_compliance_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="nachhaltigkeit/eudr-compliance",
        domain="nachhaltigkeit",
        title="Eudr compliance",
        subtitle="nachhaltigkeit",
        endpoint="/api/v1/compliance/eudr",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Eudr compliance im nachhaltigkeit-Bereich finden und auswerten.",
        prompts=["Zeige Eudr compliance.", "Filtere die Liste."],
        bundle="nachhaltigkeit",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_personal_hrm_operations_gates_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="personal/hrm-operations-gates",
        domain="personal",
        title="Hrm operations gates",
        subtitle="personal",
        endpoint="/api/v1/personal/absences",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Hrm operations gates im personal-Bereich finden und auswerten.",
        prompts=["Zeige Hrm operations gates.", "Filtere die Liste."],
        bundle="personal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_personal_mitarbeiter_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="personal/mitarbeiter/neu",
        domain="personal",
        title="Mitarbeiter stamm",
        subtitle="personal",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/personal/absences/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="personal.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Mitarbeiter stamm als Stammblatt pflegen.",
        example_prompts=["Oeffne Mitarbeiter stamm.", "Bearbeite Stammdaten."],
        test_id="personal-mitarbeiter-neu",
    )


def build_personal_organigramm_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="personal/organigramm",
        domain="personal",
        title="Organigramm",
        subtitle="personal",
        endpoint="/api/v1/personal/org-chart",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Organigramm im personal-Bereich finden und auswerten.",
        prompts=["Zeige Organigramm.", "Filtere die Liste."],
        bundle="personal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_personal_schulung_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="personal/schulung-neu",
        domain="personal",
        title="Schulung neu",
        subtitle="personal",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/personal/absences/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="personal.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Schulung neu als Stammblatt pflegen.",
        example_prompts=["Oeffne Schulung neu.", "Bearbeite Stammdaten."],
        test_id="personal-schulung-neu",
    )


def build_personal_stundenzettel_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="personal/stundenzettel",
        domain="personal",
        title="Stundenzettel",
        subtitle="personal",
        endpoint="/api/v1/personal/absences",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Stundenzettel im personal-Bereich finden und auswerten.",
        prompts=["Zeige Stundenzettel.", "Filtere die Liste."],
        bundle="personal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_personal_zeiterfassung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="personal/zeiterfassung",
        domain="personal",
        title="Zeiterfassung",
        subtitle="personal",
        endpoint="/api/v1/personal/absences",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zeiterfassung im personal-Bereich finden und auswerten.",
        prompts=["Zeige Zeiterfassung.", "Filtere die Liste."],
        bundle="personal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_anfragen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/anfragen",
        domain="portal",
        title="Anfragen",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Anfragen im portal-Bereich finden und auswerten.",
        prompts=["Zeige Anfragen.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_bestellungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/bestellungen",
        domain="portal",
        title="Bestellungen",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Bestellungen im portal-Bereich finden und auswerten.",
        prompts=["Zeige Bestellungen.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_dokumente_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/dokumente",
        domain="portal",
        title="Dokumente",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Dokumente im portal-Bereich finden und auswerten.",
        prompts=["Zeige Dokumente.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_empfehlungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/empfehlungen",
        domain="portal",
        title="Empfehlungen",
        subtitle="portal",
        endpoint="/api/v1/portal/empfehlungen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Empfehlungen im portal-Bereich finden und auswerten.",
        prompts=["Zeige Empfehlungen.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_feldbuch_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/feldbuch",
        domain="portal",
        title="Feldbuch",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Feldbuch im portal-Bereich finden und auswerten.",
        prompts=["Zeige Feldbuch.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_lohndienste_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/lohndienste/neu",
        domain="portal",
        title="Lohndienste",
        subtitle="portal",
        endpoint="/api/v1/portal/lohndienste",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lohndienste im portal-Bereich finden und auswerten.",
        prompts=["Zeige Lohndienste.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_naehrstoffbilanzen_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="portal/naehrstoffbilanzen",
        domain="portal",
        title="Naehrstoffbilanzen",
        subtitle="portal",
        business_purpose="Naehrstoffbilanzen mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Naehrstoffbilanzen.", "Aktualisiere die Kennzahlen."],
        test_id="portal-naehrstoffbilanzen",
        data_sources=[cockpit_entity_source("/api/v1/portal/anfragen")],
        tables=[cockpit_summary_table(table_key="list", label="Naehrstoffbilanzen", columns=cols)],
        actions=[cockpit_refresh_action(permission="portal.read")],
        context_rail="combined",
    )


def build_portal_onboarding_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/onboarding",
        domain="portal",
        title="Onboarding",
        subtitle="portal",
        endpoint="/api/v1/portal/interessenten",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Onboarding im portal-Bereich finden und auswerten.",
        prompts=["Zeige Onboarding.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_preisspiegel_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/preisspiegel",
        domain="portal",
        title="Preisspiegel",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Preisspiegel im portal-Bereich finden und auswerten.",
        prompts=["Zeige Preisspiegel.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_rationsoptimierung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/rationsoptimierung",
        domain="portal",
        title="Rationsoptimierung",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rationsoptimierung im portal-Bereich finden und auswerten.",
        prompts=["Zeige Rationsoptimierung.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_rechnungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/rechnungen",
        domain="portal",
        title="Rechnungen",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rechnungen im portal-Bereich finden und auswerten.",
        prompts=["Zeige Rechnungen.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_shop_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/shop",
        domain="portal",
        title="Shop",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Shop im portal-Bereich finden und auswerten.",
        prompts=["Zeige Shop.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_vertraege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/vertraege",
        domain="portal",
        title="Vertraege",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Vertraege im portal-Bereich finden und auswerten.",
        prompts=["Zeige Vertraege.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_whatsapp_simulator_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/whatsapp-simulator",
        domain="portal",
        title="Whatsapp simulator",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Whatsapp simulator im portal-Bereich finden und auswerten.",
        prompts=["Zeige Whatsapp simulator.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_zertifikate_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="portal/zertifikate",
        domain="portal",
        title="{zertifikat.name}",
        subtitle="portal",
        endpoint="/api/v1/portal/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="{zertifikat.name} im portal-Bereich finden und auswerten.",
        prompts=["Zeige {zertifikat.name}.", "Filtere die Liste."],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_customer_display_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/customer-display",
        domain="pos",
        title="Customer display",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Customer display im pos-Bereich finden und auswerten.",
        prompts=["Zeige Customer display.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_gift_cards_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/gift-cards",
        domain="pos",
        title="Gift cards",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Gift cards im pos-Bereich finden und auswerten.",
        prompts=["Zeige Gift cards.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_promotionen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/promotionen",
        domain="pos",
        title="Promotionen",
        subtitle="pos",
        endpoint="/api/v1/pos/promotions",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Promotionen im pos-Bereich finden und auswerten.",
        prompts=["Zeige Promotionen.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_rabatte_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/rabatte",
        domain="pos",
        title="Rabatte",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rabatte im pos-Bereich finden und auswerten.",
        prompts=["Zeige Rabatte.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_retoure_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/retoure",
        domain="pos",
        title="Retoure",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Retoure im pos-Bereich finden und auswerten.",
        prompts=["Zeige Retoure.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_suspended_sales_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/suspended-sales",
        domain="pos",
        title="Suspended sales",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Suspended sales im pos-Bereich finden und auswerten.",
        prompts=["Zeige Suspended sales.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_tagesabschluss_enhanced_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/tagesabschluss-enhanced",
        domain="pos",
        title="Tagesabschluss enhanced",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/status",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Tagesabschluss enhanced im pos-Bereich finden und auswerten.",
        prompts=["Zeige Tagesabschluss enhanced.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_terminal_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/terminal",
        domain="pos",
        title="Terminal",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Terminal im pos-Bereich finden und auswerten.",
        prompts=["Zeige Terminal.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_pos_tse_journal_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/tse-journal",
        domain="pos",
        title="Tse journal",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Tse journal im pos-Bereich finden und auswerten.",
        prompts=["Zeige Tse journal.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        table_profile="financial",
    )


def build_pos_uebernahme_kasse_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="pos/uebernahme-kasse",
        domain="pos",
        title="Uebernahme kasse",
        subtitle="pos",
        endpoint="/api/v1/pos/dsfinvk/export",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Uebernahme kasse im pos-Bereich finden und auswerten.",
        prompts=["Zeige Uebernahme kasse.", "Filtere die Liste."],
        bundle="pos",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_preise_historie_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="preise/historie",
        domain="preise",
        title="Historie",
        subtitle="preise",
        endpoint="/api/v1/preise/historie",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Historie im preise-Bereich finden und auswerten.",
        prompts=["Zeige Historie.", "Filtere die Liste."],
        bundle="preise",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_preise_individualpreise_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="preise/individualpreise",
        domain="preise",
        title="Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}]",
        subtitle="preise",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/preise/historie/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}].", "Bearbeite Stammdaten."],
        test_id="preise-individualpreise",
    )


def build_preise_konditionen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="preise/konditionen",
        domain="preise",
        title="Konditionen",
        subtitle="preise",
        endpoint="/api/v1/preise/konditionen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Konditionen im preise-Bereich finden und auswerten.",
        prompts=["Zeige Konditionen.", "Filtere die Liste."],
        bundle="preise",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_preise_rabattgruppen_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="preise/rabattgruppen",
        domain="preise",
        title="Neue Rabattgruppe [RAG]",
        subtitle="preise",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/preise/historie/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Rabattgruppe [RAG] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Rabattgruppe [RAG].", "Bearbeite Stammdaten."],
        test_id="preise-rabattgruppen",
    )


def build_preise_zu_abschlaggruppen_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="preise/zu-abschlaggruppen",
        domain="preise",
        title="Neue Zu-/Abschlaggruppe [ZAGR]",
        subtitle="preise",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/preise/historie/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Zu-/Abschlaggruppe [ZAGR] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Zu-/Abschlaggruppe [ZAGR].", "Bearbeite Stammdaten."],
        test_id="preise-zu-abschlaggruppen",
    )


def build_produktion_mischfutter_produktion_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="produktion/mischfutter-produktion",
        domain="produktion",
        title="Mischfutter produktion",
        subtitle="produktion",
        endpoint="/api/v1/produktion/mischfutter/auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Mischfutter produktion im produktion-Bereich finden und auswerten.",
        prompts=["Zeige Mischfutter produktion.", "Filtere die Liste."],
        bundle="produktion",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_produktion_produktions_dokumente_drucken_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="produktion/produktions-dokumente-drucken",
        domain="produktion",
        title="Produktions dokumente drucken",
        subtitle="produktion",
        endpoint="/api/v1/produktion/mischfutter/auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Produktions dokumente drucken im produktion-Bereich finden und auswerten.",
        prompts=["Zeige Produktions dokumente drucken.", "Filtere die Liste."],
        bundle="produktion",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_produktion_rezepturgruppen_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="produktion/rezepturgruppen",
        domain="produktion",
        title="Neue Rezepturgruppe anlegen",
        subtitle="produktion",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/produktion/mischfutter/auftraege/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="produktion.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Rezepturgruppe anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Rezepturgruppe anlegen.", "Bearbeite Stammdaten."],
        test_id="produktion-rezepturgruppen",
    )


def build_prospecting_leads_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="prospecting/leads",
        domain="prospecting",
        title="LeadExplorer",
        subtitle="prospecting",
        endpoint="/api/v1/prospecting/lead-candidates",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="LeadExplorer im prospecting-Bereich finden und auswerten.",
        prompts=["Zeige LeadExplorer.", "Filtere die Liste."],
        bundle="prospecting",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_qualitaet_labor_auftrag_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="qualitaet/labor-auftrag",
        domain="qualitaet",
        title="Labor auftrag",
        subtitle="qualitaet",
        endpoint="/api/v1/qualitaet/labor-auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Labor auftrag im qualitaet-Bereich finden und auswerten.",
        prompts=["Zeige Labor auftrag.", "Filtere die Liste."],
        bundle="qualitaet",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_qualitaet_labor_detail_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="qualitaet/labor-detail",
        domain="qualitaet",
        title="Labor detail",
        subtitle="qualitaet",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/qualitaet/labor-auftraege/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="qualitaet.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Labor detail als Stammblatt pflegen.",
        example_prompts=["Oeffne Labor detail.", "Bearbeite Stammdaten."],
        test_id="qualitaet-labor-detail",
    )


def build_qualitaet_reklamation_detail_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="qualitaet/reklamation-detail",
        domain="qualitaet",
        title="Status geaendert",
        subtitle="qualitaet",
        endpoint="/api/v1/qualitaet/labor-auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Status geaendert im qualitaet-Bereich finden und auswerten.",
        prompts=["Zeige Status geaendert.", "Filtere die Liste."],
        bundle="qualitaet",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_qualitaet_reklamationen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="qualitaet/reklamationen",
        domain="qualitaet",
        title="Reklamationen",
        subtitle="qualitaet",
        endpoint="/api/v1/qualitaet/labor-auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Reklamationen im qualitaet-Bereich finden und auswerten.",
        prompts=["Zeige Reklamationen.", "Filtere die Liste."],
        bundle="qualitaet",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_reports_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="reports",
        domain="workspace",
        title="Reports",
        subtitle="workspace",
        business_purpose="Reports mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Reports.", "Aktualisiere die Kennzahlen."],
        test_id="reports",
        data_sources=[cockpit_entity_source("/api/v1/agrar/rations-optimization/feeding/reports")],
        tables=[cockpit_summary_table(table_key="list", label="Reports", columns=cols)],
        actions=[cockpit_refresh_action(permission="workspace.read")],
        context_rail="combined",
    )


def build_reports_reportsdashboardcharts_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="reports/ReportsDashboardCharts",
        domain="reports",
        title="ReportsDashboardCharts",
        subtitle="reports",
        business_purpose="ReportsDashboardCharts mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige ReportsDashboardCharts.", "Aktualisiere die Kennzahlen."],
        test_id="reports-ReportsDashboardCharts",
        data_sources=[cockpit_entity_source("/api/v1/reports/customer-analytics")],
        tables=[cockpit_summary_table(table_key="list", label="ReportsDashboardCharts", columns=cols)],
        actions=[cockpit_refresh_action(permission="reports.read")],
        context_rail="combined",
    )


def build_reports_deckungsbeitrag_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="reports/deckungsbeitrag",
        domain="reports",
        title="Deckungsbeitrag",
        subtitle="reports",
        endpoint="/api/v1/reports/customer-analytics",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Deckungsbeitrag im reports-Bereich finden und auswerten.",
        prompts=["Zeige Deckungsbeitrag.", "Filtere die Liste."],
        bundle="reports",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_reports_lagerbestand_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="reports/lagerbestand",
        domain="reports",
        title="Lagerbestand",
        subtitle="reports",
        endpoint="/api/v1/reports/customer-analytics",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lagerbestand im reports-Bereich finden und auswerten.",
        prompts=["Zeige Lagerbestand.", "Filtere die Liste."],
        bundle="reports",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_reports_umsatz_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="reports/umsatz",
        domain="reports",
        title="Umsatz",
        subtitle="reports",
        endpoint="/api/v1/reports/customer-analytics",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Umsatz im reports-Bereich finden und auswerten.",
        prompts=["Zeige Umsatz.", "Filtere die Liste."],
        bundle="reports",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_rezepte_editor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="rezepte/editor",
        domain="rezepte",
        title="Grunddaten",
        subtitle="rezepte",
        endpoint="/api/v1/fibu/kreditoren",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Grunddaten im rezepte-Bereich finden und auswerten.",
        prompts=["Zeige Grunddaten.", "Filtere die Liste."],
        bundle="rezepte",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_angebote_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/angebote/neu",
        domain="sales",
        title="Angebot erstellen",
        subtitle="sales",
        endpoint="/api/v1/sales/offers/",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Angebot erstellen im sales-Bereich finden und auswerten.",
        prompts=["Zeige Angebot erstellen.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_auftrag_lieferschein_abgleich_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/auftrag-lieferschein-abgleich",
        domain="sales",
        title="Auftrag lieferschein abgleich",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Auftrag lieferschein abgleich im sales-Bereich finden und auswerten.",
        prompts=["Zeige Auftrag lieferschein abgleich.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_auftragskette_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/auftragskette",
        domain="sales",
        title="Auftragskette",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Auftragskette im sales-Bereich finden und auswerten.",
        prompts=["Zeige Auftragskette.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_credit_notes_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/credit-notes",
        domain="sales",
        title="Credit note editor",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Credit note editor im sales-Bereich finden und auswerten.",
        prompts=["Zeige Credit note editor.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_delivery_editor_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="sales/delivery-editor",
        domain="sales",
        title="Delivery editor",
        subtitle="sales",
        identity_field="create",
        data_sources=[stamm_entity_source("/api/v1/sales/blanket-orders/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "create", "label": "Create", "type": "text"}, {"key": "read", "label": "Read", "type": "text"}, {"key": "update", "label": "Update", "type": "text"}, {"key": "approve", "label": "Approve", "type": "text"}, {"key": "audit", "label": "Audit", "type": "text"}])],
        edit_permission="sales.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Delivery editor als Stammblatt pflegen.",
        example_prompts=["Oeffne Delivery editor.", "Bearbeite Stammdaten."],
        test_id="sales-delivery-editor",
    )


def build_sales_delivery_editor_new_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="sales/delivery-editor-new",
        domain="sales",
        title="Delivery editor new",
        subtitle="sales",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/sales/blanket-orders/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="sales.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Delivery editor new als Stammblatt pflegen.",
        example_prompts=["Oeffne Delivery editor new.", "Bearbeite Stammdaten."],
        test_id="sales-delivery-editor-new",
    )


def build_sales_kalkulationen_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/kalkulationen/neu",
        domain="sales",
        title="Kalkulation",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kalkulation im sales-Bereich finden und auswerten.",
        prompts=["Zeige Kalkulation.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_lieferung_storno_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/lieferung-storno",
        domain="sales",
        title="Lieferung storno",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lieferung storno im sales-Bereich finden und auswerten.",
        prompts=["Zeige Lieferung storno.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_lieferungen_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/lieferungen/neu",
        domain="sales",
        title="Lieferungen liste",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lieferungen liste im sales-Bereich finden und auswerten.",
        prompts=["Zeige Lieferungen liste.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_orders_modern_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/orders-modern",
        domain="sales",
        title="Orders modern",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Orders modern im sales-Bereich finden und auswerten.",
        prompts=["Zeige Orders modern.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_sales_rechnungen_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="sales/rechnungen-liste",
        domain="sales",
        title="Rechnungen liste",
        subtitle="sales",
        endpoint="/api/v1/sales/blanket-orders",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rechnungen liste im sales-Bereich finden und auswerten.",
        prompts=["Zeige Rechnungen liste.", "Filtere die Liste."],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_schaeden_meldung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="schaeden/meldung",
        domain="schaeden",
        title="Meldung",
        subtitle="schaeden",
        endpoint="/api/v1/schaeden/meldungen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Meldung im schaeden-Bereich finden und auswerten.",
        prompts=["Zeige Meldung.", "Filtere die Liste."],
        bundle="schaeden",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_service_abschluss_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="service/abschluss",
        domain="service",
        title="Abschluss",
        subtitle="service",
        endpoint="/api/v1/service/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Abschluss im service-Bereich finden und auswerten.",
        prompts=["Zeige Abschluss.", "Filtere die Liste."],
        bundle="service",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_service_anfrage_detail_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="service/anfrage-detail",
        domain="service",
        title="Anfrage detail",
        subtitle="service",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/service/anfragen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="service.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Anfrage detail als Stammblatt pflegen.",
        example_prompts=["Oeffne Anfrage detail.", "Bearbeite Stammdaten."],
        test_id="service-anfrage-detail",
    )


def build_service_anfrage_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="service/anfrage/neu",
        domain="service",
        title="Anfrage erstellt",
        subtitle="service",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/service/anfragen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="service.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Anfrage erstellt als Stammblatt pflegen.",
        example_prompts=["Oeffne Anfrage erstellt.", "Bearbeite Stammdaten."],
        test_id="service-anfrage-neu",
    )


def build_service_anfragen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="service/anfragen",
        domain="service",
        title="Anfragen",
        subtitle="service",
        endpoint="/api/v1/service/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Anfragen im service-Bereich finden und auswerten.",
        prompts=["Zeige Anfragen.", "Filtere die Liste."],
        bundle="service",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_service_rueckmeldung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="service/rueckmeldung",
        domain="service",
        title="Rueckmeldung",
        subtitle="service",
        endpoint="/api/v1/service/anfragen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rueckmeldung im service-Bereich finden und auswerten.",
        prompts=["Zeige Rueckmeldung.", "Filtere die Liste."],
        bundle="service",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_setup_firma_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="setup/firma",
        domain="setup",
        title="Firma",
        subtitle="setup",
        endpoint="/api/v1/setup/firma",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Firma im setup-Bereich finden und auswerten.",
        prompts=["Zeige Firma.", "Filtere die Liste."],
        bundle="setup",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_silo_kapazitaeten_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="silo/kapazitaeten",
        domain="silo",
        title="Silos Gesamt",
        subtitle="silo",
        endpoint="/api/v1/silo/kapazitaeten",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Silos Gesamt im silo-Bereich finden und auswerten.",
        prompts=["Zeige Silos Gesamt.", "Filtere die Liste."],
        bundle="silo",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_stammdaten_artikel_stoffstrom_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/artikel-stoffstrom",
        domain="stammdaten",
        title="Stoffstrom-Datensätze",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Stoffstrom-Datensätze als Stammblatt pflegen.",
        example_prompts=["Oeffne Stoffstrom-Datensätze.", "Bearbeite Stammdaten."],
        test_id="stammdaten-artikel-stoffstrom",
    )


def build_stammdaten_artikelbestandteile_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/artikelbestandteile",
        domain="stammdaten",
        title="Neuen Bestandteil anlegen",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neuen Bestandteil anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neuen Bestandteil anlegen.", "Bearbeite Stammdaten."],
        test_id="stammdaten-artikelbestandteile",
    )


def build_stammdaten_artikelverpackung_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/artikelverpackung",
        domain="stammdaten",
        title="Neue Verpackung anlegen",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Verpackung anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Verpackung anlegen.", "Bearbeite Stammdaten."],
        test_id="stammdaten-artikelverpackung",
    )


def build_stammdaten_betriebsstaetten_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/betriebsstaetten",
        domain="stammdaten",
        title="Neue Betriebsstätte",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Betriebsstätte als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Betriebsstätte.", "Bearbeite Stammdaten."],
        test_id="stammdaten-betriebsstaetten",
    )


def build_stammdaten_hausbanken_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/hausbanken",
        domain="stammdaten",
        title="Neue Hausbank anlegen",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Hausbank anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Hausbank anlegen.", "Bearbeite Stammdaten."],
        test_id="stammdaten-hausbanken",
    )


def build_stammdaten_individuelle_artikelnummern_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/individuelle-artikelnummern",
        domain="stammdaten",
        title="Neue Zuordnung anlegen",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Zuordnung anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Zuordnung anlegen.", "Bearbeite Stammdaten."],
        test_id="stammdaten-individuelle-artikelnummern",
    )


def build_stammdaten_mengeneinheiten_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/mengeneinheiten",
        domain="stammdaten",
        title="Neue Mengeneinheit",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/stammdaten/betriebsstaetten/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Mengeneinheit als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Mengeneinheit.", "Bearbeite Stammdaten."],
        test_id="stammdaten-mengeneinheiten",
    )


def build_start_dashboard_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="start-dashboard",
        domain="workspace",
        title="Start dashboard",
        subtitle="workspace",
        business_purpose="Start dashboard mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Start dashboard.", "Aktualisiere die Kennzahlen."],
        test_id="start-dashboard",
        data_sources=[cockpit_entity_source("/api/v1/analytics/kpis")],
        tables=[cockpit_summary_table(table_key="list", label="Start dashboard", columns=cols)],
        actions=[cockpit_refresh_action(permission="workspace.read")],
        context_rail="combined",
    )


def build_strecke_menu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="strecke/menu",
        domain="strecke",
        title="Menu",
        subtitle="strecke",
        endpoint="/api/v1/strecke/speditionen/frachttarife",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Menu im strecke-Bereich finden und auswerten.",
        prompts=["Zeige Menu.", "Filtere die Liste."],
        bundle="strecke",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_strecke_nawaro_uebersicht_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="strecke/nawaro-uebersicht",
        domain="strecke",
        title="Nawaro uebersicht",
        subtitle="strecke",
        business_purpose="Nawaro uebersicht mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Nawaro uebersicht.", "Aktualisiere die Kennzahlen."],
        test_id="strecke-nawaro-uebersicht",
        data_sources=[cockpit_entity_source("/api/v1/strecke/speditionen/frachttarife")],
        tables=[cockpit_summary_table(table_key="list", label="Nawaro uebersicht", columns=cols)],
        actions=[cockpit_refresh_action(permission="strecke.read")],
        context_rail="combined",
    )


def build_strecke_nawaro_uebersicht_drucken_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="strecke/nawaro-uebersicht-drucken",
        domain="strecke",
        title="Nawaro uebersicht drucken",
        subtitle="strecke",
        business_purpose="Nawaro uebersicht drucken mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Nawaro uebersicht drucken.", "Aktualisiere die Kennzahlen."],
        test_id="strecke-nawaro-uebersicht-drucken",
        data_sources=[cockpit_entity_source("/api/v1/strecke/speditionen/frachttarife")],
        tables=[cockpit_summary_table(table_key="list", label="Nawaro uebersicht drucken", columns=cols)],
        actions=[cockpit_refresh_action(permission="strecke.read")],
        context_rail="combined",
    )


def build_strecke_speditionen_fracht_preise_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="strecke/speditionen-fracht-preise",
        domain="strecke",
        title="Speditionen fracht preise",
        subtitle="strecke",
        endpoint="/api/v1/strecke/speditionen/frachttarife",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Speditionen fracht preise im strecke-Bereich finden und auswerten.",
        prompts=["Zeige Speditionen fracht preise.", "Filtere die Liste."],
        bundle="strecke",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_strecke_vorlaeufige_streckengeschaefte_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="strecke/vorlaeufige-streckengeschaefte",
        domain="strecke",
        title="Vorlaeufige streckengeschaefte",
        subtitle="strecke",
        endpoint="/api/v1/strecke/speditionen/frachttarife",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Vorlaeufige streckengeschaefte im strecke-Bereich finden und auswerten.",
        prompts=["Zeige Vorlaeufige streckengeschaefte.", "Filtere die Liste."],
        bundle="strecke",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_system_live_monitor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="system/live-monitor",
        domain="system",
        title="Live monitor",
        subtitle="system",
        endpoint="/api/v1/system/business",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Live monitor im system-Bereich finden und auswerten.",
        prompts=["Zeige Live monitor.", "Filtere die Liste."],
        bundle="system",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_tankstelle_zapfungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="tankstelle/zapfungen",
        domain="tankstelle",
        title="Zapfungen",
        subtitle="tankstelle",
        endpoint="/api/v1/tankstelle/bestand",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zapfungen im tankstelle-Bereich finden und auswerten.",
        prompts=["Zeige Zapfungen.", "Filtere die Liste."],
        bundle="tankstelle",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_transporte_fahrer_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="transporte/fahrer/neu",
        domain="transporte",
        title="Fahrer liste",
        subtitle="transporte",
        endpoint="/api/v1/transporte/fahrer",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Fahrer liste im transporte-Bereich finden und auswerten.",
        prompts=["Zeige Fahrer liste.", "Filtere die Liste."],
        bundle="transporte",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_auftraege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/auftraege",
        domain="verkauf",
        title="Auftraege liste",
        subtitle="verkauf",
        endpoint="/api/v1/verkauf/kunden",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Auftraege liste im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Auftraege liste.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_auftraege_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/auftraege/neu",
        domain="verkauf",
        title="Order editor",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Order editor als Stammblatt pflegen.",
        example_prompts=["Oeffne Order editor.", "Bearbeite Stammdaten."],
        test_id="verkauf-auftraege-neu",
    )


def build_verkauf_betriebs_auftraege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/betriebs-auftraege",
        domain="verkauf",
        title="Betriebs auftraege",
        subtitle="verkauf",
        endpoint="/api/v1/verkauf/kunden",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Betriebs auftraege im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Betriebs auftraege.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_dauerauftraege_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/dauerauftraege",
        domain="verkauf",
        title="Neuen Dauerauftrag anlegen",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neuen Dauerauftrag anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neuen Dauerauftrag anlegen.", "Bearbeite Stammdaten."],
        test_id="verkauf-dauerauftraege",
    )


def build_verkauf_kommissions_auftraege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/kommissions-auftraege",
        domain="verkauf",
        title="Kommissions auftraege",
        subtitle="verkauf",
        endpoint="/api/v1/verkauf/kunden",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kommissions auftraege im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Kommissions auftraege.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_kunde_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/kunde-neu",
        domain="verkauf",
        title="Kunde neu",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kunde neu als Stammblatt pflegen.",
        example_prompts=["Oeffne Kunde neu.", "Bearbeite Stammdaten."],
        test_id="verkauf-kunde-neu",
    )


def build_verkauf_kunden_liste_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/kunden-liste",
        domain="verkauf",
        title="Kunden liste",
        subtitle="verkauf",
        endpoint="/api/v1/crm/customers/lookup",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kunden liste im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Kunden liste.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_kunden_stamm_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/kunden-stamm",
        domain="verkauf",
        title="Vorlage übernommen",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Vorlage übernommen als Stammblatt pflegen.",
        example_prompts=["Oeffne Vorlage übernommen.", "Bearbeite Stammdaten."],
        test_id="verkauf-kunden-stamm",
    )


def build_verkauf_kunden_stamm_enhanced_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/kunden-stamm-enhanced",
        domain="verkauf",
        title="Kunden stamm enhanced",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kunden stamm enhanced als Stammblatt pflegen.",
        example_prompts=["Oeffne Kunden stamm enhanced.", "Bearbeite Stammdaten."],
        test_id="verkauf-kunden-stamm-enhanced",
    )


def build_verkauf_lieferschein_erfassung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/lieferschein-erfassung",
        domain="verkauf",
        title="Lieferschein erfassung",
        subtitle="verkauf",
        endpoint="/api/v1/admin/branches",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lieferschein erfassung im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Lieferschein erfassung.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_rechnungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/rechnungen",
        domain="verkauf",
        title="Rechnungen worklist",
        subtitle="verkauf",
        endpoint="/api/v1/verkauf/kunden",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rechnungen worklist im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Rechnungen worklist.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verkauf_rechnungen_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/rechnungen/neu",
        domain="verkauf",
        title="Invoice editor",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/verkauf/kunden/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Invoice editor als Stammblatt pflegen.",
        example_prompts=["Oeffne Invoice editor.", "Bearbeite Stammdaten."],
        test_id="verkauf-rechnungen-neu",
    )


def build_verkauf_unerledigte_auftrags_positionen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verkauf/unerledigte-auftrags-positionen",
        domain="verkauf",
        title="Unerledigte auftrags positionen",
        subtitle="verkauf",
        endpoint="/api/v1/verkauf/kunden",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Unerledigte auftrags positionen im verkauf-Bereich finden und auswerten.",
        prompts=["Zeige Unerledigte auftrags positionen.", "Filtere die Liste."],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_verladung_lkw_beladung_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="verladung/lkw-beladung",
        domain="verladung",
        title="Lkw beladung",
        subtitle="verladung",
        endpoint="/api/v1/silo/kapazitaeten",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Lkw beladung im verladung-Bereich finden und auswerten.",
        prompts=["Zeige Lkw beladung.", "Filtere die Liste."],
        bundle="verladung",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_vertrag_neu_screen_definition() -> dict[str, Any]:
    columns = [
        {"key": "alternate_articles", "label": "Alternate Articles", "sortable": True, "filterable": True, "width": 160},
        {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160},
    ]
    return build_stamm_list_screen(
        screen_id="vertrag/neu",
        domain="vertrag",
        title="Gespeichert",
        subtitle="vertrag",
        endpoint="/api/v1/price-hedge/hedges",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Gespeichert im vertrag-Bereich finden und auswerten.",
        prompts=["Zeige Gespeichert.", "Filtere die Liste."],
        bundle="vertrag",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_vertrag_rahmenvertraege_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="vertrag/rahmenvertraege",
        domain="vertrag",
        title="Rahmenvertraege",
        subtitle="vertrag",
        endpoint="/api/v1/vertrag/rahmenvertraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Rahmenvertraege im vertrag-Bereich finden und auswerten.",
        prompts=["Zeige Rahmenvertraege.", "Filtere die Liste."],
        bundle="vertrag",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_vertrieb_kundenumsatz_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="vertrieb/kundenumsatz",
        domain="vertrieb",
        title="Kundenumsatz",
        subtitle="vertrieb",
        endpoint="/api/v1/crm/customers/",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Kundenumsatz im vertrieb-Bereich finden und auswerten.",
        prompts=["Zeige Kundenumsatz.", "Filtere die Liste."],
        bundle="vertrieb",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="waage/neu",
        domain="waage",
        title="Liste",
        subtitle="waage",
        endpoint="/api/v1/waage/hofliste",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Liste im waage-Bereich finden und auswerten.",
        prompts=["Zeige Liste.", "Filtere die Liste."],
        bundle="waage",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_vorlagen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="waage/vorlagen",
        domain="waage",
        title="Vorlagen",
        subtitle="waage",
        endpoint="/api/v1/waage/vorlagen",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Vorlagen im waage-Bereich finden und auswerten.",
        prompts=["Zeige Vorlagen.", "Filtere die Liste."],
        bundle="waage",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_wiegeschein_detail_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="waage/wiegeschein-detail",
        domain="waage",
        title="Wiegeschein detail",
        subtitle="waage",
        endpoint="/api/v1/waage/hofliste",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Wiegeschein detail im waage-Bereich finden und auswerten.",
        prompts=["Zeige Wiegeschein detail.", "Filtere die Liste."],
        bundle="waage",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_wiegungen_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="waage/wiegungen",
        domain="waage",
        title="Wiegungen",
        subtitle="waage",
        endpoint="/api/v1/waage/hofliste",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Wiegungen im waage-Bereich finden und auswerten.",
        prompts=["Zeige Wiegungen.", "Filtere die Liste."],
        bundle="waage",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_complaint_to_resolution_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-complaint-to-resolution",
        domain="workflow",
        title="Flow spine complaint to resolution",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine complaint to resolution im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine complaint to resolution.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_compliance_to_report_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="workflow/flow-spine-compliance-to-report",
        domain="workflow",
        title="Flow spine compliance to report",
        subtitle="workflow",
        business_purpose="Flow spine compliance to report mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Flow spine compliance to report.", "Aktualisiere die Kennzahlen."],
        test_id="workflow-flow-spine-compliance-to-report",
        data_sources=[cockpit_entity_source("/api/v1/workflow/cockpit-db/dead-letter")],
        tables=[cockpit_summary_table(table_key="list", label="Flow spine compliance to report", columns=cols)],
        actions=[cockpit_refresh_action(permission="workflow.read")],
        context_rail="combined",
    )


def build_workflow_flow_spine_contract_to_settlement_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-contract-to-settlement",
        domain="workflow",
        title="Flow spine contract to settlement",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine contract to settlement im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine contract to settlement.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_finance_to_close_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-finance-to-close",
        domain="workflow",
        title="Flow spine finance to close",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine finance to close im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine finance to close.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_harvest_to_settlement_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-harvest-to-settlement",
        domain="workflow",
        title="Flow spine harvest to settlement",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine harvest to settlement im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine harvest to settlement.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_inventory_to_settlement_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-inventory-to-settlement",
        domain="workflow",
        title="Flow spine inventory to settlement",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine inventory to settlement im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine inventory to settlement.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        table_profile="inventory",
    )


def build_workflow_flow_spine_order_to_cash_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-order-to-cash",
        domain="workflow",
        title="Flow spine order to cash",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine order to cash im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine order to cash.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_procure_to_pay_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-procure-to-pay",
        domain="workflow",
        title="Flow spine procure to pay",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine procure to pay im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine procure to pay.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_service_to_customer_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-service-to-customer",
        domain="workflow",
        title="Flow spine service to customer",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine service to customer im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine service to customer.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_flow_spine_studio_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/flow-spine-studio",
        domain="workflow",
        title="Flow spine studio",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Flow spine studio im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Flow spine studio.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_process_mining_analytics_screen_definition() -> dict[str, Any]:
    cols = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_cockpit_overview_screen(
        screen_id="workflow/process-mining-analytics",
        domain="workflow",
        title="Process mining analytics",
        subtitle="workflow",
        business_purpose="Process mining analytics mandantensicher als Cockpit bereitstellen.",
        example_prompts=["Zeige Process mining analytics.", "Aktualisiere die Kennzahlen."],
        test_id="workflow-process-mining-analytics",
        data_sources=[cockpit_entity_source("/api/v1/workflow/cockpit-db/dead-letter")],
        tables=[cockpit_summary_table(table_key="list", label="Process mining analytics", columns=cols)],
        actions=[cockpit_refresh_action(permission="workflow.read")],
        context_rail="combined",
    )


def build_workflow_workflow_regeln_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/workflow-regeln",
        domain="workflow",
        title="Workflow regeln",
        subtitle="workflow",
        endpoint="/api/v1/workflow/cockpit-db/dead-letter",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Workflow regeln im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Workflow regeln.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflow_workflow_sandbox_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflow/workflow-sandbox",
        domain="workflow",
        title="Workflow sandbox",
        subtitle="workflow",
        endpoint="/api/v1/admin/process-variants",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Workflow sandbox im workflow-Bereich finden und auswerten.",
        prompts=["Zeige Workflow sandbox.", "Filtere die Liste."],
        bundle="workflow",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflows_history_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflows/history",
        domain="workflows",
        title="Workflow monitoring",
        subtitle="workflows",
        endpoint="/api/v1/agent/integrations/providers/superglue/sync-history",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Workflow monitoring im workflows-Bereich finden und auswerten.",
        prompts=["Zeige Workflow monitoring.", "Filtere die Liste."],
        bundle="workflows",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_workflows_supervisor_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="workflows/supervisor",
        domain="workflows",
        title="Supervisor",
        subtitle="workflows",
        endpoint="/api/v1/agents/neuroassist/runs",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Supervisor im workflows-Bereich finden und auswerten.",
        prompts=["Zeige Supervisor.", "Filtere die Liste."],
        bundle="workflows",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_zertifikate_neu_screen_definition() -> dict[str, Any]:
    columns = [{"key": "id", "label": "Id", "sortable": True, "filterable": True, "width": 160}, {"key": "name", "label": "Name", "sortable": True, "filterable": True, "width": 160}, {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160}, {"key": "updated_at", "label": "Updated At", "sortable": True, "filterable": True, "width": 160}]
    return build_stamm_list_screen(
        screen_id="zertifikate/neu",
        domain="zertifikate",
        title="Liste",
        subtitle="zertifikate",
        endpoint="/api/v1/zertifikate",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Liste im zertifikate-Bereich finden und auswerten.",
        prompts=["Zeige Liste.", "Filtere die Liste."],
        bundle="zertifikate",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )

BATCH15_SCREEN_BUILDERS: dict[str, Any] = {
    "contracts-v2": build_contracts_v2_screen_definition,
    "einkauf/rechnung-abgleich": build_einkauf_rechnung_abgleich_screen_definition,
    "einkauf/rechnung-eingang-erfassung": build_einkauf_rechnung_eingang_erfassung_screen_definition,
    "einkauf/rechnungseingang/neu": build_einkauf_rechnungseingang_neu_screen_definition,
    "einkauf/reports": build_einkauf_reports_screen_definition,
    "einkauf/retouren": build_einkauf_retouren_screen_definition,
    "einkauf/rfq-bids": build_einkauf_rfq_bids_screen_definition,
    "einkauf/service-entry-sheets": build_einkauf_service_entry_sheets_screen_definition,
    "einkauf/wareneingang": build_einkauf_wareneingang_screen_definition,
    "einkauf/wareneingangsabgleich": build_einkauf_wareneingangsabgleich_screen_definition,
    "etiketten/drucken": build_etiketten_drucken_screen_definition,
    "export/ustva": build_export_ustva_screen_definition,
    "fibu/abschluss-checklist-detail": build_fibu_abschluss_checklist_detail_screen_definition,
    "fibu/anlagen": build_fibu_anlagen_screen_definition,
    "fibu/anlagen-suite": build_fibu_anlagen_suite_screen_definition,
    "fibu/atlas": build_fibu_atlas_screen_definition,
    "fibu/bilanz": build_fibu_bilanz_screen_definition,
    "fibu/buchhaltungsuebersicht": build_fibu_buchhaltungsuebersicht_screen_definition,
    "fibu/buchungsuebernahme-connectors": build_fibu_buchungsuebernahme_connectors_screen_definition,
    "fibu/bwa": build_fibu_bwa_screen_definition,
    "fibu/debitoren": build_fibu_debitoren_screen_definition,
    "fibu/debitoren-api": build_fibu_debitoren_api_screen_definition,
    "fibu/elster-online": build_fibu_elster_online_screen_definition,
    "fibu/erloeskennziffern": build_fibu_erloeskennziffern_screen_definition,
    "fibu/erloeskontenzuordnung": build_fibu_erloeskontenzuordnung_screen_definition,
    "fibu/forderungsgruppen": build_fibu_forderungsgruppen_screen_definition,
    "fibu/geschaeftsjahre": build_fibu_geschaeftsjahre_screen_definition,
    "fibu/guv": build_fibu_guv_screen_definition,
    "fibu/hauptbuch": build_fibu_hauptbuch_screen_definition,
    "fibu/kontenplan": build_fibu_kontenplan_screen_definition,
    "fibu/kostenstellenrechnung": build_fibu_kostenstellenrechnung_screen_definition,
    "fibu/kreditlinien": build_fibu_kreditlinien_screen_definition,
    "fibu/kreditoren": build_fibu_kreditoren_screen_definition,
    "fibu/lohn-connector": build_fibu_lohn_connector_screen_definition,
    "fibu/monatswerte": build_fibu_monatswerte_screen_definition,
    "fibu/op-skonto-auszifferung": build_fibu_op_skonto_auszifferung_screen_definition,
    "fibu/op-verwaltung": build_fibu_op_verwaltung_screen_definition,
    "fibu/periodische-buchungen": build_fibu_periodische_buchungen_screen_definition,
    "fibu/quadriga-connector": build_fibu_quadriga_connector_screen_definition,
    "fibu/sachkonto": build_fibu_sachkonto_screen_definition,
    "fibu/schnittstelle-fibu": build_fibu_schnittstelle_fibu_screen_definition,
    "fibu/schnittstellen-center": build_fibu_schnittstellen_center_screen_definition,
    "fibu/sicherheiten": build_fibu_sicherheiten_screen_definition,
    "fibu/stammdaten": build_fibu_stammdaten_screen_definition,
    "fibu/verbindlichkeiten": build_fibu_verbindlichkeiten_screen_definition,
    "fibu/zahlungseingaenge": build_fibu_zahlungseingaenge_screen_definition,
    "fibu/zahlungslaeufe": build_fibu_zahlungslaeufe_screen_definition,
    "fibu/zahlungsmeldungen": build_fibu_zahlungsmeldungen_screen_definition,
    "fibu/zahlungsvorschlaege": build_fibu_zahlungsvorschlaege_screen_definition,
    "finance/abschluss": build_finance_abschluss_screen_definition,
    "finance/ap/invoices": build_finance_ap_invoices_screen_definition,
    "finance/ap/invoices/new": build_finance_ap_invoices_new_screen_definition,
    "finance/bank-abgleich": build_finance_bank_abgleich_screen_definition,
    "finance/bank-stamm": build_finance_bank_stamm_screen_definition,
    "finance/bankkonten-stamm": build_finance_bankkonten_stamm_screen_definition,
    "finance/bookings/new": build_finance_bookings_new_screen_definition,
    "finance/buchungserfassung": build_finance_buchungserfassung_screen_definition,
    "finance/buchungsimport": build_finance_buchungsimport_screen_definition,
    "finance/datev-export": build_finance_datev_export_screen_definition,
    "finance/debitoren/new": build_finance_debitoren_new_screen_definition,
    "finance/dunning-editor": build_finance_dunning_editor_screen_definition,
    "finance/invoices-list": build_finance_invoices_list_screen_definition,
    "finance/invoices/new": build_finance_invoices_new_screen_definition,
    "finance/kasse": build_finance_kasse_screen_definition,
    "finance/kontenplan": build_finance_kontenplan_screen_definition,
    "finance/kreditoren": build_finance_kreditoren_screen_definition,
    "finance/kreditoren-stamm": build_finance_kreditoren_stamm_screen_definition,
    "finance/lastschriften-debitoren": build_finance_lastschriften_debitoren_screen_definition,
    "finance/nebenbuch-abstimmung": build_finance_nebenbuch_abstimmung_screen_definition,
    "finance/offene-posten": build_finance_offene_posten_screen_definition,
    "finance/op-debitoren": build_finance_op_debitoren_screen_definition,
    "finance/op-kreditoren": build_finance_op_kreditoren_screen_definition,
    "finance/payments": build_finance_payments_screen_definition,
    "finance/periodenabschluss": build_finance_periodenabschluss_screen_definition,
    "finance/periods": build_finance_periods_screen_definition,
    "finance/skonto-optimizer": build_finance_skonto_optimizer_screen_definition,
    "finance/umsatz": build_finance_umsatz_screen_definition,
    "finance/ustva": build_finance_ustva_screen_definition,
    "finance/zahlungseingang": build_finance_zahlungseingang_screen_definition,
    "finance/zahlungslauf-kreditoren": build_finance_zahlungslauf_kreditoren_screen_definition,
    "finanzplanung/liquiditaet": build_finanzplanung_liquiditaet_screen_definition,
    "foerderung/antrag": build_foerderung_antrag_screen_definition,
    "fuhrpark/ausgehende-belege-dokumente": build_fuhrpark_ausgehende_belege_dokumente_screen_definition,
    "fuhrpark/fahrzeug/neu": build_fuhrpark_fahrzeug_neu_screen_definition,
    "fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug": build_fuhrpark_fuhrpark_auswertung_kosten_pro_fahrzeug_screen_definition,
    "fuhrpark/fuhrpark-auswertungen-menu": build_fuhrpark_fuhrpark_auswertungen_menu_screen_definition,
    "fuhrpark/fuhrpark-klassisch": build_fuhrpark_fuhrpark_klassisch_screen_definition,
    "fuhrpark/fuhrpark-menue": build_fuhrpark_fuhrpark_menue_screen_definition,
    "fuhrpark/fuhrpark-rechnungen": build_fuhrpark_fuhrpark_rechnungen_screen_definition,
    "fuhrpark/fuhrpark-stammdaten": build_fuhrpark_fuhrpark_stammdaten_screen_definition,
    "futter/einzel/liste": build_futter_einzel_liste_screen_definition,
    "futter/einzel/stamm/neu": build_futter_einzel_stamm_neu_screen_definition,
    "futter/misch/liste": build_futter_misch_liste_screen_definition,
    "futter/misch/stamm/neu": build_futter_misch_stamm_neu_screen_definition,
    "futtermittel/beratung": build_futtermittel_beratung_screen_definition,
    "futtermittel/chargen/neu": build_futtermittel_chargen_neu_screen_definition,
    "futtermittel/einzelfuttermittel/liste": build_futtermittel_einzelfuttermittel_liste_screen_definition,
    "futtermittel/einzelfuttermittel/stamm/new": build_futtermittel_einzelfuttermittel_stamm_new_screen_definition,
    "futtermittel/fuetterungsdokumentation-mobil": build_futtermittel_fuetterungsdokumentation_mobil_screen_definition,
    "futtermittel/futtermittel-bestellung": build_futtermittel_futtermittel_bestellung_screen_definition,
    "futtermittel/futtermittel-statistik": build_futtermittel_futtermittel_statistik_screen_definition,
    "futtermittel/grundfutteranalysen": build_futtermittel_grundfutteranalysen_screen_definition,
    "futtermittel/integrationsmonitor": build_futtermittel_integrationsmonitor_screen_definition,
    "futtermittel/mischfuttermittel/liste": build_futtermittel_mischfuttermittel_liste_screen_definition,
    "futtermittel/mischfuttermittel/stamm/new": build_futtermittel_mischfuttermittel_stamm_new_screen_definition,
    "futtermittel/rations-schnittstellen-import": build_futtermittel_rations_schnittstellen_import_screen_definition,
    "futtermittel/rations-zugang": build_futtermittel_rations_zugang_screen_definition,
    "futtermittel/rationseditor": build_futtermittel_rationseditor_screen_definition,
    "futtermittel/rationsoptimierung": build_futtermittel_rationsoptimierung_screen_definition,
    "futtermittel/rationsvergleich": build_futtermittel_rationsvergleich_screen_definition,
    "futtermittel/wareneingang": build_futtermittel_wareneingang_screen_definition,
    "genossenschaft/mitglieder": build_genossenschaft_mitglieder_screen_definition,
    "inventory-reports": build_inventory_reports_screen_definition,
    "inventory/epcis": build_inventory_epcis_screen_definition,
    "kasse/tagesabschluss": build_kasse_tagesabschluss_screen_definition,
    "kontrakte/FrmKontraktProtokoll": build_kontrakte_frmkontraktprotokoll_screen_definition,
    "kontrakte/KontraktAlarmDashboard": build_kontrakte_kontraktalarmdashboard_screen_definition,
    "kontrakte/LstKontraktUebersicht": build_kontrakte_lstkontraktuebersicht_screen_definition,
    "kontrakte/kontraktklassen": build_kontrakte_kontraktklassen_screen_definition,
    "kontrakte/mengenzeitraeume": build_kontrakte_mengenzeitraeume_screen_definition,
    "kontrakte/positionen": build_kontrakte_positionen_screen_definition,
    "lager/auslagerung": build_lager_auslagerung_screen_definition,
    "lager/bestandsbewertung": build_lager_bestandsbewertung_screen_definition,
    "lager/bestandskorrektur": build_lager_bestandskorrektur_screen_definition,
    "lager/einlagerung": build_lager_einlagerung_screen_definition,
    "lager/gs1-scanner": build_lager_gs1_scanner_screen_definition,
    "lager/inventur": build_lager_inventur_screen_definition,
    "lager/kommissionierung": build_lager_kommissionierung_screen_definition,
    "lager/lagerplaetze": build_lager_lagerplaetze_screen_definition,
    "lager/massebilanz": build_lager_massebilanz_screen_definition,
    "lager/materialfluss": build_lager_materialfluss_screen_definition,
    "lager/materialfluss-visualisierung": build_lager_materialfluss_visualisierung_screen_definition,
    "lager/partiestamm": build_lager_partiestamm_screen_definition,
    "lager/permanente-inventur": build_lager_permanente_inventur_screen_definition,
    "lager/rueckverfolgbarkeit": build_lager_rueckverfolgbarkeit_screen_definition,
    "lager/silo-mobil": build_lager_silo_mobil_screen_definition,
    "lager/silo-uebersicht": build_lager_silo_uebersicht_screen_definition,
    "lager/terminal": build_lager_terminal_screen_definition,
    "lager/umlagerung": build_lager_umlagerung_screen_definition,
    "logistik/frachtbriefe": build_logistik_frachtbriefe_screen_definition,
    "mahnwesen/mahnlauf": build_mahnwesen_mahnlauf_screen_definition,
    "marketing/kampagnen": build_marketing_kampagnen_screen_definition,
    "mobile/scanner": build_mobile_scanner_screen_definition,
    "nachhaltigkeit/eudr-compliance": build_nachhaltigkeit_eudr_compliance_screen_definition,
    "personal/hrm-operations-gates": build_personal_hrm_operations_gates_screen_definition,
    "personal/mitarbeiter/neu": build_personal_mitarbeiter_neu_screen_definition,
    "personal/organigramm": build_personal_organigramm_screen_definition,
    "personal/schulung-neu": build_personal_schulung_neu_screen_definition,
    "personal/stundenzettel": build_personal_stundenzettel_screen_definition,
    "personal/zeiterfassung": build_personal_zeiterfassung_screen_definition,
    "portal/anfragen": build_portal_anfragen_screen_definition,
    "portal/bestellungen": build_portal_bestellungen_screen_definition,
    "portal/dokumente": build_portal_dokumente_screen_definition,
    "portal/empfehlungen": build_portal_empfehlungen_screen_definition,
    "portal/feldbuch": build_portal_feldbuch_screen_definition,
    "portal/lohndienste/neu": build_portal_lohndienste_neu_screen_definition,
    "portal/naehrstoffbilanzen": build_portal_naehrstoffbilanzen_screen_definition,
    "portal/onboarding": build_portal_onboarding_screen_definition,
    "portal/preisspiegel": build_portal_preisspiegel_screen_definition,
    "portal/rationsoptimierung": build_portal_rationsoptimierung_screen_definition,
    "portal/rechnungen": build_portal_rechnungen_screen_definition,
    "portal/shop": build_portal_shop_screen_definition,
    "portal/vertraege": build_portal_vertraege_screen_definition,
    "portal/whatsapp-simulator": build_portal_whatsapp_simulator_screen_definition,
    "portal/zertifikate": build_portal_zertifikate_screen_definition,
    "pos/customer-display": build_pos_customer_display_screen_definition,
    "pos/gift-cards": build_pos_gift_cards_screen_definition,
    "pos/promotionen": build_pos_promotionen_screen_definition,
    "pos/rabatte": build_pos_rabatte_screen_definition,
    "pos/retoure": build_pos_retoure_screen_definition,
    "pos/suspended-sales": build_pos_suspended_sales_screen_definition,
    "pos/tagesabschluss-enhanced": build_pos_tagesabschluss_enhanced_screen_definition,
    "pos/terminal": build_pos_terminal_screen_definition,
    "pos/tse-journal": build_pos_tse_journal_screen_definition,
    "pos/uebernahme-kasse": build_pos_uebernahme_kasse_screen_definition,
    "preise/historie": build_preise_historie_screen_definition,
    "preise/individualpreise": build_preise_individualpreise_screen_definition,
    "preise/konditionen": build_preise_konditionen_screen_definition,
    "preise/rabattgruppen": build_preise_rabattgruppen_screen_definition,
    "preise/zu-abschlaggruppen": build_preise_zu_abschlaggruppen_screen_definition,
    "produktion/mischfutter-produktion": build_produktion_mischfutter_produktion_screen_definition,
    "produktion/produktions-dokumente-drucken": build_produktion_produktions_dokumente_drucken_screen_definition,
    "produktion/rezepturgruppen": build_produktion_rezepturgruppen_screen_definition,
    "prospecting/leads": build_prospecting_leads_screen_definition,
    "qualitaet/labor-auftrag": build_qualitaet_labor_auftrag_screen_definition,
    "qualitaet/labor-detail": build_qualitaet_labor_detail_screen_definition,
    "qualitaet/reklamation-detail": build_qualitaet_reklamation_detail_screen_definition,
    "qualitaet/reklamationen": build_qualitaet_reklamationen_screen_definition,
    "reports": build_reports_screen_definition,
    "reports/ReportsDashboardCharts": build_reports_reportsdashboardcharts_screen_definition,
    "reports/deckungsbeitrag": build_reports_deckungsbeitrag_screen_definition,
    "reports/lagerbestand": build_reports_lagerbestand_screen_definition,
    "reports/umsatz": build_reports_umsatz_screen_definition,
    "rezepte/editor": build_rezepte_editor_screen_definition,
    "sales/angebote/neu": build_sales_angebote_neu_screen_definition,
    "sales/auftrag-lieferschein-abgleich": build_sales_auftrag_lieferschein_abgleich_screen_definition,
    "sales/auftragskette": build_sales_auftragskette_screen_definition,
    "sales/credit-notes": build_sales_credit_notes_screen_definition,
    "sales/delivery-editor": build_sales_delivery_editor_screen_definition,
    "sales/delivery-editor-new": build_sales_delivery_editor_new_screen_definition,
    "sales/kalkulationen/neu": build_sales_kalkulationen_neu_screen_definition,
    "sales/lieferung-storno": build_sales_lieferung_storno_screen_definition,
    "sales/lieferungen/neu": build_sales_lieferungen_neu_screen_definition,
    "sales/orders-modern": build_sales_orders_modern_screen_definition,
    "sales/rechnungen-liste": build_sales_rechnungen_liste_screen_definition,
    "schaeden/meldung": build_schaeden_meldung_screen_definition,
    "service/abschluss": build_service_abschluss_screen_definition,
    "service/anfrage-detail": build_service_anfrage_detail_screen_definition,
    "service/anfrage/neu": build_service_anfrage_neu_screen_definition,
    "service/anfragen": build_service_anfragen_screen_definition,
    "service/rueckmeldung": build_service_rueckmeldung_screen_definition,
    "setup/firma": build_setup_firma_screen_definition,
    "silo/kapazitaeten": build_silo_kapazitaeten_screen_definition,
    "stammdaten/artikel-stoffstrom": build_stammdaten_artikel_stoffstrom_screen_definition,
    "stammdaten/artikelbestandteile": build_stammdaten_artikelbestandteile_screen_definition,
    "stammdaten/artikelverpackung": build_stammdaten_artikelverpackung_screen_definition,
    "stammdaten/betriebsstaetten": build_stammdaten_betriebsstaetten_screen_definition,
    "stammdaten/hausbanken": build_stammdaten_hausbanken_screen_definition,
    "stammdaten/individuelle-artikelnummern": build_stammdaten_individuelle_artikelnummern_screen_definition,
    "stammdaten/mengeneinheiten": build_stammdaten_mengeneinheiten_screen_definition,
    "start-dashboard": build_start_dashboard_screen_definition,
    "strecke/menu": build_strecke_menu_screen_definition,
    "strecke/nawaro-uebersicht": build_strecke_nawaro_uebersicht_screen_definition,
    "strecke/nawaro-uebersicht-drucken": build_strecke_nawaro_uebersicht_drucken_screen_definition,
    "strecke/speditionen-fracht-preise": build_strecke_speditionen_fracht_preise_screen_definition,
    "strecke/vorlaeufige-streckengeschaefte": build_strecke_vorlaeufige_streckengeschaefte_screen_definition,
    "system/live-monitor": build_system_live_monitor_screen_definition,
    "tankstelle/zapfungen": build_tankstelle_zapfungen_screen_definition,
    "transporte/fahrer/neu": build_transporte_fahrer_neu_screen_definition,
    "verkauf/auftraege": build_verkauf_auftraege_screen_definition,
    "verkauf/auftraege/neu": build_verkauf_auftraege_neu_screen_definition,
    "verkauf/betriebs-auftraege": build_verkauf_betriebs_auftraege_screen_definition,
    "verkauf/dauerauftraege": build_verkauf_dauerauftraege_screen_definition,
    "verkauf/kommissions-auftraege": build_verkauf_kommissions_auftraege_screen_definition,
    "verkauf/kunde-neu": build_verkauf_kunde_neu_screen_definition,
    "verkauf/kunden-liste": build_verkauf_kunden_liste_screen_definition,
    "verkauf/kunden-stamm": build_verkauf_kunden_stamm_screen_definition,
    "verkauf/kunden-stamm-enhanced": build_verkauf_kunden_stamm_enhanced_screen_definition,
    "verkauf/lieferschein-erfassung": build_verkauf_lieferschein_erfassung_screen_definition,
    "verkauf/rechnungen": build_verkauf_rechnungen_screen_definition,
    "verkauf/rechnungen/neu": build_verkauf_rechnungen_neu_screen_definition,
    "verkauf/unerledigte-auftrags-positionen": build_verkauf_unerledigte_auftrags_positionen_screen_definition,
    "verladung/lkw-beladung": build_verladung_lkw_beladung_screen_definition,
    "vertrag/neu": build_vertrag_neu_screen_definition,
    "vertrag/rahmenvertraege": build_vertrag_rahmenvertraege_screen_definition,
    "vertrieb/kundenumsatz": build_vertrieb_kundenumsatz_screen_definition,
    "waage/neu": build_waage_neu_screen_definition,
    "waage/vorlagen": build_waage_vorlagen_screen_definition,
    "waage/wiegeschein-detail": build_waage_wiegeschein_detail_screen_definition,
    "waage/wiegungen": build_waage_wiegungen_screen_definition,
    "workflow/flow-spine-complaint-to-resolution": build_workflow_flow_spine_complaint_to_resolution_screen_definition,
    "workflow/flow-spine-compliance-to-report": build_workflow_flow_spine_compliance_to_report_screen_definition,
    "workflow/flow-spine-contract-to-settlement": build_workflow_flow_spine_contract_to_settlement_screen_definition,
    "workflow/flow-spine-finance-to-close": build_workflow_flow_spine_finance_to_close_screen_definition,
    "workflow/flow-spine-harvest-to-settlement": build_workflow_flow_spine_harvest_to_settlement_screen_definition,
    "workflow/flow-spine-inventory-to-settlement": build_workflow_flow_spine_inventory_to_settlement_screen_definition,
    "workflow/flow-spine-order-to-cash": build_workflow_flow_spine_order_to_cash_screen_definition,
    "workflow/flow-spine-procure-to-pay": build_workflow_flow_spine_procure_to_pay_screen_definition,
    "workflow/flow-spine-service-to-customer": build_workflow_flow_spine_service_to_customer_screen_definition,
    "workflow/flow-spine-studio": build_workflow_flow_spine_studio_screen_definition,
    "workflow/process-mining-analytics": build_workflow_process_mining_analytics_screen_definition,
    "workflow/workflow-regeln": build_workflow_workflow_regeln_screen_definition,
    "workflow/workflow-sandbox": build_workflow_workflow_sandbox_screen_definition,
    "workflows/history": build_workflows_history_screen_definition,
    "workflows/supervisor": build_workflows_supervisor_screen_definition,
    "zertifikate/neu": build_zertifikate_neu_screen_definition,
}


def _register_batch15_via_finisher() -> None:
    from app.core import screen_definitions_finisher as finisher

    for key, builder in BATCH15_SCREEN_BUILDERS.items():
        finisher.FINISHER_SCREEN_BUILDERS.setdefault(key, builder)


_register_batch15_via_finisher()
