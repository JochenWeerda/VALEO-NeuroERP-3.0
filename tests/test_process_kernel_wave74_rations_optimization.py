"""
Wave 74 — Rationsoptimierung: GfE-2023 Contracts + Proxy-Contract
Deckt ab:
  A) GfE-2023 Nährstoffformel-Kontrakte (direkt vom Microservice-Modul)
  B) Proxy-Contract: ERP-Router liefert 503 wenn RATIONS_OPTIMIZATION_URL fehlt

sys.path muss rationsoptimierung/ enthalten (wird hier dynamisch gesetzt).
"""
from __future__ import annotations

import sys
import os
import pytest

# ---------------------------------------------------------------------------
# Microservice-Modul zum Python-Pfad hinzufügen (nur für diese Tests)
# ---------------------------------------------------------------------------

_RATIONS_ROOT = os.path.join(os.path.dirname(__file__), "..", "rationsoptimierung")
if _RATIONS_ROOT not in sys.path:
    sys.path.insert(0, _RATIONS_ROOT)


# ---------------------------------------------------------------------------
# Imports aus Microservice (nach sys.path-Patch)
# ---------------------------------------------------------------------------

from app.nutrition.gfe2023 import (
    metabolic_body_weight_kg,
    energy_maintenance_me_mj,
    energy_corrected_milk_kg,
    energy_lactation_me_mj,
    total_me_requirement_mj,
    ME_PER_KG_ECM,
    ME_MAINTENANCE_MJ_PER_KG_METABOLIC_BW,
)
from app.domain.models import CowProfile, Breed


# ===========================================================================
# A) GfE-2023 Nährstoffformel-Kontrakte
# ===========================================================================

class TestMetabolicBodyWeight:
    """LM^0.75 — Basis aller GfE-Bedarfsberechnungen."""

    def test_positive_weight(self):
        result = metabolic_body_weight_kg(650)
        # 650^0.75 ≈ 128.7
        assert result == pytest.approx(650 ** 0.75, rel=1e-6)

    def test_100kg_cow(self):
        assert metabolic_body_weight_kg(100) == pytest.approx(31.62, abs=0.05)

    def test_higher_weight_yields_higher_metabolic_weight(self):
        assert metabolic_body_weight_kg(700) > metabolic_body_weight_kg(600)

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError):
            metabolic_body_weight_kg(0)

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError):
            metabolic_body_weight_kg(-50)


class TestEnergyMaintenanceME:
    """Erhaltungsbedarf ME = 0,64 × LM^0,75 [MJ/Tag]."""

    def test_holstein_650kg(self):
        # 0.64 × 650^0.75 ≈ 82.4 MJ
        result = energy_maintenance_me_mj(650)
        expected = 0.64 * (650 ** 0.75)
        assert result == pytest.approx(expected, rel=1e-5)

    def test_maintenance_positive(self):
        assert energy_maintenance_me_mj(500) > 0

    def test_heavier_cow_needs_more_maintenance(self):
        assert energy_maintenance_me_mj(700) > energy_maintenance_me_mj(550)

    def test_constant_factor_applied(self):
        """ME_Erhalt / LM^0,75 = 0,64 für beliebige LM."""
        for lm in [400, 550, 650, 750]:
            mbw = metabolic_body_weight_kg(lm)
            assert energy_maintenance_me_mj(lm) == pytest.approx(
                ME_MAINTENANCE_MJ_PER_KG_METABOLIC_BW * mbw, rel=1e-5
            )


class TestECM:
    """Energie-korrigierte Milch (ECM) nach GfE 2023."""

    def test_ecm_higher_fat_more_energy(self):
        """Höherer Fettgehalt → höhere ECM."""
        ecm_lo = energy_corrected_milk_kg(30, fat_percent=3.5, protein_percent=3.2)
        ecm_hi = energy_corrected_milk_kg(30, fat_percent=4.5, protein_percent=3.2)
        assert ecm_hi > ecm_lo

    def test_ecm_positive_for_realistic_values(self):
        assert energy_corrected_milk_kg(35, fat_percent=3.8, protein_percent=3.2) > 0

    def test_zero_milk_zero_ecm(self):
        assert energy_corrected_milk_kg(0, fat_percent=3.8, protein_percent=3.2) == pytest.approx(0.0, abs=0.001)


