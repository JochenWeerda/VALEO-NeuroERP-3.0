"""RATIONS-LP-SPLIT-001: Unit-Tests fuer build_lp_constraint_matrix.

Prueft:
- Korrekte Zeilen-Anzahl und Registry-Indizes
- TMR-Only-Scoping
- RMD-Limit je Fuetterungstyp
- Wizard-Hard-Bounds werden als zusaetzliche Rows eingetragen
- Baseline-L1-Extension
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from collections import namedtuple

import pytest

from app.agrar.rations.solver.lp_constraints import build_lp_constraint_matrix, LPConstraintResult
from app.agrar.rations.solver.constraint_registry import (
    CONSTR_ME_GEQ,
    CONSTR_SIDP_GEQ,
    CONSTR_ANDFOM_TOT_GEQ,
    CONSTR_ANDFOM_GF_GEQ,
    CONSTR_PABKH_LEQ,
    CONSTR_XL_DENSITY,
    CONSTR_CP_DENSITY,
    CONSTR_RMD_DENSITY,
    CONSTR_ME_DENSITY,
    CONSTR_ME_ABS_LEQ,
    CONSTR_ANDFOM_TOT_LEQ,
    CONSTR_CA_LEQ,
    CONSTR_P_LEQ,
    CONSTR_NA_LEQ,
    CONSTR_MG_LEQ,
    CONSTR_DMI_GEQ,
    CONSTR_DMI_LEQ,
)


_CowReq = namedtuple(
    "_CowReq",
    ["me_mj", "sidp_g", "ndf_min_g", "ca_min_g", "p_min_g", "na_min_g", "mg_min_g",
     "k_max_g", "dmi_min_kg", "dmi_max_kg"],
)

_REQ = _CowReq(
    me_mj=180.0, sidp_g=2200.0, ndf_min_g=180.0,
    ca_min_g=130.0, p_min_g=70.0, na_min_g=30.0, mg_min_g=40.0,
    k_max_g=280.0, dmi_min_kg=18.0, dmi_max_kg=25.0,
)


def _make_feed(
    idx: int,
    *,
    forage: bool = False,
    structural_coproduct: bool = False,
    min_kg: float = 0.0,
    max_kg: float = 10.0,
    rmd: float = 1.0,
    k: float = 10.0,
    is_pasture_grass: bool = False,
) -> Dict[str, Any]:
    return {
        "id": str(idx),
        "me": 6.0 + idx * 0.1,
        "sidp": 80.0 + idx,
        "ndf": 200.0 + idx,
        "ca": 5.0,
        "p": 3.0,
        "na": 1.5,
        "mg": 2.0,
        "xl": 20.0,
        "st": 50.0,
        "zu": 5.0,
        "bst": 10.0,
        "cp": 120.0,
        "rmd": rmd,
        "k": k,
        "price": 0.20,
        "forage": forage,
        "structural_coproduct": structural_coproduct,
        "min_kg": min_kg,
        "max_kg": max_kg,
        "dm": 0.88 if not is_pasture_grass else 0.18,
        "group": "grobfutter" if forage else "kraftfutter",
        "_special": None,
    }


_FEEDS_2 = [_make_feed(0, forage=True), _make_feed(1)]
_FEEDS_3 = [_make_feed(0, forage=True), _make_feed(1), _make_feed(2)]


def _juice_fn(f: Dict[str, Any]) -> bool:
    return False


def _grass_fn(f: Dict[str, Any]) -> Optional[str]:
    dm = f.get("dm", 1.0)
    if isinstance(dm, float) and dm < 0.30:
        return "pasture"
    return "grass_silage"


def _build(
    feeds=_FEEDS_2,
    req=_REQ,
    feeding_type="TMR",
    pasture_pmr=False,
    block_labels=None,
    block_scoping_struct=False,
    andfom_gf_min=200.0,
    pabkh_max=210.0,
    xl_max=40.0,
    cp_max=165.0,
    k_max=280.0,
    seasonal=None,
    runtime_options=None,
) -> LPConstraintResult:
    if block_labels is None:
        block_labels = ["tmr_block"] * len(feeds)
    return build_lp_constraint_matrix(
        feeds=feeds,
        req=req,
        feeding_type=feeding_type,
        pasture_pmr=pasture_pmr,
        block_labels=block_labels,
        block_scoping_struct=block_scoping_struct,
        andfom_gf_min=andfom_gf_min,
        pabkh_max=pabkh_max,
        xl_max=xl_max,
        cp_max=cp_max,
        k_max=k_max,
        seasonal=seasonal or {},
        runtime_options=runtime_options,
        juice_wet_cap_fn=_juice_fn,
        grass_feed_kind_fn=_grass_fn,
    )


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

def test_returns_lp_constraint_result():
    res = _build()
    assert isinstance(res, LPConstraintResult)


def test_a_ub_and_b_ub_same_length():
    res = _build()
    assert len(res.A_ub) == len(res.b_ub)


def test_bounds_length_matches_feeds():
    res = _build(feeds=_FEEDS_3)
    assert len(res.bounds) == len(_FEEDS_3)


def test_all_rows_have_n_cols():
    res = _build(feeds=_FEEDS_2)
    n = len(_FEEDS_2)
    for row in res.A_ub:
        assert len(row) == n


# ---------------------------------------------------------------------------
# Registry — expected named-constraint indices
# ---------------------------------------------------------------------------

EXPECTED_INDICES = {
    CONSTR_ME_GEQ: 0,
    CONSTR_SIDP_GEQ: 1,
    CONSTR_ANDFOM_TOT_GEQ: 2,
    CONSTR_ANDFOM_GF_GEQ: 3,
    CONSTR_PABKH_LEQ: 4,
    CONSTR_XL_DENSITY: 5,
    CONSTR_CP_DENSITY: 6,
    CONSTR_RMD_DENSITY: 7,
    CONSTR_ME_DENSITY: 8,
    CONSTR_ME_ABS_LEQ: 9,
    CONSTR_ANDFOM_TOT_LEQ: 10,
    CONSTR_CA_LEQ: 11,
    CONSTR_P_LEQ: 12,
    CONSTR_NA_LEQ: 13,
    CONSTR_MG_LEQ: 14,
    CONSTR_DMI_GEQ: 15,
    CONSTR_DMI_LEQ: 16,
}


@pytest.mark.parametrize("name,expected_idx", list(EXPECTED_INDICES.items()))
def test_registry_index(name, expected_idx):
    res = _build()
    assert res.registry.index_of(name) == expected_idx


# ---------------------------------------------------------------------------
# RMD max per feeding type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("feeding_type,expected_rmd_max", [
    ("TMR",      1.5),
    ("PMR",      3.0),
    ("PMR+Weide", 8.0),
])
def test_rmd_max_by_feeding_type(feeding_type, expected_rmd_max):
    res = _build(feeding_type=feeding_type)
    assert abs(res.rmd_max - expected_rmd_max) < 1e-9


def test_rmd_max_boost_from_seasonal():
    res = _build(feeding_type="TMR", seasonal={"rmd_max_boost": 1.0})
    assert abs(res.rmd_max - 2.5) < 1e-9


# ---------------------------------------------------------------------------
# Block scoping: TMR-only coefficients
# ---------------------------------------------------------------------------

def test_block_scoping_zeroes_non_tmr_feeds():
    feeds = [
        _make_feed(0, forage=True),   # tmr_block
        _make_feed(1),                 # concentrate_staged_block
    ]
    block_labels = ["tmr_block", "concentrate_staged_block"]
    res = _build(
        feeds=feeds,
        block_labels=block_labels,
        block_scoping_struct=True,
    )
    # CONSTR_XL_DENSITY row: only feed[0] should have non-zero coeff
    idx_xl = res.registry.index_of(CONSTR_XL_DENSITY)
    row = res.A_ub[idx_xl]
    assert row[1] == 0.0  # non-TMR feed zeroed out


def test_no_block_scoping_all_feeds_included():
    feeds = [
        _make_feed(0, forage=True),
        _make_feed(1),
    ]
    block_labels = ["tmr_block", "concentrate_staged_block"]
    res = _build(
        feeds=feeds,
        block_labels=block_labels,
        block_scoping_struct=False,  # scoping OFF
    )
    idx_xl = res.registry.index_of(CONSTR_XL_DENSITY)
    row = res.A_ub[idx_xl]
    # Both feeds should contribute
    assert row[1] != 0.0


# ---------------------------------------------------------------------------
# Wizard hard bounds add extra rows
# ---------------------------------------------------------------------------

def test_wizard_me_min_adds_row():
    base_res = _build()
    base_rows = len(base_res.A_ub)
    res = _build(runtime_options={
        "policy_overrides": {"wizard_hard_bounds": {"me_min_mj_per_kg_dm": 6.5}}
    })
    assert len(res.A_ub) == base_rows + 1


def test_wizard_starch_max_adds_row():
    base_rows = len(_build().A_ub)
    res = _build(runtime_options={
        "policy_overrides": {"wizard_hard_bounds": {"starch_max_pct_tm": 25.0}}
    })
    assert len(res.A_ub) == base_rows + 1


def test_wizard_ndf_min_adds_row():
    base_rows = len(_build().A_ub)
    res = _build(runtime_options={
        "policy_overrides": {"wizard_hard_bounds": {"andfom_min_pct_tm": 30.0}}
    })
    assert len(res.A_ub) == base_rows + 1


# ---------------------------------------------------------------------------
# Baseline L1 extension
# ---------------------------------------------------------------------------

def test_baseline_l1_extends_bounds():
    feeds = _FEEDS_2
    res = _build(
        feeds=feeds,
        runtime_options={
            "policy_overrides": {
                "wizard_soft_goals": {"minimize_deviation_from_baseline": True},
                "wizard_baseline_kg_dm": {"0": 8.0, "1": 4.0},
            }
        }
    )
    assert res.k_lp_extra == 2
    assert len(res.bounds) == len(feeds) + 2
    assert len(res.baseline_positions) == 2


def test_no_baseline_no_extras():
    res = _build()
    assert res.k_lp_extra == 0
    assert res.baseline_positions == []


# ---------------------------------------------------------------------------
# Column vectors
# ---------------------------------------------------------------------------

def test_me_per_kg_matches_feeds():
    res = _build(feeds=_FEEDS_2)
    for i, f in enumerate(_FEEDS_2):
        assert abs(res.me_per_kg[i] - f["me"]) < 1e-9


def test_rmd_per_kg_matches_feeds():
    res = _build(feeds=_FEEDS_2)
    for i, f in enumerate(_FEEDS_2):
        assert abs(res.rmd_per_kg[i] - float(f.get("rmd") or 0.0)) < 1e-9
