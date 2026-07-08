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
            "contextRail": "combined",
            "contextRailSections": ["workflow", "audit", "copilot", "collab"],
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
        "summaryEndpoint": "/api/v1/masks/einkauf/lieferanten/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/lieferanten/{entity_id}"},
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
            {"key": "neue_bestellung", "label": "Bestellung anlegen", "kind": "secondary", "dangerLevel": "safe", "permission": "einkauf.bestellung.create", "commandEndpoint": "/api/v1/einkauf/lieferanten/{entity_id}/actions/neue_bestellung", "method": "POST"},
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
            {
                "key": "create_activity",
                "label": "Aktivitaet anlegen",
                "kind": "secondary",
                "dangerLevel": "safe",
                "permission": "crm.activity.create",
                "commandEndpoint": "/api/v1/crm/opportunities/{entity_id}/actions/create_activity",
                "method": "POST",
            },
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
            {
                "key": "drucken",
                "label": "Lieferschein drucken",
                "kind": "primary",
                "dangerLevel": "safe",
                "permission": "sales.lieferschein.drucken",
                "commandEndpoint": "/api/v1/sales/delivery-notes/{entity_id}/actions/drucken",
                "method": "POST",
            },
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
        "summaryEndpoint": "/api/v1/masks/einkauf/bestellungen/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/bestellungen/{entity_id}"},
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
        "summaryEndpoint": "/api/v1/masks/finance/ap/invoices/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/ap/invoices/{entity_id}"},
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
            {"key": "freigeben", "label": "Freigeben", "kind": "primary", "dangerLevel": "moderate", "permission": "finance.ap.freigabe", "requiresConfirmation": True, "commandEndpoint": "/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben", "method": "POST"},
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
        "summaryEndpoint": "/api/v1/masks/finance/open-items/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/open-items/{entity_id}"},
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
            {"key": "mahnen", "label": "Mahnung erstellen", "kind": "primary", "dangerLevel": "moderate", "permission": "finance.ar.mahnung", "requiresConfirmation": True, "commandEndpoint": "/api/v1/finance/open-items/{entity_id}/actions/mahnen", "method": "POST"},
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
            {"key": "stornieren", "label": "Stornieren", "kind": "primary", "dangerLevel": "high", "permission": "lager.bewegung.stornieren", "requiresConfirmation": True, "humanApprovalRequired": True, "commandEndpoint": "/api/v1/lager/stock-movements/{entity_id}/actions/stornieren", "method": "POST"},
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
        "summaryEndpoint": "/api/v1/masks/agrar/settlements/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/agrar/settlements/{entity_id}"},
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
            {
                "key": "drucken",
                "label": "Abrechnung drucken",
                "kind": "primary",
                "dangerLevel": "safe",
                "permission": "agrar.abrechnung.drucken",
                "commandEndpoint": "/api/v1/agrar/harvest-settlements/{entity_id}/actions/drucken",
                "method": "POST",
            },
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
        "summaryEndpoint": "/api/v1/masks/finance/payment-runs/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/payment-runs/{entity_id}"},
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
                "commandEndpoint": "/api/v1/finance/payment-runs/{entity_id}/actions/freigeben",
                "method": "POST",
            },
        ],
        "noWorkflowReason": "Zahlungslauf ist Batch-Vorgang — Freigabe-Gate separat; kein laufender Prozess nach Ausfuehrung.",
        "agentContract": {
            "businessPurpose": "Zahlungslauf-Cockpit (read-only fuer Agenten): Laufdetails und Einzelzahlungen fuer Audit und Reconciliation. Freigabe ist Agent-gesperrt.",
            "examplePrompts": [
                "Was ist der Status von Zahlungslauf {entity_id} und wie hoch ist der Gesamtbetrag?",
                "Zeige alle Einzelzahlungen von Zahlungslauf {entity_id} mit Status 'fehler'.",
            ],
            "dangerousActions": [
                {
                    "key": "freigeben",
                    "reason": "Geldausgang: Zahlungslauf-Freigabe ist forbiddenForAgents — nur Mensch mit finance.payment_run.freigabe, Vier-Augen-Bestaetigung und Audit-Grund.",
                },
            ],
            "sensitiveFields": ["gesamtbetrag", "bank"],
            "testSelectors": {"screenRoot": "[data-testid='finance-payment-run']", "primaryAction": "[data-testid='action-freigeben']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_agrar_duenger_screen_definition() -> dict[str, Any]:
    """Native SD fuer agrar/duenger (Duenger-Stammdaten)."""
    return {
        "schemaVersion": 1, "id": "agrar/duenger", "domain": "agrar", "mode": "detail",
        "title": "Duenger", "subtitle": "Agrar / Duenger-Stammdaten",
        "adapter": {"type": "native", "sourceId": "agrar/duenger", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/agrar/duenger/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/agrar/duenger/entity/{entity_id}"},
            {"key": "verwendung", "endpoint": "/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/verwendung", "pageSize": 25},
            {"key": "preise", "endpoint": "/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/preise", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "duenger_nr", "label": "Duenger-Nr.", "type": "text", "readOnly": True},
                 {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                 {"key": "typ", "label": "Typ", "type": "text"},
                 {"key": "naehrstoff_n", "label": "N %", "type": "number"},
                 {"key": "naehrstoff_p", "label": "P2O5 %", "type": "number"},
                 {"key": "naehrstoff_k", "label": "K2O %", "type": "number"},
                 {"key": "einheit", "label": "Einheit", "type": "text"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "verwendung", "label": "Verwendung", "lazy": True, "keepAlive": False,
             "tables": [{"key": "verwendung", "label": "Verwendungs-Historie", "dataSourceKey": "verwendung",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "datum", "label": "Datum", "sortable": True, "renderKind": "date", "width": 110},
                             {"key": "flaeche", "label": "Flaeche", "width": 160, "filterable": True},
                             {"key": "menge", "label": "Menge", "numeric": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 80},
                         ]}]},
            {"key": "preise", "label": "Preise", "lazy": True, "keepAlive": False,
             "tables": [{"key": "preise", "label": "Preise", "dataSourceKey": "preise",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "gueltig_ab", "label": "Gueltig ab", "sortable": True, "renderKind": "date", "width": 110},
                             {"key": "preis", "label": "Preis", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "lieferant", "label": "Lieferant", "width": 180, "filterable": True},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "agrar.duenger.update"}],
        "noWorkflowReason": "Duenger-Stammdaten sind Referenzdaten ohne Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Duenger-Stammdaten: Naehrstoffgehalte, Verwendungshistorie und Preise fuer Duengungsplanung.",
            "examplePrompts": ["Welche Naehrstoffgehalte hat Duenger {entity_id}?", "Zeige die Preisentwicklung von Duenger {entity_id}."],
            "sensitiveFields": ["preis"],
            "testSelectors": {"screenRoot": "[data-testid='agrar-duenger']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "agrar"},
    }


def build_agrar_saatgut_screen_definition() -> dict[str, Any]:
    """Native SD fuer agrar/saatgut (Saatgut-Stammdaten)."""
    return {
        "schemaVersion": 1, "id": "agrar/saatgut", "domain": "agrar", "mode": "detail",
        "title": "Saatgut", "subtitle": "Agrar / Saatgut-Stammdaten",
        "adapter": {"type": "native", "sourceId": "agrar/saatgut", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/agrar/saatgut/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/agrar/saatgut/entity/{entity_id}"},
            {"key": "lagerbestaende", "endpoint": "/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/lagerbestaende", "pageSize": 25},
            {"key": "vertraege", "endpoint": "/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/vertraege", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "saatgut_nr", "label": "Saatgut-Nr.", "type": "text", "readOnly": True},
                 {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                 {"key": "sorte", "label": "Sorte", "type": "text"},
                 {"key": "kultur", "label": "Kulturart", "type": "text"},
                 {"key": "zulassungs_nr", "label": "Zulassungs-Nr.", "type": "text"},
                 {"key": "tausendkorngewicht", "label": "TKG (g)", "type": "number"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "lagerbestaende", "label": "Lagerbestaende", "lazy": True, "keepAlive": False,
             "tables": [{"key": "lagerbestaende", "label": "Bestaende", "dataSourceKey": "lagerbestaende",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "lagerort", "label": "Lagerort", "sortable": True, "filterable": True},
                             {"key": "menge", "label": "Menge (kg)", "numeric": True, "sortable": True, "renderKind": "number"},
                             {"key": "charge", "label": "Charge", "width": 120},
                             {"key": "lager_datum", "label": "Eingelagert", "renderKind": "date", "width": 110},
                         ]}]},
            {"key": "vertraege", "label": "Vertraege", "lazy": True, "keepAlive": False,
             "tables": [{"key": "vertraege", "label": "Anbauvertraege", "dataSourceKey": "vertraege",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "vertrag_nr", "label": "Vertrag-Nr.", "sortable": True},
                             {"key": "erzeuger", "label": "Erzeuger", "filterable": True},
                             {"key": "menge", "label": "Menge (kg)", "numeric": True, "sortable": True, "renderKind": "number"},
                             {"key": "ernte_jahr", "label": "Erntejahr", "width": 90},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "agrar.saatgut.update"}],
        "noWorkflowReason": "Saatgut-Stammdaten sind Referenzdaten ohne Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Saatgut-Stammdaten: Sorteninfo, Lagerbestaende und Anbauvertraege fuer Saatgutplanung.",
            "examplePrompts": ["Welche Lagerbestaende hat Saatgut {entity_id}?", "Zeige alle Anbauvertraege fuer Saatgut {entity_id}."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='agrar-saatgut']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "agrar"},
    }


def build_finance_debitor_screen_definition() -> dict[str, Any]:
    """Native SD fuer finance/debitor (Debitoren-Stammdaten)."""
    return {
        "schemaVersion": 1, "id": "finance/debitor", "domain": "finance", "mode": "detail",
        "title": "Debitor", "subtitle": "Finance / Debitorenstamm",
        "adapter": {"type": "native", "sourceId": "finance/debitor", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/finance/debitoren/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/debitor/entity/{entity_id}"},
            {"key": "offene_posten", "endpoint": "/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/offene-posten", "pageSize": 25},
            {"key": "umsaetze", "endpoint": "/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/umsaetze", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "debitoren_nr", "label": "Debitoren-Nr.", "type": "text", "readOnly": True},
                 {"key": "name", "label": "Name", "type": "text", "required": True},
                 {"key": "kreditlimit", "label": "Kreditlimit", "type": "currency"},
                 {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text"},
                 {"key": "steuernummer", "label": "Steuernummer", "type": "text"},
                 {"key": "ust_id", "label": "USt-IdNr.", "type": "text"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "offene_posten", "label": "Offene Posten", "lazy": True, "keepAlive": False,
             "tables": [{"key": "offene_posten", "label": "Offene Posten", "dataSourceKey": "offene_posten",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "beleg_nr", "label": "Beleg-Nr.", "sortable": True},
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "faellig", "label": "Faellig", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "status", "label": "Status", "filterable": True, "width": 100},
                         ]}]},
            {"key": "umsaetze", "label": "Umsaetze", "lazy": True, "keepAlive": False,
             "tables": [{"key": "umsaetze", "label": "Umsaetze", "dataSourceKey": "umsaetze",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "periode", "label": "Periode", "sortable": True, "filterable": True, "width": 100},
                             {"key": "umsatz", "label": "Umsatz", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "anzahl_belege", "label": "Belege", "numeric": True},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "finance.debitor.update"}],
        "noWorkflowReason": "Debitorenstamm ist Referenzdaten — kein Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Debitoren-Stammdaten: Kreditlimit, offene Posten und Umsatzhistorie fuer Debitorenbuchhaltung.",
            "examplePrompts": ["Was ist das Kreditlimit von Debitor {entity_id}?", "Zeige alle offenen Posten von Debitor {entity_id}."],
            "sensitiveFields": ["kreditlimit", "steuernummer", "ust_id"],
            "testSelectors": {"screenRoot": "[data-testid='finance-debitor']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 40, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_finance_kreditor_screen_definition() -> dict[str, Any]:
    """Native SD fuer finance/kreditor (Kreditoren-Stammdaten)."""
    return {
        "schemaVersion": 1, "id": "finance/kreditor", "domain": "finance", "mode": "detail",
        "title": "Kreditor", "subtitle": "Finance / Kreditorenstamm",
        "adapter": {"type": "native", "sourceId": "finance/kreditor", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/finance/kreditoren/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/kreditor/entity/{entity_id}"},
            {"key": "offene_posten", "endpoint": "/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/offene-posten", "pageSize": 25},
            {"key": "bestellungen", "endpoint": "/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/bestellungen", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "kreditoren_nr", "label": "Kreditoren-Nr.", "type": "text", "readOnly": True},
                 {"key": "name", "label": "Name", "type": "text", "required": True},
                 {"key": "zahlungsbedingungen", "label": "Zahlungsbedingungen", "type": "text"},
                 {"key": "iban", "label": "IBAN", "type": "text"},
                 {"key": "steuernummer", "label": "Steuernummer", "type": "text"},
                 {"key": "ust_id", "label": "USt-IdNr.", "type": "text"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "offene_posten", "label": "Offene Posten", "lazy": True, "keepAlive": False,
             "tables": [{"key": "offene_posten", "label": "Offene Posten", "dataSourceKey": "offene_posten",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "beleg_nr", "label": "Beleg-Nr.", "sortable": True},
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "faellig", "label": "Faellig", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "status", "label": "Status", "filterable": True, "width": 100},
                         ]}]},
            {"key": "bestellungen", "label": "Bestellungen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "bestellungen", "label": "Bestellungen", "dataSourceKey": "bestellungen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "bestell_nr", "label": "Bestell-Nr.", "sortable": True},
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "status", "label": "Status", "filterable": True, "width": 100},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "finance.kreditor.update"}],
        "noWorkflowReason": "Kreditorenstamm ist Referenzdaten — kein Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Kreditoren-Stammdaten: Zahlungsbedingungen, offene Posten und Bestellhistorie fuer Kreditorenbuchhaltung.",
            "examplePrompts": ["Welche offenen Posten hat Kreditor {entity_id}?", "Zeige alle Bestellungen bei Kreditor {entity_id}."],
            "sensitiveFields": ["iban", "steuernummer", "ust_id"],
            "testSelectors": {"screenRoot": "[data-testid='finance-kreditor']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 40, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_finance_bankkonto_screen_definition() -> dict[str, Any]:
    """Native SD fuer finance/bankkonto (Bankkonten-Stammdaten)."""
    return {
        "schemaVersion": 1, "id": "finance/bankkonto", "domain": "finance", "mode": "detail",
        "title": "Bankkonto", "subtitle": "Finance / Bankkonten-Stamm",
        "adapter": {"type": "native", "sourceId": "finance/bankkonto", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/finance/bankkonten/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/finance/bankkonto/entity/{entity_id}"},
            {"key": "buchungen", "endpoint": "/api/v1/masks/finance/bankkonten/entity/{entity_id}/tabs/buchungen", "pageSize": 50},
        ],
        "tabs": [
            {"key": "kopf", "label": "Konto-Stamm", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "konto_nr", "label": "Kontonummer", "type": "text", "readOnly": True},
                 {"key": "bank_name", "label": "Bank", "type": "text"},
                 {"key": "iban", "label": "IBAN", "type": "text"},
                 {"key": "bic", "label": "BIC", "type": "text"},
                 {"key": "waehrung", "label": "Waehrung", "type": "text"},
                 {"key": "saldo", "label": "Saldo", "type": "currency"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "buchungen", "label": "Buchungen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "buchungen", "label": "Buchungen", "dataSourceKey": "buchungen",
                         "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "verwendungszweck", "label": "Verwendungszweck", "width": 240, "filterable": True},
                             {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "gegenpartei", "label": "Gegenpartei", "width": 180},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "finance.bankkonto.update"}],
        "noWorkflowReason": "Bankkonten-Stammdaten sind Referenzdaten ohne Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Bankkonto-Stamm: Kontodaten und Buchungshistorie fuer Finanzbuchhaltung.",
            "examplePrompts": ["Was ist der aktuelle Saldo von Bankkonto {entity_id}?", "Zeige die letzten Buchungen auf Bankkonto {entity_id}."],
            "sensitiveFields": ["iban", "bic", "saldo"],
            "testSelectors": {"screenRoot": "[data-testid='finance-bankkonto']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 40, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "finance"},
    }


def build_einkauf_anfrage_screen_definition() -> dict[str, Any]:
    """Native SD fuer einkauf/anfrage (Einkaufsanfrage)."""
    return {
        "schemaVersion": 1, "id": "einkauf/anfrage", "domain": "einkauf", "mode": "detail",
        "title": "Einkaufsanfrage", "subtitle": "Einkauf / Anfrage",
        "adapter": {"type": "native", "sourceId": "einkauf/anfrage", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/einkauf/anfragen/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/anfrage/entity/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/masks/einkauf/anfragen/entity/{entity_id}/tabs/positionen", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Anfrage-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "anfrage_nr", "label": "Anfrage-Nr.", "type": "text", "readOnly": True},
                 {"key": "lieferant", "label": "Lieferant", "type": "text"},
                 {"key": "datum", "label": "Datum", "type": "date"},
                 {"key": "rueckmeldung_bis", "label": "Rueckmeldung bis", "type": "date"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "artikel_nr", "label": "Artikel-Nr.", "sortable": True},
                             {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "width": 200},
                             {"key": "menge", "label": "Menge", "numeric": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 70},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "einkauf.anfrage.update"}],
        "noWorkflowReason": "Anfrage-Status wird durch Lieferantenantwort gesetzt — kein deklarativer Workflow.",
        "agentContract": {
            "businessPurpose": "Einkaufsanfrage: Kopfdaten und Positionen fuer Beschaffungsanfragen an Lieferanten.",
            "examplePrompts": ["Was ist der Status von Anfrage {entity_id}?", "Zeige alle Positionen von Anfrage {entity_id}."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='einkauf-anfrage']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 32, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "einkauf"},
    }


def build_einkauf_angebot_screen_definition() -> dict[str, Any]:
    """Native SD fuer einkauf/angebot (Lieferantenangebot)."""
    return {
        "schemaVersion": 1, "id": "einkauf/angebot", "domain": "einkauf", "mode": "detail",
        "title": "Lieferantenangebot", "subtitle": "Einkauf / Angebot",
        "adapter": {"type": "native", "sourceId": "einkauf/angebot", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/einkauf/angebote/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/angebot/entity/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/masks/einkauf/angebote/entity/{entity_id}/tabs/positionen", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Angebot-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "angebot_nr", "label": "Angebot-Nr.", "type": "text", "readOnly": True},
                 {"key": "lieferant", "label": "Lieferant", "type": "text"},
                 {"key": "datum", "label": "Datum", "type": "date"},
                 {"key": "gueltig_bis", "label": "Gueltig bis", "type": "date"},
                 {"key": "gesamtbetrag", "label": "Gesamtbetrag", "type": "currency"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "artikel_nr", "label": "Artikel-Nr.", "sortable": True},
                             {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "width": 200},
                             {"key": "menge", "label": "Menge", "numeric": True, "renderKind": "number"},
                             {"key": "einzelpreis", "label": "Einzelpreis", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "betrag", "label": "Betrag", "numeric": True, "sortable": True, "renderKind": "currency"},
                         ]}]},
        ],
        "actions": [{"key": "bestellen", "label": "Bestellung erstellen", "kind": "primary", "dangerLevel": "safe", "permission": "einkauf.angebot.order", "commandEndpoint": "/api/v1/einkauf/bestellungen/{entity_id}/actions/bestellen", "method": "POST"}],
        "noWorkflowReason": "Angebots-Status wird durch Bestellvorgang gesetzt — kein separater Workflow.",
        "agentContract": {
            "businessPurpose": "Lieferantenangebot: Preise und Positionen fuer Angebotsvergleich und Bestellentscheidung.",
            "examplePrompts": ["Wie lange ist Angebot {entity_id} gueltig?", "Zeige alle Positionen und Preise von Angebot {entity_id}."],
            "sensitiveFields": ["gesamtbetrag", "einzelpreis"],
            "testSelectors": {"screenRoot": "[data-testid='einkauf-angebot']", "primaryAction": "[data-testid='action-bestellen']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 32, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "einkauf"},
    }


def build_einkauf_anlieferavis_screen_definition() -> dict[str, Any]:
    """Native SD fuer einkauf/anlieferavis."""
    return {
        "schemaVersion": 1, "id": "einkauf/anlieferavis", "domain": "einkauf", "mode": "detail",
        "title": "Anlieferavis", "subtitle": "Einkauf / Wareneingangsankuendigung",
        "adapter": {"type": "native", "sourceId": "einkauf/anlieferavis", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/einkauf/anlieferavise/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/anlieferavis/entity/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/masks/einkauf/anlieferavise/entity/{entity_id}/tabs/positionen", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Avis-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "avis_nr", "label": "Avis-Nr.", "type": "text", "readOnly": True},
                 {"key": "lieferant", "label": "Lieferant", "type": "text"},
                 {"key": "lieferdatum", "label": "Lieferdatum", "type": "date"},
                 {"key": "lieferschein_nr", "label": "Lieferanten-LS-Nr.", "type": "text"},
                 {"key": "lagerort", "label": "Lagerort", "type": "text"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "artikel_nr", "label": "Artikel-Nr.", "sortable": True},
                             {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "width": 200},
                             {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 70},
                             {"key": "charge", "label": "Charge", "width": 120},
                         ]}]},
        ],
        "actions": [{"key": "wareneingang", "label": "Wareneingang buchen", "kind": "primary", "dangerLevel": "moderate", "permission": "lager.wareneingang.create", "requiresConfirmation": True, "commandEndpoint": "/api/v1/lager/artikel/{entity_id}/actions/wareneingang", "method": "POST"}],
        "noWorkflowReason": "Avis-Status wird durch Wareneingangsbuchung automatisch gesetzt.",
        "agentContract": {
            "businessPurpose": "Anlieferavis: Ankuendigung eines Wareneingangs mit Positionen und Lieferdatum.",
            "examplePrompts": ["Wann ist Avis {entity_id} angekuendigt?", "Zeige alle Positionen von Avis {entity_id}."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='einkauf-anlieferavis']", "primaryAction": "[data-testid='action-wareneingang']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 32, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "einkauf"},
    }


