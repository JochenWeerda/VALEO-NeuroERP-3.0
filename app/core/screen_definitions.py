"""Native ScreenDefinition payloads for Universal Mask Generator."""

from __future__ import annotations

from typing import Any

from app.core.mask_rollout_catalog import ROLLOUT_WAVES_42_51


def build_crm_customer_360_screen_definition() -> dict[str, Any]:
    """Canonical ScreenDefinition for crm/customer-360 (Wave 29)."""

    return {
        "schemaVersion": 1,
        "id": "crm/customer-360",
        "domain": "crm",
        "mode": "detail",
        "title": "Kundenstamm",
        "subtitle": "CRM 360",
        "adapter": {
            "type": "native",
            "sourceId": "crm/customer-360",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/crm/customers/{customer_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/crm/customers/{entity_id}"},
            {"key": "contacts",    "endpoint": "/api/v1/crm/customers/{entity_id}/tabs/contacts",    "pageSize": 25},
            {"key": "auftraege",   "endpoint": "/api/v1/crm/customers/{entity_id}/tabs/auftraege",   "pageSize": 25},
            {"key": "aktivitaeten","endpoint": "/api/v1/crm/customers/{entity_id}/tabs/aktivitaeten","pageSize": 25},
            {"key": "dokumente",   "endpoint": "/api/v1/crm/customers/{entity_id}/tabs/dokumente",   "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "masterdata", "label": "Stammdaten", "lazy": True, "keepAlive": True,
                "fields": [
                    {"key": "kunden_nr", "label": "Kundennummer", "type": "text", "readOnly": True},
                    {"key": "firma", "label": "Firma / Name", "type": "text", "required": True},
                    {"key": "branche", "label": "Branche", "type": "text"},
                    {"key": "segment", "label": "Segment", "type": "text"},
                    {"key": "kreditlimit", "label": "Kreditlimit", "type": "currency"},
                    {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text"},
                    {"key": "notizen", "label": "Notizen / Chefanweisung", "type": "textarea"},
                ],
            },
            {
                "key": "address", "label": "Adresse & Kommunikation", "lazy": True, "keepAlive": True,
                "fields": [
                    {"key": "strasse", "label": "Straße", "type": "text"},
                    {"key": "plz", "label": "PLZ", "type": "text", "width": 80},
                    {"key": "ort", "label": "Ort", "type": "text"},
                    {"key": "land", "label": "Land", "type": "text"},
                    {"key": "telefon", "label": "Telefon", "type": "text"},
                    {"key": "fax", "label": "Fax", "type": "text"},
                    {"key": "email", "label": "E-Mail", "type": "email"},
                ],
            },
            {
                "key": "contacts", "label": "Ansprechpartner", "lazy": True, "keepAlive": True,
                "tables": [{"key": "contacts", "label": "Ansprechpartner", "dataSourceKey": "contacts",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "name", "label": "Name", "width": 180, "sortable": True},
                                {"key": "funktion", "label": "Funktion", "width": 140, "filterable": True},
                                {"key": "telefon", "label": "Telefon", "width": 130},
                                {"key": "email", "label": "E-Mail", "width": 200},
                            ]}],
            },
            {"key": "finance", "label": "Finanzen", "lazy": True, "keepAlive": True},
            {
                "key": "auftraege", "label": "Auftraege", "lazy": True, "keepAlive": True,
                "tables": [{"key": "auftraege", "label": "Auftraege", "dataSourceKey": "auftraege",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "auftrag_nr", "label": "Auftrag-Nr.", "width": 130, "sortable": True},
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                            ]}],
            },
            {
                "key": "aktivitaeten", "label": "Aktivitaeten", "lazy": True, "keepAlive": True,
                "tables": [{"key": "aktivitaeten", "label": "Aktivitaeten", "dataSourceKey": "aktivitaeten",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 100, "filterable": True},
                                {"key": "betreff", "label": "Betreff", "width": 220},
                                {"key": "verantwortlich", "label": "Verantwortlich", "width": 140},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                            ]}],
            },
            {
                "key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True,
                "tables": [{"key": "dokumente", "label": "Dokumente", "dataSourceKey": "dokumente",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 120, "filterable": True},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 220},
                                {"key": "benutzer", "label": "Benutzer", "width": 140},
                            ]}],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "crm.customer.update"},
            {
                "key": "create_activity",
                "label": "Aktivitaet anlegen",
                "kind": "secondary",
                "dangerLevel": "safe",
                "permission": "crm.activity.create",
                "commandEndpoint": "/api/v1/crm/customers/{entity_id}/actions/create_activity",
                "method": "POST",
                "requiresConfirmation": False,
                "humanApprovalRequired": False,
                "auditReasonRequired": False,
                "forbiddenForAgents": False,
            },
        ],
        "noWorkflowReason": "Kundenstamm ist ein reines Verwaltungsobjekt ohne prozessgesteuerten Lebenszyklus — Statuswechsel erfolgen implizit ueber Auftraege und Aktivitaeten.",
        "agentContract": {
            "businessPurpose": "360-Grad-Kundenstamm-Cockpit fuer Vertrieb und CRM — Stammdaten, Aktivitaeten, offene Auftraege und Dokumente in einer Ansicht.",
            "examplePrompts": [
                "Analysiere Kunde {entity_id}: offene Posten, letzte Aktivitaeten, Umsatz 12M.",
                "Lege eine Aktivitaet fuer Kunde {entity_id} an — Betreff: {betreff}, Typ: Anruf.",
                "Zeige alle offenen Auftraege von Kunde {entity_id} mit Status 'offen'.",
            ],
            "sensitiveFields": ["kreditlimit", "zahlungsbedingungen", "notizen"],
            "testSelectors": {
                "screenRoot": "[data-testid='crm-customer-360']",
                "primaryAction": "[data-testid='action-edit']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "crm",
        },
    }


