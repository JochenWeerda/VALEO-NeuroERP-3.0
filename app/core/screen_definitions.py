"""Native ScreenDefinition payloads for Universal Mask Generator."""

from __future__ import annotations

from typing import Any


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
        "tabs": [
            {"key": "masterdata", "label": "Stammdaten", "lazy": True, "keepAlive": True},
            {"key": "address", "label": "Adresse & Kommunikation", "lazy": True, "keepAlive": True},
            {"key": "contacts", "label": "Ansprechpartner", "lazy": True, "keepAlive": True},
            {"key": "finance", "label": "Finanzen", "lazy": True, "keepAlive": True},
            {"key": "auftraege", "label": "Auftraege", "lazy": True, "keepAlive": True},
            {"key": "aktivitaeten", "label": "Aktivitaeten", "lazy": True, "keepAlive": True},
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "crm.customer.update"},
            {"key": "create_activity", "label": "Aktivitaet anlegen", "kind": "secondary", "permission": "crm.activity.create"},
        ],
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
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True},
            {"key": "lieferung", "label": "Lieferung", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "sales.order.update"},
        ],
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


_SCREEN_DEFINITIONS: dict[str, Any] = {
    "crm/customer-360": build_crm_customer_360_screen_definition,
    "sales/sales-order": build_sales_order_screen_definition,
}


def get_screen_definition(mask_id: str) -> dict[str, Any] | None:
    builder = _SCREEN_DEFINITIONS.get(mask_id)
    if builder is None:
        return None
    return builder()