def build_einkauf_auftragsbestaetigung_screen_definition() -> dict[str, Any]:
    """Native SD fuer einkauf/auftragsbestaetigung."""
    return {
        "schemaVersion": 1, "id": "einkauf/auftragsbestaetigung", "domain": "einkauf", "mode": "detail",
        "title": "Auftragsbestaetigung", "subtitle": "Einkauf / Lieferanten-AB",
        "adapter": {"type": "native", "sourceId": "einkauf/auftragsbestaetigung", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/einkauf/auftragsbestaetigungen/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/einkauf/auftragsbestaetigung/entity/{entity_id}"},
            {"key": "positionen", "endpoint": "/api/v1/masks/einkauf/auftragsbestaetigungen/entity/{entity_id}/tabs/positionen", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "AB-Kopf", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "ab_nr", "label": "AB-Nr.", "type": "text", "readOnly": True},
                 {"key": "bestell_nr", "label": "Bestell-Nr.", "type": "text", "readOnly": True},
                 {"key": "lieferant", "label": "Lieferant", "type": "text"},
                 {"key": "datum", "label": "Datum", "type": "date"},
                 {"key": "lieferdatum", "label": "Zugesagter Liefertermin", "type": "date"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "positionen", "label": "Positionen", "dataSourceKey": "positionen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "artikel_nr", "label": "Artikel-Nr.", "sortable": True},
                             {"key": "bezeichnung", "label": "Bezeichnung", "filterable": True, "width": 200},
                             {"key": "menge", "label": "Menge", "numeric": True, "sortable": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 70},
                             {"key": "einzelpreis", "label": "Einzelpreis", "numeric": True, "renderKind": "currency"},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "einkauf.ab.update"}],
        "noWorkflowReason": "AB-Status wird durch Lieferfortschritt gesetzt — kein separater Workflow.",
        "agentContract": {
            "businessPurpose": "Auftragsbestaetigung: Lieferanten-Rueckmeldung auf Bestellung mit zugesagtem Liefertermin.",
            "examplePrompts": ["Wann hat Lieferant den Liefertermin fuer AB {entity_id} zugesagt?", "Zeige alle Positionen von AB {entity_id}."],
            "sensitiveFields": ["einzelpreis"],
            "testSelectors": {"screenRoot": "[data-testid='einkauf-auftragsbestaetigung']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 32, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "einkauf"},
    }


def build_qualitaet_reklamation_screen_definition() -> dict[str, Any]:
    """Native SD fuer qualitaet/reklamation."""
    return {
        "schemaVersion": 1, "id": "qualitaet/reklamation", "domain": "qualitaet", "mode": "detail",
        "title": "Reklamation", "subtitle": "Qualitaet / Reklamationsbearbeitung",
        "adapter": {"type": "native", "sourceId": "qualitaet/reklamation", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/qualitaet/reklamationen/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/qualitaet/reklamation/entity/{entity_id}"},
            {"key": "massnahmen", "endpoint": "/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/massnahmen", "pageSize": 25},
            {"key": "dokumente", "endpoint": "/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/dokumente", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Reklamation", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "rekl_nr", "label": "Reklamations-Nr.", "type": "text", "readOnly": True},
                 {"key": "titel", "label": "Titel", "type": "text", "required": True},
                 {"key": "kunde", "label": "Kunde / Lieferant", "type": "text"},
                 {"key": "datum", "label": "Datum", "type": "date"},
                 {"key": "artikel", "label": "Artikel", "type": "text"},
                 {"key": "prioritaet", "label": "Prioritaet", "type": "text"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "massnahmen", "label": "Massnahmen", "lazy": True, "keepAlive": False,
             "tables": [{"key": "massnahmen", "label": "Massnahmen", "dataSourceKey": "massnahmen",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "typ", "label": "Typ", "filterable": True, "width": 120},
                             {"key": "beschreibung", "label": "Beschreibung", "width": 240},
                             {"key": "verantwortlich", "label": "Verantwortlich", "width": 140},
                             {"key": "status", "label": "Status", "filterable": True, "width": 100},
                         ]}]},
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": False,
             "tables": [{"key": "dokumente", "label": "Dokumente", "dataSourceKey": "dokumente",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "typ", "label": "Typ", "filterable": True, "width": 120},
                             {"key": "bezeichnung", "label": "Bezeichnung", "width": 220},
                         ]}]},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "qualitaet.reklamation.update"},
            {"key": "abschliessen", "label": "Abschliessen", "kind": "secondary", "dangerLevel": "moderate", "permission": "qualitaet.reklamation.close", "requiresConfirmation": True, "commandEndpoint": "/api/v1/reklamationen/{entity_id}/actions/abschliessen", "method": "POST"},
        ],
        "noWorkflowReason": "Reklamations-Status wird manuell gesetzt — Massnahmentracking ist tabellenbasiert.",
        "agentContract": {
            "businessPurpose": "Reklamation: Qualitaetsmaengel mit Massnahmen und Dokumenten fuer Reklamationsbearbeitung.",
            "examplePrompts": ["Was ist der Status von Reklamation {entity_id}?", "Zeige alle offenen Massnahmen von Reklamation {entity_id}."],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='qualitaet-reklamation']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "qualitaet"},
    }


