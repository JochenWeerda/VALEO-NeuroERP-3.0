"""Wave 88 — Unit-Tests fuer gap_progress, geo_pipeline, compat_helpers,
command_handlers_procurement (pure domain functions)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# gap_progress — create_pipeline_job, get_pipeline_progress  (in-memory job store)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_create_pipeline_job_returns_job_id() -> None:
    from app.services.gap_progress import create_pipeline_job
    job_id = create_pipeline_job(2024)
    assert isinstance(job_id, str)
    assert len(job_id) > 0


@pytest.mark.unit
def test_create_pipeline_job_id_is_uuid_format() -> None:
    from app.services.gap_progress import create_pipeline_job
    job_id = create_pipeline_job(2024)
    parts = job_id.split("-")
    assert len(parts) == 5


@pytest.mark.unit
def test_get_pipeline_progress_returns_job() -> None:
    from app.services.gap_progress import create_pipeline_job, get_pipeline_progress
    job_id = create_pipeline_job(2023)
    progress = get_pipeline_progress(job_id)
    assert progress is not None
    assert progress["job_id"] == job_id


@pytest.mark.unit
def test_get_pipeline_progress_year_stored() -> None:
    from app.services.gap_progress import create_pipeline_job, get_pipeline_progress
    job_id = create_pipeline_job(2022)
    progress = get_pipeline_progress(job_id)
    assert progress["year"] == 2022


@pytest.mark.unit
def test_get_pipeline_progress_initial_status() -> None:
    from app.services.gap_progress import create_pipeline_job, get_pipeline_progress
    job_id = create_pipeline_job(2024)
    progress = get_pipeline_progress(job_id)
    assert progress["status"] == "running"
    assert progress["progress"] == 0


@pytest.mark.unit
def test_get_pipeline_progress_unknown_id_returns_none() -> None:
    from app.services.gap_progress import get_pipeline_progress
    result = get_pipeline_progress("00000000-0000-0000-0000-nonexistent")
    assert result is None


@pytest.mark.unit
def test_create_pipeline_job_has_required_keys() -> None:
    from app.services.gap_progress import create_pipeline_job, get_pipeline_progress
    job_id = create_pipeline_job(2024, total_steps=10)
    progress = get_pipeline_progress(job_id)
    for key in ("job_id", "year", "current_step", "progress", "total_steps", "status"):
        assert key in progress


# ---------------------------------------------------------------------------
# geo_pipeline — normalize_name  (pure string normalization)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_geo_normalize_name_lowercases() -> None:
    from app.services.geo_pipeline import normalize_name
    result = normalize_name("AGRAR HANDELS AG")
    assert result == result.lower()


@pytest.mark.unit
def test_geo_normalize_name_converts_umlauts() -> None:
    from app.services.geo_pipeline import normalize_name
    result = normalize_name("Müller GmbH")
    assert "ue" in result or "mueller" in result
    assert "ü" not in result


@pytest.mark.unit
def test_geo_normalize_name_removes_legal_form() -> None:
    from app.services.geo_pipeline import normalize_name
    result = normalize_name("Agrar GmbH")
    assert "gmbh" not in result


@pytest.mark.unit
def test_geo_normalize_name_none_returns_empty() -> None:
    from app.services.geo_pipeline import normalize_name
    result = normalize_name(None)
    assert result == ""


@pytest.mark.unit
def test_geo_normalize_name_empty_returns_empty() -> None:
    from app.services.geo_pipeline import normalize_name
    result = normalize_name("")
    assert result == ""


# ---------------------------------------------------------------------------
# compat_helpers — safe_float, cache_key  (pure utility functions)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compat_safe_float_numeric() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float(3.14) == pytest.approx(3.14)


@pytest.mark.unit
def test_compat_safe_float_none_returns_zero() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float(None) == 0.0


@pytest.mark.unit
def test_compat_safe_float_invalid_string_returns_zero() -> None:
    from app.services.compat_helpers import safe_float
    assert safe_float("not_a_number") == 0.0


@pytest.mark.unit
def test_compat_cache_key_basic() -> None:
    from app.services.compat_helpers import cache_key
    key = cache_key("orders", "ORD-001", "T001")
    assert key.startswith("compat:")
    assert "orders" in key
    assert "ORD-001" in key


@pytest.mark.unit
def test_compat_cache_key_excludes_none() -> None:
    from app.services.compat_helpers import cache_key
    key = cache_key("orders", None, "T001")
    assert "None" not in key


# ---------------------------------------------------------------------------
# command_handlers_procurement — build_procurement_superglue_rollout
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_procurement_superglue_rollout_has_required_keys() -> None:
    from app.services.command_handlers_procurement import build_procurement_superglue_rollout
    result = build_procurement_superglue_rollout("T001")
    for key in ("provider_key", "tenant_id", "domain_key", "rollout", "schema_version"):
        assert key in result


@pytest.mark.unit
def test_build_procurement_superglue_rollout_domain_key() -> None:
    from app.services.command_handlers_procurement import build_procurement_superglue_rollout
    result = build_procurement_superglue_rollout("T001")
    assert result["domain_key"] == "procurement"


@pytest.mark.unit
def test_build_procurement_superglue_rollout_tenant_id_preserved() -> None:
    from app.services.command_handlers_procurement import build_procurement_superglue_rollout
    result = build_procurement_superglue_rollout("TENANT-XYZ")
    assert result["tenant_id"] == "TENANT-XYZ"
