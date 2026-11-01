"""Native finance creation screens backed by the actual debtor aggregate."""

from __future__ import annotations

from typing import Any

from app.core.stamm_object_page_parent import build_stamm_object_page, stamm_entity_source, stamm_kopf_tab


DEBTOR_FIELDS: list[dict[str, Any]] = [
    {"key": "debtor_number", "label": "Debitorennummer", "type": "text", "required": True},
    {"key": "company_name", "label": "Firma", "type": "text", "required": True},
    {"key": "contact_person", "label": "Kontaktperson", "type": "text"},
    {"key": "street", "label": "Straße", "type": "text", "required": True},
    {"key": "postal_code", "label": "Postleitzahl", "type": "text", "required": True},
    {"key": "city", "label": "Ort", "type": "text", "required": True},
    {"key": "country", "label": "Land", "type": "text", "required": True},
    {"key": "phone", "label": "Telefon", "type": "text"},
    {"key": "email", "label": "E-Mail", "type": "text"},
    {"key": "vat_id", "label": "USt-IdNr.", "type": "text"},
    {"key": "tax_number", "label": "Steuernummer", "type": "text"},
    {"key": "iban", "label": "IBAN", "type": "text"},
    {"key": "bic", "label": "BIC", "type": "text"},
    {"key": "bank_name", "label": "Bank", "type": "text"},
    {"key": "account_holder", "label": "Kontoinhaber", "type": "text"},
    {"key": "payment_terms_days", "label": "Zahlungsziel (Tage)", "type": "number"},
    {"key": "discount_days", "label": "Skontofrist (Tage)", "type": "number"},
    {"key": "discount_percent", "label": "Skonto (%)", "type": "number"},
    {"key": "credit_limit", "label": "Kreditlimit", "type": "currency"},
    {"key": "is_active", "label": "Aktiv", "type": "boolean"},
    {"key": "notes", "label": "Notizen", "type": "textarea"},
]


def build_debtor_capture() -> dict[str, Any]:
    definition = build_stamm_object_page(
        screen_id="finance/debitoren/new",
        domain="finance",
        title="Debitor",
        subtitle="Debitorenstamm",
        identity_field="debtor_number",
        data_sources=[stamm_entity_source("/api/v1/finance/debtors/{entity_id}")],
        tabs=[stamm_kopf_tab(DEBTOR_FIELDS)],
        edit_permission="finance.debitor.update",
        edit_action_overrides={
            "commandEndpoint": "/api/v1/finance/debtors/{entity_id}",
            "method": "PUT",
            "responseAdapter": "resource.v1",
            "inputPrefill": "entity",
            "inputFields": [f for f in DEBTOR_FIELDS if f["key"] != "debtor_number"],
            "auditReasonRequired": True,
            "forbiddenForAgents": True,
        },
        creation={
            "endpoint": "/api/v1/finance/debtors/",
            "permission": "finance.debitor.update",
            "detailRoute": "/finance/debitoren/{entity_id}",
            "cancelRoute": "/finance/debitoren-liste",
            "defaults": {"country": "DE", "payment_terms_days": 30, "discount_days": 0,
                         "discount_percent": 0, "credit_limit": 0, "is_active": True},
            "fields": DEBTOR_FIELDS,
        },
        no_workflow_reason="Debitorenstamm ist Referenzdaten ohne Beleglebenszyklus.",
        business_purpose="Debitoren beim verifizierten Mandanten anlegen und pflegen.",
        example_prompts=["Lege einen Debitor an.", "Zeige Debitor {entity_id}."],
        test_id="finance-debitoren-new",
        density="expertDense",
        context_rail="audit",
    )
    return definition