def build_futtermittel_einzelfuttermittel_screen_definition() -> dict[str, Any]:
    """Native SD fuer futtermittel/einzelfuttermittel."""
    return {
        "schemaVersion": 1, "id": "futtermittel/einzelfuttermittel", "domain": "futtermittel", "mode": "detail",
        "title": "Einzelfuttermittel", "subtitle": "Futtermittel / Rohstoff-Stamm",
        "adapter": {"type": "native", "sourceId": "futtermittel/einzelfuttermittel", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/futtermittel/einzelfuttermittel/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/futtermittel/einzelfuttermittel/entity/{entity_id}"},
            {"key": "naehrstoffe", "endpoint": "/api/v1/masks/futtermittel/einzelfuttermittel/entity/{entity_id}/tabs/naehrstoffe", "pageSize": 50},
            {"key": "preise", "endpoint": "/api/v1/masks/futtermittel/einzelfuttermittel/entity/{entity_id}/tabs/preise", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "futtermittel_nr", "label": "FM-Nr.", "type": "text", "readOnly": True},
                 {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                 {"key": "quelle", "label": "Quelle / Kategorie", "type": "text"},
                 {"key": "trockensubstanz", "label": "Trockensubstanz %", "type": "number"},
                 {"key": "energie_nel", "label": "NEL (MJ)", "type": "number"},
                 {"key": "rohprotein", "label": "Rohprotein %", "type": "number"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "naehrstoffe", "label": "Naehrstoffe", "lazy": True, "keepAlive": False,
             "tables": [{"key": "naehrstoffe", "label": "Naehrstoffgehalte", "dataSourceKey": "naehrstoffe",
                         "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "naehrstoff", "label": "Naehrstoff", "sortable": True, "filterable": True},
                             {"key": "gehalt", "label": "Gehalt", "numeric": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 80},
                             {"key": "quelle", "label": "Quelle", "filterable": True, "width": 120},
                         ]}]},
            {"key": "preise", "label": "Preise", "lazy": True, "keepAlive": False,
             "tables": [{"key": "preise", "label": "Preise", "dataSourceKey": "preise",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "gueltig_ab", "label": "Gueltig ab", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "preis", "label": "Preis/t", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "lieferant", "label": "Lieferant", "filterable": True, "width": 180},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.einzelfm.update"}],
        "noWorkflowReason": "Futtermittel-Stammdaten sind Referenzdaten ohne Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Einzelfuttermittel-Stamm: Naehrstoffgehalte und Preise fuer Rationsoptimierung.",
            "examplePrompts": ["Welche NEL und Rohprotein-Gehalte hat Futtermittel {entity_id}?", "Zeige die aktuellen Preise fuer Futtermittel {entity_id}."],
            "sensitiveFields": ["preis"],
            "testSelectors": {"screenRoot": "[data-testid='futtermittel-einzelfuttermittel']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "futtermittel"},
    }


def build_futtermittel_mischfuttermittel_screen_definition() -> dict[str, Any]:
    """Native SD fuer futtermittel/mischfuttermittel."""
    return {
        "schemaVersion": 1, "id": "futtermittel/mischfuttermittel", "domain": "futtermittel", "mode": "detail",
        "title": "Mischfuttermittel", "subtitle": "Futtermittel / Misch-Rezeptur",
        "adapter": {"type": "native", "sourceId": "futtermittel/mischfuttermittel", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/futtermittel/mischfuttermittel/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}"},
            {"key": "rezeptur", "endpoint": "/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/rezeptur", "pageSize": 50},
            {"key": "naehrstoffe", "endpoint": "/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/naehrstoffe", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "misch_nr", "label": "Misch-Nr.", "type": "text", "readOnly": True},
                 {"key": "bezeichnung", "label": "Bezeichnung", "type": "text", "required": True},
                 {"key": "tierart", "label": "Tierart", "type": "text"},
                 {"key": "leistungsgruppe", "label": "Leistungsgruppe", "type": "text"},
                 {"key": "preis_je_t", "label": "Preis/t", "type": "currency"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "rezeptur", "label": "Rezeptur", "lazy": True, "keepAlive": False,
             "tables": [{"key": "rezeptur", "label": "Komponenten", "dataSourceKey": "rezeptur",
                         "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "futtermittel", "label": "Einzelfuttermittel", "sortable": True, "filterable": True, "width": 220},
                             {"key": "anteil_pct", "label": "Anteil %", "numeric": True, "sortable": True, "renderKind": "number"},
                             {"key": "menge_je_t", "label": "Menge/t", "numeric": True, "renderKind": "number"},
                         ]}]},
            {"key": "naehrstoffe", "label": "Naehrstoffe (berechnet)", "lazy": True, "keepAlive": False,
             "tables": [{"key": "naehrstoffe", "label": "Naehrstoffgehalte", "dataSourceKey": "naehrstoffe",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "naehrstoff", "label": "Naehrstoff", "sortable": True, "filterable": True},
                             {"key": "gehalt", "label": "Gehalt", "numeric": True, "renderKind": "number"},
                             {"key": "einheit", "label": "Einheit", "width": 80},
                         ]}]},
        ],
        "actions": [{"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.mischfm.update"}],
        "noWorkflowReason": "Mischfuttermittel-Stamm ist Referenzdaten ohne Prozess-Lebenszyklus.",
        "agentContract": {
            "businessPurpose": "Mischfuttermittel: Rezeptur-Komponenten und berechnete Naehrstoffgehalte fuer Rationsoptimierung.",
            "examplePrompts": ["Welche Komponenten hat Mischfutter {entity_id}?", "Zeige die berechneten Naehrstoffgehalte von Mischfutter {entity_id}."],
            "sensitiveFields": ["preis_je_t"],
            "testSelectors": {"screenRoot": "[data-testid='futtermittel-mischfuttermittel']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "futtermittel"},
    }


def build_crm_lead_screen_definition() -> dict[str, Any]:
    """Native SD fuer crm/lead."""
    return {
        "schemaVersion": 1, "id": "crm/lead", "domain": "crm", "mode": "detail",
        "title": "Lead", "subtitle": "CRM / Lead-Verwaltung",
        "adapter": {"type": "native", "sourceId": "crm/lead", "temporary": False},
        "summaryEndpoint": "/api/v1/masks/crm/leads/{entity_id}/screen-summary",
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/masks/crm/lead/entity/{entity_id}"},
            {"key": "aktivitaeten", "endpoint": "/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aktivitaeten", "pageSize": 25},
            {"key": "aufgaben", "endpoint": "/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aufgaben", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Lead-Daten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "lead_nr", "label": "Lead-Nr.", "type": "text", "readOnly": True},
                 {"key": "titel", "label": "Titel", "type": "text", "required": True},
                 {"key": "unternehmen", "label": "Unternehmen", "type": "text"},
                 {"key": "kontakt", "label": "Ansprechpartner", "type": "text"},
                 {"key": "quelle", "label": "Quelle", "type": "text"},
                 {"key": "wert", "label": "Geschaetzter Wert", "type": "currency"},
                 {"key": "status", "label": "Status", "type": "text"},
             ]},
            {"key": "aktivitaeten", "label": "Aktivitaeten", "lazy": True, "keepAlive": False,
             "tables": [{"key": "aktivitaeten", "label": "Aktivitaeten", "dataSourceKey": "aktivitaeten",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "datum", "label": "Datum", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "typ", "label": "Typ", "filterable": True, "width": 100},
                             {"key": "betreff", "label": "Betreff", "width": 220},
                             {"key": "benutzer", "label": "Benutzer", "width": 140},
                         ]}]},
            {"key": "aufgaben", "label": "Aufgaben", "lazy": True, "keepAlive": False,
             "tables": [{"key": "aufgaben", "label": "Aufgaben", "dataSourceKey": "aufgaben",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "faellig", "label": "Faellig", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "titel", "label": "Titel", "filterable": True, "width": 220},
                             {"key": "prioritaet", "label": "Prioritaet", "filterable": True, "width": 100},
                             {"key": "status", "label": "Status", "filterable": True, "width": 100},
                         ]}]},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "dangerLevel": "safe", "permission": "crm.lead.update"},
            {"key": "qualifizieren", "label": "Als Opportunity qualifizieren", "kind": "secondary", "dangerLevel": "safe", "permission": "crm.lead.qualify", "commandEndpoint": "/api/v1/crm/leads/{entity_id}/actions/qualifizieren", "method": "POST"},
        ],
        "noWorkflowReason": "Lead-Status wird manuell gesetzt — Qualifizierung erzeugt Opportunity (separate Maske).",
        "agentContract": {
            "businessPurpose": "Lead-Cockpit: Kundenpotenzial mit Aktivitaeten und Aufgaben fuer Vertriebssteuerung.",
            "examplePrompts": ["Was ist der Status von Lead {entity_id}?", "Zeige alle offenen Aufgaben fuer Lead {entity_id}.", "Welche Aktivitaeten wurden fuer Lead {entity_id} erfasst?"],
            "sensitiveFields": ["wert"],
            "testSelectors": {"screenRoot": "[data-testid='crm-lead']", "primaryAction": "[data-testid='action-edit']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 36, "requiresLazyTabs": True, "requiresVirtualTables": False, "lookupMinChars": 2, "bundleGroup": "crm"},
    }


# ── Rollen-Workspaces (UIX-061) ──────────────────────────────────────────────
# Native cockpit-SDs als rollenbasierte Startseiten. Inhalt aus Bestand:
# KPI-Summary-Slots + Worklist-Kacheln, die in vorhandene Prozessmasken
# navigieren (targetScreenId -> reale Listen-Route via _SCREEN_LIST_ROUTE).
# Kacheln tragen einen Ton (neutral|warning|danger); Live-Zaehler (countEndpoint)
# folgen als Nachtrag, sobald count_only-Worklist-GETs existieren.

def _build_workspace_screen_definition(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    purpose: str,
    summary: list[dict[str, Any]],
    tiles: list[dict[str, Any]],
) -> dict[str, Any]:
    slug = screen_id.replace("/", "-")
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "cockpit",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "summary": summary,
        "tiles": tiles,
        "noWorkflowReason": (
            "Workspace ist eine rollenbasierte Aggregations-Startseite ohne eigenen "
            "Objekt-Lebenszyklus — Aktionen fuehren in die jeweiligen Prozessmasken."
        ),
        "agentContract": {
            "businessPurpose": purpose,
            "examplePrompts": [
                f"Was steht heute in {title} an?",
                "Zeige die dringendsten Worklists fuer meine Rolle.",
            ],
            "testSelectors": {"screenRoot": f"[data-testid='{slug}']"},
        },
    }