def build_sales_order_screen_definition() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": "sales/sales-order",
        "domain": "sales",
        "mode": "detail",
        "title": "Verkaufsauftrag",
        "subtitle": "Sales Order",
        "adapter": {
            "type": "native",
            "sourceId": "sales/sales-order",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/sales/orders/{order_id}/screen-summary",
        "dataSources": [
            {"key": "entity",    "endpoint": "/api/v1/sales/orders/{entity_id}"},
            {"key": "positionen","endpoint": "/api/v1/sales/orders/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "lieferung", "endpoint": "/api/v1/sales/orders/{entity_id}/tabs/lieferung",  "pageSize": 25},
            {"key": "dokumente", "endpoint": "/api/v1/sales/orders/{entity_id}/tabs/dokumente",  "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {
                "key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True,
                "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "pos_nr", "label": "Pos.", "width": 50},
                                {"key": "artikel_nr", "label": "Artikel-Nr.", "width": 120},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 220, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True},
                                {"key": "einheit", "label": "Einheit", "width": 70},
                                {"key": "einzelpreis", "label": "Einzelpreis", "numeric": True, "renderKind": "currency"},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                            ]}],
            },
            {
                "key": "lieferung", "label": "Lieferung", "lazy": True, "keepAlive": True,
                "tables": [{"key": "lieferung", "label": "Lieferscheine", "dataSourceKey": "lieferung",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "ls_nr", "label": "LS-Nr.", "width": 130, "sortable": True},
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True},
                            ]}],
            },
            {
                "key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True,
                "tables": [{"key": "dokumente", "label": "Dokumente", "dataSourceKey": "dokumente",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 120, "filterable": True},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 220},
                            ]}],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "sales.order.update"},
        ],
        "noWorkflowReason": "Verkaufsauftrag-Status wird durch Liefer- und Rechnungsfortschritt automatisch gesetzt — kein deklarativer Prozess-Workflow.",
        "agentContract": {
            "businessPurpose": "Verkaufsauftrag-Cockpit: Kopfdaten, Positionen, Lieferscheine und Dokumente fuer Auftragsabwicklung und Kundenkommunikation.",
            "examplePrompts": [
                "Was ist der Status von Auftrag {entity_id} und welche Positionen sind noch offen?",
                "Welche Lieferscheine wurden fuer Auftrag {entity_id} erstellt?",
                "Zeige alle Dokumente von Auftrag {entity_id}.",
            ],
            "sensitiveFields": ["einzelpreis", "betrag"],
            "testSelectors": {"screenRoot": "[data-testid='sales-sales-order']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 56,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "sales",
        },
    }


def build_agrar_kontrakt_screen_definition() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": "agrar/kontrakte",
        "domain": "agrar",
        "mode": "detail",
        "title": "Kontrakt",
        "subtitle": "Agrar-Kontrakt",
        "adapter": {
            "type": "native",
            "sourceId": "agrar/kontrakte",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/kontrakte/{contract_id}/screen-summary",
        "dataSources": [
            {"key": "entity",    "endpoint": "/api/v1/kontrakte/{entity_id}"},
            {"key": "positionen","endpoint": "/api/v1/kontrakte/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "umsaetze",  "endpoint": "/api/v1/kontrakte/{entity_id}/tabs/umsaetze",  "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {
                "key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True,
                "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "pos_nr", "label": "Pos.", "width": 50},
                                {"key": "sorte", "label": "Sorte", "width": 160, "filterable": True},
                                {"key": "menge", "label": "Menge (t)", "numeric": True, "sortable": True},
                                {"key": "preis", "label": "Preis", "numeric": True, "renderKind": "currency"},
                                {"key": "ernte_jahr", "label": "Erntejahr", "width": 90},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100},
                            ]}],
            },
            {
                "key": "umsaetze", "label": "Umsaetze", "lazy": True, "keepAlive": True,
                "tables": [{"key": "umsaetze", "label": "Umsaetze", "dataSourceKey": "umsaetze",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "lieferschein_nr", "label": "LS-Nr.", "width": 130, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                            ]}],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "kontrakt.update"},
        ],
        "noWorkflowReason": "Kontrakt-Status wird durch Lieferfortschritt automatisch gesetzt — Freigabe erfolgt ausserhalb des Masken-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Agrar-Kontrakt-Cockpit: Positionen (Sorte, Menge, Preis) und Umsaetze fuer Erzeuger-Vertragsmanagement.",
            "examplePrompts": [
                "Was ist der Erfuellungsstand von Kontrakt {entity_id}?",
                "Zeige alle Lieferschein-Umsaetze fuer Kontrakt {entity_id}.",
                "Welche Sorten und Mengen sind in Kontrakt {entity_id} vereinbart?",
            ],
            "sensitiveFields": ["preis"],
            "testSelectors": {"screenRoot": "[data-testid='agrar-kontrakte']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 52,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "agrar",
        },
    }


