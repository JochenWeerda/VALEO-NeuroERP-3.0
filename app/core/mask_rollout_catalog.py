"""Catalog of batch mask rollout pilots (Waves 42–51)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MaskRolloutSpec:
    screen_id: str
    domain: str
    label: str
    api_prefix: str
    entity_param: str
    available_tabs: tuple[str, ...]
    lazy_tabs: tuple[str, ...]
    budget_kb: int = 56
    permission: str | None = None
    registry_mask_id: str | None = None


ROLLOUT_WAVES_42_51: tuple[MaskRolloutSpec, ...] = (
    MaskRolloutSpec(
        screen_id="lager/stock-movement",
        domain="lager",
        label="Lagerbewegung",
        api_prefix="/api/v1/inventory/stock-movements",
        entity_param="movement_id",
        available_tabs=("kopf", "details"),
        lazy_tabs=("details",),
        budget_kb=48,
        registry_mask_id="lager/stock-movement",
    ),
    MaskRolloutSpec(
        screen_id="lager/article-stock",
        domain="lager",
        label="Artikelbestand",
        api_prefix="/api/v1/articles",
        entity_param="article_id",
        available_tabs=("kopf", "bestand", "bewegungen"),
        lazy_tabs=("bestand", "bewegungen"),
        budget_kb=52,
        registry_mask_id="lager/article-stock",
    ),
    MaskRolloutSpec(
        screen_id="finance/ap-invoice",
        domain="finance",
        label="Eingangsrechnung",
        api_prefix="/api/v1/finance/ap/invoices",
        entity_param="invoice_id",
        available_tabs=("kopf", "positionen", "freigabe"),
        lazy_tabs=("positionen", "freigabe"),
        budget_kb=56,
        permission="finance.ap.read",
        registry_mask_id="finance/ap-invoice-form",
    ),
    MaskRolloutSpec(
        screen_id="finance/ar-open-item",
        domain="finance",
        label="OP Debitor",
        api_prefix="/api/v1/finance/open-items",
        entity_param="op_id",
        available_tabs=("kopf", "ausgleich"),
        lazy_tabs=("ausgleich",),
        budget_kb=48,
        registry_mask_id="finance/op-debitoren",
    ),
    MaskRolloutSpec(
        screen_id="einkauf/purchase-order",
        domain="einkauf",
        label="Bestellung",
        api_prefix="/api/v1/einkauf/bestellungen",
        entity_param="bestellung_id",
        available_tabs=("kopf", "positionen", "kommunikation"),
        lazy_tabs=("positionen", "kommunikation"),
        budget_kb=56,
        registry_mask_id="einkauf/bestellung-stamm",
    ),
    MaskRolloutSpec(
        screen_id="einkauf/supplier",
        domain="einkauf",
        label="Lieferant",
        api_prefix="/api/v1/einkauf/lieferanten",
        entity_param="lieferant_id",
        available_tabs=("kopf", "bestellungen", "kontakte"),
        lazy_tabs=("bestellungen", "kontakte"),
        budget_kb=48,
        registry_mask_id="einkauf/lieferanten-stamm",
    ),
    MaskRolloutSpec(
        screen_id="crm/opportunity",
        domain="crm",
        label="Opportunity",
        api_prefix="/api/v1/crm/opportunities",
        entity_param="opportunity_id",
        available_tabs=("kopf", "aktivitaeten", "angebote"),
        lazy_tabs=("aktivitaeten", "angebote"),
        budget_kb=48,
        registry_mask_id="crm/opportunity-detail",
    ),
    MaskRolloutSpec(
        screen_id="sales/delivery-note",
        domain="sales",
        label="Lieferschein",
        api_prefix="/api/v1/sales/delivery-notes",
        entity_param="ls_id",
        available_tabs=("kopf", "positionen", "dokumente"),
        lazy_tabs=("positionen", "dokumente"),
        budget_kb=52,
        registry_mask_id="sales/delivery-note",
    ),
    MaskRolloutSpec(
        screen_id="agrar/harvest-settlement",
        domain="agrar",
        label="Ernte-Abrechnung",
        api_prefix="/api/v1/agrar/settlements",
        entity_param="settlement_id",
        available_tabs=("kopf", "abzuege", "positionen"),
        lazy_tabs=("abzuege", "positionen"),
        budget_kb=52,
        registry_mask_id="agrar/harvest-settlement",
    ),
    MaskRolloutSpec(
        screen_id="finance/payment-run",
        domain="finance",
        label="Zahlungslauf",
        api_prefix="/api/v1/finance/payment-runs",
        entity_param="run_id",
        available_tabs=("kopf", "zahlungen"),
        lazy_tabs=("zahlungen",),
        budget_kb=52,
        permission="finance.payment_run.read",
        registry_mask_id="finance/zahlungslauf-kreditoren",
    ),
)


def get_rollout_spec(screen_id: str) -> MaskRolloutSpec | None:
    normalized = screen_id.strip("/")
    for spec in ROLLOUT_WAVES_42_51:
        if spec.screen_id == normalized:
            return spec
    return None


def all_rollout_screen_ids() -> list[str]:
    return [spec.screen_id for spec in ROLLOUT_WAVES_42_51]
