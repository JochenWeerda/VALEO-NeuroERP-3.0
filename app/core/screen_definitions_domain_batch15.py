"""Domain ScreenDefinitions — Batch 15 (einkauf/preisspiegel .. workflow, auto-generated)."""
from __future__ import annotations

from typing import Any

from app.core.screen_definitions_finance_workbench import build_bank_workbench, build_dunning_workbench
from app.core.screen_definitions_finance_capture import build_debtor_capture
from app.core.screen_definitions_feed_workbench import build_feed_workbench
from app.core.screen_definitions_stamm import build_feed_einzel_create, build_feed_misch_create

from app.core.screen_definitions_intake_weighing import build_scale_create, build_weighing_tickets

from app.core.cockpit_overview_parent import (
    build_cockpit_overview_screen,
    cockpit_entity_source,
    cockpit_refresh_action,
    cockpit_summary_table,
)
from app.core.stamm_list_parent import build_stamm_list_screen, stamm_list_export_action
from app.core.stamm_object_page_parent import (
    build_stamm_object_page,
    stamm_entity_source,
    stamm_kopf_tab,
)





_FILTER_LIST_PROMPT = "Filtere die Liste."

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


def build_einkauf_service_entry_sheets_screen_definition() -> dict[str, Any]:
    columns = [
        {"key": key, "label": label, "sortable": True, "filterable": True, "width": width}
        for key, label, width in (
            ("number", "Nachweisnummer", 160), ("supplierId", "Lieferant", 160),
            ("purchaseOrderId", "Bestellung", 160), ("serviceDate", "Leistungsdatum", 140),
            ("description", "Leistung", 220), ("quantity", "Menge", 100),
            ("unitPrice", "Einzelpreis", 120), ("amount", "Betrag", 120),
            ("status", "Status", 130),
        )
    ]
    return build_stamm_list_screen(
        screen_id="einkauf/service-entry-sheets",
        domain="einkauf",
        title="Leistungsnachweise",
        subtitle="Einkauf",
        endpoint="/api/v1/einkauf/service-entry-sheets",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Leistungsnachweise im Einkauf finden und auswerten.",
        prompts=["Zeige Leistungsnachweise.", "Filtere Leistungsnachweise nach Status."],
        bundle="einkauf",
        no_workflow="Diese Liste zeigt Leistungsnachweise; Anlage, Bearbeitung und Freigabe sind hier nicht verfügbar.",
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
        prompts=["Zeige Wareneingangsabgleich.", _FILTER_LIST_PROMPT],
        bundle="einkauf",
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
        prompts=["Zeige Umsatzsteuervoranmeldung.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/finance/closing-checklists/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "period", "label": "Periode", "type": "text"}, {"key": "closing_type", "label": "Abschlussart", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "progress_percentage", "label": "Fortschritt %", "type": "number"}, {"key": "updated_at", "label": "Aktualisiert", "type": "datetime"}])],
        edit_permission="fibu.write",
        # Saldenvortrag ins neue Geschaeftsjahr (M3, 24.11.2026): Eroeffnungsbuchung ueber den kanonischen Buchungsdienst,
        # erst wenn alle Perioden des Jahres gesperrt sind; ein zweiter Vortrag fuer dasselbe Jahr wird abgewiesen (409).
        extra_actions=[
            {
                "key": "saldenvortrag",
                "label": "Saldenvortrag buchen",
                "kind": "secondary",
                "dangerLevel": "high",
                "permission": "finance.closing.saldenvortrag",
                "commandEndpoint": "/api/v1/finance/closing/saldenvortrag",
                "method": "POST",
                "forbiddenForAgents": True,
                "inputFields": [
                    {"key": "jahr", "label": "Abgeschlossenes Geschaeftsjahr", "type": "number", "required": True},
                ],
            },
        ],
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Abschluss checklist detail als Stammblatt pflegen.",
        example_prompts=["Oeffne Abschluss checklist detail.", "Bearbeite Stammdaten."],
        test_id="fibu-abschluss-checklist-detail",
    )


def build_fibu_anlagen_screen_definition() -> dict[str, Any]:
    # Spalten der Anlagenbuchhaltung (domain_finance, /finance/asset-accounting/assets); bis 23.11.2026 las die Maske
    # den entfernten Altweg /fibu/anlagen auf einer leeren Tabelle.
    columns = [{"key": "asset_number", "label": "Anlagennr", "sortable": True, "filterable": True, "width": 140}, {"key": "description", "label": "Bezeichnung", "sortable": True, "filterable": True, "width": 220}, {"key": "asset_class", "label": "Anlagenklasse", "sortable": True, "filterable": True, "width": 140}, {"key": "acquisition_date", "label": "Anschaffung", "sortable": True, "filterable": True, "width": 130}, {"key": "acquisition_cost", "label": "Anschaffungswert", "sortable": True, "filterable": True, "width": 150}, {"key": "useful_life_years", "label": "Nutzungsdauer (Jahre)", "sortable": True, "filterable": True, "width": 150}, {"key": "book_value", "label": "Buchwert", "sortable": True, "filterable": True, "width": 140}]
    return build_stamm_list_screen(
        screen_id="fibu/anlagen",
        domain="fibu",
        title="Anlagen Gesamt",
        subtitle="fibu",
        endpoint="/api/v1/finance/asset-accounting/assets",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Anlagen Gesamt im fibu-Bereich finden und auswerten.",
        prompts=["Zeige Anlagen Gesamt.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Atlas.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Bilanz.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/fibu/geschaeftsjahre/detail/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "jahr_nr", "label": "Jahr", "type": "number"}, {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"}, {"key": "datum_beginn", "label": "Beginn", "type": "date"}, {"key": "datum_ende", "label": "Ende", "type": "date"}, {"key": "status", "label": "Status", "type": "text"}])],
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
        prompts=["Zeige Guv.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Monatswerte.", _FILTER_LIST_PROMPT],
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
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "op_id", "label": "Offener Posten", "type": "text"}, {"key": "zahlungsdatum", "label": "Zahlungsdatum", "type": "date"}, {"key": "zahlungsbetrag_eur", "label": "Zahlungsbetrag EUR", "type": "number"}, {"key": "skonto_betrag_eur", "label": "Skonto EUR", "type": "number"}, {"key": "status", "label": "Status", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Auszifferungen als Stammblatt pflegen.",
        example_prompts=["Oeffne Auszifferungen.", "Bearbeite Stammdaten."],
        test_id="fibu-op-skonto-auszifferung",
    )