def build_workspace_einkauf_screen_definition() -> dict[str, Any]:
    return _build_workspace_screen_definition(
        screen_id="workspace/einkauf",
        domain="einkauf",
        title="Einkauf-Cockpit",
        subtitle="Startseite Einkauf",
        purpose="Rollen-Startseite Einkauf — offene Bestellungen, Avis und Preisabweichungen mit direktem Sprung in die Prozessmasken.",
        summary=[
            {"key": "offene_bestellungen", "label": "Offene Bestellungen", "tone": "neutral"},
            {"key": "avis_heute", "label": "Avis heute", "tone": "neutral"},
            {"key": "preisabweichung", "label": "Preisabweichungen", "tone": "warning"},
        ],
        tiles=[
            {"key": "rechnungspruefung", "label": "Rechnungspruefung-Abweichungen", "targetScreenId": "finance/ap-invoice", "targetFilters": {"status": "abweichung"}, "tone": "warning"},
            {"key": "offene_avis", "label": "Offene Avis", "targetScreenId": "einkauf/anlieferavis", "targetFilters": {}, "tone": "neutral"},
            {"key": "rfq", "label": "RFQ / Anfragen", "targetScreenId": "einkauf/anfrage", "targetFilters": {}, "tone": "neutral"},
        ],
    )


