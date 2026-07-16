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
        "summary": [
            {"key": "bestand", "label": "Bestand", "tone": "neutral"},
            {"key": "mindestbestand", "label": "Meldebestand", "tone": "warning"},
            {"key": "esg_co2e", "label": "CO2e Charge", "tone": "neutral"},
        ],
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
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}"},
            {"key": "naehrstoffe", "endpoint": "/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/reference-values", "pageSize": 50},
            {"key": "preise", "endpoint": "/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/products", "pageSize": 25},
            {"key": "history", "endpoint": "/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/history", "pageSize": 25},
        ],
        "tabs": [
            {"key": "kopf", "label": "Stammdaten", "lazy": False, "keepAlive": True, "dataSourceKey": "entity",
             "fields": [
                 {"key": "artikel_nummer", "label": "FM-Nr.", "type": "text", "readOnly": True},
                 {"key": "name", "label": "Bezeichnung", "type": "text", "required": True},
                 {"key": "art", "label": "Kategorie", "type": "text"},
                 {"key": "feed_kind", "label": "Futterart", "type": "text"},
                 {"key": "species_scope", "label": "Tierarten", "type": "text"},
                 {"key": "trockensubstanz", "label": "Trockensubstanz %", "type": "number"},
                 {"key": "energie", "label": "ME (MJ/kg TM)", "type": "number"},
                 {"key": "protein", "label": "Rohprotein %", "type": "number"},
                 {"key": "approval_status", "label": "Freigabestatus", "type": "text"},
                 {"key": "revision", "label": "Revision", "type": "number", "readOnly": True},
             ]},
            {"key": "naehrstoffe", "label": "Naehrstoffe", "lazy": True, "keepAlive": False,
             "tables": [{"key": "naehrstoffe", "label": "Naehrstoffgehalte", "dataSourceKey": "naehrstoffe",
                         "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "nutrient_name", "label": "Naehrstoff", "sortable": True, "filterable": True},
                             {"key": "value", "label": "Gehalt", "numeric": True, "renderKind": "number"},
                             {"key": "unit_code", "label": "Einheit", "width": 110},
                             {"key": "basis", "label": "Basis", "filterable": True, "width": 130},
                             {"key": "source_type", "label": "Quelle", "filterable": True, "width": 130},
                             {"key": "value_status", "label": "Wertstatus", "renderKind": "status", "width": 120},
                         ]}]},
            {"key": "preise", "label": "Preise", "lazy": True, "keepAlive": False,
             "tables": [{"key": "preise", "label": "Preise", "dataSourceKey": "preise",
                         "serverPagination": True, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "valid_from", "label": "Gueltig ab", "renderKind": "date", "sortable": True, "width": 110},
                             {"key": "price_eur_t", "label": "Preis/t", "numeric": True, "sortable": True, "renderKind": "currency"},
                             {"key": "display_name", "label": "Produkt", "filterable": True, "width": 200},
                             {"key": "packaging_unit", "label": "Gebinde", "width": 100},
                             {"key": "minimum_order_qty", "label": "Mindestabnahme", "numeric": True, "width": 140},
                         ]}]},
            {"key": "history", "label": "Historie", "lazy": True, "keepAlive": False,
             "tables": [{"key": "history", "label": "Revisionen", "dataSourceKey": "history",
                         "serverPagination": False, "pageSize": 25, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                             {"key": "changed_at", "label": "Geaendert", "renderKind": "datetime", "sortable": True, "width": 180},
                             {"key": "changed_by", "label": "Bearbeiter", "filterable": True, "width": 180},
                             {"key": "reason", "label": "Aenderungsgrund", "width": 320},
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


def build_futtermittel_analysen_screen_definition() -> dict[str, Any]:
    """Native Analyse-Worklist; Import/Freigabe stay explicit domain commands."""
    return {
        "schemaVersion": 1, "id": "futtermittel/analysen", "domain": "futtermittel", "mode": "list",
        "title": "Futteranalysen", "subtitle": "Laborwerte, Provenienz und Freigabe",
        "adapter": {"type": "native", "sourceId": "futtermittel/analysen", "temporary": False},
        "dataSources": [
            {"key": "list", "endpoint": "/api/v1/agrar/rations-optimization/feed-analyses", "pageSize": 50},
        ],
        "tabs": [
            {"key": "analysen", "label": "Analysen", "lazy": False, "keepAlive": True,
             "tables": [{"key": "list", "label": "Futteranalysen", "dataSourceKey": "list",
                         "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "rowRouteTemplate": "/futtermittel/grundfutteranalysen/{id}",
                         "columns": [
                             {"key": "probe_nr", "label": "Probe", "sortable": True, "width": 120},
                             {"key": "bezeichnung", "label": "Material", "sortable": True, "filterable": True, "width": 240},
                             {"key": "labor", "label": "Labor", "filterable": True, "width": 180},
                             {"key": "analyse_datum", "label": "Analysedatum", "renderKind": "date", "sortable": True, "width": 130},
                             {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                             {"key": "is_active", "label": "Aktiv", "renderKind": "boolean", "width": 80},
                             {"key": "revision", "label": "Revision", "numeric": True, "width": 90},
                         ]}]},
        ],
        "actions": [
            {"key": "import_analysis", "label": "Analyse erfassen", "kind": "primary",
             "dangerLevel": "safe", "permission": "futtermittel.analyse.create"},
        ],
        "noWorkflowReason": "Die Worklist priorisiert Analysen; Statuswechsel erfolgen auf der Analyse-ObjectPage.",
        "agentContract": {
            "businessPurpose": "Futteranalysen nach Plausibilitaet, Freigabe und Aktualitaet priorisieren.",
            "examplePrompts": ["Welche Analysen warten auf Pruefung?", "Welche aktiven Analysen sind veraltet?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='futtermittel-analysen']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"floorplan": "worklist", "density": "expertDense", "contextRail": "none",
                   "tableProfile": "standard", "preferredMode": "desktopDense",
                   "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 40, "requiresLazyTabs": False, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "futtermittel"},
    }


def build_futtermittel_analyse_screen_definition() -> dict[str, Any]:
    """Native analysis ObjectPage with provenance, findings and immutable history."""
    base = "/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}"
    return {
        "schemaVersion": 1, "id": "futtermittel/analyse", "domain": "futtermittel", "mode": "detail",
        "title": "Futteranalyse", "subtitle": "Pruefung, Provenienz und aktive Version",
        "adapter": {"type": "native", "sourceId": "futtermittel/analyse", "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": base},
            {"key": "values", "endpoint": base + "/values", "pageSize": 100},
            {"key": "findings", "endpoint": base + "/findings", "pageSize": 50},
            {"key": "history", "endpoint": base + "/history", "pageSize": 50},
        ],
        "tabs": [
            {"key": "overview", "label": "Probe & Freigabe", "lazy": False, "keepAlive": True,
             "dataSourceKey": "entity", "fields": [
                 {"key": "probe_nr", "label": "Probe", "type": "text", "readOnly": True},
                 {"key": "bezeichnung", "label": "Material", "type": "text", "readOnly": True},
                 {"key": "labor", "label": "Labor", "type": "text", "readOnly": True},
                 {"key": "method", "label": "Methode", "type": "text", "readOnly": True},
                 {"key": "analyse_datum", "label": "Analysedatum", "type": "date", "readOnly": True},
                 {"key": "status", "label": "Status", "type": "text", "readOnly": True},
                 {"key": "is_active", "label": "Aktive Analyse", "type": "boolean", "readOnly": True},
                 {"key": "revision", "label": "Revision", "type": "number", "readOnly": True},
                 {"key": "original_document_id", "label": "Originalbeleg", "type": "text", "readOnly": True},
             ]},
            {"key": "values", "label": "Messwerte", "lazy": True, "keepAlive": False,
             "tables": [{"key": "values", "label": "Labor- und Rechenwerte", "dataSourceKey": "values",
                         "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "nutrient_code", "label": "Naehrstoff", "sortable": True, "filterable": True, "width": 190},
                             {"key": "original_value", "label": "Original", "numeric": True, "renderKind": "number"},
                             {"key": "original_unit_code", "label": "Orig.-Einheit", "width": 120},
                             {"key": "canonical_value", "label": "Rechenwert", "numeric": True, "renderKind": "number"},
                             {"key": "canonical_unit_code", "label": "Einheit", "width": 110},
                             {"key": "basis", "label": "Basis", "filterable": True, "width": 120},
                             {"key": "value_status", "label": "Provenienz", "renderKind": "status", "width": 120},
                         ]}]},
            {"key": "findings", "label": "Plausibilitaet", "lazy": True, "keepAlive": False,
             "tables": [{"key": "findings", "label": "Befunde", "dataSourceKey": "findings",
                         "serverPagination": False, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "severity", "label": "Prioritaet", "renderKind": "status", "filterable": True, "width": 110},
                             {"key": "code", "label": "Regel", "width": 190},
                             {"key": "message", "label": "Befund", "width": 420},
                             {"key": "observed_value", "label": "Wert", "numeric": True, "renderKind": "number"},
                         ]}]},
            {"key": "history", "label": "Audit", "lazy": True, "keepAlive": False,
             "tables": [{"key": "history", "label": "Unveraenderliche Revisionen", "dataSourceKey": "history",
                         "serverPagination": False, "pageSize": 50, "virtualized": True, "rowHeight": 52,
                         "columns": [
                             {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                             {"key": "changed_at", "label": "Zeitpunkt", "renderKind": "datetime", "sortable": True, "width": 180},
                             {"key": "changed_by", "label": "Akteur", "filterable": True, "width": 180},
                             {"key": "reason", "label": "Grund", "width": 360},
                         ]}]},
        ],
        "actions": [
            {"key": "validate", "label": "Plausibilitaet pruefen", "kind": "primary", "dangerLevel": "safe",
             "permission": "futtermittel.analyse.validate"},
            {"key": "release", "label": "Analyse freigeben", "kind": "primary", "dangerLevel": "high",
             "permission": "futtermittel.analyse.release", "requiresConfirmation": True,
             "humanApprovalRequired": True, "auditReasonRequired": True,
             "commandEndpoint": base + "/actions/release", "method": "POST"},
            {"key": "reject", "label": "Zurueckweisen", "kind": "secondary", "dangerLevel": "moderate",
             "permission": "futtermittel.analyse.reject", "requiresConfirmation": True,
             "auditReasonRequired": True, "commandEndpoint": base + "/actions/reject", "method": "POST"},
        ],
        "noWorkflowReason": "Der Analyse-Lifecycle wird durch serverseitig validierte Status-Commands gesteuert.",
        "agentContract": {
            "businessPurpose": "Laborbefund nachvollziehbar pruefen und genau eine Analyseversion bewusst aktivieren.",
            "examplePrompts": ["Welche Blocker verhindern die Freigabe?", "Zeige Original- und Rechenwerte dieser Analyse."],
            "sensitiveFields": ["original_document_id", "original_sha256"],
            "testSelectors": {"screenRoot": "[data-testid='futtermittel-analyse']", "primaryAction": "[data-testid='action-validate']", "summaryArea": "[data-testid='mask-summary']"},
        },
        "layout": {"floorplan": "objectPage", "density": "expertDense", "contextRail": "audit",
                   "tableProfile": "audit", "preferredMode": "desktopDense",
                   "mobileMode": "mobileStack", "touchTargetPx": 44},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "futtermittel"},
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


def build_agrar_feed_advice_screen_definition() -> dict[str, Any]:
    """Native Meridian entry cockpit for feeding advice.

    The cockpit owns orientation and daily task selection. The mathematically
    dense solver remains a deliberately specialised task workspace reached
    from here; mobile execution, stock and analyses stay separate role-sized
    tasks instead of becoming modes in one monolithic page.
    """
    return {
        "schemaVersion": 1,
        "id": "agrar/feed-advice",
        "domain": "agrar",
        "mode": "cockpit",
        "title": "Fuetterungsberatung",
        "subtitle": "Rationen planen, freigeben und im Stall nachhalten",
        "adapter": {"type": "native", "sourceId": "agrar/feed-advice", "temporary": False},
        "summary": [
            {"key": "aktive_rationen", "label": "Aktive Rationen", "value": "–", "tone": "neutral"},
            {"key": "heute_fuettern", "label": "Heute fuettern", "value": "Taeglicher Ablauf", "tone": "success"},
            {"key": "pruefbedarf", "label": "Pruefbedarf", "value": "Analysen und Bestand", "tone": "warning"},
        ],
        "tiles": [
            {
                "key": "ration_planen",
                "label": "Ration planen oder optimieren",
                "targetScreenId": "agrar/feed-advice",
                "targetRoute": "/portal/rationsoptimierung?mode=expert",
                "tone": "neutral",
            },
            {
                "key": "stallarbeit",
                "label": "Heutige Fuetterung dokumentieren",
                "targetScreenId": "agrar/feed-advice",
                "targetRoute": "/futtermittel/fuetterungsdokumentation-mobil",
                "tone": "neutral",
            },
            {
                "key": "aktive_rationen",
                "label": "Rationen und Freigaben",
                "targetScreenId": "agrar/feed-advice",
                "targetRoute": "/portal/rationsoptimierung?view=rations",
                "tone": "warning",
            },
            {
                "key": "betriebe",
                "label": "Betriebe und Herden",
                "targetScreenId": "agrar/feeding-businesses",
                "targetRoute": "/portal/rationsoptimierung?view=businesses",
                "tone": "neutral",
            },
            {
                "key": "futterbestand",
                "label": "Futterbestand und Reichweite",
                "targetScreenId": "agrar/feed-readiness",
                "targetRoute": "/portal/rationsoptimierung?view=readiness",
                "tone": "warning",
            },
            {
                "key": "analysen",
                "label": "Grundfutteranalysen pruefen",
                "targetScreenId": "futtermittel/einzelfuttermittel",
                "targetRoute": "/futtermittel/grundfutteranalysen",
                "tone": "neutral",
            },
            {
                "key": "controlling",
                "label": "Soll-Ist und Effizienz auswerten",
                "targetScreenId": "agrar/feed-advice",
                "targetRoute": "/portal/rationsoptimierung?view=controlling",
                "tone": "neutral",
            },
        ],
        "noWorkflowReason": "Das Cockpit priorisiert Aufgaben; Freigabe- und Fuetterungsstatus gehoeren zur jeweiligen Ration.",
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "floorplan": "cockpit",
            "density": "comfortable",
            "contextRail": "copilot",
            "tableProfile": "standard",
        },
        "performance": {
            "initialPayloadBudgetKb": 24,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Aufgabenorientierter Einstieg in Planung, Freigabe, Stallausfuehrung und Controlling der Fuetterung.",
            "examplePrompts": [
                "Welche Ration braucht heute Aufmerksamkeit?",
                "Wo fehlen aktuelle Analysen oder ausreichend Bestand?",
                "Zeige mir den schnellsten Weg zur heutigen Fuetterung.",
            ],
            "sensitiveFields": ["futterkosten", "milchleistung"],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feed-advice']"},
        },
    }


def build_agrar_rations_lifecycle_screen_definition() -> dict[str, Any]:
    """Native worklist for persistent ration versions."""
    return {
        "schemaVersion": 1,
        "id": "agrar/rations-lifecycle",
        "domain": "agrar",
        "mode": "list",
        "title": "Rationen und Freigaben",
        "subtitle": "Versionen, Status und Fuetterungsbeginn je Tiergruppe",
        "adapter": {"type": "native", "sourceId": "agrar/rations-lifecycle", "temporary": False},
        "dataSources": [
            {
                "key": "rations",
                "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/rations",
                "pageSize": 100,
                "staleTimeMs": 10_000,
            },
            {
                "key": "groups",
                "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/groups",
                "pageSize": 100,
                "staleTimeMs": 15_000,
            },
        ],
        "tables": [
            {
                "key": "rations",
                "label": "Rationsversionen",
                "dataSourceKey": "rations",
                "serverPagination": True,
                "pageSize": 100,
                "virtualized": True,
                "rowHeight": 48,
                "rowRouteTemplate": "/portal/rationsoptimierung?view=ration&ration_id={id}",
                "columns": [
                    {"key": "name", "label": "Ration", "sortable": True, "filterable": True, "width": 230},
                    {"key": "group_name", "label": "Tiergruppe", "sortable": True, "filterable": True, "width": 220},
                    {"key": "version_no", "label": "Version", "numeric": True, "sortable": True, "width": 90},
                    {"key": "status", "label": "Status", "renderKind": "status", "sortable": True, "filterable": True, "width": 130},
                    {"key": "feeding_start", "label": "Fuetterungsbeginn", "renderKind": "datetime", "sortable": True, "width": 180},
                    {"key": "animal_count", "label": "Tiere", "numeric": True, "width": 80},
                    {"key": "updated_at", "label": "Geaendert", "renderKind": "datetime", "sortable": True, "width": 170},
                ],
            },
            {
                "key": "groups", "label": "Tiergruppen", "dataSourceKey": "groups",
                "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                "rowRouteTemplate": "/portal/rationsoptimierung?view=group&group_id={id}",
                "columns": [
                    {"key": "name", "label": "Tiergruppe", "sortable": True, "filterable": True, "width": 230},
                    {"key": "profile_code", "label": "Profil", "filterable": True, "width": 170},
                    {"key": "animal_count", "label": "Tiere", "numeric": True, "sortable": True, "width": 90},
                    {"key": "risk_level", "label": "Risiko", "renderKind": "status", "filterable": True, "width": 110},
                    {"key": "valid_from", "label": "Gueltig ab", "renderKind": "date", "sortable": True, "width": 120},
                    {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                ],
            },
        ],
        "actions": [
            {"key": "plan_ration", "label": "Neue Ration planen", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"},
            {"key": "create_group", "label": "Tiergruppe anlegen", "kind": "secondary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"},
        ],
        "noWorkflowReason": "Die Worklist aggregiert Lifecycle-Objekte; Statuswechsel erfolgen an einer konkreten Rationsversion.",
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "worklist", "density": "compact", "contextRail": "copilot", "tableProfile": "standard",
        },
        "performance": {
            "initialPayloadBudgetKb": 36, "requiresLazyTabs": True,
            "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Rationsversionen nach Tiergruppe, Status und Fuetterungsbeginn steuern.",
            "examplePrompts": ["Welche Rationen warten auf Freigabe?", "Welche Ration ist je Tiergruppe aktiv?"],
            "sensitiveFields": ["snapshot_checksum"],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/rations-lifecycle']", "primaryAction": "[data-action-kind='primary']"},
        },
    }


def build_agrar_feeding_businesses_screen_definition() -> dict[str, Any]:
    """Native worklist for grant-aware feeding businesses (FEED-CORE-015)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/feeding-businesses",
        "domain": "agrar",
        "mode": "list",
        "title": "Fuetterungsbetriebe",
        "subtitle": "Betriebe, Herden und Tiergruppen im erlaubten Beratungsscope",
        "adapter": {"type": "native", "sourceId": "agrar/feeding-businesses", "temporary": False},
        "dataSources": [{
            "key": "businesses",
            "endpoint": "/api/v1/agrar/rations-optimization/feeding/businesses",
            "pageSize": 100,
            "staleTimeMs": 15_000,
        }],
        "tables": [{
            "key": "businesses",
            "label": "Betriebe im Zugriff",
            "dataSourceKey": "businesses",
            "serverPagination": False,
            "pageSize": 100,
            "virtualized": True,
            "rowHeight": 48,
            "rowRouteTemplate": "/futtermittel/fuetterungsbetrieb/{id}",
            "columns": [
                {"key": "name", "label": "Betrieb", "sortable": True, "filterable": True, "width": 260},
                {"key": "production_type", "label": "Produktionsrichtung", "filterable": True, "width": 180},
                {"key": "feeding_system", "label": "Fuetterungssystem", "filterable": True, "width": 160},
                {"key": "advisory_status", "label": "Beratungsstatus", "renderKind": "status", "filterable": True, "width": 150},
                {"key": "herd_count", "label": "Herden", "numeric": True, "sortable": True, "width": 90},
                {"key": "group_count", "label": "Gruppen", "numeric": True, "sortable": True, "width": 100},
                {"key": "updated_at", "label": "Geaendert", "renderKind": "datetime", "sortable": True, "width": 170},
            ],
        }],
        "actions": [{
            "key": "create_business",
            "label": "Betrieb anlegen",
            "kind": "primary",
            "dangerLevel": "safe",
            "permission": "futtermittel.rations.update",
        }],
        "noWorkflowReason": "Betriebe sind Stammdaten; Beratung und Rationsfreigabe besitzen eigene Workflows.",
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
            "floorplan": "worklist",
            "density": "compact",
            "contextRail": "audit",
            "tableProfile": "standard",
        },
        "performance": {
            "initialPayloadBudgetKb": 36,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Autorisierte Fuetterungsbetriebe und ihre Beratungsreife steuern.",
            "examplePrompts": ["Welche Betriebe betreue ich?", "Wo fehlen Herden oder Tiergruppen?"],
            "sensitiveFields": ["business_partner_id", "preferences"],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-agrar/feeding-businesses']",
                "primaryAction": "[data-action-kind='primary']",
            },
        },
    }


def build_agrar_feeding_business_screen_definition() -> dict[str, Any]:
    """Prioritized feeding-business file over existing aggregates (FEED-EDITOR-025)."""
    base = "/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}"
    return {
        "schemaVersion": 1,
        "id": "agrar/feeding-business",
        "domain": "agrar",
        "mode": "detail",
        "title": "Fuetterungsbetrieb",
        "subtitle": "Gruppen, Rationsstatus, Analysereife und offene Befunde in einer Arbeitsakte",
        "adapter": {"type": "native", "sourceId": "agrar/feeding-business", "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": f"{base}/overview", "staleTimeMs": 15_000},
            {"key": "groups", "endpoint": f"{base}/groups", "pageSize": 100},
            {"key": "rations", "endpoint": f"{base}/rations", "pageSize": 100},
            {"key": "findings", "endpoint": f"{base}/findings", "pageSize": 100},
            {"key": "templates", "endpoint": f"{base}/ration-templates", "pageSize": 100},
        ],
        "tabs": [
            {
                "key": "overview", "label": "Arbeitsuebersicht", "lazy": False, "keepAlive": True,
                "fields": [
                    {"key": "name", "label": "Betrieb", "type": "text", "required": True},
                    {"key": "advisory_status", "label": "Beratungsstatus", "type": "text"},
                    {"key": "data_status", "label": "Datenlage", "type": "text"},
                    {"key": "group_count", "label": "Tiergruppen", "type": "number"},
                    {"key": "ration_count", "label": "Rationen", "type": "number"},
                    {"key": "active_ration_count", "label": "Aktive Rationen", "type": "number"},
                    {"key": "readiness_blocked_count", "label": "Blockierte Rationen", "type": "number"},
                    {"key": "readiness_unknown_count", "label": "Reife ungeprueft", "type": "number"},
                    {"key": "template_count", "label": "Vorlagen", "type": "number"},
                ],
            },
            {
                "key": "groups", "label": "Tiergruppen", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "groups", "label": "Gruppen im Betrieb", "dataSourceKey": "groups",
                    "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                    "rowRouteTemplate": "/futtermittel/tiergruppe/{id}",
                    "columns": [
                        {"key": "name", "label": "Gruppe", "sortable": True, "filterable": True, "width": 240},
                        {"key": "animal_count", "label": "Tiere", "numeric": True, "width": 90},
                        {"key": "profile_code", "label": "Profil", "filterable": True, "width": 150},
                        {"key": "risk_level", "label": "Risiko", "renderKind": "status", "width": 110},
                        {"key": "ration_count", "label": "Rationen", "numeric": True, "width": 100},
                        {"key": "updated_at", "label": "Geaendert", "renderKind": "datetime", "width": 170},
                    ],
                }],
            },
            {
                "key": "rations", "label": "Rationen und Reife", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "rations", "label": "Neuester Stand je Ration", "dataSourceKey": "rations",
                    "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                    "rowRouteTemplate": "/futtermittel/ration/{id}",
                    "columns": [
                        {"key": "name", "label": "Ration", "sortable": True, "filterable": True, "width": 240},
                        {"key": "group_name", "label": "Gruppe", "filterable": True, "width": 200},
                        {"key": "version_no", "label": "Version", "numeric": True, "width": 90},
                        {"key": "status", "label": "Lifecycle", "renderKind": "status", "width": 120},
                        {"key": "readiness_status", "label": "Analysereife", "renderKind": "status", "width": 150},
                        {"key": "readiness_blockers", "label": "Blocker", "numeric": True, "width": 90},
                        {"key": "readiness_warnings", "label": "Warnungen", "numeric": True, "width": 110},
                    ],
                }],
            },
            {
                "key": "findings", "label": "Offene Befunde", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "findings", "label": "Priorisiert nach Schwere", "dataSourceKey": "findings",
                    "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 56,
                    "columns": [
                        {"key": "severity", "label": "Prioritaet", "renderKind": "status", "width": 110},
                        {"key": "group_name", "label": "Gruppe", "filterable": True, "width": 180},
                        {"key": "ration_name", "label": "Ration", "filterable": True, "width": 200},
                        {"key": "message", "label": "Befund", "width": 420},
                        {"key": "evaluated_at", "label": "Bewertet", "renderKind": "datetime", "width": 170},
                    ],
                }],
            },
            {
                "key": "templates", "label": "Rationsvorlagen", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "templates", "label": "Unveraenderliche Vorlagen", "dataSourceKey": "templates",
                    "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                    "columns": [
                        {"key": "name", "label": "Vorlage", "sortable": True, "filterable": True, "width": 260},
                        {"key": "source_ration_name", "label": "Quellration", "width": 220},
                        {"key": "source_version_no", "label": "Version", "numeric": True, "width": 90},
                        {"key": "created_by", "label": "Erstellt von", "width": 180},
                        {"key": "created_at", "label": "Erstellt", "renderKind": "datetime", "width": 170},
                    ],
                }],
            },
        ],
        "actions": [{
            "key": "create_template", "label": "Vorlage anlegen", "kind": "primary",
            "dangerLevel": "safe", "permission": "futtermittel.rations.update",
        }, {
            "key": "apply_template", "label": "Vorlage anwenden", "kind": "secondary",
            "dangerLevel": "safe", "permission": "futtermittel.rations.update",
        }],
        "noWorkflowReason": "Die Betriebsakte priorisiert vorhandene Aggregate; Freigaben bleiben im Rations-Lifecycle.",
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "objectPage", "density": "compact", "contextRail": "findings", "tableProfile": "audit",
        },
        "performance": {
            "initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True,
            "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Die naechste fachliche Fuetterungsentscheidung aus belastbarer Datenlage ableiten.",
            "examplePrompts": ["Welche Ration ist blockiert?", "Wo fehlt eine belastbare Analyse?", "Welche Befunde sind kritisch?"],
            "sensitiveFields": ["business_partner_id", "preferences", "snapshot_checksum"],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feeding-business']", "primaryAction": "[data-action-kind='primary']"},
        },
    }


def build_agrar_feeding_group_screen_definition() -> dict[str, Any]:
    """Native object page for versioned feeding-group parameters (FEED-CORE-016)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/feeding-group",
        "domain": "agrar",
        "mode": "detail",
        "title": "Tiergruppe",
        "subtitle": "Leistung, Traechtigkeit, Gueltigkeit und Parameterhistorie",
        "adapter": {"type": "native", "sourceId": "agrar/feeding-group", "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}"},
            {"key": "history", "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}/history", "pageSize": 50},
        ],
        "tabs": [
            {
                "key": "masterdata", "label": "Stammdaten", "lazy": True, "keepAlive": True,
                "fields": [
                    {"key": "name", "label": "Gruppenname", "type": "text", "required": True},
                    {"key": "profile_code", "label": "Gruppenprofil", "type": "text", "required": True},
                    {"key": "animal_type", "label": "Tierart", "type": "text", "required": True},
                    {"key": "animal_count", "label": "Tierzahl", "type": "number", "required": True},
                    {"key": "feeding_system", "label": "Fuetterungssystem", "type": "text", "required": True},
                    {"key": "location", "label": "Standort/Stall", "type": "text"},
                    {"key": "active", "label": "Aktiv", "type": "boolean"},
                ],
            },
            {
                "key": "parameters", "label": "Leistung und Bedarf", "lazy": True, "keepAlive": True,
                "fields": [
                    {"key": "body_mass_kg", "label": "Lebendmasse kg", "type": "number"},
                    {"key": "days_in_milk", "label": "Laktationstag", "type": "number"},
                    {"key": "lactation_number", "label": "Laktationsnummer", "type": "number"},
                    {"key": "target_milk_kg", "label": "Milchziel kg", "type": "number"},
                    {"key": "milk_fat_pct", "label": "Milchfett %", "type": "number"},
                    {"key": "milk_protein_pct", "label": "Milchprotein %", "type": "number"},
                    {"key": "milk_urea_mg_dl", "label": "Milchharnstoff mg/dl", "type": "number"},
                    {"key": "pregnancy_status", "label": "Traechtigkeitsstatus", "type": "text"},
                    {"key": "gestation_day", "label": "Traechtigkeitstag", "type": "number"},
                    {"key": "risk_level", "label": "Risikostufe", "type": "text"},
                    {"key": "valid_from", "label": "Gueltig ab", "type": "date"},
                    {"key": "valid_until", "label": "Gueltig bis", "type": "date"},
                ],
            },
            {
                "key": "history", "label": "Parameterhistorie", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "history", "label": "Revisionen", "dataSourceKey": "history",
                    "serverPagination": False, "pageSize": 50, "virtualized": True, "rowHeight": 48,
                    "columns": [
                        {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                        {"key": "changed_at", "label": "Geaendert", "renderKind": "datetime", "sortable": True, "width": 180},
                        {"key": "changed_by", "label": "Bearbeiter", "filterable": True, "width": 180},
                        {"key": "reason", "label": "Aenderungsgrund", "width": 360},
                    ],
                }],
            },
        ],
        "actions": [{
            "key": "edit_group", "label": "Tiergruppe bearbeiten", "kind": "primary",
            "dangerLevel": "safe", "permission": "futtermittel.rations.update",
        }],
        "noWorkflowReason": "Parameter werden versioniert; Rationsfreigaben besitzen einen eigenen Lifecycle.",
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "objectPage", "density": "compact", "contextRail": "audit", "tableProfile": "audit",
        },
        "performance": {
            "initialPayloadBudgetKb": 40, "requiresLazyTabs": True,
            "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Tiergruppenparameter und ihre zeitliche Herkunft sicher pflegen.",
            "examplePrompts": ["Zeige die aktuelle Leistung der Tiergruppe.", "Welche Parameter wurden zuletzt geaendert?"],
            "sensitiveFields": ["business_id", "herd_id", "external_ref"],
            "testSelectors": {
                "screenRoot": "[data-testid='screen-agrar/feeding-group']",
                "primaryAction": "[data-action-kind='primary']",
            },
        },
    }


