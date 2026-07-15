from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]


def test_analysis_status_machine_and_release_readiness() -> None:
    from app.agrar.rations.feed_analysis import AnalysisStatus, transition_analysis

    assert transition_analysis(AnalysisStatus.UPLOADED, AnalysisStatus.MAPPED, []) == AnalysisStatus.MAPPED
    assert transition_analysis(AnalysisStatus.MAPPED, AnalysisStatus.DRAFT, []) == AnalysisStatus.DRAFT
    assert transition_analysis(AnalysisStatus.VALIDATED, AnalysisStatus.RELEASED, []) == AnalysisStatus.RELEASED
    with pytest.raises(ValueError, match="Statuswechsel"):
        transition_analysis(AnalysisStatus.UPLOADED, AnalysisStatus.RELEASED, [])
    with pytest.raises(ValueError, match="Blocker"):
        transition_analysis(
            AnalysisStatus.VALIDATED,
            AnalysisStatus.RELEASED,
            [{"severity": "blocker", "code": "missing-dm"}],
        )


def test_analysis_value_preserves_original_and_marks_estimates() -> None:
    from app.agrar.rations.feed_analysis import normalize_analysis_value

    measured = normalize_analysis_value(
        nutrient_code="crude_protein",
        original_value=Decimal("8.1"),
        original_unit_code="percent",
        canonical_unit_code="g_per_kg",
        basis="dry_matter",
        value_status="measured",
    )
    assert measured.original_value == Decimal("8.1")
    assert measured.original_unit_code == "percent"
    assert measured.canonical_value == Decimal("81.0")
    assert measured.estimated is False

    estimated = normalize_analysis_value(
        nutrient_code="metabolizable_energy",
        original_value=Decimal("10.7"),
        original_unit_code="MJ_per_kg",
        canonical_unit_code="MJ_per_kg",
        basis="dry_matter",
        value_status="estimated",
    )
    assert estimated.estimated is True
    with pytest.raises(ValueError, match="Status"):
        normalize_analysis_value("crude_protein", Decimal("1"), "percent", "g_per_kg", "dry_matter", "unknown")


def test_analysis_plausibility_never_turns_missing_values_into_zero() -> None:
    from app.agrar.rations.feed_analysis import evaluate_analysis

    findings = evaluate_analysis([
        {"nutrient_code": "dry_matter", "canonical_value": None},
        {"nutrient_code": "crude_protein", "canonical_value": Decimal("1200")},
    ])
    by_code = {finding["code"]: finding for finding in findings}
    assert by_code["missing-dry-matter"]["severity"] == "blocker"
    assert by_code["crude-protein-out-of-range"]["severity"] == "warning"
    assert all(finding.get("value") != 0 for finding in findings)


def test_feed_analysis_migration_is_additive_versioned_and_single_head() -> None:
    source = (ROOT / "alembic" / "versions" / "feed_core_feed_analyses_20260715.py").read_text(encoding="utf-8")
    assert 'down_revision = "feed_core_feed_catalog_20260715"' in source
    assert "ALTER TABLE domain_shared.grundfutter_analysen" in source
    for table in ("feeding_feed_analysis_values", "feeding_feed_analysis_revisions", "feeding_feed_analysis_findings"):
        assert table in source
    assert "WHERE status = 'released' AND is_active" in source
    assert "tenant_id, feed_id, scope_code" in source
    assert "guard_immutable_feeding_feed_analysis_revision" in source


def test_feed_analysis_api_and_native_screen_contracts() -> None:
    from app.api.v1.endpoints.feeding_feed_analyses import AnalysisDetailOut, AnalysisRevisionOut, router
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    response_models = {
        (route.path, next(iter(route.methods or []))): route.response_model
        for route in router.routes if hasattr(route, "response_model")
    }
    assert response_models[("/feed-analyses/{analysis_id}", "GET")] is AnalysisDetailOut
    assert response_models[("/feed-analyses/{analysis_id}/history", "GET")] == list[AnalysisRevisionOut]
    definition = get_screen_definition("futtermittel/analysen")
    assert definition is not None
    endpoints = {source["key"]: source["endpoint"] for source in definition["dataSources"]}
    assert endpoints["list"].endswith("/feed-analyses")
    assert _check_readiness(definition)["generatorReady"] is True
    detail = get_screen_definition("futtermittel/analyse")
    assert detail is not None
    detail_endpoints = {source["key"]: source["endpoint"] for source in detail["dataSources"]}
    assert detail_endpoints["entity"].endswith("/feed-analyses/{entity_id}")
    assert detail_endpoints["values"].endswith("/{entity_id}/values")
    assert _check_readiness(detail)["generatorReady"] is True
    aliases = (ROOT / "packages" / "frontend-web" / "src" / "app" / "route-aliases.json").read_text(encoding="utf-8")
    assert 'futtermittel/grundfutteranalysen/:id' in aliases
    assert 'grundfutteranalyse-native' in aliases