def build_workspace_verkauf_screen_definition() -> dict[str, Any]:
    return _build_workspace_screen_definition(
        screen_id="workspace/verkauf",
        domain="sales",
        title="Verkauf-Cockpit",
        subtitle="Startseite Verkauf",
        purpose="Rollen-Startseite Verkauf — Auftragsbestand, Ueberfaellige und Kreditlimit-Warnungen mit Sprung in Auftrags- und CRM-Masken.",
        summary=[
            {"key": "auftragsbestand", "label": "Auftragsbestand", "tone": "neutral"},
            {"key": "ueberfaellig", "label": "Ueberfaellige Auftraege", "tone": "warning"},
            {"key": "kreditlimit", "label": "Kreditlimit-Warnungen", "tone": "danger"},
        ],
        tiles=[
            {"key": "offene_auftraege", "label": "Offene Auftraege", "targetScreenId": "sales/sales-order", "targetFilters": {"status": "offen"}, "tone": "neutral"},
            {"key": "lieferscheine", "label": "Offene Lieferscheine", "targetScreenId": "sales/delivery-note", "targetFilters": {}, "tone": "neutral"},
            {"key": "wiedervorlagen", "label": "Angebots-Wiedervorlagen", "targetScreenId": "crm/lead", "targetFilters": {}, "tone": "warning"},
        ],
    )


