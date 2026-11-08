"""Native finance creation screens; debtors are created in the leading customer master (domain_crm.customers)."""

from __future__ import annotations

from typing import Any

from app.core.stamm_object_page_parent import build_stamm_object_page, stamm_entity_source, stamm_kopf_tab


#: Felder des fuehrenden Kundenstamms (domain_crm.customers); Bank, Skonto und Steuernummer legt die Anlage
#: seit Stufe 3 am Geschaeftspartner ab (ADR Geschaeftspartnerstamm).
DEBTOR_FIELDS: list[dict[str, Any]] = [
    # Kundennummer des Kundenstamms; die Debitorennummer vergibt der Nummernkreis am Partner (Stufe 3b).
    {"key": "debtor_number", "label": "Kunden-Nr.", "type": "text", "required": True},
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
]


def build_debtor_capture() -> dict[str, Any]:
    definition = build_stamm_object_page(
        screen_id="finance/debitoren/new",
        domain="finance",
        title="Debitor",
        subtitle="Debitorenstamm",
        identity_field="debtor_number",
        data_sources=[stamm_entity_source("/api/v1/finance/debitoren/{entity_id}")],
        tabs=[stamm_kopf_tab(DEBTOR_FIELDS)],
        edit_permission="finance.debitor.update",
        edit_action_overrides={
            "commandEndpoint": "/api/v1/finance/debitoren/{entity_id}/actions/bearbeiten",
            "method": "POST",
            "inputFields": [{"key": "credit_limit", "label": "Kreditlimit", "type": "number"},
                            {"key": "is_active", "label": "Aktiv (nicht gesperrt)", "type": "boolean"}],
            "auditReasonRequired": True,
            "forbiddenForAgents": True,
        },
        creation={
            "endpoint": "/api/v1/finance/debitoren",
            "permission": "finance.debitor.update",
            "detailRoute": "/finance/debitoren/{entity_id}",
            "cancelRoute": "/finance/debitoren-liste",
            "defaults": {"country": "DE", "payment_terms_days": 30, "credit_limit": 0, "is_active": True},
            "fields": DEBTOR_FIELDS,
        },
        no_workflow_reason="Debitorenstamm ist Referenzdaten ohne Beleglebenszyklus.",
        business_purpose="Debitoren beim verifizierten Mandanten im fuehrenden Kundenstamm anlegen.",
        example_prompts=["Lege einen Debitor an.", "Zeige Debitor {entity_id}."],
        sensitive_fields=["credit_limit", "vat_id", "tax_number", "iban", "bic"],
        test_id="finance-debitoren-new",
        density="expertDense",
        context_rail="audit",
    )
    return definition


# Die Rechnungserfassung des Dokumentspeichers (build_invoice_capture) entfiel 09.11.2026: Rechnungen legt die
# Belegmaske in DocFlow an (BELEG-052).