class TestEnergyLactationME:
    """ME-Bedarf für Milchbildung: ECM × ME_PER_KG_ECM."""

    def test_positive_ecm_yields_positive_energy(self):
        ecm = energy_corrected_milk_kg(35, fat_percent=3.8, protein_percent=3.2)
        assert energy_lactation_me_mj(ecm) > 0

    def test_more_ecm_more_energy(self):
        assert energy_lactation_me_mj(40) > energy_lactation_me_mj(20)

    def test_zero_ecm_no_energy(self):
        assert energy_lactation_me_mj(0) == pytest.approx(0.0, abs=0.001)

    def test_me_per_ecm_constant(self):
        """ME/kg ECM ≈ 4,77 (3,15 / 0,66)."""
        assert ME_PER_KG_ECM == pytest.approx(3.15 / 0.66, rel=1e-5)

    def test_total_me_reasonable_for_high_yield_cow(self):
        """Holstein 650 kg, 35 l/d: Gesamtbedarf 180–280 MJ/d plausibel."""
        me_maint = energy_maintenance_me_mj(650)
        ecm = energy_corrected_milk_kg(35, fat_percent=3.8, protein_percent=3.2)
        me_milk = energy_lactation_me_mj(ecm)
        total = me_maint + me_milk
        assert 180 <= total <= 280


# ===========================================================================
# B) CowProfile Pydantic-Schema-Kontrakte
# ===========================================================================

class TestCowProfileSchema:
    def test_valid_holstein(self):
        profile = CowProfile(
            breed=Breed.HOLSTEIN,
            body_weight_kg=650,
            milk_kg_day=35,
            milk_fat_pct=3.8,
            milk_protein_pct=3.2,
            lactation_stage_days=150,
            parity=2,
        )
        assert profile.breed == Breed.HOLSTEIN
        assert profile.body_weight_kg == 650

    def test_zero_body_weight_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CowProfile(
                body_weight_kg=0,
                milk_kg_day=35,
                milk_fat_pct=3.8,
                milk_protein_pct=3.2,
                lactation_stage_days=150,
                parity=1,
            )

    def test_negative_parity_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CowProfile(
                body_weight_kg=600,
                milk_kg_day=30,
                milk_fat_pct=3.8,
                milk_protein_pct=3.2,
                lactation_stage_days=100,
                parity=0,
            )

    def test_unreasonable_lactation_stage_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CowProfile(
                body_weight_kg=600,
                milk_kg_day=30,
                milk_fat_pct=3.8,
                milk_protein_pct=3.2,
                lactation_stage_days=501,
                parity=1,
            )

    def test_optional_target_dmi_none_allowed(self):
        profile = CowProfile(
            body_weight_kg=600,
            milk_kg_day=30,
            milk_fat_pct=3.8,
            milk_protein_pct=3.2,
            lactation_stage_days=100,
            parity=1,
        )
        assert profile.target_dmi_kg is None


# ===========================================================================
# C) ERP Hybrid-Contract (wave74 v2): Interner GfE-2023-Solver als Default
#
# Kontrakt-Update 2026-04-21 (FAN-MODE-V1):
# Frueherer wave74-Vertrag verlangte 503 fuer alle Endpunkte, wenn
# RATIONS_OPTIMIZATION_URL fehlt. Mit FAN-MODE-V1 ist jedoch ein vollstaendiger
# interner GfE-2023-LP-Solver aktiv, der ohne externen Proxy arbeitet. Der
# neue Vertrag ist hybrid:
#   - Kein Proxy gesetzt -> interner Solver liefert Ergebnisse (200)
#   - /health meldet success=True mit solver="internal-gfe2023"
#   - 503 nur wenn proxy gesetzt UND nicht erreichbar
# ===========================================================================

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints import rations_optimization
from unittest.mock import patch