def build_workspace_lager_screen_definition() -> dict[str, Any]:
    return _build_workspace_screen_definition(
        screen_id="workspace/lager",
        domain="lager",
        title="Lager-Cockpit",
        subtitle="Startseite Lager & Annahme",
        purpose="Rollen-Startseite Lager — Annahmen, Wartezeiten und Trocknerauslastung mit Sprung in Bestands- und Qualitaetsmasken.",
        summary=[
            {"key": "annahmen_heute", "label": "Annahmen heute", "tone": "neutral"},
            {"key": "wartezeit", "label": "Durchschn. Wartezeit", "tone": "neutral"},
            {"key": "trockner", "label": "Trocknerauslastung", "tone": "warning"},
        ],
        tiles=[
            {"key": "qualitaet_nachtrag", "label": "Qualitaets-Nachtrag", "targetScreenId": "qualitaet/reklamation", "targetFilters": {"typ": "nachtrag"}, "tone": "warning"},
            {"key": "lagerbewegungen", "label": "Lagerbewegungen", "targetScreenId": "lager/stock-movement", "targetFilters": {}, "tone": "neutral"},
            {"key": "bestand", "label": "Bestandsuebersicht", "targetScreenId": "lager/article-stock", "targetFilters": {}, "tone": "neutral"},
        ],
    )


def build_workspace_fibu_screen_definition() -> dict[str, Any]:
    return _build_workspace_screen_definition(
        screen_id="workspace/fibu",
        domain="finance",
        title="FIBU-Cockpit",
        subtitle="Startseite Finanzbuchhaltung",
        purpose="Rollen-Startseite FIBU — offene Posten, faellige Zahlungen und Mahnstufen mit Sprung in Zahlungslauf und OP-Masken.",
        summary=[
            {"key": "op_debitoren", "label": "OP Debitoren", "tone": "neutral"},
            {"key": "op_kreditoren", "label": "OP Kreditoren", "tone": "neutral"},
            {"key": "faellige_zahlungen", "label": "Faellige Zahlungen", "tone": "warning"},
        ],
        tiles=[
            {"key": "zahlungslauf", "label": "Zahlungslauf-Vorschlag", "targetScreenId": "finance/payment-run", "targetFilters": {}, "tone": "warning"},
            {"key": "op_debitoren", "label": "Offene Posten Debitoren", "targetScreenId": "finance/ar-open-item", "targetFilters": {"overdue": "1"}, "tone": "neutral"},
            {"key": "eingangsrechnungen", "label": "Eingangsrechnungen", "targetScreenId": "finance/ap-invoice", "targetFilters": {}, "tone": "neutral"},
        ],
    )


def build_workspace_leitung_screen_definition() -> dict[str, Any]:
    return _build_workspace_screen_definition(
        screen_id="workspace/leitung",
        domain="management",
        title="Leitungs-Cockpit",
        subtitle="Startseite Geschaeftsleitung",
        purpose="Rollen-Startseite Leitung — Umsatz, Rohertrag und Top-Ausnahmen mit Sprung in Eskalations- und Audit-Ansichten.",
        summary=[
            {"key": "umsatz_ytd", "label": "Umsatz YTD", "tone": "neutral"},
            {"key": "rohertrag", "label": "Rohertrag", "tone": "neutral"},
            {"key": "top_ausnahmen", "label": "Top-Ausnahmen", "tone": "warning"},
        ],
        tiles=[
            {"key": "eskalationen", "label": "Eskalationen", "targetScreenId": "qualitaet/reklamation", "targetFilters": {"prioritaet": "hoch"}, "tone": "danger"},
            {"key": "op_gesamt", "label": "Offene Posten (Ueberfaellig)", "targetScreenId": "finance/ar-open-item", "targetFilters": {"overdue": "1"}, "tone": "warning"},
            {"key": "kontrakte", "label": "Kontrakt-Fristen", "targetScreenId": "agrar/kontrakte", "targetFilters": {}, "tone": "neutral"},
        ],
    )


def build_lager_leitstand_screen_definition() -> dict[str, Any]:
    """Native cockpit ScreenDefinition fuer UIX-081 Twin-Panel Leitstand."""

    return {
        "schemaVersion": 1,
        "id": "lager/leitstand",
        "domain": "lager",
        "mode": "cockpit",
        "title": "Lager-Leitstand",
        "subtitle": "Twin-Panel fuer Silozellen, Fuellstand und QS-Sperren",
        "adapter": {"type": "native", "sourceId": "lager/leitstand", "temporary": False},
        "summary": [
            {"key": "silozellen", "label": "Silozellen", "tone": "neutral"},
            {"key": "qs_sperren", "label": "QS-Sperren", "tone": "warning"},
            {"key": "cache", "label": "Read-Model 30s", "tone": "neutral"},
        ],
        "twin": {
            "endpoint": "/api/v1/lager/silo/cells",
            "planId": "lager-leitstand",
            "cacheTtlSeconds": 30,
            "activateRouteTemplate": "/lager/silo-zellen/{cellId}",
            "activateScreenId": "lager/silo-cell",
            "metrics": [
                {"key": "fill_pct", "label": "Fuellstand", "kind": "percent", "warnAbove": 90},
                {"key": "stock_kg", "label": "Bestand kg", "kind": "number"},
                {"key": "capacity_kg", "label": "Kapazitaet kg", "kind": "number"},
                {"key": "locked", "label": "Gesperrt", "kind": "flag"},
                {"key": "qs_status", "label": "QS", "kind": "status"},
            ],
        },
        "layout": {
            "floorplan": "cockpit",
            "density": "expertDense",
            "contextRail": "combined",
            "tableProfile": "inventory",
        },
        "workflow": {
            "processKey": "lager-leitstand",
            "status": "read-model",
            "nextActionKey": "refresh",
            "auditRequired": False,
        },
        "actions": [
            {
                "key": "refresh",
                "label": "Aktualisieren",
                "kind": "secondary",
                "permission": "lager.silo.read",
                "dangerLevel": "safe",
            }
        ],
        "noWorkflowReason": "Leitstand ist ein Read-Model-Cockpit; Statuswechsel erfolgen in den Silozellen-/Materialfluss-Prozessmasken.",
        "agentContract": {
            "businessPurpose": "Physische Silozellen-Belegung, Fuellstand und QS-Sperren als klickbares Werkzeug im Lager-Leitstand anzeigen.",
            "examplePrompts": [
                "Welche Silozellen sind gesperrt?",
                "Zeige den Fuellstand im Lager-Leitstand.",
                "Welche Zelle ist ueber 90 Prozent belegt?",
            ],
            "testSelectors": {"screenRoot": "[data-testid='lager-leitstand']"},
        },
        "performance": {
            "initialPayloadBudgetKb": 48,
            "requiresLazyTabs": False,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "lager",
        },
    }


