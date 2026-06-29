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
            {"key": "dokumente", "label": "Dokumente", "lazy": True, "keepAlive": True},
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
        "tabs": [
            {"key": "kopf", "label": "Kopfdaten", "lazy": True, "keepAlive": True},
            {"key": "positionen", "label": "Positionen", "lazy": True, "keepAlive": True},
            {"key": "umsaetze", "label": "Umsaetze", "lazy": True, "keepAlive": True},
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary", "permission": "kontrakt.update"},
        ],
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


_SCREEN_DEFINITIONS: dict[str, Any] = {
    "crm/customer-360": build_crm_customer_360_screen_definition,
    "sales/sales-order": build_sales_order_screen_definition,
    "agrar/kontrakte": build_agrar_kontrakt_screen_definition,
}


def _build_rollout_screen_definition(
    *,
    screen_id: str,
    domain: str,
    title: str,
    subtitle: str,
    tabs: list[dict[str, Any]],
    summary_endpoint: str,
    budget_kb: int,
    bundle_group: str,
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "detail",
        "title": title,
        "subtitle": subtitle,
        "adapter": {
            "type": "native",
            "sourceId": screen_id,
            "temporary": False,
        },
        "summaryEndpoint": summary_endpoint,
        "tabs": tabs,
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "kind": "primary"},
        ],
        "layout": {
            "preferredMode": "desktopDense",
            "mobileMode": "mobileStack",
            "touchTargetPx": 44,
        },
        "performance": {
            "initialPayloadBudgetKb": budget_kb,
            "requiresLazyTabs": True,
            "requiresVirtualTables": True,
            "lookupMinChars": 2,
            "bundleGroup": bundle_group,
        },
    }


def _rollout_tab_defs(keys: list[str]) -> list[dict[str, Any]]:
    labels = {
        "kopf": "Kopfdaten",
        "details": "Details",
        "bestand": "Bestand",
        "bewegungen": "Bewegungen",
        "positionen": "Positionen",
        "freigabe": "Freigabe",
        "ausgleich": "Ausgleich",
        "kommunikation": "Kommunikation",
        "kontakte": "Kontakte",
        "bestellungen": "Bestellungen",
        "aktivitaeten": "Aktivitaeten",
        "angebote": "Angebote",
        "dokumente": "Dokumente",
        "abzuege": "Abzuege",
        "zahlungen": "Zahlungen",
    }
    return [
        {"key": key, "label": labels.get(key, key.title()), "lazy": key != "kopf", "keepAlive": True}
        for key in keys
    ]


def build_rollout_screen_definitions() -> dict[str, Any]:
    result: dict[str, Any] = {}
    for spec in ROLLOUT_WAVES_42_51:
        result[spec.screen_id] = _build_rollout_screen_definition(
            screen_id=spec.screen_id,
            domain=spec.domain,
            title=spec.label,
            subtitle=f"Rollout Pilot {spec.screen_id}",
            tabs=_rollout_tab_defs(list(spec.available_tabs)),
            summary_endpoint=f"/api/v1/mask-rollouts/{spec.screen_id}/{{entity_id}}/screen-summary",
            budget_kb=spec.budget_kb,
            bundle_group=spec.domain,
        )
    return result


for _spec in ROLLOUT_WAVES_42_51:
    _sid = _spec.screen_id

    def _make_builder(screen_id: str = _sid):
        def _builder() -> dict[str, Any]:
            return build_rollout_screen_definitions()[screen_id]

        return _builder

    _SCREEN_DEFINITIONS[_sid] = _make_builder()


def get_screen_definition(mask_id: str) -> dict[str, Any] | None:
    builder = _SCREEN_DEFINITIONS.get(mask_id)
    if builder is None:
        return None
    return builder()