def build_invoice_capture(*, purchase: bool) -> dict[str, Any]:
    """Capture contract for the document-store invoice APIs and server tax preview."""
    screen_id = "einkauf/rechnungseingang/neu" if purchase else "finance/invoices/new"
    endpoint = "/api/v1/finance/ap/invoices/" if purchase else "/api/v1/finance/invoices"
    permission = "finance.ap.invoice.create" if purchase else "finance.invoice.create"
    label = "Eingangsrechnung" if purchase else "Ausgangsrechnung"
    fields: list[dict[str, Any]] = [
        {"key": "number", "label": "Rechnungsnummer", "type": "text", "required": True},
        {"key": "date", "label": "Rechnungsdatum", "type": "date", "required": True},
        {"key": "customerId", "label": "Lieferant" if purchase else "Kunde", "type": "lookup", "required": True,
         "dataSourceKey": "partners"},
        {"key": "sourceOrder", "label": "Bestellung" if purchase else "Auftrag", "type": "text"},
        {"key": "sourceDelivery", "label": "Wareneingang" if purchase else "Lieferschein", "type": "text"},
        {"key": "dueDate", "label": "Fälligkeit", "type": "date", "required": True},
        {"key": "paymentTerms", "label": "Zahlungsbedingung", "type": "select", "options": [
            {"value": "net7", "label": "7 Tage netto"},
            {"value": "net14", "label": "14 Tage netto"},
            {"value": "net30", "label": "30 Tage netto"},
            {"value": "net60", "label": "60 Tage netto"},
        ]},
        {"key": "notes", "label": "Notizen", "type": "textarea"},
        {"key": "pos_article", "label": "Position: Artikel", "type": "text"},
        {"key": "pos_qty", "label": "Position: Menge", "type": "number"},
        {"key": "pos_price", "label": "Position: Einzelpreis netto", "type": "currency"},
        {"key": "pos_taxCode", "label": "Position: Steuerschlüssel", "type": "select", "options": [],
         "dataSourceKey": "tax_keys"},
    ]
    return {
        "schemaVersion": 1,
        "id": screen_id, "domain": "einkauf" if purchase else "finance", "mode": "list",
        "title": label + " erfassen", "subtitle": "Beleg als Entwurf mit Positionen erfassen",
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "dataSources": [
            {"key": "partners", "endpoint": "/api/v1/finance/ap/invoices/supplier-lookup" if purchase
             else "/api/v1/finance/invoices/customer-lookup", "pageSize": 25},
            {"key": "tax_keys", "endpoint": "/api/v1/finance/tax-keys/auswahl", "pageSize": 200},
            {"key": "tax_preview", "endpoint": endpoint.rstrip("/") + "/steuer-vorschau", "method": "POST"},
        ],
        "fields": fields,
        "summary": [
            {"key": "netto", "label": "Netto", "value": "offen", "kind": "kpi"},
            {"key": "steuer", "label": "Vorsteuer" if purchase else "Umsatzsteuer", "value": "offen", "kind": "kpi"},
            {"key": "brutto", "label": "Brutto", "value": "offen", "kind": "kpi"},
        ],
        "tables": [{"key": "positionen", "label": "Positionen", "columns": [
            {"key": "article", "label": "Artikel", "width": 180},
            {"key": "qty", "label": "Menge", "numeric": True, "renderKind": "number"},
            {"key": "price", "label": "Einzelpreis", "numeric": True, "renderKind": "currency"},
            {"key": "taxCode", "label": "Steuerschlüssel"},
        ], "rowActions": [{"key": "remove", "label": "Entfernen", "command": "finance.invoicePositionEntfernen",
                          "kind": "secondary", "dangerLevel": "safe", "permission": permission}]}],
        "actions": [
            {"key": "position", "label": "Position übernehmen", "command": "finance.invoicePosition",
             "kind": "secondary", "dangerLevel": "safe", "permission": permission},
            {"key": "save", "label": "Als Entwurf speichern", "command": "finance.invoiceSpeichern",
             "kind": "primary", "dangerLevel": "safe", "permission": permission,
             "commandEndpoint": endpoint, "method": "POST"},
        ],
        "noWorkflowReason": "Die Freigabe und Buchung erfolgen nach Anlage am Beleg.",
        "agentContract": {"businessPurpose": f"{label} mit Positionen und mandantenspezifischen Steuerschlüsseln erfassen.",
                          "examplePrompts": [f"Erfasse eine {label}."],
                          "testSelectors": {"screenRoot": f"[data-testid='{screen_id.replace('/', '-')}']",
                                            "primaryAction": "[data-testid='action-save']", "summaryArea": "[data-testid='mask-summary']"}},
        "layout": {"preferredMode": "desktopDense", "floorplan": "transaction", "density": "expertDense",
                   "contextRail": "workflow", "tableProfile": "financial", "sectionNavigation": "anchors"},
        "performance": {"initialPayloadBudgetKb": 32, "requiresLazyTabs": False,
                        "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "finance"},
    }