def build_planung_kalender_screen_definition() -> dict[str, Any]:
    """Native cockpit ScreenDefinition fuer UIX-063 Planungskalender."""

    return {
        "schemaVersion": 1,
        "id": "planung/kalender",
        "domain": "platform",
        "mode": "cockpit",
        "title": "Planungskalender",
        "subtitle": "Zeitprojektionen aus Belegen, Fristen, CRM und Sachkunde",
        "adapter": {"type": "native", "sourceId": "planung/kalender", "temporary": False},
        "summary": [
            {"key": "naechste_14_tage", "label": "Fristenband 14 Tage", "tone": "warning"},
            {"key": "aktive_layer", "label": "Layer", "tone": "neutral"},
            {"key": "ics_feed", "label": "ICS read-only", "tone": "neutral"},
        ],
        "calendar": {
            "endpoint": "/api/v1/planung/kalender",
            "reprojectEndpoint": "/api/v1/planung/kalender/reproject",
            "icsTokenEndpoint": "/api/v1/planung/kalender/ics-token",
            "defaultView": "agenda",
            "deadlineBandDays": 14,
            "layers": [
                {"key": "finanzen", "label": "Finanzen", "defaultVisible": True},
                {"key": "fristen", "label": "Fristen", "defaultVisible": True},
                {"key": "crm", "label": "CRM", "defaultVisible": True},
                {"key": "logistik", "label": "Logistik", "defaultVisible": True},
                {"key": "personal", "label": "Personal", "defaultVisible": False},
                {"key": "saison", "label": "Saison", "defaultVisible": False},
            ],
        },
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "combined",
        },
        "workflow": {
            "processKey": "planung-kalender",
            "status": "projected",
            "nextActionKey": "reproject",
            "auditRequired": True,
        },
        "actions": [
            {
                "key": "reproject",
                "label": "Neu projizieren",
                "kind": "secondary",
                "permission": "planung.calendar.reproject",
                "commandEndpoint": "/api/v1/planung/kalender/reproject",
                "method": "POST",
                "dangerLevel": "moderate",
                "requiresConfirmation": True,
            }
        ],
        "noWorkflowReason": "Kalender ist ein Read-Model-Cockpit; Statuswechsel erfolgen an vorgeschlagenen Eintraegen ueber normale Commands.",
        "agentContract": {
            "businessPurpose": "Zeitbezogene Fristen, Wiedervorlagen und Laeufe ohne Doppelpflege als Planungscockpit sichtbar machen.",
            "examplePrompts": [
                "Was steht naechste Woche an?",
                "Zeige Fristen der naechsten 14 Tage.",
                "Welche OP-Faelligkeiten kommen diese Woche?",
            ],
            "testSelectors": {"screenRoot": "[data-testid='planung-kalender']"},
        },
    }


