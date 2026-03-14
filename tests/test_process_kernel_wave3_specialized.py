"""
Wave-3 Specialized Domain Models — Contract Tests (AP3–AP6)
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# AP3: IoT Telemetry
# ---------------------------------------------------------------------------

from app.core.iot_telemetry import (
    DeviceType,
    DeviceStatus,
    TelemetryReading,
    DeviceManifest,
    TelemetryAggregation,
)


def test_telemetry_reading_has_schema_version():
    reading = TelemetryReading(
        device_id="d1",
        device_type=DeviceType.weighbridge,
        tenant_id="t1",
        timestamp="2026-03-11T08:00:00Z",
        value=42.5,
        unit="t",
    )
    assert reading.schema_version == 1


def test_device_manifest_has_process_context():
    manifest = DeviceManifest(
        device_id="d2",
        device_type=DeviceType.silo_sensor,
        tenant_id="t1",
        location="Silo 3 Nord",
        status=DeviceStatus.online,
        process_context="harvest_acceptance",
    )
    assert manifest.process_context == "harvest_acceptance"


def test_telemetry_aggregation_has_stats_fields():
    agg = TelemetryAggregation(
        device_id="d1",
        tenant_id="t1",
        period_from="2026-03-01T00:00:00Z",
        period_to="2026-03-11T00:00:00Z",
        readings_count=100,
        avg_value=14.2,
        min_value=12.0,
        max_value=16.5,
        unit="%",
    )
    assert agg.min_value == 12.0
    assert agg.max_value == 16.5
    assert agg.avg_value == 14.2


def test_device_manifest_default_schema_version():
    manifest = DeviceManifest(
        device_id="d3",
        device_type=DeviceType.moisture_sensor,
        tenant_id="t1",
        location="Lager A",
        status=DeviceStatus.calibrating,
    )
    assert manifest.schema_version == 1
    assert manifest.calibration_due is None


# ---------------------------------------------------------------------------
# AP4: Pricing Governance
# ---------------------------------------------------------------------------

from app.core.pricing_governance import (
    PricingSourceType,
    PricingSourceReliability,
    PricingSourceManifest,
    PricingGovernancePolicy,
    build_default_pricing_sources,
)


def test_pricing_source_manifest_manual_override_requires_approval():
    sources = build_default_pricing_sources()
    manual = next(s for s in sources if s.source_id == "manual_override")
    assert manual.requires_approval_for_use is True
    assert manual.reliability == PricingSourceReliability.override


def test_pricing_governance_policy_get_source_returns_none_for_unknown():
    policy = PricingGovernancePolicy(
        tenant_id="t1",
        sources=build_default_pricing_sources(),
    )
    result = policy.get_source("does_not_exist")
    assert result is None


def test_default_pricing_sources_includes_matif():
    sources = build_default_pricing_sources()
    source_ids = [s.source_id for s in sources]
    assert "MATIF" in source_ids
    matif = next(s for s in sources if s.source_id == "MATIF")
    assert matif.source_type == PricingSourceType.exchange
    assert matif.reliability == PricingSourceReliability.authoritative


def test_pricing_governance_policy_get_source_returns_source():
    policy = PricingGovernancePolicy(
        tenant_id="t1",
        sources=build_default_pricing_sources(),
    )
    matif = policy.get_source("MATIF")
    assert matif is not None
    assert matif.source_id == "MATIF"


# ---------------------------------------------------------------------------
# AP5: Quality-Lot Binding
# ---------------------------------------------------------------------------

from app.core.quality_lot_binding import (
    LotQualityProfile,
    QualityPriceDeductionRule,
    QualityReleaseDecision,
    compute_price_deduction,
)


def test_lot_quality_profile_has_schema_version():
    profile = LotQualityProfile(
        lot_id="L001",
        tenant_id="t1",
    )
    assert profile.schema_version == 1
    assert profile.approval_status == "pending"
    assert profile.price_deduction_pct == 0.0


def test_compute_price_deduction_applies_rule_for_moisture():
    profile = LotQualityProfile(
        lot_id="L001",
        tenant_id="t1",
        moisture_pct=16.0,
    )
    rule = QualityPriceDeductionRule(
        rule_id="R1",
        parameter="moisture_pct",
        threshold=14.0,
        deduction_pct_per_unit=0.5,
        max_deduction_pct=10.0,
    )
    deduction = compute_price_deduction(profile, [rule])
    # (16.0 - 14.0) * 0.5 = 1.0
    assert deduction == pytest.approx(1.0)


def test_compute_price_deduction_respects_max():
    profile = LotQualityProfile(
        lot_id="L002",
        tenant_id="t1",
        moisture_pct=30.0,
    )
    rule = QualityPriceDeductionRule(
        rule_id="R2",
        parameter="moisture_pct",
        threshold=14.0,
        deduction_pct_per_unit=1.0,
        max_deduction_pct=5.0,  # cap at 5%
    )
    deduction = compute_price_deduction(profile, [rule])
    # raw = (30 - 14) * 1.0 = 16.0, but capped at 5.0
    assert deduction == pytest.approx(5.0)


def test_quality_release_decision_has_deduction_field():
    decision = QualityReleaseDecision(
        lot_id="L001",
        protocol_id="P001",
        decision="approve",
        decided_by="user@example.com",
        decided_at="2026-03-11T10:00:00Z",
        price_deduction_applied_pct=1.0,
    )
    assert decision.price_deduction_applied_pct == 1.0
    assert decision.schema_version == 1


# ---------------------------------------------------------------------------
# AP6: Import Pipeline
# ---------------------------------------------------------------------------

from app.core.import_pipeline import (
    ImportFormat,
    ImportStage,
    ImportValidationResult,
    ImportPipelineJob,
    ImportPipelineConfig,
)


def test_import_pipeline_job_has_schema_version():
    job = ImportPipelineJob(
        job_id="J001",
        tenant_id="t1",
        import_format=ImportFormat.csv,
        domain="finance",
        entity_type="ap_invoice",
        created_at="2026-03-11T08:00:00Z",
        updated_at="2026-03-11T08:00:00Z",
    )
    assert job.schema_version == 1


def test_import_pipeline_job_default_stage_is_received():
    job = ImportPipelineJob(
        job_id="J002",
        tenant_id="t1",
        import_format=ImportFormat.edifact,
        domain="agrar",
        entity_type="harvest_acceptance",
        created_at="2026-03-11T08:00:00Z",
        updated_at="2026-03-11T08:00:00Z",
    )
    assert job.stage == ImportStage.received


def test_import_validation_result_counts_errors():
    result = ImportValidationResult(
        is_valid=False,
        error_count=3,
        warning_count=1,
        errors=["Row 1: missing field", "Row 2: invalid date", "Row 5: duplicate key"],
        warnings=["Row 3: optional field missing"],
    )
    assert result.error_count == 3
    assert result.warning_count == 1
    assert len(result.errors) == 3


def test_import_pipeline_config_require_approval_before_post_default_true():
    config = ImportPipelineConfig(
        config_id="C001",
        tenant_id="t1",
        import_format=ImportFormat.csv,
        domain="finance",
        entity_type="ap_invoice",
    )
    assert config.require_approval_before_post is True
    assert config.auto_post is False