def build_agrar_feeding_plan_screen_definition() -> dict[str, Any]:
    """Native object page for immutable feeding-plan versions (FEED-PLAN-027)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/feeding-plan",
        "domain": "agrar",
        "mode": "detail",
        "title": "Fuetterungsplan",
        "subtitle": "Freigegebene Mischfolge, Chargenmengen und Rundungsnachweis",
        "adapter": {"type": "native", "sourceId": "agrar/feeding-plan", "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}"},
            {"key": "instructions", "endpoint": "/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}/instructions", "pageSize": 100},
        ],
        "tabs": [
            {
                "key": "plan", "label": "Plan und Gueltigkeit", "lazy": False, "keepAlive": True,
                "fields": [
                    {"key": "name", "label": "Plan", "type": "text"},
                    {"key": "plan_status", "label": "Ausfuehrungsstatus", "type": "text"},
                    {"key": "version_no", "label": "Planversion", "type": "number"},
                    {"key": "animal_count", "label": "Tierzahl", "type": "number"},
                    {"key": "valid_from", "label": "Gueltig ab", "type": "date"},
                    {"key": "valid_until", "label": "Gueltig bis", "type": "date"},
                    {"key": "dosing_step_kg", "label": "Dosierschritt kg", "type": "number"},
                    {"key": "rounding_mode", "label": "Rundungsmodus", "type": "text"},
                    {"key": "reason", "label": "Publikationsgrund", "type": "textarea"},
                ],
            },
            {
                "key": "mixing", "label": "Mischanweisung", "lazy": True, "keepAlive": True,
                "tables": [{
                    "key": "instructions", "label": "Dosierbare Mischfolge", "dataSourceKey": "instructions",
                    "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                    "columns": [
                        {"key": "sequence", "label": "Folge", "numeric": True, "sortable": True, "width": 80},
                        {"key": "feed_name", "label": "Futtermittel", "filterable": True, "width": 260},
                        {"key": "kg_fm_per_animal", "label": "kg FM/Tier", "numeric": True, "width": 130},
                        {"key": "raw_batch_kg", "label": "Charge roh kg", "numeric": True, "width": 140},
                        {"key": "target_batch_kg", "label": "Dosierziel kg", "numeric": True, "width": 140},
                        {"key": "rounding_delta_kg", "label": "Rundungsdelta kg", "numeric": True, "width": 150},
                    ],
                }],
            },
            {
                "key": "provenance", "label": "Herkunft und Audit", "lazy": True, "keepAlive": True,
                "fields": [
                    {"key": "id", "label": "Planversions-ID", "type": "text"},
                    {"key": "plan_id", "label": "Plan-ID", "type": "text"},
                    {"key": "source_ration_version_id", "label": "Quell-Rationsversion", "type": "text"},
                    {"key": "published_by", "label": "Publiziert von", "type": "text"},
                    {"key": "published_at", "label": "Publiziert am", "type": "datetime"},
                ],
            },
        ],
        "actions": [{
            "key": "print_plan", "label": "Drucken / als PDF speichern", "kind": "primary",
            "dangerLevel": "safe", "permission": "futtermittel.rations.read",
        }, {
            "key": "open_mobile", "label": "Mobile Stallansicht", "kind": "secondary",
            "dangerLevel": "safe", "permission": "futtermittel.rations.read",
        }],
        "noWorkflowReason": "Publizierte Planversionen sind unveraenderlich; Aenderungen entstehen als neue Publikation.",
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "objectPage", "density": "compact", "contextRail": "audit", "tableProfile": "audit",
        },
        "performance": {
            "initialPayloadBudgetKb": 32, "requiresLazyTabs": True, "requiresVirtualTables": True,
            "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Eine publizierte Mischanweisung sicher ausfuehren und ihre Herkunft nachweisen.",
            "examplePrompts": ["Welche Menge kommt als Naechstes?", "Ist dieser Plan noch aktuell?", "Warum wurde gerundet?"],
            "sensitiveFields": ["source_ration_version_id", "published_by"],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feeding-plan']", "primaryAction": "[data-action-kind='primary']"},
        },
    }


def build_agrar_feeding_reference_data_screen_definition() -> dict[str, Any]:
    """Native read model for canonical nutrient and unit definitions (FEED-CORE-017)."""
    return {
        "schemaVersion": 1,
        "id": "agrar/feeding-reference-data",
        "domain": "agrar",
        "mode": "list",
        "title": "Naehrstoffe und Einheiten",
        "subtitle": "Verbindliche Bezugsbasis, Dimension, Herkunft und Rundung",
        "adapter": {
            "type": "native", "sourceId": "agrar/feeding-reference-data", "temporary": False,
        },
        "dataSources": [
            {
                "key": "nutrients",
                "endpoint": "/api/v1/agrar/rations-optimization/reference-data/nutrients",
                "pageSize": 100,
                "staleTimeMs": 60_000,
            },
            {
                "key": "units",
                "endpoint": "/api/v1/agrar/rations-optimization/reference-data/units",
                "pageSize": 100,
                "staleTimeMs": 60_000,
            },
        ],
        "tables": [
            {
                "key": "nutrients", "label": "Naehrstoffdefinitionen", "dataSourceKey": "nutrients",
                "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                "columns": [
                    {"key": "display_name", "label": "Naehrstoff", "sortable": True, "filterable": True, "width": 240},
                    {"key": "code", "label": "Code", "filterable": True, "width": 190},
                    {"key": "canonical_unit_code", "label": "Einheit", "filterable": True, "width": 140},
                    {"key": "default_basis", "label": "Bezugsbasis", "filterable": True, "width": 150},
                    {"key": "minimum_value", "label": "Minimum", "numeric": True, "width": 110},
                    {"key": "maximum_value", "label": "Maximum", "numeric": True, "width": 110},
                    {"key": "source", "label": "Herkunft", "filterable": True, "width": 180},
                    {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                ],
            },
            {
                "key": "units", "label": "Einheitendefinitionen", "dataSourceKey": "units",
                "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                "columns": [
                    {"key": "display_name", "label": "Einheit", "sortable": True, "filterable": True, "width": 220},
                    {"key": "code", "label": "Code", "filterable": True, "width": 150},
                    {"key": "dimension", "label": "Dimension", "filterable": True, "width": 190},
                    {"key": "factor_to_base", "label": "Basisfaktor", "numeric": True, "width": 140},
                    {"key": "precision", "label": "Nachkommastellen", "numeric": True, "width": 150},
                    {"key": "source", "label": "Herkunft", "filterable": True, "width": 180},
                    {"key": "revision", "label": "Revision", "numeric": True, "sortable": True, "width": 90},
                ],
            },
        ],
        "actions": [],
        "noWorkflowReason": "Referenzdaten werden hier revisionssicher gelesen; Aenderungen folgen einem separaten Governance-Prozess.",
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "listReport", "density": "compact", "contextRail": "audit", "tableProfile": "standard",
        },
        "performance": {
            "initialPayloadBudgetKb": 28, "requiresLazyTabs": True,
            "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Einheiten, Bezugsbasen und Naehrstoffherkunft fuer Berechnung und Beratung erklaerbar machen.",
            "examplePrompts": ["In welcher Einheit wird Rohprotein bewertet?", "Welche Naehrstoffe sind auf TM bezogen?"],
            "sensitiveFields": [],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feeding-reference-data']"},
        },
    }


def build_agrar_feed_readiness_screen_definition() -> dict[str, Any]:
    """Native worklist for inventory, lab-analysis and price readiness."""
    return {
        "schemaVersion": 1, "id": "agrar/feed-readiness", "domain": "agrar", "mode": "list",
        "title": "Futter-Einsatzbereitschaft",
        "subtitle": "Reichweite, Laboranalyse und Preisstand der aktiven Rationen",
        "adapter": {"type": "native", "sourceId": "agrar/feed-readiness", "temporary": False},
        "dataSources": [{"key": "materials", "endpoint": "/api/v1/agrar/rations-optimization/readiness/materials", "pageSize": 100, "staleTimeMs": 30_000}],
        "tables": [{
            "key": "materials", "label": "Eingesetzte Futtermittel", "dataSourceKey": "materials",
            "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
            "columns": [
                {"key": "name", "label": "Futtermittel", "sortable": True, "filterable": True, "width": 220},
                {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 120},
                {"key": "daily_kg", "label": "Soll kg/Tag", "numeric": True, "width": 120},
                {"key": "stock_kg", "label": "Bestand kg", "numeric": True, "width": 120},
                {"key": "reach_days", "label": "Reichweite Tage", "numeric": True, "sortable": True, "width": 140},
                {"key": "analysis_date", "label": "Analyse", "renderKind": "date", "width": 130},
                {"key": "price_eur_t", "label": "EUR/t", "renderKind": "currency", "numeric": True, "width": 120},
                {"key": "price_valid_to", "label": "Preis gueltig bis", "renderKind": "date", "width": 150},
                {"key": "issue_summary", "label": "Handlungsbedarf", "width": 360},
            ],
        }],
        "actions": [
            {"key": "open_inventory", "label": "Bestaende pflegen", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"},
            {"key": "open_analyses", "label": "Analysen pruefen", "kind": "secondary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"},
        ],
        "noWorkflowReason": "Das Read-Model bewertet vorhandene Stamm-, Bestands-, Labor- und Preisdaten ohne sie zu duplizieren.",
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44, "floorplan": "worklist", "density": "compact", "contextRail": "copilot", "tableProfile": "inventory"},
        "performance": {"initialPayloadBudgetKb": 40, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice"},
        "agentContract": {"businessPurpose": "Engpaesse und Datenluecken vor Freigabe oder Fuetterungsstart erklaerbar erkennen.", "examplePrompts": ["Welche Futtermittel reichen weniger als 14 Tage?", "Welche Analyse oder welcher Preis ist abgelaufen?"], "sensitiveFields": ["price_eur_t"], "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feed-readiness']"}},
    }


def build_agrar_feed_controlling_screen_definition() -> dict[str, Any]:
    """Native daily target/actual feeding-control worklist."""
    return {
        "schemaVersion": 1, "id": "agrar/feed-controlling", "domain": "agrar", "mode": "list",
        "title": "Fuetterungscontrolling", "subtitle": "Soll-Ist-Trends je Tiergruppe und aktiver Rationsversion",
        "adapter": {"type": "native", "sourceId": "agrar/feed-controlling", "temporary": False},
        "dataSources": [{"key": "series", "endpoint": "/api/v1/agrar/rations-optimization/controlling/series", "pageSize": 100, "staleTimeMs": 30_000}],
        "tables": [{"key": "series", "label": "Tageswerte der letzten 30 Tage", "dataSourceKey": "series",
            "serverPagination": False, "pageSize": 100, "virtualized": True, "rowHeight": 48,
            "columns": [
                {"key": "observation_date", "label": "Tag", "renderKind": "date", "sortable": True, "width": 120},
                {"key": "group_name", "label": "Tiergruppe", "sortable": True, "filterable": True, "width": 200},
                {"key": "source", "label": "Quelle", "filterable": True, "width": 120},
                {"key": "actual_dmi_kg_cow", "label": "Aufnahme Ist kg", "numeric": True, "width": 140},
                {"key": "dmi_deviation_kg", "label": "Abw. Aufnahme", "numeric": True, "width": 140},
                {"key": "actual_cost_eur_cow", "label": "Kosten Ist", "renderKind": "currency", "numeric": True, "width": 125},
                {"key": "cost_deviation_eur", "label": "Abw. Kosten", "renderKind": "currency", "numeric": True, "width": 125},
                {"key": "actual_milk_kg_cow", "label": "Milch kg", "numeric": True, "width": 110},
                {"key": "actual_ecm_kg_cow", "label": "ECM kg", "numeric": True, "width": 110},
                {"key": "nitrogen_efficiency_pct", "label": "N-Effizienz %", "numeric": True, "width": 140},
                {"key": "actual_methane_kg_cow", "label": "Methan kg", "numeric": True, "width": 120},
            ]}],
        "actions": [{"key": "record_observation", "label": "Tageswerte erfassen", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"}],
        "noWorkflowReason": "Idempotente Tagesbeobachtungen sind Messwerte; fachliche Freigaben bleiben am Rationslebenszyklus.",
        "layout": {"preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44, "floorplan": "worklist", "density": "compact", "contextRail": "copilot", "tableProfile": "standard"},
        "performance": {"initialPayloadBudgetKb": 48, "requiresLazyTabs": True, "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice"},
        "agentContract": {"businessPurpose": "Aufnahme, Kosten, Milch/ECM, Stickstoff und Methan je Tiergruppe im Zeitverlauf vergleichen.", "examplePrompts": ["Welche Gruppe weicht bei der Aufnahme ab?", "Wie entwickeln sich ECM und Futterkosten?"], "sensitiveFields": ["actual_cost_eur_cow"], "testSelectors": {"screenRoot": "[data-testid='screen-agrar/feed-controlling']"}},
    }


def build_agrar_ration_detail_screen_definition() -> dict[str, Any]:
    """Native object page for one ration and its immutable versions."""
    return {
        "schemaVersion": 1,
        "id": "agrar/ration",
        "domain": "agrar",
        "mode": "detail",
        "title": "Rationsfreigabe",
        "subtitle": "Version, Freigabe, Fuetterungsbeginn und Audit",
        "adapter": {"type": "native", "sourceId": "agrar/ration", "temporary": False},
        "dataSources": [
            {"key": "entity", "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}"},
            {"key": "versions", "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/versions", "pageSize": 50},
            {"key": "audit", "endpoint": "/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/audit", "pageSize": 100},
        ],
        "fields": [
            {"key": "name", "label": "Ration", "type": "text", "readOnly": True},
            {"key": "group_name", "label": "Tiergruppe", "type": "text", "readOnly": True},
            {"key": "latest_version_no", "label": "Aktuelle Version", "type": "number", "readOnly": True},
            {"key": "latest_status", "label": "Status", "type": "text", "readOnly": True},
            {"key": "latest_feeding_start", "label": "Fuetterungsbeginn", "type": "datetime", "readOnly": True},
            {"key": "latest_readiness_status", "label": "Bestandsreife", "type": "text", "readOnly": True},
            {"key": "latest_readiness_blockers", "label": "Blockierende Befunde", "type": "number", "readOnly": True},
            {"key": "latest_readiness_warnings", "label": "Hinweise", "type": "number", "readOnly": True},
        ],
        "tabs": [
            {
                "key": "versions", "label": "Versionen", "lazy": False, "keepAlive": True,
                "tables": [{
                    "key": "versions", "label": "Unveraenderliche Fachstaende", "dataSourceKey": "versions",
                    "serverPagination": True, "pageSize": 50, "virtualized": True, "rowHeight": 48,
                    "columns": [
                        {"key": "version_no", "label": "Version", "numeric": True, "sortable": True, "width": 90},
                        {"key": "status", "label": "Status", "renderKind": "status", "filterable": True, "width": 130},
                        {"key": "source", "label": "Quelle", "width": 110},
                        {"key": "created_by", "label": "Erstellt durch", "width": 150},
                        {"key": "created_at", "label": "Erstellt", "renderKind": "datetime", "width": 180},
                        {"key": "feeding_start", "label": "Fuetterungsbeginn", "renderKind": "datetime", "width": 180},
                    ],
                }],
            },
            {
                "key": "audit", "label": "Audit", "lazy": True, "keepAlive": False,
                "tables": [{
                    "key": "audit", "label": "Status- und Versionsereignisse", "dataSourceKey": "audit",
                    "serverPagination": True, "pageSize": 100, "virtualized": True, "rowHeight": 48,
                    "columns": [
                        {"key": "occurred_at", "label": "Zeit", "renderKind": "datetime", "sortable": True, "width": 180},
                        {"key": "event_type", "label": "Ereignis", "filterable": True, "width": 150},
                        {"key": "from_status", "label": "Von", "renderKind": "status", "width": 110},
                        {"key": "to_status", "label": "Nach", "renderKind": "status", "width": 110},
                        {"key": "actor", "label": "Akteur", "width": 140},
                        {"key": "reason", "label": "Grund", "width": 300},
                    ],
                }],
            },
        ],
        "actions": [
            {"key": "submit_review", "label": "Zur Pruefung", "kind": "primary", "dangerLevel": "safe", "permission": "futtermittel.rations.update"},
            {"key": "approve", "label": "Freigeben", "kind": "workflow", "dangerLevel": "moderate", "permission": "futtermittel.rations.update", "requiresConfirmation": True, "humanApprovalRequired": True},
            {"key": "schedule", "label": "Fuetterungsbeginn planen", "kind": "secondary", "dangerLevel": "moderate", "permission": "futtermittel.rations.update"},
            {"key": "activate", "label": "Jetzt aktivieren", "kind": "workflow", "dangerLevel": "moderate", "permission": "futtermittel.rations.update", "requiresConfirmation": True, "humanApprovalRequired": True},
            {"key": "retire", "label": "Fuetterung beenden", "kind": "secondary", "dangerLevel": "high", "permission": "futtermittel.rations.update", "requiresConfirmation": True, "auditReasonRequired": True},
            {"key": "archive", "label": "Archivieren", "kind": "danger", "dangerLevel": "high", "permission": "futtermittel.rations.update", "requiresConfirmation": True, "auditReasonRequired": True},
        ],
        "workflow": {"processKey": "ration-version-lifecycle", "auditRequired": True, "evidenceRequired": False},
        "layout": {
            "preferredMode": "desktopDense", "mobileMode": "mobileStack", "touchTargetPx": 44,
            "floorplan": "objectPage", "density": "compact", "contextRail": "combined", "tableProfile": "audit",
        },
        "performance": {
            "initialPayloadBudgetKb": 48, "requiresLazyTabs": True,
            "requiresVirtualTables": True, "lookupMinChars": 2, "bundleGroup": "agrar-feed-advice",
        },
        "agentContract": {
            "businessPurpose": "Eine Rationsversion pruefen, freigeben, terminieren, aktivieren oder revisionssicher beenden.",
            "examplePrompts": ["Warum wurde diese Ration freigegeben?", "Wann beginnt die Fuetterung dieser Version?"],
            "sensitiveFields": ["snapshot", "snapshot_checksum"],
            "testSelectors": {"screenRoot": "[data-testid='screen-agrar/ration']", "primaryAction": "[data-action-kind='primary']"},
        },
    }


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
    "agrar/feed-advice": build_agrar_feed_advice_screen_definition,
    "agrar/rations-lifecycle": build_agrar_rations_lifecycle_screen_definition,
    "agrar/feeding-businesses": build_agrar_feeding_businesses_screen_definition,
    "agrar/feeding-business": build_agrar_feeding_business_screen_definition,
    "agrar/feeding-group": build_agrar_feeding_group_screen_definition,
    "agrar/feeding-plan": build_agrar_feeding_plan_screen_definition,
    "agrar/feeding-reference-data": build_agrar_feeding_reference_data_screen_definition,
    "agrar/feed-readiness": build_agrar_feed_readiness_screen_definition,
    "agrar/feed-controlling": build_agrar_feed_controlling_screen_definition,
    "agrar/ration": build_agrar_ration_detail_screen_definition,
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
    "futtermittel/analysen": build_futtermittel_analysen_screen_definition,
    "futtermittel/analyse": build_futtermittel_analyse_screen_definition,
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
    "futtermittel/analysen": ["futteranalyse", "laboranalyse", "grundfutteranalyse", "lufa"],
    "futtermittel/analyse": ["analysepruefung", "laborbefund", "probe"],
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
    "agrar/feed-advice": "/portal/rationsoptimierung",
    "agrar/rations-lifecycle": "/portal/rationsoptimierung?view=rations",
    "agrar/feeding-businesses": "/portal/rationsoptimierung?view=businesses",
    "agrar/feeding-business": "/portal/rationsoptimierung?view=businesses",
    "agrar/feeding-group": "/portal/rationsoptimierung?view=rations",
    "agrar/feeding-plan": "/portal/rationsoptimierung?view=rations",
    "agrar/feeding-reference-data": "/portal/rationsoptimierung?view=reference-data",
    "agrar/feed-readiness": "/portal/rationsoptimierung?view=readiness",
    "agrar/feed-controlling": "/portal/rationsoptimierung?view=controlling",
    "agrar/ration": "/portal/rationsoptimierung?view=rations",
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
    "futtermittel/analysen": "/futtermittel/grundfutteranalysen",
    "futtermittel/analyse": "/futtermittel/grundfutteranalysen",
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
    contract.setdefault("sensitiveFields", [])
    contract.setdefault("synonyms", _AGENT_SYNONYMS.get(mask_id, []))
    _resolve_tile_routes(definition)
    _apply_season_profile(definition, today)
    return definition


# Public alias for inventory / governance scripts (SPEC-P1-04)
SCREEN_DEFINITION_BUILDERS = _SCREEN_DEFINITIONS