def build_supplier_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer einkauf/supplier (UIX-038)."""
    return {
        "schemaVersion": 1,
        "id": "einkauf/supplier",
        "domain": "einkauf",
        "mode": "detail",
        "title": "Lieferant",
        "subtitle": "Lieferantenstamm",
        "adapter": {
            "type": "native",
            "sourceId": "einkauf/supplier",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/einkauf/lieferanten/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/einkauf/lieferanten/{entity_id}"},
            {"key": "bestellungen", "endpoint": "/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/bestellungen", "pageSize": 25},
            {"key": "kontakte", "endpoint": "/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/kontakte", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf",
                "label": "Stammdaten",
                "lazy": False,
                "keepAlive": True,
                "dataSourceKey": "entity",
                "fields": [
                    {"key": "lieferanten_nr", "label": "Lieferanten-Nr.", "type": "text", "readOnly": True},
                    {"key": "firma", "label": "Firma", "type": "text", "required": True},
                    {"key": "strasse", "label": "Strasse", "type": "text"},
                    {"key": "plz", "label": "PLZ", "type": "text", "width": 80},
                    {"key": "ort", "label": "Ort", "type": "text"},
                    {"key": "land", "label": "Land", "type": "text"},
                    {"key": "telefon", "label": "Telefon", "type": "text"},
                    {"key": "email", "label": "E-Mail", "type": "email"},
                    {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text"},
                    {"key": "lieferzeit_tage", "label": "Lieferzeit (Tage)", "type": "number"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "bestellungen",
                "label": "Bestellungen",
                "lazy": True,
                "keepAlive": False,
                "tables": [{
                    "key": "bestellungen",
                    "label": "Bestellungen",
                    "dataSourceKey": "bestellungen",
                    "serverPagination": True,
                    "pageSize": 25,
                    "virtualized": True,
                    "rowHeight": 52,
                    "columns": [
                        {"key": "bestell_nr", "label": "Bestell-Nr.", "width": 130, "sortable": True},
                        {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                        {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                        {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                        {"key": "waehrung", "label": "Waehrung", "width": 70},
                    ],
                }],
            },
            {
                "key": "kontakte",
                "label": "Ansprechpartner",
                "lazy": True,
                "keepAlive": False,
                "tables": [{
                    "key": "kontakte",
                    "label": "Ansprechpartner",
                    "dataSourceKey": "kontakte",
                    "serverPagination": True,
                    "pageSize": 25,
                    "virtualized": True,
                    "rowHeight": 52,
                    "columns": [
                        {"key": "name", "label": "Name", "width": 180, "sortable": True},
                        {"key": "funktion", "label": "Funktion", "width": 140, "filterable": True},
                        {"key": "telefon", "label": "Telefon", "width": 130},
                        {"key": "email", "label": "E-Mail", "width": 200},
                    ],
                }],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "einkauf.lieferant.update"},
            {"key": "neue_bestellung", "label": "Bestellung anlegen", "kind": "secondary", "dangerLevel": "safe", "permission": "einkauf.bestellung.create", "stubReason": "commandEndpoint folgt in UIX-039"},
        ],
        "noWorkflowReason": "Lieferantenstamm ist ein Verwaltungsobjekt — Prozessstatus liegt in den Bestellungen, nicht im Stammsatz.",
        "agentContract": {
            "businessPurpose": "Lieferantenstamm-Cockpit fuer Einkauf — Stammdaten, offene Bestellungen und Ansprechpartner in einer Ansicht.",
            "examplePrompts": [
                "Zeige alle offenen Bestellungen von Lieferant {entity_id} mit Status 'offen'.",
                "Welche Ansprechpartner gibt es bei Lieferant {entity_id}?",
                "Wie sind die Zahlungsbedingungen und Lieferzeiten von Lieferant {entity_id}?",
            ],
            "sensitiveFields": ["zahlungsbedingungen", "lieferzeit_tage"],
            "testSelectors": {
                "screenRoot": "[data-testid='einkauf-supplier-360']",
                "primaryAction": "[data-testid='action-edit']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "einkauf",
        },
    }


def build_crm_opportunity_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer crm/opportunity (UIX-039)."""
    return {
        "schemaVersion": 1,
        "id": "crm/opportunity",
        "domain": "crm",
        "mode": "detail",
        "title": "Opportunity",
        "subtitle": "CRM Verkaufschance",
        "adapter": {
            "type": "native",
            "sourceId": "crm/opportunity",
            "temporary": False,
        },
        "summaryEndpoint": "/api/v1/crm/opportunities/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/crm/opportunities/{entity_id}"},
            {"key": "aktivitaeten", "endpoint": "/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/aktivitaeten", "pageSize": 25},
            {"key": "angebote", "endpoint": "/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/angebote", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf",
                "label": "Stammdaten",
                "lazy": False,
                "keepAlive": True,
                "dataSourceKey": "entity",
                "fields": [
                    {"key": "opportunity_nr", "label": "Opportunity-Nr.", "type": "text", "readOnly": True},
                    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                    {"key": "kunde", "label": "Kunde", "type": "text"},
                    {"key": "verantwortlich", "label": "Verantwortlich", "type": "text"},
                    {"key": "phase", "label": "Phase", "type": "text"},
                    {"key": "wert", "label": "Wert", "type": "currency"},
                    {"key": "wahrscheinlichkeit", "label": "Wahrscheinlichkeit %", "type": "number"},
                    {"key": "abschluss_datum", "label": "Abschlussdatum", "type": "date"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "aktivitaeten",
                "label": "Aktivitaeten",
                "lazy": True,
                "keepAlive": False,
                "tables": [{
                    "key": "aktivitaeten",
                    "label": "Aktivitaeten",
                    "dataSourceKey": "aktivitaeten",
                    "serverPagination": True,
                    "pageSize": 25,
                    "virtualized": True,
                    "rowHeight": 52,
                    "columns": [
                        {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                        {"key": "typ", "label": "Typ", "width": 100, "filterable": True},
                        {"key": "betreff", "label": "Betreff", "width": 220},
                        {"key": "verantwortlich", "label": "Verantwortlich", "width": 140},
                        {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                    ],
                }],
            },
            {
                "key": "angebote",
                "label": "Angebote",
                "lazy": True,
                "keepAlive": False,
                "tables": [{
                    "key": "angebote",
                    "label": "Angebote",
                    "dataSourceKey": "angebote",
                    "serverPagination": True,
                    "pageSize": 25,
                    "virtualized": True,
                    "rowHeight": 52,
                    "columns": [
                        {"key": "angebot_nr", "label": "Angebot-Nr.", "width": 130, "sortable": True},
                        {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                        {"key": "wert", "label": "Wert", "numeric": True, "sortable": True, "renderKind": "currency"},
                        {"key": "waehrung", "label": "Waehrung", "width": 70},
                        {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                    ],
                }],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "crm.opportunity.update"},
            {"key": "create_activity", "label": "Aktivitaet anlegen", "kind": "secondary", "dangerLevel": "safe", "permission": "crm.activity.create", "stubReason": "commandEndpoint ueber crm_360 bei Bedarf"},
        ],
        "noWorkflowReason": "Opportunity-Phasen werden manuell gesteuert — kein automatischer Prozess-Lebenszyklus erforderlich.",
        "agentContract": {
            "businessPurpose": "CRM-Verkaufschance: Phase, Wert, Wahrscheinlichkeit, Aktivitaeten und Angebote in einer Ansicht fuer Vertriebssteuerung.",
            "examplePrompts": [
                "Was ist der aktuelle Status und die Wahrscheinlichkeit von Opportunity {entity_id}?",
                "Zeige alle Aktivitaeten der letzten 30 Tage fuer Opportunity {entity_id}.",
                "Welche Angebote sind mit Opportunity {entity_id} verknuepft?",
            ],
            "sensitiveFields": ["wert", "wahrscheinlichkeit"],
            "testSelectors": {
                "screenRoot": "[data-testid='crm-opportunity-360']",
                "primaryAction": "[data-testid='action-edit']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "crm",
        },
    }


def build_lager_article_stock_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer lager/article-stock (UIX-040)."""
    return {
        "schemaVersion": 1,
        "id": "lager/article-stock",
        "domain": "lager",
        "mode": "detail",
        "title": "Artikelbestand",
        "subtitle": "Lager / Bestandsfuehrung",
        "adapter": {"type": "native", "sourceId": "lager/article-stock", "temporary": False},
        "summaryEndpoint": "/api/v1/articles/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/articles/{entity_id}"},
            {"key": "bestand", "endpoint": "/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bestand", "pageSize": 25},
            {"key": "bewegungen", "endpoint": "/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bewegungen", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Artikelstamm", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text", "readOnly": True},
                    {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                    {"key": "artikel_gruppe", "label": "Artikelgruppe", "type": "text"},
                    {"key": "einheit", "label": "Basiseinheit", "type": "text"},
                    {"key": "mindestbestand", "label": "Mindestbestand", "type": "number"},
                    {"key": "meldebestand", "label": "Meldebestand", "type": "number"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "bestand", "label": "Bestand je Lagerort", "lazy": True, "keepAlive": False,
                "tables": [{"key": "bestand", "label": "Bestand", "dataSourceKey": "bestand",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "lagerort_nr", "label": "Lagerort-Nr.", "width": 120, "sortable": True},
                                {"key": "lagerort_bezeichnung", "label": "Bezeichnung", "width": 180},
                                {"key": "bestand_menge", "label": "Bestand", "numeric": True, "sortable": True, "renderKind": "number"},
                                {"key": "einheit", "label": "Einheit", "width": 70},
                                {"key": "reserviert", "label": "Reserviert", "numeric": True, "sortable": True, "renderKind": "number"},
                                {"key": "mindestbestand", "label": "Mindestbest.", "numeric": True, "renderKind": "number", "filterable": True},
                            ]}],
            },
            {
                "key": "bewegungen", "label": "Lagerbewegungen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "bewegungen", "label": "Bewegungen", "dataSourceKey": "bewegungen",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 100, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                                {"key": "einheit", "label": "Einheit", "width": 70},
                                {"key": "beleg_nr", "label": "Beleg-Nr.", "width": 120},
                            ]}],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "lager.artikel.update"},
        ],
        "noWorkflowReason": "Artikelstamm ist ein reines Verwaltungsobjekt — kein prozessgesteuerter Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Artikelbestand-Cockpit: Stammdaten, Bestand je Lagerort und Bewegungshistorie fuer Disposition und Einkauf.",
            "examplePrompts": [
                "Wie hoch ist der aktuelle Bestand von Artikel {entity_id} je Lagerort?",
                "Zeige alle Lagerbewegungen von Artikel {entity_id} der letzten 30 Tage.",
                "Welche Lagerorte haben Bestand unter Mindestbestand fuer Artikel {entity_id}?",
            ],
            "sensitiveFields": ["mindestbestand", "meldebestand"],
            "testSelectors": {
                "screenRoot": "[data-testid='lager-article-stock']",
                "primaryAction": "[data-testid='action-edit']",
                "summaryArea": "[data-testid='mask-summary']",
            },
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "lager"},
    }


def build_sales_delivery_note_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer sales/delivery-note (UIX-041)."""
    return {
        "schemaVersion": 1,
        "id": "sales/delivery-note",
        "domain": "sales",
        "mode": "detail",
        "title": "Lieferschein",
        "subtitle": "Verkauf / Warenausgang",
        "adapter": {"type": "native", "sourceId": "sales/delivery-note", "temporary": False},
        "summaryEndpoint": "/api/v1/sales/delivery-notes/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/sales/delivery-notes/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "dokumente", "endpoint": "/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/dokumente", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Lieferschein-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "ls_nr", "label": "LS-Nr.", "type": "text", "readOnly": True},
                    {"key": "auftrag_nr", "label": "Auftrag-Nr.", "type": "text", "readOnly": True},
                    {"key": "kunde", "label": "Kunde", "type": "text"},
                    {"key": "datum", "label": "Datum", "type": "date"},
                    {"key": "versandart", "label": "Versandart", "type": "text"},
                    {"key": "lagerort", "label": "Lagerort", "type": "text"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "pos_nr", "label": "Pos.", "width": 50, "sortable": True},
                                {"key": "artikel_nr", "label": "Artikel-Nr.", "width": 120},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 200, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                                {"key": "einheit", "label": "Einheit", "width": 70},
                                {"key": "charge", "label": "Charge", "width": 120},
                            ]}],
            },
            {
                "key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": False,
                "tables": [{"key": "dokumente", "label": "Dokumente", "dataSourceKey": "dokumente",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 120, "filterable": True},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 220},
                                {"key": "benutzer", "label": "Benutzer", "width": 140},
                            ]}],
            },
        ],
        "actions": [
            {"key": "drucken", "label": "Lieferschein drucken", "kind": "primary", "dangerLevel": "safe", "permission": "sales.lieferschein.drucken", "stubReason": "PDF-Druck commandEndpoint folgt"},
        ],
        "noWorkflowReason": "Lieferschein-Status wird ueber den Verkaufsauftrag gesteuert — kein eigener Workflow-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Lieferschein-Cockpit: Kopfdaten, Positionen und Dokumente fuer Warenausgang und Lieferverfolgung.",
            "examplePrompts": [
                "Zeige alle Positionen und Chargen von Lieferschein {entity_id}.",
                "Welche Dokumente sind mit Lieferschein {entity_id} verknuepft?",
                "Was ist der aktuelle Status von Lieferschein {entity_id}?",
            ],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='sales-delivery-note']", "primaryAction": "[data-testid='action-drucken']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "sales"},
    }


