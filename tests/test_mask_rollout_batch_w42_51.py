"""Unit tests for batch mask rollout screen-summary (Waves 42–51)."""

from __future__ import annotations

import pytest

from app.core.mask_rollout_catalog import ROLLOUT_WAVES_42_51, all_rollout_screen_ids, get_rollout_spec
from app.core.mask_screen_summary_common import build_screen_summary_payload, paginate_tab_items
from app.core.mask_classification import build_mask_registry
from app.core.screen_definitions import get_screen_definition


pytestmark = pytest.mark.unit


def test_rollout_catalog_has_ten_candidates() -> None:
    assert len(ROLLOUT_WAVES_42_51) == 10
    assert len(all_rollout_screen_ids()) == 10


def test_rollout_catalog_lookup() -> None:
    spec = get_rollout_spec("finance/ap-invoice")
    assert spec is not None
    assert spec.registry_mask_id == "finance/ap-invoice-form"


def test_build_screen_summary_payload_contract() -> None:
    payload = build_screen_summary_payload(
        screen_id="lager/stock-movement",
        entity_id="mov-1",
        tenant_id="tenant-1",
        title="BW-001",
        subtitle="in",
        summary={"quantity": 10.0},
        available_tabs=["kopf", "details"],
        api_prefix="/api/v1/inventory/stock-movements",
        lazy_tab_keys=["details"],
        entity_key="movement_id",
    )
    assert payload["schema_version"] == 1
    assert payload["movement_id"] == "mov-1"
    assert payload["tab_endpoints"]["details"].endswith("/mov-1/tabs/details")


def test_paginate_tab_items_filters_and_pages() -> None:
    items = [{"name": "Alpha"}, {"name": "Beta"}, {"name": "Gamma"}]
    page, total = paginate_tab_items(items, page=1, limit=2, q="alph")
    assert total == 1
    assert len(page) == 1


def test_paginate_tab_items_applies_filter_plan() -> None:
    items = [
        {"name": "Anna", "rolle": "Einkauf"},
        {"name": "Bernd", "rolle": "Logistik"},
        {"name": "Clara", "rolle": "Einkauf"},
    ]

    page, total = paginate_tab_items(
        items,
        page=1,
        limit=25,
        filter_plan={"rolle": {"op": "eq", "value": "Einkauf"}},
    )

    assert total == 2
    assert [row["name"] for row in page] == ["Anna", "Clara"]


@pytest.mark.parametrize("screen_id", all_rollout_screen_ids())
def test_rollout_screen_definitions_exist(screen_id: str) -> None:
    definition = get_screen_definition(screen_id)
    assert definition is not None
    assert definition["id"] == screen_id
    assert definition["performance"]["requiresLazyTabs"] is True


@pytest.mark.parametrize(
    "registry_mask_id",
    [
        "lager/stock-movement",
        "lager/article-stock",
        "finance/ap-invoice-form",
        "finance/op-debitoren",
        "einkauf/bestellung-stamm",
        "einkauf/lieferanten-stamm",
        "crm/opportunity-detail",
        "sales/delivery-note",
        "agrar/harvest-settlement",
        "finance/zahlungslauf-kreditoren",
    ],
)
def test_mask_registry_generator_ready_for_rollouts(registry_mask_id: str) -> None:
    registry = build_mask_registry()
    mask = registry.get(registry_mask_id)
    assert mask is not None
    assert mask.generator_ready is True
    assert mask.summary_endpoint is not None
    assert mask.requires_lazy_tabs is True
