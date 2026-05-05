"""FAN-MODE-V1 Slice 5 (FAN-MODE-005) - Gate-Tests fuer saisonale Policy-Auswahl.

Spec 6.2: feeding_type + season_profile wird auf versioniertes Policy-Profil gemappt:
  TMR                           -> tmr_standard
  PMR + spring_young/mid/late   -> pmr_pasture_spring
  sonst                         -> pmr_standard
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.rations_optimization import (  # type: ignore
    _resolve_policy_profile,
    _resolve_runtime_options,
    _POLICY_PROFILES,
)


def test_tmr_resolves_to_tmr_standard():
    assert _resolve_policy_profile("TMR", None) == "tmr_standard"
    assert _resolve_policy_profile("TMR", "spring_young") == "tmr_standard"


def test_pmr_pasture_spring_activates_for_any_spring_subseason():
    for season in ("spring_young", "spring_mid", "spring_late"):
        got = _resolve_policy_profile("PMR+Weide", season)
        assert got == "pmr_pasture_spring", f"{season}: {got}"


def test_pmr_pasture_season_specific_profiles():
    """Spec §12 Erweiterung: PMR+Weide mit summer_* / autumn bekommt eigene Policy."""
    assert _resolve_policy_profile("PMR+Weide", "summer_young") == "pmr_pasture_summer"
    assert _resolve_policy_profile("PMR+Weide", "summer_mid") == "pmr_pasture_summer"
    assert _resolve_policy_profile("PMR+Weide", "summer_late") == "pmr_pasture_summer"
    assert _resolve_policy_profile("PMR+Weide", "autumn") == "pmr_pasture_autumn"


def test_pmr_without_season_falls_back_to_pmr_standard():
    assert _resolve_policy_profile("PMR+Weide", None) == "pmr_standard"
    assert _resolve_policy_profile("PMR+Weide", "winter") == "pmr_standard"
    assert _resolve_policy_profile("PMR", None) == "pmr_standard"


def test_explicit_profile_wins_when_whitelisted():
    for p in _POLICY_PROFILES:
        assert _resolve_policy_profile("TMR", None, explicit=p) == p


def test_explicit_profile_is_ignored_when_unknown():
    got = _resolve_policy_profile("TMR", None, explicit="unknown_profile")
    assert got == "tmr_standard"


def test_runtime_options_carry_active_policy_profile():
    cow = {"feeding_type": "PMR+Weide", "season_profile": "spring_mid"}
    opts = _resolve_runtime_options(cow, None, None, None, None, None, None)
    assert opts["policy_profile"] == "pmr_pasture_spring"
    assert opts["season_profile"] == "spring_mid"
    assert opts["relaxation_policy"] == "standard"
    assert opts["fan"]["mode"] == "auto_iterative"


def test_runtime_options_prefers_explicit_season_over_profile_field():
    cow = {"feeding_type": "PMR+Weide", "season_profile": "summer_mid"}
    opts = _resolve_runtime_options(cow, None, None, None, season_profile="spring_young")
    assert opts["policy_profile"] == "pmr_pasture_spring"
    assert opts["season_profile"] == "spring_young"