def build_fibu_op_verwaltung_screen_definition() -> dict[str, Any]:
    columns = [
        {"key":"rechnungsnr","label":"Beleg","filterable":True,"priority":"primary"},
        {"key":"konto_typ","label":"Kontotyp","filterable":True,"priority":"primary"},
        {"key":"kunde_name","label":"Debitor","filterable":True},
        {"key":"lieferant_name","label":"Kreditor","filterable":True},
        {"key":"faelligkeit","label":"Faelligkeit","renderKind":"date","sortable":True},
        {"key":"offen","label":"Offen","renderKind":"currency","currencyField":"waehrung","numeric":True,"priority":"primary"},
        {"key":"waehrung","label":"Waehrung","filterable":True},
        {"key":"ueberfaellig","label":"Ueberfaellig","renderKind":"boolean"},
    ]
    definition = build_stamm_list_screen(
        screen_id="fibu/op-verwaltung", domain="finance", title="OP-Verwaltung",
        subtitle="Offene Forderungen und Verbindlichkeiten", endpoint="/api/v1/finance/open-items?only_open=true",
        row_route="/finance/ar-open-item/{id}", columns=columns, actions=[stamm_list_export_action()], row_actions=[],
        table_profile="financial", purpose="Offene Posten mandantensicher pruefen und oeffnen.",
        prompts=["Zeige offene Posten."], bundle="finance",
        no_workflow="Ausgleich und Mahnung erfolgen am eigenen offenen Posten.",
    )
    definition["listExperience"] = {
        "searchFields":["rechnungsnr","kunde_name","lieferant_name","konto_typ"],
        "aggregates":[{"key":"all","label":"Offene Posten","conditions":[]}],
        "export":{"filenamePrefix":"Offene-Posten-","delimiter":";","columns":[{"key":c["key"],"label":c["label"]} for c in columns]},
    }
    return definition

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
        prompts=["Zeige Sachkonto.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Sicherheiten.", _FILTER_LIST_PROMPT],
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
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "formular_nr", "label": "Formular-Nr.", "type": "text"}, {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"}, {"key": "formularklasse", "label": "Klasse", "type": "text"}, {"key": "bank_iban", "label": "IBAN", "type": "text"}, {"key": "aktiv", "label": "Aktiv", "type": "boolean"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neues Zahlungsformular [FIZAF] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neues Zahlungsformular [FIZAF].", "Bearbeite Stammdaten."],
        test_id="fibu-stammdaten",
    )


def build_fibu_zahlungsmeldungen_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="fibu/zahlungsmeldungen",
        domain="fibu",
        title="Neue Zahlungsmeldung [KASSZAME]",
        subtitle="fibu",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/fibu/zahlungsmeldungen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "meldungs_nr", "label": "Meldungs-Nr.", "type": "text"}, {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text"}, {"key": "zahlungsdatum", "label": "Zahlungsdatum", "type": "date"}, {"key": "zahlungsbetrag_eur", "label": "Zahlungsbetrag EUR", "type": "number"}, {"key": "status", "label": "Status", "type": "text"}])],
        edit_permission="fibu.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Zahlungsmeldung [KASSZAME] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Zahlungsmeldung [KASSZAME].", "Bearbeite Stammdaten."],
        test_id="fibu-zahlungsmeldungen",
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
        prompts=["Zeige Monats-/Jahresabschluss.", _FILTER_LIST_PROMPT],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_bank_abgleich_screen_definition() -> dict[str, Any]:
    return build_bank_workbench()


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
        prompts=["Zeige Vorgang.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Buchungsimport.", _FILTER_LIST_PROMPT],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_finance_datev_export_screen_definition() -> dict[str, Any]:
    from app.core.screen_definition_datev_export import build_datev_export
    return build_datev_export()


def build_finance_debitoren_new_screen_definition() -> dict[str, Any]:
    return build_debtor_capture()


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
        prompts=["Zeige Mahnvorgang.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Kasse.", _FILTER_LIST_PROMPT],
        bundle="finance",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
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
        prompts=["Zeige Debitorenlauf.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige OP-Lage.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Meldekontext.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Zahlungslage.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Liquiditaet.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Antrag.", _FILTER_LIST_PROMPT],
        bundle="foerderung",
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
        prompts=["Zeige Beratung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Charge-Verfolgung.", _FILTER_LIST_PROMPT],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_einzelfuttermittel_stamm_new_screen_definition() -> dict[str, Any]:
    return build_feed_einzel_create()


def build_futtermittel_fuetterungsdokumentation_mobil_screen_definition() -> dict[str, Any]:
    return build_feed_workbench("futtermittel/fuetterungsdokumentation-mobil")


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
        prompts=["Zeige Futtermittel bestellung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Futtermittel statistik.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Integrationsmonitor.", _FILTER_LIST_PROMPT],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_mischfuttermittel_stamm_new_screen_definition() -> dict[str, Any]:
    return build_feed_misch_create()


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
        prompts=["Zeige Rations schnittstellen import.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Rations zugang.", _FILTER_LIST_PROMPT],
        bundle="futtermittel",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_futtermittel_rationseditor_screen_definition() -> dict[str, Any]:
    return build_feed_workbench("futtermittel/rationseditor")


