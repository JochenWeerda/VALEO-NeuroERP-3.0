from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def test_feed_catalog_cross_field_rules() -> None:
    from app.agrar.rations.feed_catalog import FeedApprovalStatus, FeedKind, validate_feed

    result = validate_feed(
        feed_kind=FeedKind.FORAGE,
        approval_status=FeedApprovalStatus.APPROVED,
        valid_from="2026-07-01",
        valid_until="2026-12-31",
        dry_matter_pct=Decimal("35"),
    )
    assert result["feed_kind"] == "forage"
    with pytest.raises(ValueError, match="Trockenmasse"):
        validate_feed(FeedKind.CONCENTRATE, FeedApprovalStatus.DRAFT, None, None, Decimal("101"))
    with pytest.raises(ValueError, match="Gueltigkeit"):
        validate_feed(FeedKind.MINERAL, FeedApprovalStatus.APPROVED, "2026-08-01", "2026-07-01", None)


def test_persisted_values_and_legacy_fields_are_solver_golden_equivalent() -> None:
    from app.agrar.rations.feed_catalog import build_solver_feed
    from app.agrar.rations.solver.feed import Feed

    head = {
        "id": "feed-1", "name": "Maissilage", "art": "Grundfutter",
        "feed_kind": "forage", "trockensubstanz": Decimal("35"),
        "protein": Decimal("8.1"), "energie": Decimal("10.7"),
        "preis_pro_t": Decimal("42"),
    }
    legacy = Feed.from_dict(build_solver_feed(head, []))
    flexible = Feed.from_dict(build_solver_feed(head, [
        {"nutrient_code": "dry_matter", "value": Decimal("35"), "unit_code": "percent"},
        {"nutrient_code": "crude_protein", "value": Decimal("81"), "unit_code": "g_per_kg"},
        {"nutrient_code": "metabolizable_energy", "value": Decimal("10.7"), "unit_code": "MJ_per_kg"},
    ]))
    assert flexible.dm_frac == legacy.dm_frac == 0.35
    assert flexible.cp == legacy.cp == 81.0
    assert flexible.me == legacy.me == 10.7
    assert flexible.price == legacy.price == pytest.approx(0.12)
    assert flexible.forage is legacy.forage is True


def test_feed_catalog_migration_reuses_existing_head_and_versions_children() -> None:
    migration = ROOT / "alembic" / "versions" / "feed_core_feed_catalog_20260715.py"
    source = migration.read_text(encoding="utf-8")
    assert 'down_revision = "feed_core_reference_data_20260715"' in source
    assert "ALTER TABLE domain_shared.futtermittel_einzelfutter" in source
    for table in ("feeding_feed_products", "feeding_feed_reference_values", "feeding_feed_revisions"):
        assert table in source
    assert "guard_immutable_feeding_feed_revision" in source
    assert "ON CONFLICT" in source


def test_feed_catalog_api_contract_is_typed_and_versioned() -> None:
    from app.api.v1.endpoints.feeding_feed_catalog import (
        FeedDetailOut,
        FeedRevisionOut,
        FeedUpdateIn,
        router,
    )

    response_models = {
        (route.path, next(iter(route.methods or []))): route.response_model
        for route in router.routes if hasattr(route, "response_model")
    }
    assert response_models[("/feed-catalog/feeds/{feed_id}", "GET")] is FeedDetailOut
    assert response_models[("/feed-catalog/feeds/{feed_id}", "PATCH")] is FeedDetailOut
    assert response_models[("/feed-catalog/feeds/{feed_id}/history", "GET")] == list[FeedRevisionOut]
    with pytest.raises(Exception):
        FeedUpdateIn(expected_revision=0, reason="x")


def test_existing_feed_object_page_uses_real_catalog_sources() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("futtermittel/einzelfuttermittel")
    assert definition is not None
    endpoints = {source["key"]: source["endpoint"] for source in definition["dataSources"]}
    assert endpoints["entity"] == "/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}"
    assert endpoints["naehrstoffe"].endswith("/{entity_id}/reference-values")
    assert endpoints["preise"].endswith("/{entity_id}/products")
    assert _check_readiness(definition)["generatorReady"] is True
