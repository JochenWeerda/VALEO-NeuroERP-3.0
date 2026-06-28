"""Wave 79 — Unit-Tests fuer bedarfsdeckung_service, articles_service, admin_core_service (pure)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# bedarfsdeckung_service — ecm_kg, gruppen_profil  (pure domain math)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_ecm_kg_basic() -> None:
    from app.services.bedarfsdeckung_service import ecm_kg
    result = ecm_kg(milch_kg=10000.0, fett_pct=4.0, eiw_pct=3.4)
    assert result is not None
    assert result > 10000  # ECM corrected weight is typically higher for high-quality milk


@pytest.mark.unit
def test_ecm_kg_none_inputs_returns_none() -> None:
    from app.services.bedarfsdeckung_service import ecm_kg
    result = ecm_kg(milch_kg=None, fett_pct=4.0, eiw_pct=3.4)
    assert result is None


@pytest.mark.unit
def test_ecm_kg_zero_milk_returns_none_or_zero() -> None:
    from app.services.bedarfsdeckung_service import ecm_kg
    result = ecm_kg(milch_kg=0, fett_pct=4.0, eiw_pct=3.4)
    # Zero milk may return None (guard against division) or approx 0
    assert result is None or result == pytest.approx(0.0, abs=1.0)


@pytest.mark.unit
def test_gruppen_profil_strategischer_stammkunde() -> None:
    from app.services.bedarfsdeckung_service import gruppen_profil
    from app.services.kaeufergruppe import GruppenProfil
    result = gruppen_profil("STRATEGISCHER_STAMMKUNDE")
    assert isinstance(result, GruppenProfil)
    assert result.ziel_anteil_min <= result.ziel_anteil_max


@pytest.mark.unit
def test_gruppen_profil_returns_valid_structure() -> None:
    from app.services.bedarfsdeckung_service import gruppen_profil
    from app.services.kaeufergruppe import GruppenProfil
    result = gruppen_profil("PREISABFRAGER")
    assert isinstance(result, GruppenProfil)
    assert hasattr(result, "label")
    assert hasattr(result, "abschluss_faktor")
    assert hasattr(result, "grenzaufwand")


# ---------------------------------------------------------------------------
# articles_service — resolve_article_tenant, build_article_dq_datensatz  (pure)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_resolve_article_tenant_none_uses_tenant() -> None:
    from app.services.articles_service import resolve_article_tenant
    result = resolve_article_tenant(None, "T001")
    assert result == "T001"


@pytest.mark.unit
def test_resolve_article_tenant_same_tenant_ok() -> None:
    from app.services.articles_service import resolve_article_tenant
    result = resolve_article_tenant("T001", "T001")
    assert result == "T001"


@pytest.mark.unit
def test_resolve_article_tenant_cross_tenant_raises() -> None:
    from app.services.articles_service import resolve_article_tenant
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        resolve_article_tenant("T001", "T002")
    assert exc_info.value.status_code == 403


@pytest.mark.unit
def test_build_article_dq_datensatz_has_standard_fields() -> None:
    from app.services.articles_service import build_article_dq_datensatz
    ds = build_article_dq_datensatz({"artikel_nr": "ART-001", "bezeichnung": "Weizen"})
    for key in ("artikel_nr", "bezeichnung", "einheit"):
        assert key in ds


@pytest.mark.unit
def test_build_article_dq_datensatz_empty_input() -> None:
    from app.services.articles_service import build_article_dq_datensatz
    ds = build_article_dq_datensatz({})
    # Should return a dict even with empty input
    assert isinstance(ds, dict)


# ---------------------------------------------------------------------------
# admin_core_service — merge_workflow_variants  (pure dict merge)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_merge_workflow_variants_disjoint() -> None:
    from app.services.admin_core_service import merge_workflow_variants
    result = merge_workflow_variants({"v1": {"a": 1}}, {"v2": {"b": 2}})
    assert "v1" in result
    assert "v2" in result


@pytest.mark.unit
def test_merge_workflow_variants_custom_overrides_default() -> None:
    from app.services.admin_core_service import merge_workflow_variants
    result = merge_workflow_variants({"v1": {"a": 1}}, {"v1": {"a": 99}})
    assert result["v1"]["a"] == 99


@pytest.mark.unit
def test_merge_workflow_variants_empty_custom() -> None:
    from app.services.admin_core_service import merge_workflow_variants
    result = merge_workflow_variants({"v1": {"a": 1}}, {})
    assert result == {"v1": {"a": 1}}


@pytest.mark.unit
def test_merge_workflow_variants_empty_default() -> None:
    from app.services.admin_core_service import merge_workflow_variants
    result = merge_workflow_variants({}, {"v1": {"a": 1}})
    assert result == {"v1": {"a": 1}}