_SCREEN_DEFINITIONS: dict[str, Any] = {
    "crm/customer-360": build_crm_customer_360_screen_definition,
    "planung/kalender": build_planung_kalender_screen_definition,
    "lager/leitstand": build_lager_leitstand_screen_definition,
    "workspace/einkauf": build_workspace_einkauf_screen_definition,
    "workspace/verkauf": build_workspace_verkauf_screen_definition,
    "workspace/lager": build_workspace_lager_screen_definition,
    "workspace/fibu": build_workspace_fibu_screen_definition,
    "workspace/leitung": build_workspace_leitung_screen_definition,
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
    # Wave 2: alle verbleibenden ObjectPage-Masken (UIX-043)
    "agrar/duenger": build_agrar_duenger_screen_definition,
    "agrar/saatgut": build_agrar_saatgut_screen_definition,
    "finance/debitor": build_finance_debitor_screen_definition,
    "finance/kreditor": build_finance_kreditor_screen_definition,
    "finance/bankkonto": build_finance_bankkonto_screen_definition,
    "einkauf/anfrage": build_einkauf_anfrage_screen_definition,
    "einkauf/angebot": build_einkauf_angebot_screen_definition,
    "einkauf/anlieferavis": build_einkauf_anlieferavis_screen_definition,
    "einkauf/auftragsbestaetigung": build_einkauf_auftragsbestaetigung_screen_definition,
    "qualitaet/reklamation": build_qualitaet_reklamation_screen_definition,
    "futtermittel/einzelfuttermittel": build_futtermittel_einzelfuttermittel_screen_definition,
    "futtermittel/mischfuttermittel": build_futtermittel_mischfuttermittel_screen_definition,
    "crm/lead": build_crm_lead_screen_definition,
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


def _infer_meridian_floorplan(definition: dict[str, Any]) -> str:
    screen_id = definition.get("id", "")
    mode = definition.get("mode")
    if mode == "list":
        return "worklist"
    if mode == "cockpit" or screen_id == "crm/customer-360":
        return "cockpit"
    if mode == "wizard":
        return "wizard"
    if screen_id in {"finance/payment-run", "lager/stock-movement", "einkauf/anlieferavis"}:
        return "transaction"
    return "objectPage"


def _infer_meridian_table_profile(definition: dict[str, Any]) -> str:
    screen_id = definition.get("id", "")
    domain = definition.get("domain", "")
    if domain == "finance" or any(token in screen_id for token in ("invoice", "open-item", "payment", "debitor", "kreditor", "bankkonto")):
        return "financial"
    if domain in {"lager", "inventory"} or any(token in screen_id for token in ("stock", "article")):
        return "inventory"
    if domain in {"compliance", "qualitaet"}:
        return "audit"
    return "standard"


def _has_tables(definition: dict[str, Any]) -> bool:
    if definition.get("tables"):
        return True
    return any(tab.get("tables") for tab in definition.get("tabs") or [])


def _with_meridian_layout(definition: dict[str, Any]) -> dict[str, Any]:
    """Adds the Meridian layout contract without changing existing builders."""

    layout = dict(definition.get("layout") or {})
    floorplan = layout.get("floorplan") or _infer_meridian_floorplan(definition)
    layout.setdefault("preferredMode", "desktopDense")
    layout.setdefault("mobileMode", "mobileStack")
    layout.setdefault("touchTargetPx", 44)
    layout["floorplan"] = floorplan
    layout.setdefault("density", "expertDense" if _infer_meridian_table_profile(definition) in {"financial", "inventory"} else "compact")
    layout.setdefault("contextRail", "none" if floorplan == "worklist" else ("audit" if definition.get("domain") == "finance" else "combined"))
    if _has_tables(definition):
        layout.setdefault("tableProfile", _infer_meridian_table_profile(definition))
    definition["layout"] = layout
    return definition


for _spec in ROLLOUT_WAVES_42_51:
    if _spec.screen_id in _SCREEN_DEFINITIONS:
        continue

    def _make_builder(_s: Any = _spec) -> Any:
        def _builder() -> dict[str, Any]:
            return _build_rollout_screen_definition_from_spec(_s)
        return _builder

    _SCREEN_DEFINITIONS[_spec.screen_id] = _make_builder()


# ── Omnibox-Synonyme (UIX-060) ───────────────────────────────────────────────
# Kuratierte deutsche Suchbegriffe je Maske — Matching-Basis fuer den
# Intent-Compiler. Zentral gepflegt statt je SD, damit der Katalog
# (/ui/mask-registry/omnibox-catalog) eine Wartungsstelle hat.
_AGENT_SYNONYMS: dict[str, list[str]] = {
    "agrar/duenger": ["duenger", "duengemittel", "kas", "npk"],
    "agrar/harvest-settlement": ["ernteabrechnung", "sammelabrechnung", "gutschrift ernte"],
    "agrar/kontrakte": ["kontrakt", "vorkontrakt", "liefervertrag", "andienung"],
    "agrar/saatgut": ["saatgut", "sorte", "z-saatgut"],
    "crm/customer-360": ["kunde", "kundenakte", "kunden-360", "kundenstamm"],
    "crm/lead": ["lead", "interessent", "verkaufschance"],
    "crm/opportunity": ["opportunity", "chance", "verkaufschance"],
    "einkauf/anfrage": ["anfrage", "rfq", "preisanfrage"],
    "einkauf/angebot": ["lieferantenangebot", "einkaufsangebot"],
    "einkauf/anlieferavis": ["avis", "anlieferavis", "anlieferung"],
    "einkauf/auftragsbestaetigung": ["auftragsbestaetigung", "ab", "bestellbestaetigung"],
    "einkauf/purchase-order": ["bestellung", "einkaufsauftrag", "po"],
    "einkauf/supplier": ["lieferant", "kreditor-stamm", "lieferantenstamm"],
    "finance/ap-invoice": ["eingangsrechnung", "kreditorenrechnung", "rechnungseingang"],
    "finance/ar-open-item": ["offene posten", "op", "debitoren-op", "forderungen"],
    "finance/bankkonto": ["bankkonto", "bank", "kontoauszug"],
    "finance/debitor": ["debitor", "debitorenstamm", "kundenkonto"],
    "finance/kreditor": ["kreditor", "kreditorenstamm", "lieferantenkonto"],
    "finance/payment-run": ["zahlungslauf", "zahllauf", "sepa-lauf", "zahlungsvorschlag"],
    "futtermittel/einzelfuttermittel": ["einzelfuttermittel", "futtermittel", "efm"],
    "futtermittel/mischfuttermittel": ["mischfutter", "mischfuttermittel", "mfm"],
    "lager/article-stock": ["artikelbestand", "lagerbestand", "bestand"],
    "lager/leitstand": ["lager leitstand", "silo twin", "silozellen", "hofplan", "silo belegung"],
    "lager/stock-movement": ["lagerbewegung", "warenbewegung", "umbuchung"],
    "qualitaet/reklamation": ["reklamation", "beanstandung", "maengelruege"],
    "sales/delivery-note": ["lieferschein", "lieferung", "warenausgang"],
    "sales/sales-order": ["verkaufsauftrag", "auftrag", "kundenauftrag"],
    "workspace/einkauf": ["einkauf cockpit", "einkauf startseite", "beschaffung workspace"],
    "workspace/verkauf": ["verkauf cockpit", "vertrieb startseite", "sales workspace"],
    "workspace/lager": ["lager cockpit", "annahme startseite", "lager workspace"],
    "workspace/fibu": ["fibu cockpit", "finanzbuchhaltung startseite", "finance workspace"],
    "workspace/leitung": ["leitung cockpit", "geschaeftsleitung", "management workspace"],
    "planung/kalender": ["planungskalender", "kalender", "fristenkalender", "was steht naechste woche an"],
}


# ── Omnibox-Listen-Routen (UIX-060) ──────────────────────────────────────────
# Kuratiertes screen_id → Frontend-Listen-Route Mapping. Die nativen SD-Routen
# sind Detail-Ansichten (screen_id/:id); fuer die Omnibox-Landung ("offene
# posten folkerts") braucht der Compiler eine *filterbare Liste*. Diese Map ist
# die eine Wartungsstelle, die jede Maske an ihre real existierende Listen-Seite
# bindet — der Katalog (/ui/mask-registry/omnibox-catalog) emittiert die Route
# direkt, sodass das Frontend keinen fragilen ID-Join gegen die MaskRegistry
# (deren mask_ids fuer 19 von 26 SDs divergieren) mehr braucht.
_SCREEN_LIST_ROUTE: dict[str, str] = {
    "agrar/duenger": "/agrar/duenger",
    "agrar/harvest-settlement": "/agrar/kontrakt-settlement",
    "agrar/kontrakte": "/kontrakte",
    "agrar/saatgut": "/agrar/saatgut",
    "crm/customer-360": "/verkauf/kunden-liste",
    "crm/lead": "/crm/leads",
    "crm/opportunity": "/crm/opportunities",
    "einkauf/anfrage": "/einkauf/anfragen",
    "einkauf/angebot": "/einkauf/angebote",
    "einkauf/anlieferavis": "/einkauf/anlieferavis",
    "einkauf/auftragsbestaetigung": "/einkauf/auftragsbestaetigungen",
    "einkauf/purchase-order": "/einkauf/bestellungen",
    "einkauf/supplier": "/einkauf/lieferanten",
    "finance/ap-invoice": "/einkauf/rechnungseingang",
    "finance/ar-open-item": "/finance/op-debitoren",
    "finance/bankkonto": "/finance/bankkonten",
    "finance/debitor": "/finance/debitoren-liste",
    "finance/kreditor": "/finance/kreditoren",
    "finance/payment-run": "/fibu/zahlungslaeufe",
    "futtermittel/einzelfuttermittel": "/futtermittel/einzelfuttermittel-liste",
    "futtermittel/mischfuttermittel": "/futtermittel/mischfuttermittel-liste",
    "lager/article-stock": "/lager/bestandsuebersicht",
    "lager/leitstand": "/lager/materialfluss-visualisierung",
    "lager/stock-movement": "/lager/lagerbewegungen",
    "qualitaet/reklamation": "/qualitaet/reklamationen",
    "sales/delivery-note": "/verkauf/lieferschein-erfassung",
    "sales/sales-order": "/verkauf/auftraege",
    "workspace/einkauf": "/workspace/einkauf",
    "workspace/verkauf": "/workspace/verkauf",
    "workspace/lager": "/workspace/lager",
    "workspace/fibu": "/workspace/fibu",
    "workspace/leitung": "/workspace/leitung",
    "planung/kalender": "/planung/kalender",
}


def get_screen_list_route(mask_id: str) -> str | None:
    """Kuratierte Listen-Route einer Maske fuer die Omnibox-Navigation (UIX-060)."""
    return _SCREEN_LIST_ROUTE.get(mask_id)


def _resolve_tile_routes(definition: dict[str, Any]) -> None:
    """Reichert cockpit-Kacheln (UIX-061) um die aufgeloeste targetRoute an —
    Wiederverwendung der Omnibox-Routen-Bruecke, damit das Frontend keinen
    eigenen screenId->Route-Join braucht."""
    for tile in definition.get("tiles") or []:
        target = tile.get("targetScreenId")
        if target and "targetRoute" not in tile:
            route = get_screen_list_route(target)
            if route:
                tile["targetRoute"] = route


def _apply_season_profile(definition: dict[str, Any], today: str | None) -> None:
    """Sortiert Kacheln gemaess seasonProfile.tileOrderOverride um, wenn das
    heutige Datum (MM-TT) im aktiven Fenster liegt. Reine Umsortierung — kein
    Inhaltswechsel (UIX-061)."""
    profile = definition.get("seasonProfile")
    tiles = definition.get("tiles")
    if not profile or not tiles:
        return
    order = profile.get("tileOrderOverride")
    if not order:
        return
    from datetime import date as _date

    md = (today or _date.today().isoformat())[5:10]  # MM-TT
    active_from = profile.get("activeFrom", "01-01")
    active_to = profile.get("activeTo", "12-31")
    # Fenster kann das Jahresende ueberspannen (z.B. 11-01..02-15)
    in_window = (active_from <= md <= active_to) if active_from <= active_to else (md >= active_from or md <= active_to)
    if not in_window:
        return
    rank = {key: idx for idx, key in enumerate(order)}
    definition["tiles"] = sorted(tiles, key=lambda t: rank.get(t.get("key"), len(order)))


def get_screen_definition(mask_id: str, *, today: str | None = None) -> dict[str, Any] | None:
    builder = _SCREEN_DEFINITIONS.get(mask_id)
    if builder is None:
        return None
    definition = _with_meridian_layout(builder())
    contract = definition.setdefault("agentContract", {})
    contract.setdefault("synonyms", _AGENT_SYNONYMS.get(mask_id, []))
    _resolve_tile_routes(definition)
    _apply_season_profile(definition, today)
    return definition


# Public alias for inventory / governance scripts (SPEC-P1-04)
SCREEN_DEFINITION_BUILDERS = _SCREEN_DEFINITIONS