def build_futtermittel_rationsoptimierung_screen_definition() -> dict[str, Any]:
    return build_feed_workbench("futtermittel/rationsoptimierung")


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
        prompts=["Zeige Rationsvergleich.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Futtermittel wareneingang.", _FILTER_LIST_PROMPT],
        bundle="futtermittel",
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
        prompts=["Zeige Index.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Tagesabschluss.", _FILTER_LIST_PROMPT],
        bundle="kasse",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_kontrakte_frmkontraktprotokoll_screen_definition() -> dict[str, Any]:
    columns = [
        {"key": "changed_at", "label": "Wann", "renderKind": "datetime", "filterable": False, "width": 220},
        {"key": "changed_by", "label": "Benutzer", "filterable": True},
        {"key": "field_name", "label": "Feld", "filterable": True},
        {"key": "old_value", "label": "Alt", "renderKind": "text", "filterable": False},
        {"key": "new_value", "label": "Neu", "renderKind": "text", "filterable": False},
        {"key": "action", "label": "Aktion", "filterable": False},
    ]
    return build_stamm_list_screen(
        screen_id="kontrakte/FrmKontraktProtokoll", domain="kontrakte",
        title="Kontraktprotokoll", subtitle="Änderungen am Kontrakt",
        endpoint="/api/v1/kontrakte/{entity_id}/audit", row_route=None,
        columns=columns, actions=[], row_actions=[], table_profile="audit",
        purpose="Änderungen eines Kontrakts nachvollziehen.",
        prompts=["Zeige das Kontraktprotokoll."], bundle="kontrakte",
        no_workflow="Das unveränderliche Protokoll ist eine lesende Ansicht.",
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
        prompts=["Zeige KontraktPositionsmonitor.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Auslagerung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Bestandskorrektur.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Einlagerung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Gs1 scanner.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Lagerplaetze.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/massebilanz/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "periode", "label": "Periode", "type": "text"}, {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text"}, {"key": "anfangsbestand_kg", "label": "Anfangsbestand kg", "type": "number"}, {"key": "endbestand_kg", "label": "Endbestand kg", "type": "number"}, {"key": "status", "label": "Status", "type": "text"}])],
        edit_permission="lager.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Massebilanz anlegen als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Massebilanz anlegen.", "Bearbeite Stammdaten."],
        test_id="lager-massebilanz",
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
        prompts=["Zeige Materialfluss visualisierung.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/inventory/counts/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "warehouse_id", "label": "Lager", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "total_items", "label": "Positionen", "type": "number"}, {"key": "discrepancies_found", "label": "Differenzen", "type": "number"}])],
        edit_permission="lager.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Abschlüsse als Stammblatt pflegen.",
        example_prompts=["Oeffne Abschlüsse.", "Bearbeite Stammdaten."],
        test_id="lager-permanente-inventur",
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
        prompts=["Zeige Terminal.", _FILTER_LIST_PROMPT],
        bundle="lager",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_mahnwesen_mahnlauf_screen_definition() -> dict[str, Any]:
    return build_dunning_workbench()


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
        prompts=["Zeige Scanner.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Eudr compliance.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Hrm operations gates.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/personal/mitarbeiter/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "email", "label": "E-Mail", "type": "text"}, {"key": "abteilung", "label": "Abteilung", "type": "text"}, {"key": "position", "label": "Position", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}])],
        edit_permission="personal.write",
        creation={
            "endpoint": "/api/v1/personal/mitarbeiter",
            "permission": "personal.mitarbeiter.create",
            "detailRoute": "/personal/mitarbeiter/{entity_id}",
            "defaults": {"abteilung": "Allgemein", "position": "Mitarbeiter", "status": "aktiv"},
            "fields": [
                {"key": "name", "label": "Name", "type": "text", "required": True},
                {"key": "email", "label": "E-Mail", "type": "email", "required": True},
                {"key": "abteilung", "label": "Abteilung", "type": "text"},
                {"key": "position", "label": "Position", "type": "text"},
                {"key": "status", "label": "Status", "type": "select",
                 "options": [{"value": "aktiv", "label": "aktiv"}, {"value": "urlaub", "label": "urlaub"},
                             {"value": "krank", "label": "krank"}]},
            ],
        },
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
        prompts=["Zeige Organigramm.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/training/courses/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "ID", "type": "text"}, {"key": "course_code", "label": "Kursnummer", "type": "text"}, {"key": "title", "label": "Titel", "type": "text"}, {"key": "topic", "label": "Thema", "type": "text"}])],
        edit_permission="personal.write",
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Schulung neu als Stammblatt pflegen.",
        example_prompts=["Oeffne Schulung neu.", "Bearbeite Stammdaten."],
        test_id="personal-schulung-neu",
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
        prompts=["Zeige Lohndienste.", _FILTER_LIST_PROMPT],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
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
        prompts=["Zeige Onboarding.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Preisspiegel.", _FILTER_LIST_PROMPT],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_rationsoptimierung_screen_definition() -> dict[str, Any]:
    return build_feed_workbench("portal/rationsoptimierung")








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
        prompts=["Zeige Whatsapp simulator.", _FILTER_LIST_PROMPT],
        bundle="portal",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_portal_zertifikate_screen_definition() -> dict[str, Any]:
    columns = [
        {"key": "id", "label": "ID", "sortable": True, "filterable": True, "width": 160},
        {"key": "art", "label": "Art", "sortable": True, "filterable": True, "width": 160},
        {"key": "nummer", "label": "Nummer", "sortable": True, "filterable": True, "width": 160},
        {"key": "gueltigBis", "label": "Gültig bis", "sortable": True, "filterable": True, "width": 160},
        {"key": "status", "label": "Status", "sortable": True, "filterable": True, "width": 160},
    ]
    return build_stamm_list_screen(
        screen_id="portal/zertifikate",
        domain="portal",
        title="Zertifikate",
        subtitle="Zertifikate des zugeordneten Kundenkontos",
        endpoint="/api/v1/portal/zertifikate",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Zertifikate des zugeordneten Kundenkontos finden und auswerten.",
        prompts=["Zeige meine Zertifikate.", "Filtere die Zertifikate."],
        bundle="portal",
        no_workflow="Das Portal zeigt nur dem Kundenkonto zugeordnete Zertifikate; ein Detailweg braucht eine gesicherte Dokumentzuordnung.",
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
        prompts=["Zeige Customer display.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Gift cards.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Promotionen.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Rabatte.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Retoure.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Suspended sales.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Tagesabschluss enhanced.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Terminal.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Tse journal.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Uebernahme kasse.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Historie.", _FILTER_LIST_PROMPT],
        bundle="preise",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_preise_individualpreise_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="preise/individualpreise",
        domain="preise",
        title="Neuer Individualpreis [PRI]",
        subtitle="preise",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/preise/individualpreise/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        creation={
            "endpoint": "/api/v1/preise/individualpreise",
            "permission": "preise.individualpreis.create",
            "detailRoute": "/preise/individualpreise/{entity_id}",
            "defaults": {"preis_typ": "VK", "staffel_menge": 0, "waehrung": "EUR"},
            "fields": [
                {"key": "preis_typ", "label": "Preis-Typ", "type": "select", "required": True,
                 "options": [{"value": "VK", "label": "Verkauf"}, {"value": "EK", "label": "Einkauf"}]},
                {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text", "required": True},
                {"key": "partner_nr", "label": "Partner-Nr.", "type": "text"},
                {"key": "gueltig_von", "label": "Gueltig von", "type": "date", "required": True},
                {"key": "gueltig_bis", "label": "Gueltig bis", "type": "date"},
                {"key": "preis_eur", "label": "Preis EUR", "type": "number", "required": True},
                {"key": "mengeneinheit", "label": "Mengeneinheit", "type": "text"},
                {"key": "staffel_menge", "label": "Staffelmenge", "type": "number"},
                {"key": "waehrung", "label": "Waehrung", "type": "text"},
                {"key": "notiz", "label": "Notiz", "type": "textarea"},
            ],
        },
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neuer Individualpreis [PRI] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neuer Individualpreis.", "Bearbeite Stammdaten."],
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
        prompts=["Zeige Konditionen.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/preise/rabatte/gruppen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        creation={
            "endpoint": "/api/v1/preise/rabatte/gruppen",
            "permission": "preise.rabattgruppe.create",
            "detailRoute": "/preise/rabattgruppen/{entity_id}",
            "defaults": {"richtung": "VK"},
            "fields": [
                {"key": "gruppe_nr", "label": "Gruppen-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "richtung", "label": "Richtung", "type": "select", "required": True,
                 "options": [{"value": "VK", "label": "Verkauf"}, {"value": "EK", "label": "Einkauf"}]},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/kontrakte/zuabschlagsgruppen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="preise.write",
        creation={
            "endpoint": "/api/v1/kontrakte/zuabschlagsgruppen",
            "permission": "preise.zuabschlaggruppe.create",
            "detailRoute": "/preise/zu-abschlaggruppen/{entity_id}",
            "defaults": {"typ": "zuschlag"},
            "fields": [
                {"key": "gruppe_nr", "label": "Gruppen-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "typ", "label": "Typ", "type": "select", "required": True,
                 "options": [{"value": "zuschlag", "label": "Zuschlag"}, {"value": "abschlag", "label": "Abschlag"}]},
            ],
        },
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Neue Zu-/Abschlaggruppe [ZAGR] als Stammblatt pflegen.",
        example_prompts=["Oeffne Neue Zu-/Abschlaggruppe [ZAGR].", "Bearbeite Stammdaten."],
        test_id="preise-zu-abschlaggruppen",
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
        prompts=["Zeige Produktions dokumente drucken.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/produktion/mischfutter/rezepturgruppen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="produktion.write",
        creation={
            "endpoint": "/api/v1/produktion/mischfutter/rezepturgruppen",
            "permission": "produktion.rezepturgruppe.create",
            "detailRoute": "/produktion/rezepturgruppen/{entity_id}",
            "responseIdKey": "gruppe_nr",
            "fields": [
                {"key": "gruppe_nr", "label": "Gruppen-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "tierart", "label": "Tierart", "type": "text"},
                {"key": "nutzungsrichtung", "label": "Nutzungsrichtung", "type": "text"},
            ],
        },
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
        prompts=["Zeige LeadExplorer.", _FILTER_LIST_PROMPT],
        bundle="prospecting",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_qualitaet_labor_auftrag_screen_definition() -> dict[str, Any]:
    # Spalten aus LaborAuftragOut (Batch 8, 03.11.2026); vorher Platzhalter id/name/status/updated_at.
    columns = [{"key": "charge", "label": "Charge", "sortable": True, "filterable": True, "priority": "primary"},
               {"key": "labor", "label": "Labor", "sortable": True, "filterable": True, "priority": "primary"},
               {"key": "auftragsdatum", "label": "Auftragsdatum", "sortable": True, "renderKind": "date", "priority": "primary"},
               {"key": "analysen", "label": "Analysen", "numeric": True, "renderKind": "number", "sortable": True, "priority": "secondary"},
               {"key": "status", "label": "Status", "sortable": True, "filterable": True, "renderKind": "status", "priority": "primary"},
               {"key": "qs_entscheidung", "label": "QS-Entscheidung", "sortable": True, "filterable": True, "priority": "secondary"}]
    return build_stamm_list_screen(
        screen_id="qualitaet/labor-auftrag",
        domain="qualitaet",
        title="Laborauftraege",
        subtitle="Auftraege je Charge mit Labor, Analysen und QS-Entscheidung",
        endpoint="/api/v1/qualitaet/labor-auftraege",
        row_route=None,
        columns=columns,
        actions=[stamm_list_export_action()],
        row_actions=[],
        purpose="Offene Laborauftraege und QS-Entscheidungen je Charge finden.",
        prompts=["Welche Laborauftraege sind noch offen?", "Welche Chargen wurden gesperrt?"],
        bundle="qualitaet",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_qualitaet_labor_detail_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="qualitaet/labor-detail",
        domain="qualitaet",
        title="Laborauftrag",
        subtitle="Auftrag, Labor und Befund zur Charge",
        identity_field="charge",
        data_sources=[stamm_entity_source("/api/v1/qualitaet/labor-auftraege/{entity_id}")],
        # Felder aus LaborAuftragOut (Batch 8, 03.11.2026); vorher Platzhalter id/name/status/updated_at.
        tabs=[stamm_kopf_tab([{"key": "charge", "label": "Charge", "type": "text"}, {"key": "labor", "label": "Labor", "type": "text"},
                              {"key": "auftragsdatum", "label": "Auftragsdatum", "type": "date"}, {"key": "analysen", "label": "Analysen", "type": "number"},
                              {"key": "status", "label": "Status", "type": "text"}, {"key": "qs_entscheidung", "label": "QS-Entscheidung", "type": "text"},
                              {"key": "bemerkung", "label": "Bemerkung", "type": "text"}])],
        edit_permission="qualitaet.write",
        creation={
            "endpoint": "/api/v1/qualitaet/labor-auftraege",
            "permission": "qualitaet.labor.create",
            "detailRoute": "/qualitaet/labor/{entity_id}",
            "defaults": {"prioritaet": "normal"},
            "fields": [
                {"key": "chargenId", "label": "Chargen-ID", "type": "text", "required": True},
                {"key": "labor", "label": "Labor", "type": "text", "required": True},
                {"key": "artikel", "label": "Artikel", "type": "text"},
                {"key": "prioritaet", "label": "Prioritaet", "type": "select",
                 "options": [{"value": "normal", "label": "normal"}, {"value": "express", "label": "express"}]},
                {"key": "bemerkungen", "label": "Bemerkungen", "type": "textarea"},
            ],
        },
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Labor detail als Stammblatt pflegen.",
        example_prompts=["Oeffne Labor detail.", "Bearbeite Stammdaten."],
        test_id="qualitaet-labor-detail",
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
        prompts=["Zeige Deckungsbeitrag.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Grunddaten.", _FILTER_LIST_PROMPT],
        bundle="rezepte",
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
        prompts=["Zeige Auftrag lieferschein abgleich.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Auftragskette.", _FILTER_LIST_PROMPT],
        bundle="sales",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
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
        prompts=["Zeige Kalkulation.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Lieferung storno.", _FILTER_LIST_PROMPT],
        bundle="sales",
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
        prompts=["Zeige Abschluss.", _FILTER_LIST_PROMPT],
        bundle="service",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


_SERVICE_ANFRAGE_CREATION = {
    "endpoint": "/api/v1/service/anfragen",
    "permission": "service.anfrage.create",
    "detailRoute": "/service/anfrage/{entity_id}",
    "defaults": {"prioritaet": "normal"},
    "fields": [
        {"key": "kunde", "label": "Kunde", "type": "text", "required": True},
        {"key": "betreff", "label": "Betreff", "type": "text", "required": True},
        {"key": "beschreibung", "label": "Beschreibung", "type": "textarea"},
        {"key": "prioritaet", "label": "Prioritaet", "type": "select",
         "options": [{"value": "niedrig", "label": "niedrig"}, {"value": "normal", "label": "normal"},
                     {"value": "hoch", "label": "hoch"}]},
        {"key": "kategorie", "label": "Kategorie", "type": "text"},
    ],
}


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
        creation=dict(_SERVICE_ANFRAGE_CREATION),
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
        creation=dict(_SERVICE_ANFRAGE_CREATION),
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Anfrage erstellt als Stammblatt pflegen.",
        example_prompts=["Oeffne Anfrage erstellt.", "Bearbeite Stammdaten."],
        test_id="service-anfrage-neu",
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
        prompts=["Zeige Rueckmeldung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Firma.", _FILTER_LIST_PROMPT],
        bundle="setup",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_stammdaten_artikel_stoffstrom_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="stammdaten/artikel-stoffstrom",
        domain="stammdaten",
        title="Stoffstrom-Datensätze",
        subtitle="stammdaten",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/artikel/stoffstrom/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/artikel/stoffstrom",
            "permission": "stammdaten.stoffstrom.create",
            "detailRoute": "/stammdaten/artikel-stoffstrom/{entity_id}",
            "defaults": {"nachhaltig": True, "iscc_zertifiziert": False, "red_konform": False},
            "fields": [
                {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text", "required": True},
                {"key": "anbauland", "label": "Anbauland", "type": "text"},
                {"key": "rohstoff_kategorie", "label": "Rohstoff-Kategorie", "type": "text"},
                {"key": "co2_aequivalent_kg_per_t", "label": "CO2-Aeq (kg/t)", "type": "number"},
                {"key": "thg_wert", "label": "THG-Wert", "type": "number"},
                {"key": "nachhaltig", "label": "Nachhaltig", "type": "boolean"},
                {"key": "iscc_zertifiziert", "label": "ISCC", "type": "boolean"},
                {"key": "red_konform", "label": "RED-konform", "type": "boolean"},
                {"key": "bemerkung", "label": "Bemerkung", "type": "textarea"},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/artikel/bestandteile/stamm/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/artikel/bestandteile/stamm",
            "permission": "stammdaten.bestandteil.create",
            "detailRoute": "/stammdaten/artikelbestandteile/{entity_id}",
            "responseIdKey": "bestandteil_nr",
            "fields": [
                {"key": "bestandteil_nr", "label": "Bestandteil-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "einheit", "label": "Einheit", "type": "text"},
                {"key": "grenzwert_min", "label": "Grenzwert min", "type": "number"},
                {"key": "grenzwert_max", "label": "Grenzwert max", "type": "number"},
                {"key": "nutzung", "label": "Nutzung", "type": "text"},
                {"key": "typ_schad_naehr", "label": "Typ", "type": "text"},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/artikel/verpackungen/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/artikel/verpackungen",
            "permission": "stammdaten.verpackung.create",
            "detailRoute": "/stammdaten/artikelverpackung/{entity_id}",
            "responseIdKey": "verpackungs_nr",
            "defaults": {"stufen": 1},
            "fields": [
                {"key": "verpackungs_nr", "label": "Verpackungs-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "stufen", "label": "Stufen", "type": "number"},
                {"key": "stufe1_bezeichnung", "label": "Stufe-1 Bezeichnung", "type": "text"},
                {"key": "stufe1_menge", "label": "Stufe-1 Menge", "type": "number"},
                {"key": "stufe1_einheit", "label": "Stufe-1 Einheit", "type": "text"},
            ],
        },
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
        creation={
            # GET nutzt filial_nr — deshalb responseIdKey filial_nr.
            "endpoint": "/api/v1/stammdaten/betriebsstaetten",
            "permission": "stammdaten.betriebsstaette.create",
            "detailRoute": "/stammdaten/betriebsstaetten/{entity_id}",
            "responseIdKey": "filial_nr",
            "defaults": {"land": "Deutschland", "ist_zentrale": False},
            "fields": [
                {"key": "filial_nr", "label": "Filial-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "ist_zentrale", "label": "Zentrale", "type": "boolean"},
                {"key": "zentrale_filial_nr", "label": "Zentrale Filial-Nr.", "type": "text"},
                {"key": "strasse", "label": "Strasse", "type": "text"},
                {"key": "plz", "label": "PLZ", "type": "text"},
                {"key": "ort", "label": "Ort", "type": "text"},
                {"key": "land", "label": "Land", "type": "text"},
                {"key": "telefon", "label": "Telefon", "type": "text"},
                {"key": "email", "label": "E-Mail", "type": "email"},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/stammdaten/hausbanken/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/stammdaten/hausbanken",
            "permission": "stammdaten.hausbank.create",
            "detailRoute": "/stammdaten/hausbanken/{entity_id}",
            "responseIdKey": "bank_nr",
            "defaults": {"waehrung": "EUR", "erechnung_aktiv": False, "standard": False},
            "fields": [
                {"key": "bank_nr", "label": "Bank-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "iban", "label": "IBAN", "type": "text", "required": True},
                {"key": "bic", "label": "BIC", "type": "text"},
                {"key": "bank_name", "label": "Bankname", "type": "text"},
                {"key": "kontonummer", "label": "Kontonummer", "type": "text"},
                {"key": "blz", "label": "BLZ", "type": "text"},
                {"key": "waehrung", "label": "Waehrung", "type": "text"},
                {"key": "sepa_glaeubiger_id", "label": "SEPA-Glaeubiger-ID", "type": "text"},
                {"key": "erechnung_aktiv", "label": "E-Rechnung", "type": "boolean"},
                {"key": "standard", "label": "Standardbank", "type": "boolean"},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/artikel/individuelle-nummern/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/artikel/individuelle-nummern",
            "permission": "stammdaten.indiv_artikel.create",
            "detailRoute": "/stammdaten/individuelle-artikelnummern/{entity_id}",
            "defaults": {"partner_typ": "kunden"},
            "fields": [
                {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text", "required": True},
                {"key": "partner_nr", "label": "Partner-Nr.", "type": "text", "required": True},
                {"key": "partner_typ", "label": "Partner-Typ", "type": "select",
                 "options": [{"value": "kunden", "label": "Kunden"}, {"value": "lieferanten", "label": "Lieferanten"}]},
                {"key": "indiv_artikel_nr", "label": "Indiv. Artikel-Nr.", "type": "text", "required": True},
                {"key": "indiv_bezeichnung", "label": "Indiv. Bezeichnung", "type": "text"},
            ],
        },
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
        data_sources=[stamm_entity_source("/api/v1/artikel/mengeneinheiten/stamm/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="stammdaten.write",
        creation={
            "endpoint": "/api/v1/artikel/mengeneinheiten/stamm",
            "permission": "stammdaten.mengeneinheit.create",
            "detailRoute": "/stammdaten/mengeneinheiten/{entity_id}",
            "defaults": {"dezimalstellen": 3},
            "fields": [
                {"key": "einheit_kuerzel", "label": "Kuerzel", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                {"key": "basis_einheit", "label": "Basis-Einheit", "type": "text"},
                {"key": "umrechnungsfaktor", "label": "Umrechnungsfaktor", "type": "number"},
                {"key": "dezimalstellen", "label": "Dezimalstellen", "type": "number"},
                {"key": "nummer", "label": "Nummer", "type": "number"},
                {"key": "langtext", "label": "Langtext", "type": "text"},
                {"key": "iso_name", "label": "ISO-Name", "type": "text"},
                {"key": "un_code", "label": "UN-Code", "type": "text"},
            ],
        },
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
        prompts=["Zeige Speditionen fracht preise.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Live monitor.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Zapfungen.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Fahrer liste.", _FILTER_LIST_PROMPT],
        bundle="transporte",
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
        prompts=["Zeige Betriebs auftraege.", _FILTER_LIST_PROMPT],
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
        data_sources=[stamm_entity_source("/api/v1/dauerauftraege/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        creation={
            "endpoint": "/api/v1/dauerauftraege",
            "permission": "verkauf.dauerauftrag.create",
            "detailRoute": "/verkauf/dauerauftraege/{entity_id}",
            "responseIdKey": "da_nr",
            "defaults": {"perioden_typ": "monatlich", "perioden_wert": 1, "positionen": []},
            "fields": [
                {"key": "da_nr", "label": "DA-Nr.", "type": "text"},
                {"key": "kunden_nr", "label": "Kunden-Nr.", "type": "text", "required": True},
                {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
                {"key": "da_anfang", "label": "Anfang", "type": "date", "required": True},
                {"key": "da_naechster", "label": "Naechster Termin", "type": "date", "required": True},
                {"key": "da_ende", "label": "Ende", "type": "date"},
                {"key": "perioden_typ", "label": "Perioden-Typ", "type": "select",
                 "options": [
                     {"value": "monatlich", "label": "Monatlich"},
                     {"value": "woechentlich", "label": "Woechentlich"},
                     {"value": "alle_2_wochen", "label": "Alle 2 Wochen"},
                     {"value": "alle_3_wochen", "label": "Alle 3 Wochen"},
                     {"value": "alle_4_wochen", "label": "Alle 4 Wochen"},
                 ]},
                {"key": "perioden_wert", "label": "Perioden-Wert", "type": "number"},
                {"key": "positionen", "label": "Positionen", "type": "table",
                 "rowFields": [
                     {"key": "pos_nr", "label": "Pos.", "type": "number", "required": True},
                     {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text", "required": True},
                     {"key": "menge", "label": "Menge", "type": "number", "required": True},
                     {"key": "mengeneinheit", "label": "ME", "type": "text"},
                     {"key": "preis_eur", "label": "Preis EUR", "type": "number"},
                 ],
                 "tableEditing": {"allowAdd": True, "allowDelete": True}},
            ],
        },
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
        prompts=["Zeige Kommissions auftraege.", _FILTER_LIST_PROMPT],
        bundle="verkauf",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


_VERKAUF_KUNDE_CREATION = {
    "endpoint": "/api/v1/crm/customers/",
    "permission": "verkauf.kunde.create",
    "detailRoute": "/crm/customer-360/{entity_id}",
    "defaults": {"country": "Deutschland", "is_active": True},
    "fields": [
        {"key": "customer_number", "label": "Kunden-Nr.", "type": "text", "required": True},
        {"key": "company_name", "label": "Firmenname", "type": "text", "required": True},
        {"key": "contact_person", "label": "Ansprechpartner", "type": "text"},
        {"key": "email", "label": "E-Mail", "type": "email"},
        {"key": "phone", "label": "Telefon", "type": "text"},
        {"key": "address", "label": "Adresse", "type": "text"},
        {"key": "postal_code", "label": "PLZ", "type": "text"},
        {"key": "city", "label": "Ort", "type": "text"},
        {"key": "country", "label": "Land", "type": "text"},
        {"key": "is_active", "label": "Aktiv", "type": "boolean"},
    ],
}


def build_verkauf_kunde_neu_screen_definition() -> dict[str, Any]:
    return build_stamm_object_page(
        screen_id="verkauf/kunde-neu",
        domain="verkauf",
        title="Kunde neu",
        subtitle="verkauf",
        identity_field="id",
        data_sources=[stamm_entity_source("/api/v1/crm/customers/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        creation=dict(_VERKAUF_KUNDE_CREATION),
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kunde neu als Stammblatt pflegen.",
        example_prompts=["Oeffne Kunde neu.", "Bearbeite Stammdaten."],
        test_id="verkauf-kunde-neu",
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
        data_sources=[stamm_entity_source("/api/v1/crm/customers/{entity_id}")],
        tabs=[stamm_kopf_tab([{"key": "id", "label": "Id", "type": "text"}, {"key": "name", "label": "Name", "type": "text"}, {"key": "status", "label": "Status", "type": "text"}, {"key": "updated_at", "label": "Updated At", "type": "text"}])],
        edit_permission="verkauf.write",
        creation=dict(_VERKAUF_KUNDE_CREATION),
        no_workflow_reason="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
        business_purpose="Kunden stamm enhanced als Stammblatt pflegen.",
        example_prompts=["Oeffne Kunden stamm enhanced.", "Bearbeite Stammdaten."],
        test_id="verkauf-kunden-stamm-enhanced",
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
        prompts=["Zeige Unerledigte auftrags positionen.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Lkw beladung.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Gespeichert.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Rahmenvertraege.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Kundenumsatz.", _FILTER_LIST_PROMPT],
        bundle="vertrieb",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_neu_screen_definition() -> dict[str, Any]:
    return build_scale_create()


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
        prompts=["Zeige Vorlagen.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Wiegeschein detail.", _FILTER_LIST_PROMPT],
        bundle="waage",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


def build_waage_wiegungen_screen_definition() -> dict[str, Any]:
    return build_weighing_tickets()


def _build_flow_spine_workspace(process_key: str) -> dict[str, Any]:
    screen_id = f"workflow/flow-spine-{process_key}"
    return {
        "schemaVersion": 1, "id": screen_id, "domain": "workflow", "mode": "cockpit",
        "title": process_key, "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "expertDense", "contextRail": "workflow"},
        "flowSpineWorkspace": {"processKey": process_key},
        "agentContract": {"businessPurpose": "Prozessraum und Vorgänge bedienen.", "examplePrompts": ["Zeige den Prozessraum."], "sensitiveFields": [], "forbiddenAgentTasks": [], "testSelectors": {"screenRoot": f"[data-testid=\"workflow-flow-spine-{process_key}\"]"}},
    }


def build_workflow_flow_spine_complaint_to_resolution_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("complaint-to-resolution")


def build_workflow_flow_spine_compliance_to_report_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("compliance-to-report")


def build_workflow_flow_spine_contract_to_settlement_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("contract-to-settlement")


def build_workflow_flow_spine_finance_to_close_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("finance-to-close")


def build_workflow_flow_spine_harvest_to_settlement_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("harvest-to-settlement")


def build_workflow_flow_spine_inventory_to_settlement_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("inventory-to-settlement")


def build_workflow_flow_spine_order_to_cash_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("order-to-cash")


def build_workflow_flow_spine_procure_to_pay_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("procure-to-pay")


def build_workflow_flow_spine_service_to_customer_screen_definition() -> dict[str, Any]:
    return _build_flow_spine_workspace("service-to-customer")


def build_workflow_flow_spine_studio_screen_definition() -> dict[str, Any]:
    screen_id = "workflow/flow-spine-studio"
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": "workflow",
        "mode": "cockpit",
        "title": "Flow Spine Studio",
        "subtitle": "Prozessräume",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "expertDense", "contextRail": "workflow"},
        "flowSpineCatalog": {"enabled": True, "warmWorkspaces": True},
        "agentContract": {
            "businessPurpose": "Prozessräume aus dem Flow-Spine-Katalog öffnen.",
            "examplePrompts": ["Zeige die Prozessräume."],
            "sensitiveFields": [],
            "forbiddenAgentTasks": [],
            "testSelectors": {"screenRoot": "[data-testid='workflow-flow-spine-studio']"},
        },
        "noWorkflowReason": "Der Katalog öffnet die jeweiligen Prozessräume.",
    }


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
        prompts=["Zeige Workflow regeln.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Workflow sandbox.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Workflow monitoring.", _FILTER_LIST_PROMPT],
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
        prompts=["Zeige Liste.", _FILTER_LIST_PROMPT],
        bundle="zertifikate",
        no_workflow="Die Maske ist ein Read-Model-/Listen-Workspace; Statuswechsel erfolgen in den verlinkten Fachmasken.",
    )


BATCH15_SCREEN_BUILDERS: dict[str, Any] = {
    "einkauf/reports": build_einkauf_reports_screen_definition,
    "einkauf/service-entry-sheets": build_einkauf_service_entry_sheets_screen_definition,
    "einkauf/wareneingangsabgleich": build_einkauf_wareneingangsabgleich_screen_definition,
    "export/ustva": build_export_ustva_screen_definition,
    "fibu/abschluss-checklist-detail": build_fibu_abschluss_checklist_detail_screen_definition,
    "fibu/anlagen": build_fibu_anlagen_screen_definition,
    "fibu/atlas": build_fibu_atlas_screen_definition,
    "fibu/bilanz": build_fibu_bilanz_screen_definition,
    "fibu/geschaeftsjahre": build_fibu_geschaeftsjahre_screen_definition,
    "fibu/guv": build_fibu_guv_screen_definition,
    "fibu/monatswerte": build_fibu_monatswerte_screen_definition,
    "fibu/op-skonto-auszifferung": build_fibu_op_skonto_auszifferung_screen_definition,
    "fibu/op-verwaltung": build_fibu_op_verwaltung_screen_definition,
    "fibu/sachkonto": build_fibu_sachkonto_screen_definition,
    "fibu/sicherheiten": build_fibu_sicherheiten_screen_definition,
    "fibu/stammdaten": build_fibu_stammdaten_screen_definition,
    "fibu/zahlungsmeldungen": build_fibu_zahlungsmeldungen_screen_definition,
    "finance/abschluss": build_finance_abschluss_screen_definition,
    "finance/bank-abgleich": build_finance_bank_abgleich_screen_definition,
    "finance/bank-stamm": build_finance_bank_stamm_screen_definition,
    "finance/buchungserfassung": build_finance_buchungserfassung_screen_definition,
    "finance/buchungsimport": build_finance_buchungsimport_screen_definition,
    "finance/datev-export": build_finance_datev_export_screen_definition,
    "finance/debitoren/new": build_finance_debitoren_new_screen_definition,
    "finance/dunning-editor": build_finance_dunning_editor_screen_definition,
    "finance/kasse": build_finance_kasse_screen_definition,
    "finance/lastschriften-debitoren": build_finance_lastschriften_debitoren_screen_definition,
    "finance/op-debitoren": build_finance_op_debitoren_screen_definition,
    "finance/umsatz": build_finance_umsatz_screen_definition,
    "finance/ustva": build_finance_ustva_screen_definition,
    "finance/zahlungslauf-kreditoren": build_finance_zahlungslauf_kreditoren_screen_definition,
    "finanzplanung/liquiditaet": build_finanzplanung_liquiditaet_screen_definition,
    "foerderung/antrag": build_foerderung_antrag_screen_definition,
    "futtermittel/beratung": build_futtermittel_beratung_screen_definition,
    "futtermittel/chargen/neu": build_futtermittel_chargen_neu_screen_definition,
    "futtermittel/einzelfuttermittel/stamm/new": build_futtermittel_einzelfuttermittel_stamm_new_screen_definition,
    "futtermittel/fuetterungsdokumentation-mobil": build_futtermittel_fuetterungsdokumentation_mobil_screen_definition,
    "futtermittel/futtermittel-bestellung": build_futtermittel_futtermittel_bestellung_screen_definition,
    "futtermittel/futtermittel-statistik": build_futtermittel_futtermittel_statistik_screen_definition,
    "futtermittel/integrationsmonitor": build_futtermittel_integrationsmonitor_screen_definition,
    "futtermittel/mischfuttermittel/stamm/new": build_futtermittel_mischfuttermittel_stamm_new_screen_definition,
    "futtermittel/rations-schnittstellen-import": build_futtermittel_rations_schnittstellen_import_screen_definition,
    "futtermittel/rations-zugang": build_futtermittel_rations_zugang_screen_definition,
    "futtermittel/rationseditor": build_futtermittel_rationseditor_screen_definition,
    "futtermittel/rationsoptimierung": build_futtermittel_rationsoptimierung_screen_definition,
    "futtermittel/rationsvergleich": build_futtermittel_rationsvergleich_screen_definition,
    "futtermittel/wareneingang": build_futtermittel_wareneingang_screen_definition,
    "inventory-reports": build_inventory_reports_screen_definition,
    "inventory/epcis": build_inventory_epcis_screen_definition,
    "kasse/tagesabschluss": build_kasse_tagesabschluss_screen_definition,
    "kontrakte/FrmKontraktProtokoll": build_kontrakte_frmkontraktprotokoll_screen_definition,
    "kontrakte/mengenzeitraeume": build_kontrakte_mengenzeitraeume_screen_definition,
    "kontrakte/positionen": build_kontrakte_positionen_screen_definition,
    "lager/auslagerung": build_lager_auslagerung_screen_definition,
    "lager/bestandskorrektur": build_lager_bestandskorrektur_screen_definition,
    "lager/einlagerung": build_lager_einlagerung_screen_definition,
    "lager/gs1-scanner": build_lager_gs1_scanner_screen_definition,
    "lager/lagerplaetze": build_lager_lagerplaetze_screen_definition,
    "lager/massebilanz": build_lager_massebilanz_screen_definition,
    "lager/materialfluss-visualisierung": build_lager_materialfluss_visualisierung_screen_definition,
    "lager/permanente-inventur": build_lager_permanente_inventur_screen_definition,
    "lager/terminal": build_lager_terminal_screen_definition,
    "mahnwesen/mahnlauf": build_mahnwesen_mahnlauf_screen_definition,
    "mobile/scanner": build_mobile_scanner_screen_definition,
    "nachhaltigkeit/eudr-compliance": build_nachhaltigkeit_eudr_compliance_screen_definition,
    "personal/hrm-operations-gates": build_personal_hrm_operations_gates_screen_definition,
    "personal/mitarbeiter/neu": build_personal_mitarbeiter_neu_screen_definition,
    "personal/organigramm": build_personal_organigramm_screen_definition,
    "personal/schulung-neu": build_personal_schulung_neu_screen_definition,
    "portal/lohndienste/neu": build_portal_lohndienste_neu_screen_definition,
    "portal/onboarding": build_portal_onboarding_screen_definition,
    "portal/preisspiegel": build_portal_preisspiegel_screen_definition,
    "portal/rationsoptimierung": build_portal_rationsoptimierung_screen_definition,
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
    "produktion/produktions-dokumente-drucken": build_produktion_produktions_dokumente_drucken_screen_definition,
    "produktion/rezepturgruppen": build_produktion_rezepturgruppen_screen_definition,
    "prospecting/leads": build_prospecting_leads_screen_definition,
    "qualitaet/labor-auftrag": build_qualitaet_labor_auftrag_screen_definition,
    "qualitaet/labor-detail": build_qualitaet_labor_detail_screen_definition,
    "reports": build_reports_screen_definition,
    "reports/ReportsDashboardCharts": build_reports_reportsdashboardcharts_screen_definition,
    "reports/deckungsbeitrag": build_reports_deckungsbeitrag_screen_definition,
    "rezepte/editor": build_rezepte_editor_screen_definition,
    "sales/auftrag-lieferschein-abgleich": build_sales_auftrag_lieferschein_abgleich_screen_definition,
    "sales/auftragskette": build_sales_auftragskette_screen_definition,
    "sales/kalkulationen/neu": build_sales_kalkulationen_neu_screen_definition,
    "sales/lieferung-storno": build_sales_lieferung_storno_screen_definition,
    "service/abschluss": build_service_abschluss_screen_definition,
    "service/anfrage-detail": build_service_anfrage_detail_screen_definition,
    "service/anfrage/neu": build_service_anfrage_neu_screen_definition,
    "service/rueckmeldung": build_service_rueckmeldung_screen_definition,
    "setup/firma": build_setup_firma_screen_definition,
    "stammdaten/artikel-stoffstrom": build_stammdaten_artikel_stoffstrom_screen_definition,
    "stammdaten/artikelbestandteile": build_stammdaten_artikelbestandteile_screen_definition,
    "stammdaten/artikelverpackung": build_stammdaten_artikelverpackung_screen_definition,
    "stammdaten/betriebsstaetten": build_stammdaten_betriebsstaetten_screen_definition,
    "stammdaten/hausbanken": build_stammdaten_hausbanken_screen_definition,
    "stammdaten/individuelle-artikelnummern": build_stammdaten_individuelle_artikelnummern_screen_definition,
    "stammdaten/mengeneinheiten": build_stammdaten_mengeneinheiten_screen_definition,
    "start-dashboard": build_start_dashboard_screen_definition,
    "strecke/nawaro-uebersicht-drucken": build_strecke_nawaro_uebersicht_drucken_screen_definition,
    "strecke/speditionen-fracht-preise": build_strecke_speditionen_fracht_preise_screen_definition,
    "system/live-monitor": build_system_live_monitor_screen_definition,
    "tankstelle/zapfungen": build_tankstelle_zapfungen_screen_definition,
    "transporte/fahrer/neu": build_transporte_fahrer_neu_screen_definition,
    "verkauf/auftraege/neu": build_verkauf_auftraege_neu_screen_definition,
    "verkauf/betriebs-auftraege": build_verkauf_betriebs_auftraege_screen_definition,
    "verkauf/dauerauftraege": build_verkauf_dauerauftraege_screen_definition,
    "verkauf/kommissions-auftraege": build_verkauf_kommissions_auftraege_screen_definition,
    "verkauf/kunde-neu": build_verkauf_kunde_neu_screen_definition,
    "verkauf/kunden-stamm": build_verkauf_kunden_stamm_screen_definition,
    "verkauf/kunden-stamm-enhanced": build_verkauf_kunden_stamm_enhanced_screen_definition,
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
    "zertifikate/neu": build_zertifikate_neu_screen_definition,
}


def _register_batch15_via_finisher() -> None:
    from app.core import screen_definitions_finisher as finisher

    for key, builder in BATCH15_SCREEN_BUILDERS.items():
        finisher.FINISHER_SCREEN_BUILDERS.setdefault(key, builder)


_register_batch15_via_finisher()