def build_einkauf_purchase_order_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer einkauf/purchase-order (UIX-041)."""
    return {
        "schemaVersion": 1,
        "id": "einkauf/purchase-order",
        "domain": "einkauf",
        "mode": "detail",
        "title": "Bestellung",
        "subtitle": "Einkauf / Bestellvorgang",
        "adapter": {"type": "native", "sourceId": "einkauf/purchase-order", "temporary": False},
        "summaryEndpoint": "/api/v1/einkauf/bestellungen/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/einkauf/bestellungen/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "kommunikation", "endpoint": "/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/kommunikation", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Bestell-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "bestell_nr", "label": "Bestell-Nr.", "type": "text", "readOnly": True},
                    {"key": "lieferant", "label": "Lieferant", "type": "text"},
                    {"key": "datum", "label": "Datum", "type": "date"},
                    {"key": "lieferdatum", "label": "Lieferdatum", "type": "date"},
                    {"key": "betrag", "label": "Betrag", "type": "currency"},
                    {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "pos_nr", "label": "Pos.", "width": 50, "sortable": True},
                                {"key": "artikel_nr", "label": "Artikel-Nr.", "width": 120},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 200, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                                {"key": "einheit", "label": "Einheit", "width": 70},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                            ]}],
            },
            {
                "key": "kommunikation", "label": "Kommunikation", "lazy": True, "keepAlive": False,
                "tables": [{"key": "kommunikation", "label": "Nachrichten", "dataSourceKey": "kommunikation",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 100, "filterable": True},
                                {"key": "betreff", "label": "Betreff", "width": 220},
                                {"key": "benutzer", "label": "Benutzer", "width": 140},
                            ]}],
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "einkauf.bestellung.update"},
        ],
        "noWorkflowReason": "Bestellstatus wird im Bestellvorgang manuell gesetzt — kein automatischer Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Einkaufs-Bestellung: Kopfdaten, Positionen und Kommunikation fuer Beschaffungssteuerung.",
            "examplePrompts": [
                "Was ist der Status von Bestellung {entity_id} und wann ist der Liefertermin?",
                "Zeige alle Positionen und bestellten Mengen von Bestellung {entity_id}.",
            ],
            "sensitiveFields": ["zahlungsbedingungen", "betrag"],
            "testSelectors": {"screenRoot": "[data-testid='einkauf-purchase-order']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "einkauf"},
    }


def build_finance_ap_invoice_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer finance/ap-invoice (UIX-041)."""
    return {
        "schemaVersion": 1,
        "id": "finance/ap-invoice",
        "domain": "finance",
        "mode": "detail",
        "title": "Eingangsrechnung",
        "subtitle": "Finance / Accounts Payable",
        "adapter": {"type": "native", "sourceId": "finance/ap-invoice", "temporary": False},
        "summaryEndpoint": "/api/v1/finance/ap/invoices/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/finance/ap/invoices/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "freigabe", "endpoint": "/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/freigabe", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Rechnungs-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "beleg_nr", "label": "Beleg-Nr.", "type": "text", "readOnly": True},
                    {"key": "kreditor", "label": "Kreditor", "type": "text"},
                    {"key": "datum", "label": "Rechnungsdatum", "type": "date"},
                    {"key": "faellig_am", "label": "Faellig am", "type": "date"},
                    {"key": "brutto", "label": "Brutto", "type": "currency"},
                    {"key": "mwst", "label": "MwSt.", "type": "currency"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "pos_nr", "label": "Pos.", "width": 50, "sortable": True},
                                {"key": "bezeichnung", "label": "Bezeichnung", "width": 200, "filterable": True},
                                {"key": "menge", "label": "Menge", "numeric": True, "renderKind": "number"},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                                {"key": "konto", "label": "Konto", "width": 100},
                            ]}],
            },
            {
                "key": "freigabe", "label": "Freigabe", "lazy": True, "keepAlive": False,
                "tables": [{"key": "freigabe", "label": "Freigabe-Historie", "dataSourceKey": "freigabe",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "benutzer", "label": "Benutzer", "width": 160, "sortable": True},
                                {"key": "aktion", "label": "Aktion", "width": 120, "filterable": True},
                                {"key": "kommentar", "label": "Kommentar", "width": 240},
                            ]}],
            },
        ],
        "actions": [
            {"key": "freigeben", "label": "Freigeben", "kind": "primary", "dangerLevel": "moderate", "permission": "finance.ap.freigabe", "requiresConfirmation": True, "stubReason": "commandEndpoint folgt in UIX-042"},
        ],
        "noWorkflowReason": "Freigabe-Workflow ist tabellenbasiert — explizite Workflow-Deklaration nach vollstaendiger AP-Parity.",
        "agentContract": {
            "businessPurpose": "Eingangsrechnung: Kopfdaten, Positionen und Freigabe-Historie fuer AP-Buchhalter und Audit.",
            "examplePrompts": [
                "Was ist der Freigabe-Status von Eingangsrechnung {entity_id}?",
                "Wann ist Eingangsrechnung {entity_id} faellig und wie hoch ist der Bruttobetrag?",
            ],
            "sensitiveFields": ["brutto", "mwst", "faellig_am"],
            "testSelectors": {"screenRoot": "[data-testid='finance-ap-invoice']", "primaryAction": "[data-testid='action-freigeben']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_finance_ar_open_item_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer finance/ar-open-item (UIX-041)."""
    return {
        "schemaVersion": 1,
        "id": "finance/ar-open-item",
        "domain": "finance",
        "mode": "detail",
        "title": "Offener Posten",
        "subtitle": "Finance / Accounts Receivable",
        "adapter": {"type": "native", "sourceId": "finance/ar-open-item", "temporary": False},
        "summaryEndpoint": "/api/v1/finance/open-items/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/finance/open-items/{entity_id}"},
            {"key": "ausgleich", "endpoint": "/api/v1/mask-rollouts/finance/ar-open-item/{entity_id}/tabs/ausgleich", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "OP-Daten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "beleg_nr", "label": "Beleg-Nr.", "type": "text", "readOnly": True},
                    {"key": "debitor", "label": "Debitor", "type": "text"},
                    {"key": "datum", "label": "Belegdatum", "type": "date"},
                    {"key": "faellig_am", "label": "Faellig am", "type": "date"},
                    {"key": "brutto", "label": "Brutto", "type": "currency"},
                    {"key": "offen", "label": "Offen", "type": "currency"},
                    {"key": "skonto", "label": "Skonto", "type": "currency"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "ausgleich", "label": "Ausgleich / Zahlungen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "ausgleich", "label": "Ausgleich", "dataSourceKey": "ausgleich",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                                {"key": "zahlungsart", "label": "Zahlungsart", "width": 120, "filterable": True},
                                {"key": "bank_ref", "label": "Bank-Referenz", "width": 160},
                            ]}],
            },
        ],
        "actions": [
            {"key": "mahnen", "label": "Mahnung erstellen", "kind": "primary", "dangerLevel": "moderate", "permission": "finance.ar.mahnung", "requiresConfirmation": True, "stubReason": "commandEndpoint folgt"},
        ],
        "noWorkflowReason": "OP-Status wird durch Zahlungseingaenge automatisch gesetzt — kein separater Workflow noetig.",
        "agentContract": {
            "businessPurpose": "Offener Posten: Forderungs-Cockpit fuer Debitorenbuchhaltung mit Faelligkeiten, Skonto und Ausgleichshistorie.",
            "examplePrompts": [
                "Wann ist OP {entity_id} faellig und wie hoch ist der offene Betrag?",
                "Zeige alle bisherigen Zahlungseingaenge fuer OP {entity_id}.",
            ],
            "sensitiveFields": ["brutto", "offen", "skonto", "faellig_am"],
            "testSelectors": {"screenRoot": "[data-testid='finance-ar-open-item']", "primaryAction": "[data-testid='action-mahnen']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_lager_stock_movement_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer lager/stock-movement (UIX-041)."""
    return {
        "schemaVersion": 1,
        "id": "lager/stock-movement",
        "domain": "lager",
        "mode": "detail",
        "title": "Lagerbewegung",
        "subtitle": "Lager / Warenbewegung",
        "adapter": {"type": "native", "sourceId": "lager/stock-movement", "temporary": False},
        "summaryEndpoint": "/api/v1/inventory/stock-movements/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/inventory/stock-movements/{entity_id}"},
            {"key": "details", "endpoint": "/api/v1/mask-rollouts/lager/stock-movement/{entity_id}/tabs/details", "pageSize": 50},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Bewegungs-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "bewegungs_nr", "label": "Bewegungs-Nr.", "type": "text", "readOnly": True},
                    {"key": "typ", "label": "Typ", "type": "text"},
                    {"key": "datum", "label": "Datum", "type": "date"},
                    {"key": "beleg_nr", "label": "Beleg-Nr.", "type": "text"},
                    {"key": "lagerort", "label": "Lagerort", "type": "text"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "details", "label": "Positionen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "details", "label": "Positionen", "dataSourceKey": "details",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "typ", "label": "Typ", "width": 100, "filterable": True},
                                {"key": "beleg_nr", "label": "Beleg-Nr.", "width": 120},
                                {"key": "lagerort", "label": "Lagerort", "width": 140, "sortable": True},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100},
                            ]}],
            },
        ],
        "actions": [
            {"key": "stornieren", "label": "Stornieren", "kind": "primary", "dangerLevel": "high", "permission": "lager.bewegung.stornieren", "requiresConfirmation": True, "humanApprovalRequired": True, "stubReason": "commandEndpoint folgt"},
        ],
        "noWorkflowReason": "Lagerbewegungen sind Buchungsbelege ohne eigenstaendigen Workflow — Storno ist die einzige Mutation.",
        "agentContract": {
            "businessPurpose": "Lagerbewegung: Einzelne Warenbewegung mit Belegpositionen fuer Lager-Audit und Traceability.",
            "examplePrompts": [
                "Was ist der Status und Typ von Lagerbewegung {entity_id}?",
                "Zeige alle Positionen und betroffenen Lagerorte von Bewegung {entity_id}.",
            ],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='lager-stock-movement']", "primaryAction": "[data-testid='action-stornieren']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "lager"},
    }