@pytest.fixture
def proxy_client() -> TestClient:
    app = FastAPI()
    app.include_router(rations_optimization.router)
    return TestClient(app)


@pytest.fixture(autouse=False)
def no_rations_url():
    """Stellt sicher dass RATIONS_OPTIMIZATION_URL nicht gesetzt ist."""
    with patch.object(rations_optimization, "get_rations_base_url", return_value=None):
        yield


def test_health_returns_200_unconfigured(proxy_client, no_rations_url):
    """Ohne externen Proxy: /health liefert 200 mit aktivem internen Solver."""
    resp = proxy_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    # Interner Solver ist aktiv, Service ist betriebsbereit
    assert body["success"] is True
    assert body["configured"] is True
    assert body.get("solver") == "internal-gfe2023"
    assert body.get("energy_system") == "ME-FAN1"
    assert body.get("protein_system") == "sidP"


def test_optimize_uses_internal_solver_when_proxy_unconfigured(proxy_client, no_rations_url):
    """Ohne externen Proxy: /optimize bedient sich des internen Solvers.

    Leerer Body -> Solver optimiert mit Default-Demo-Profil (kein 503).
    """
    resp = proxy_client.post("/optimize", json={})
    assert resp.status_code == 200
    body = resp.json()
    # Response liefert immer Solver-Metadaten (Policy-Profil, constraint_report,
    # diagnosis ODER Ration je nach Feasibility)
    assert "active_policy_profile" in body
    assert any(k in body for k in ("ration", "diagnosis", "constraint_report", "solver_status"))


def test_feeds_returns_catalog_when_proxy_unconfigured(proxy_client, no_rations_url):
    """Ohne externen Proxy: /feeds liefert den bundled DLG-Katalog."""
    resp = proxy_client.get("/feeds")
    assert resp.status_code == 200
    feeds = resp.json()
    assert isinstance(feeds, list)
    assert len(feeds) >= 5  # mindestens der Fallback-Katalog


def test_requirements_calculate_uses_internal_solver(proxy_client, no_rations_url):
    """Ohne externen Proxy: /requirements/calculate berechnet via GfE-2023."""
    resp = proxy_client.post(
        "/requirements/calculate",
        json={
            "body_weight_kg": 650,
            "milk_kg_day": 35,
            "milk_fat_pct": 3.8,
            "milk_protein_pct": 3.2,
            "lactation_stage_days": 150,
            "parity": 2,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["energy_system"] == "ME-FAN1-GfE2023"
    assert body["protein_system"] == "sidP-GfE2023"
    assert body["me_mj_day"] > 0
    assert body["sidp_g_day"] > 0


def test_optimize_from_profile_uses_internal_solver(proxy_client, no_rations_url):
    """Ohne externen Proxy: /optimize/from-profile loest via internem LP-Solver."""
    resp = proxy_client.post(
        "/optimize/from-profile",
        json={
            "cow_profile": {
                "body_weight_kg": 650,
                "milk_kg_day": 30,
                "milk_fat_pct": 3.8,
                "milk_protein_pct": 3.2,
                "lactation_stage_days": 150,
                "parity": 2,
                "feeding_type": "TMR",
            }
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    # Antwort enthaelt mindestens einen der Kernbausteine aus dem internen Solver
    assert any(k in body for k in ("ration", "status", "solver_status", "success"))


def test_proxy_error_returns_503_when_configured_but_unreachable():
    """Wenn Proxy konfiguriert ABER nicht erreichbar: 503 vom Endpoint."""
    import httpx

    app = FastAPI()
    app.include_router(rations_optimization.router)
    client = TestClient(app)

    async def _fail(*_args, **_kwargs):
        raise httpx.ConnectError("connection refused")

    with patch.object(rations_optimization, "get_rations_base_url", return_value="http://localhost:9"), \
         patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.get.side_effect = _fail
        instance.post.side_effect = _fail
        resp = client.post("/optimize", json={})
        assert resp.status_code == 503
        detail = resp.json().get("detail", "").lower()
        assert "erreichbar" in detail or "konfiguriert" in detail or "url" in detail
