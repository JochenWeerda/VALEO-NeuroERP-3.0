"""Constraint-Matrix-Aufbau fuer den Rations-LP (RATIONS-LP-SPLIT-001).

Enthaelt `build_lp_constraint_matrix`, das A_ub / b_ub / bounds sowie die
Constraint-Registry fuer _run_lp aufbaut.  Die Funktion ist rein berechend
(kein I/O, kein Solver-Aufruf) und erleichtert so isoliertes Testen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from app.agrar.rations.solver.constraint_registry import (
    ConstraintRegistry,
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

_JUICE_WET_CAP_HARD_KG_DM = 8.0
_WIZARD_BASELINE_L1_WEIGHT = 0.05


@dataclass
class LPConstraintResult:
    A_ub: List[List[float]]
    b_ub: List[float]
    bounds: List[Tuple[Any, Any]]
    registry: ConstraintRegistry
    # per-nutrient column vectors (re-used in relaxation cascade and post-solve)
    me_per_kg: List[float]
    sidp_per_kg: List[float]
    ndf_per_kg: List[float]
    xl_per_kg: List[float]
    rmd_per_kg: List[float]
    pabkh_per_kg: List[float]
    k_per_kg: List[float]
    cp_per_kg: List[float]
    # scalar limits (used in relaxation cascade)
    rmd_max: float
    # baseline L1 helpers
    k_lp_extra: int = 0
    baseline_positions: List[Tuple[int, float]] = field(default_factory=list)


def build_lp_constraint_matrix(
    feeds: List[Dict[str, Any]],
    req: Any,  # _CowReq namedtuple
    feeding_type: str,
    pasture_pmr: bool,
    block_labels: List[str],
    block_scoping_struct: bool,
    andfom_gf_min: float,
    pabkh_max: float,
    xl_max: float,
    cp_max: float,
    k_max: float,
    seasonal: Dict[str, float],
    runtime_options: Optional[Dict[str, Any]],
    juice_wet_cap_fn: Any,   # callable(feed) -> bool
    grass_feed_kind_fn: Any,  # callable(feed) -> Optional[str]
) -> LPConstraintResult:
    """Baut A_ub, b_ub, bounds und Constraint-Registry fuer den Rations-LP.

    Alle Constraints folgen GfE 2023 / DLG 01|2025 / GfE-Workshop 2023.
    Rueckgabe: LPConstraintResult mit allen Spalten-Vektoren, die in der
    Relaxations-Kaskade von _run_lp benoetigt werden.
    """
    n = len(feeds)
    A_ub: List[List[float]] = []
    b_ub: List[float] = []
    registry = ConstraintRegistry()

    def _geq(col_vals: List[float], rhs: float, *, name: Optional[str] = None) -> None:
        if name is not None:
            registry.add(name)
        A_ub.append([-v for v in col_vals])
        b_ub.append(-rhs)

    def _leq(col_vals: List[float], rhs: float, *, name: Optional[str] = None) -> None:
        if name is not None:
            registry.add(name)
        A_ub.append(list(col_vals))
        b_ub.append(rhs)

    def _tmr_only(col_vals: List[float]) -> List[float]:
        if not block_scoping_struct:
            return list(col_vals)
        return [v if block_labels[i] == "tmr_block" else 0.0 for i, v in enumerate(col_vals)]

    ones         = [1.0] * n
    me_per_kg    = [f["me"]   for f in feeds]
    sidp_per_kg  = [f["sidp"] for f in feeds]
    ndf_per_kg   = [f["ndf"]  for f in feeds]
    ca_per_kg    = [f["ca"]   for f in feeds]
    p_per_kg     = [f["p"]    for f in feeds]
    na_per_kg    = [f["na"]   for f in feeds]
    mg_per_kg    = [f["mg"]   for f in feeds]
    xl_per_kg    = [f["xl"]   for f in feeds]
    pabkh_per_kg = [f["st"] + f["zu"] - f["bst"] for f in feeds]
    cp_per_kg    = [f["cp"]   for f in feeds]
    rmd_per_kg   = [float(f.get("rmd") or 0.0) for f in feeds]
    k_per_kg     = [float(f.get("k",   0.0))   for f in feeds]

    # Energie und Protein
    _geq(me_per_kg,   req.me_mj,    name=CONSTR_ME_GEQ)
    _geq(sidp_per_kg, req.sidp_g,   name=CONSTR_SIDP_GEQ)

    # aNDFom gesamt
    _geq(ndf_per_kg,  req.ndf_min_g, name=CONSTR_ANDFOM_TOT_GEQ)

    # aNDFomGF+CoP-Dichte >= Mindestwert (Mischmasse-Scope)
    def _is_forage_or_cop(feed: Dict[str, Any]) -> bool:
        return bool(feed.get("forage") or feed.get("structural_coproduct"))

    andfom_gf_cop_density = [
        f["ndf"] - andfom_gf_min if _is_forage_or_cop(f) else -andfom_gf_min
        for f in feeds
    ]
    _geq(_tmr_only(andfom_gf_cop_density), 0.0, name=CONSTR_ANDFOM_GF_GEQ)

    # pabKH-Dichte
    pabkh_density = [v - pabkh_max for v in pabkh_per_kg]
    _leq(_tmr_only(pabkh_density), 0.0, name=CONSTR_PABKH_LEQ)

    # XL-Dichte
    xl_density = [v - xl_max for v in xl_per_kg]
    _leq(_tmr_only(xl_density), 0.0, name=CONSTR_XL_DENSITY)

    # CP-Dichte
    cp_density = [v - cp_max for v in cp_per_kg]
    _leq(_tmr_only(cp_density), 0.0, name=CONSTR_CP_DENSITY)

    # RMD-Dichte
    if feeding_type == "PMR+Weide":
        rmd_max = 8.0
    elif feeding_type == "PMR":
        rmd_max = 3.0
    else:
        rmd_max = 1.5
    if "rmd_max_boost" in seasonal:
        rmd_max = rmd_max + float(seasonal["rmd_max_boost"])
    rmd_density = [v - rmd_max for v in rmd_per_kg]
    _leq(rmd_density, 0.0, name=CONSTR_RMD_DENSITY)

    # ME-Dichte Obergrenze
    _leq([v - 12.5 for v in me_per_kg], 0.0, name=CONSTR_ME_DENSITY)

    # ME absolut Obergrenze
    _leq(me_per_kg, req.me_mj * 1.12, name=CONSTR_ME_ABS_LEQ)

    # aNDFom-Dichte Obergrenze
    _leq([v - 420.0 for v in ndf_per_kg], 0.0, name=CONSTR_ANDFOM_TOT_LEQ)

    # Mengenelemente
    _geq(ca_per_kg, req.ca_min_g, name=CONSTR_CA_LEQ)
    _geq(p_per_kg,  req.p_min_g,  name=CONSTR_P_LEQ)
    _geq(na_per_kg, req.na_min_g, name=CONSTR_NA_LEQ)
    _geq(mg_per_kg, req.mg_min_g, name=CONSTR_MG_LEQ)

    # K/Mg-Antagonismus
    _leq(k_per_kg, k_max)

    # Saftfutter-/nasse-CoP-Kappe
    juice_wet_cap_mask = [1.0 if juice_wet_cap_fn(f) else 0.0 for f in feeds]
    _leq(juice_wet_cap_mask, _JUICE_WET_CAP_HARD_KG_DM)

    # Frischgras-Kappe (nur TMR)
    if feeding_type == "TMR":
        weide_mask = [1.0 if grass_feed_kind_fn(f) == "pasture" else 0.0 for f in feeds]
        _leq(weide_mask, 4.0)

    # PMR+Weide: Mg-Supplement Pflichtbaustein
    if pasture_pmr:
        mg_supplement_mask = [1.0 if f.get("_special") == "pasture_mg" else 0.0 for f in feeds]
        if any(mg_supplement_mask):
            _geq(mg_supplement_mask, 0.05)

    # Mindest-Grobfutter-Anteil ≥ 40% DMI
    grobfutter_neg = [
        -1.0 if (f.get("forage") and "grobfutter" in f.get("group", "").lower()) else 0.4
        for f in feeds
    ]
    _leq(grobfutter_neg, 0.0)

    # DMI
    _geq(ones, req.dmi_min_kg, name=CONSTR_DMI_GEQ)
    _leq(ones, req.dmi_max_kg, name=CONSTR_DMI_LEQ)

    # Wizard Step 3: lineare Dichte-Nebenbedingungen (ohne Registry-Namen)
    _wizard_hb_lp = (
        ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_hard_bounds") or {}
    )
    _me_min_u = _wizard_hb_lp.get("me_min_mj_per_kg_dm")
    if _me_min_u is not None:
        try:
            _me_min_v = float(_me_min_u)
            if _me_min_v > 0:
                _geq([f["me"] - _me_min_v for f in feeds], 0.0)
        except (TypeError, ValueError):
            pass
    _st_pct_u = _wizard_hb_lp.get("starch_max_pct_tm")
    if _st_pct_u is not None:
        try:
            _st_cap = float(_st_pct_u) * 10.0
            if _st_cap >= 0:
                _leq([f["st"] - _st_cap for f in feeds], 0.0)
        except (TypeError, ValueError):
            pass
    _ndf_pct_u = _wizard_hb_lp.get("andfom_min_pct_tm")
    if _ndf_pct_u is not None:
        try:
            _ndf_floor_d = float(_ndf_pct_u) * 10.0
            if _ndf_floor_d > 0:
                _geq([f["ndf"] - _ndf_floor_d for f in feeds], 0.0)
        except (TypeError, ValueError):
            pass

    bounds = [(f["min_kg"], f["max_kg"]) for f in feeds]

    # Wizard: L1-Baseline-Abstandsminimierung
    _wizard_sg = ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_soft_goals") or {}
    _wizard_baseline_raw = (
        ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_baseline_kg_dm") or {}
    )
    _wizard_baseline_kgdm: Dict[str, float] = {}
    if isinstance(_wizard_baseline_raw, dict):
        for _bk, _bv in _wizard_baseline_raw.items():
            try:
                _wizard_baseline_kgdm[str(_bk)] = max(0.0, float(_bv))
            except (TypeError, ValueError):
                continue

    k_lp_extra = 0
    baseline_positions: List[Tuple[int, float]] = []
    if _wizard_sg.get("minimize_deviation_from_baseline") and _wizard_baseline_kgdm:
        for _fi in range(n):
            _fid = str(feeds[_fi].get("id") or "")
            if _fid and _fid in _wizard_baseline_kgdm:
                baseline_positions.append((_fi, float(_wizard_baseline_kgdm[_fid])))
        k_lp_extra = len(baseline_positions)

    if k_lp_extra > 0:
        A_ub = [list(_r) + [0.0] * k_lp_extra for _r in A_ub]
        for _j, (_fi, _bkg) in enumerate(baseline_positions):
            _ti = n + _j
            _r_pos = [0.0] * (n + k_lp_extra)
            _r_pos[_fi] = 1.0
            _r_pos[_ti] = -1.0
            A_ub.append(_r_pos)
            b_ub.append(_bkg)
            _r_neg = [0.0] * (n + k_lp_extra)
            _r_neg[_fi] = -1.0
            _r_neg[_ti] = -1.0
            A_ub.append(_r_neg)
            b_ub.append(-_bkg)
        bounds = list(bounds) + [(0.0, None)] * k_lp_extra

    return LPConstraintResult(
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        registry=registry,
        me_per_kg=me_per_kg,
        sidp_per_kg=sidp_per_kg,
        ndf_per_kg=ndf_per_kg,
        xl_per_kg=xl_per_kg,
        rmd_per_kg=rmd_per_kg,
        pabkh_per_kg=pabkh_per_kg,
        k_per_kg=k_per_kg,
        cp_per_kg=cp_per_kg,
        rmd_max=rmd_max,
        k_lp_extra=k_lp_extra,
        baseline_positions=baseline_positions,
    )
