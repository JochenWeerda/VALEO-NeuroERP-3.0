"""UIX-044 FilterPlan query contract tests."""

from __future__ import annotations

import asyncio
import json

import pytest

from app.api.v1.endpoints.mask_rollout_summaries import get_mask_rollout_tab_data
from app.core.mask_screen_summary_common import paginate_tab_items
from app.services.mask_rollout_summary_service import MaskRolloutSummaryService


pytestmark = pytest.mark.unit


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


@pytest.mark.parametrize("query_key", ["filter_plan", "filterPlan"])
def test_rollout_tab_endpoint_accepts_filter_plan_query_aliases(
    monkeypatch: pytest.MonkeyPatch,
    query_key: str,
) -> None:
    captured: dict[str, object] = {}

    def fake_build_tab_data(
        self: MaskRolloutSummaryService,
        screen_id: str,
        entity_id: str,
        tab_key: str,
        *,
        page: int = 1,
        limit: int = 25,
        q: str | None = None,
        sort: str | None = None,
        sort_dir: str | None = None,
        filter_plan: dict | None = None,
    ) -> dict:
        captured["screen_id"] = screen_id
        captured["filter_plan"] = filter_plan
        return {
            "tab_key": tab_key,
            "table_key": "supplier_contacts",
            "items": [{"name": "Anna", "rolle": "Einkauf"}],
            "page": page,
            "limit": limit,
            "total": 1,
        }

    monkeypatch.setattr(MaskRolloutSummaryService, "build_tab_data", fake_build_tab_data)

    kwargs = {"filter_plan": None, "filter_plan_legacy": None}
    if query_key == "filter_plan":
        kwargs["filter_plan"] = json.dumps({"rolle": {"op": "eq", "value": "Einkauf"}})
    else:
        kwargs["filter_plan_legacy"] = json.dumps({"rolle": {"op": "eq", "value": "Einkauf"}})

    response = asyncio.run(
        get_mask_rollout_tab_data(
            screen_id="einkauf/supplier",
            entity_id="supplier-1",
            tab_key="kontakte",
            db=None,
            tenant_id="00000000-0000-0000-0000-000000000001",
            **kwargs,
        )
    )

    assert response["total"] == 1
    assert captured["screen_id"] == "einkauf/supplier"
    assert captured["filter_plan"] == {"rolle": {"op": "eq", "value": "Einkauf"}}