def build_agrar_harvest_settlement_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer agrar/harvest-settlement (UIX-041).

    Hinweis: Ernte-Abrechnung ist fachlich komplex — Readiness intentional
    ohne commandEndpoints fuer Zahlungs-Aktionen (Risiko-Gate).
    """
    return {
        "schemaVersion": 1,
        "id": "agrar/harvest-settlement",
        "domain": "agrar",
        "mode": "detail",
        "title": "Ernte-Abrechnung",
        "subtitle": "Agrar / Ernteannahme-Abrechnung",
        "adapter": {"type": "native", "sourceId": "agrar/harvest-settlement", "temporary": False},
        "summaryEndpoint": "/api/v1/agrar/settlements/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/agrar/settlements/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/positionen", "pageSize": 50},
            {"key": "abzuege", "endpoint": "/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/abzuege", "pageSize": 25},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Abrechnungs-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "abrechnungs_nr", "label": "Abrechnungs-Nr.", "type": "text", "readOnly": True},
                    {"key": "erzeuger", "label": "Erzeuger", "type": "text"},
                    {"key": "ernte_jahr", "label": "Erntejahr", "type": "text"},
                    {"key": "sorte", "label": "Hauptsorte", "type": "text"},
                    {"key": "gesamtmenge", "label": "Gesamtmenge (t)", "type": "number"},
                    {"key": "gesamtbetrag", "label": "Gesamtbetrag", "type": "currency"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "positionen", "label": "Lieferschein-Positionen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "positionen", "label": "Lieferscheine", "dataSourceKey": "positionen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "lieferschein_nr", "label": "LS-Nr.", "width": 130, "sortable": True},
                                {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                                {"key": "sorte", "label": "Sorte", "width": 140, "filterable": True},
                                {"key": "feuchtigkeit", "label": "Feuchte %", "numeric": True, "renderKind": "number"},
                                {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                            ]}],
            },
            {
                "key": "abzuege", "label": "Qualitaets-Abzuege", "lazy": True, "keepAlive": False,
                "tables": [{"key": "abzuege", "label": "Abzuege", "dataSourceKey": "abzuege",
                            "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "abzug_art", "label": "Abzug-Art", "width": 140, "filterable": True},
                                {"key": "beschreibung", "label": "Beschreibung", "width": 200},
                                {"key": "menge", "label": "Menge", "numeric": True, "renderKind": "number"},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                            ]}],
            },
        ],
        "actions": [
            {"key": "drucken", "label": "Abrechnung drucken", "kind": "primary", "dangerLevel": "safe", "permission": "agrar.abrechnung.drucken", "stubReason": "PDF-Druck commandEndpoint folgt"},
        ],
        "noWorkflowReason": "Ernte-Abrechnung wird manuell freigegeben — Auszahlung erfolgt ueber separaten Finance-Zahlungslauf (finance/payment-run).",
        "agentContract": {
            "businessPurpose": "Ernte-Abrechnung: Erzeuger-Abrechnung mit Lieferschein-Positionen, Qualitaets-Abzuegen und Gesamtbetrag fuer Agrar-Buchhalter.",
            "examplePrompts": [
                "Was ist der Gesamtbetrag und Status der Ernte-Abrechnung {entity_id}?",
                "Zeige alle Lieferschein-Positionen und Qualitaets-Abzuege von Abrechnung {entity_id}.",
            ],
            "sensitiveFields": ["gesamtbetrag"],
            "testSelectors": {"screenRoot": "[data-testid='agrar-harvest-settlement']", "primaryAction": "[data-testid='action-drucken']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 52, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar"},
    }


def build_finance_payment_run_screen_definition() -> dict[str, Any]:
    """Native ScreenDefinition fuer finance/payment-run (UIX-041).

    Hoechstes Risiko: commandEndpoints fuer Zahlungs-Aktionen intentional
    gestubt — humanApprovalRequired=True erzwungen.
    """
    return {
        "schemaVersion": 1,
        "id": "finance/payment-run",
        "domain": "finance",
        "mode": "detail",
        "title": "Zahlungslauf",
        "subtitle": "Finance / Massenzahlung",
        "adapter": {"type": "native", "sourceId": "finance/payment-run", "temporary": False},
        "summaryEndpoint": "/api/v1/finance/payment-runs/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/finance/payment-runs/{entity_id}"},
            {"key": "zahlungen", "endpoint": "/api/v1/mask-rollouts/finance/payment-run/{entity_id}/tabs/zahlungen", "pageSize": 50},
        ],
        "tabs": [
            {
                "key": "kopf", "label": "Zahlungslauf-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
                "fields": [
                    {"key": "lauf_nr", "label": "Lauf-Nr.", "type": "text", "readOnly": True},
                    {"key": "datum", "label": "Ausfuehrungsdatum", "type": "date"},
                    {"key": "bank", "label": "Bank", "type": "text"},
                    {"key": "gesamtbetrag", "label": "Gesamtbetrag", "type": "currency"},
                    {"key": "anzahl_zahlungen", "label": "Anzahl Zahlungen", "type": "number"},
                    {"key": "status", "label": "Status", "type": "text"},
                ],
            },
            {
                "key": "zahlungen", "label": "Einzelzahlungen", "lazy": True, "keepAlive": False,
                "tables": [{"key": "zahlungen", "label": "Zahlungen", "dataSourceKey": "zahlungen",
                            "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                            "columns": [
                                {"key": "kreditoren_nr", "label": "Kreditor-Nr.", "width": 120, "sortable": True},
                                {"key": "name", "label": "Name", "width": 200},
                                {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                                {"key": "bank", "label": "Bank", "width": 140},
                                {"key": "status", "label": "Status", "renderKind": "status", "width": 100, "filterable": True},
                            ]}],
            },
        ],
        "actions": [
            {
                "key": "freigeben",
                "label": "Zahlungslauf freigeben",
                "kind": "primary",
                "dangerLevel": "critical",
                "permission": "finance.payment_run.freigabe",
                "requiresConfirmation": True,
                "humanApprovalRequired": True,
                "auditReasonRequired": True,
                "forbiddenForAgents": True,
                "stubReason": "commandEndpoint nur nach vollstaendiger AP+AR-Parity und 4-Augen-Freigabe",
            },
        ],
        "noWorkflowReason": "Zahlungslauf ist Batch-Vorgang — Freigabe-Gate separat; kein laufender Prozess nach Ausfuehrung.",
        "agentContract": {
            "businessPurpose": "Zahlungslauf-Cockpit (read-only fuer Agenten): Laufdetails und Einzelzahlungen fuer Audit und Reconciliation. Freigabe ist Agent-gesperrt.",
            "examplePrompts": [
                "Was ist der Status von Zahlungslauf {entity_id} und wie hoch ist der Gesamtbetrag?",
                "Zeige alle Einzelzahlungen von Zahlungslauf {entity_id} mit Status 'fehler'.",
            ],
            "sensitiveFields": ["gesamtbetrag", "bank"],
            "testSelectors": {"screenRoot": "[data-testid='finance-payment-run']", "primaryAction": "[data-testid='action-freigeben']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


_SCREEN_DEFINITIONS: dict[str, Any] = {
    "crm/customer-360": build_crm_customer_360_screen_definition,
    "sales/sales-order": build_sales_order_screen_definition,
    "agrar/kontrakte": build_agrar_kontrakt_screen_definition,
    "einkauf/supplier": build_supplier_screen_definition,
    "crm/opportunity": build_crm_opportunity_screen_definition,
    "lager/article-stock": build_lager_article_stock_screen_definition,
    "sales/delivery-note": build_sales_delivery_note_screen_definition,
    "einkauf/purchase-order": build_einkauf_purchase_order_screen_definition,
    "finance/ap-invoice": build_finance_ap_invoice_screen_definition,
    "finance/ar-open-item": build_finance_ar_open_item_screen_definition,
    "lager/stock-movement": build_lager_stock_movement_screen_definition,
    "agrar/harvest-settlement": build_agrar_harvest_settlement_screen_definition,
    "finance/payment-run": build_finance_payment_run_screen_definition,
}


_TAB_LABELS: dict[str, str] = {
    "details": "Details",
    "bestand": "Bestand",
    "bewegungen": "Bewegungen",
    "positionen": "Positionen",
    "lieferungen": "Lieferungen",
    "kontakte": "Kontakte",
    "bestellungen": "Bestellungen",
    "aktivitaeten": "Aktivitaeten",
    "angebote": "Angebote",
    "abzuege": "Abzuege",
    "zahlungen": "Zahlungen",
    "belege": "Belege",
    "auftraege": "Auftraege",
    "fehler": "Fehler",
}


def _col(key: str, label: str, **kwargs: Any) -> dict[str, Any]:
    return {"key": key, "label": label, **kwargs}


def _num(key: str, label: str, render_kind: str = "number", **kwargs: Any) -> dict[str, Any]:
    return _col(key, label, numeric=True, sortable=True, renderKind=render_kind, **kwargs)


def _date(key: str, label: str) -> dict[str, Any]:
    return _col(key, label, sortable=True, renderKind="date", width=110)


def _status(key: str, label: str) -> dict[str, Any]:
    return _col(key, label, renderKind="status", width=100)


def _txt(key: str, label: str, **kwargs: Any) -> dict[str, Any]:
    return _col(key, label, **kwargs)


_ROLLOUT_TAB_COLUMNS: dict[str, dict[str, list[dict[str, Any]]]] = {
    "lager/stock-movement": {
        "details": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
            _txt("lagerort", "Lagerort"),
            _status("status", "Status"),
        ],
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("charge", "Charge", width=120),
        ],
    },
    "lager/article-stock": {
        "bestand": [
            _txt("lagerort_nr", "Lagerort-Nr.", width=120),
            _txt("lagerort_bezeichnung", "Bezeichnung", width=180),
            _num("bestand_menge", "Bestand"),
            _txt("einheit", "Einheit", width=70),
            _num("reserviert", "Reserviert"),
            _num("mindestbestand", "Mindestbest."),
        ],
        "bewegungen": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
        ],
    },
    "finance/ap-invoice": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _num("einzelpreis", "Einzelpreis", render_kind="currency"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("konto", "Konto", width=100),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("zahlungsart", "Zahlungsart", width=120),
            _txt("bank_ref", "Bank-Referenz", width=160),
        ],
        "belege": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=120),
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
    },
    "finance/ar-open-item": {
        "details": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=130),
            _date("faellig_am", "Faellig am"),
            _num("brutto", "Brutto", render_kind="currency"),
            _num("offen", "Offen", render_kind="currency"),
            _num("skonto", "Skonto", render_kind="currency"),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("zahlungsart", "Zahlungsart", width=120),
            _txt("eingang_bank", "Eingang Bank", width=160),
        ],
    },
    "einkauf/purchase-order": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _num("einzelpreis", "Einzelpreis", render_kind="currency"),
            _num("betrag", "Betrag", render_kind="currency"),
            _date("lieferdatum", "Lieferdatum"),
        ],
        "lieferungen": [
            _date("datum", "Datum"),
            _txt("lieferschein_nr", "LS-Nr.", width=130),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("lagerort", "Lagerort"),
        ],
        "belege": [
            _txt("beleg_art", "Beleg-Art", width=100),
            _txt("beleg_nr", "Beleg-Nr.", width=130),
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
    },
    "einkauf/supplier": {
        "kontakte": [
            _txt("name", "Name", width=180, sortable=True),
            _txt("funktion", "Funktion", width=140, filterable=True),
            _txt("telefon", "Telefon", width=130),
            _txt("email", "E-Mail", width=200),
        ],
        "bestellungen": [
            _txt("bestell_nr", "Bestell-Nr.", width=130, sortable=True),
            _date("datum", "Datum"),
            _status("status", "Status"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("waehrung", "Waehrung", width=70),
        ],
    },
    "crm/opportunity": {
        "aktivitaeten": [
            _date("datum", "Datum"),
            _txt("typ", "Typ", width=100),
            _txt("betreff", "Betreff", width=220),
            _txt("verantwortlich", "Verantwortlich", width=140),
            _status("status", "Status"),
        ],
        "angebote": [
            _txt("angebot_nr", "Angebot-Nr.", width=130),
            _date("datum", "Datum"),
            _num("wert", "Wert", render_kind="currency"),
            _txt("waehrung", "Waehrung", width=70),
            _status("status", "Status"),
        ],
    },
    "sales/delivery-note": {
        "positionen": [
            _txt("pos_nr", "Pos.", width=50),
            _txt("artikel_nr", "Artikel-Nr.", width=120),
            _txt("bezeichnung", "Bezeichnung", width=200),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("charge", "Charge", width=120),
            _txt("lagerort", "Lagerort"),
        ],
        "auftraege": [
            _txt("auftrag_nr", "Auftrag-Nr.", width=130),
            _date("datum", "Datum"),
            _txt("pos_nr", "Pos.", width=50),
            _num("auftragsmenge", "Auftr.-Menge"),
        ],
    },
    "agrar/harvest-settlement": {
        "positionen": [
            _txt("lieferschein_nr", "LS-Nr.", width=130),
            _date("datum", "Datum"),
            _txt("sorte", "Sorte", width=140),
            _num("feuchtigkeit", "Feuchte %", render_kind="number"),
            _num("menge", "Menge"),
            _txt("einheit", "Einheit", width=70),
            _txt("qualitaet", "Qualitaet", width=100),
        ],
        "abzuege": [
            _txt("abzug_art", "Abzug-Art", width=140),
            _txt("beschreibung", "Beschreibung", width=200),
            _num("menge", "Menge"),
            _num("betrag", "Betrag", render_kind="currency"),
        ],
        "zahlungen": [
            _date("datum", "Datum"),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("bank_ref", "Bank-Referenz", width=160),
            _txt("auszahlungs_art", "Art", width=100),
        ],
    },
    "finance/payment-run": {
        "zahlungen": [
            _txt("kreditoren_nr", "Kreditor-Nr.", width=120),
            _txt("name", "Name", width=200),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("bank", "Bank", width=140),
            _txt("iban", "IBAN", width=200),
            _date("faellig_am", "Faellig am"),
            _status("status", "Status"),
        ],
        "fehler": [
            _txt("kreditoren_nr", "Kreditor-Nr.", width=120),
            _txt("name", "Name", width=200),
            _num("betrag", "Betrag", render_kind="currency"),
            _txt("fehlertyp", "Fehlertyp", width=130),
            _txt("meldung", "Meldung", width=300),
        ],
    },
}


_ROLLOUT_KOPF_FIELDS: dict[str, list[dict[str, Any]]] = {
    "_default": [
        {"key": "nummer", "label": "Nummer", "type": "text", "readOnly": True},
        {"key": "bezeichnung", "label": "Bezeichnung", "type": "text"},
        {"key": "datum", "label": "Datum", "type": "date"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "lager": [
        {"key": "bewegungs_nr", "label": "Bewegungs-Nr.", "type": "text", "readOnly": True},
        {"key": "artikel_nr", "label": "Artikel-Nr.", "type": "text"},
        {"key": "artikel_bezeichnung", "label": "Bezeichnung", "type": "text"},
        {"key": "datum", "label": "Datum", "type": "date"},
        {"key": "typ", "label": "Typ", "type": "text"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "finance": [
        {"key": "beleg_nr", "label": "Beleg-Nr.", "type": "text", "readOnly": True},
        {"key": "kreditor_debitor", "label": "Kreditor/Debitor", "type": "text"},
        {"key": "datum", "label": "Datum", "type": "date"},
        {"key": "faellig_am", "label": "Faellig am", "type": "date"},
        {"key": "brutto", "label": "Brutto", "type": "currency"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "einkauf": [
        {"key": "bestell_nr", "label": "Bestell-Nr.", "type": "text", "readOnly": True},
        {"key": "lieferant", "label": "Lieferant", "type": "text"},
        {"key": "datum", "label": "Datum", "type": "date"},
        {"key": "betrag", "label": "Betrag", "type": "currency"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "crm": [
        {"key": "opportunity_nr", "label": "Opportunity-Nr.", "type": "text", "readOnly": True},
        {"key": "kunde", "label": "Kunde", "type": "text"},
        {"key": "phase", "label": "Phase", "type": "text"},
        {"key": "wert", "label": "Wert", "type": "currency"},
        {"key": "abschluss_datum", "label": "Abschlussdatum", "type": "date"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "sales": [
        {"key": "ls_nr", "label": "Lieferschein-Nr.", "type": "text", "readOnly": True},
        {"key": "kunde", "label": "Kunde", "type": "text"},
        {"key": "datum", "label": "Datum", "type": "date"},
        {"key": "versandart", "label": "Versandart", "type": "text"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
    "agrar": [
        {"key": "abrechnungs_nr", "label": "Abrechnungs-Nr.", "type": "text", "readOnly": True},
        {"key": "erzeuger", "label": "Erzeuger", "type": "text"},
        {"key": "ernte_jahr", "label": "Erntejahr", "type": "text"},
        {"key": "gesamtbetrag", "label": "Gesamtbetrag", "type": "currency"},
        {"key": "status", "label": "Status", "type": "text"},
    ],
}


def _build_rollout_screen_definition_from_spec(spec: Any) -> dict[str, Any]:
    """Builds a ScreenDefinition from a RolloutWaveSpec with dataSources and typed columns."""
    tab_columns = _ROLLOUT_TAB_COLUMNS.get(spec.screen_id, {})

    # Always include entity dataSource (bound to kopf tab)
    data_sources: list[dict[str, Any]] = [
        {"key": "entity", "endpoint": f"{spec.api_prefix}/{{entity_id}}"},
    ]
    data_sources += [
        {
            "key": tab_key,
            "endpoint": f"/api/v1/mask-rollouts/{spec.screen_id}/{{entity_id}}/tabs/{tab_key}",
            "pageSize": 25,
        }
        for tab_key in spec.lazy_tabs
    ]

    tabs: list[dict[str, Any]] = []
    for tab_key in spec.available_tabs:
        label = _TAB_LABELS.get(tab_key, tab_key.title())
        if tab_key == "kopf":
            # Header/detail tab: fields[] bound to entity dataSource, not a table
            tabs.append({
                "key": "kopf",
                "label": "Details",
                "lazy": False,
                "keepAlive": True,
                "dataSourceKey": "entity",
                "fields": _ROLLOUT_KOPF_FIELDS.get(spec.domain, _ROLLOUT_KOPF_FIELDS["_default"]),
            })
        else:
            tabs.append({
                "key": tab_key,
                "label": label,
                "lazy": True,
                "keepAlive": False,
                "tables": [
                    {
                        "key": tab_key,
                        "label": label,
                        "dataSourceKey": tab_key,
                        "serverPagination": True,
                        "pageSize": 25,
                        "virtualized": True,
                        "rowHeight": 52,
                        "columns": tab_columns.get(tab_key, [
                            _txt("nr", "Nr.", width=120, sortable=True),
                            _txt("bezeichnung", "Bezeichnung"),
                            _date("datum", "Datum"),
                        ]),
                    }
                ],
            })

    return {
        "schemaVersion": 1,
        "id": spec.screen_id,
        "domain": spec.domain,
        "mode": "detail",
        "title": spec.label,
        "subtitle": f"Rollout Pilot",
        "adapter": {
            "type": "native",
            "sourceId": spec.screen_id,
            "temporary": True,
        },
        "summaryEndpoint": f"{spec.api_prefix}/{{entity_id}}/screen-summary",
        "dataSources": data_sources,
        "tabs": tabs,
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "stubReason": "permission not yet assigned"},
        ],
        "noWorkflowReason": f"Rollout-Pilot fuer {spec.screen_id} — Workflow-Deklaration erfolgt nach nativer Paritaet.",
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": spec.budget_kb,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": spec.domain,
        },
    }


for _spec in ROLLOUT_WAVES_42_51:
    if _spec.screen_id in _SCREEN_DEFINITIONS:
        continue

    def _make_builder(_s: Any = _spec) -> Any:
        def _builder() -> dict[str, Any]:
            return _build_rollout_screen_definition_from_spec(_s)
        return _builder

    _SCREEN_DEFINITIONS[_spec.screen_id] = _make_builder()


def get_screen_definition(mask_id: str) -> dict[str, Any] | None:
    builder = _SCREEN_DEFINITIONS.get(mask_id)
    if builder is None:
        return None
    return builder()
