"""Stage-2-Policy-Band-LP-Erweiterung (RATIONS-LP-SPLIT-001).

Extrahiert aus rations_optimization.py (vormals Zeilen ~6450–6740).
Enthaelt:
- _POLICY_BAND_SPECS     — Bandspezifikations-Tupel (DLG 01|2025 Tab. 13-15)
- _policy_band_coeffs    — Koeffizienten je Band-Schluessel
- _policy_profile_band_evaluate  — Post-Solve-Bewertung vs. Referenzkorridore
- _build_policy_band_lp_extension — Stage-2-Slack-Erweiterung fuer den LP
- _build_policy_profile_evaluation — Response-Aggregation des Auswertungs-Ergebnisses

Re-exportiert via rations_optimization.py (unveraenderte oeffentliche Schnittstelle).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.agrar.rations.constants.solver_defaults import (
    PENALTY_BASE_COST as _PENALTY_BASE_COST,
    PENALTY_CLASS_WEIGHTS as _PENALTY_CLASS_WEIGHTS,
    RELAXATION_FACTORS as _RELAXATION_FACTORS,
)

# ---------------------------------------------------------------------------
# Band-Spezifikationen (DLG 01|2025 Tab. 13-15, Klasse B)
# ---------------------------------------------------------------------------
# Jedes Element: (anzeige_name, value_key, min_key, max_key, unit, min_halfwidth)
# value_key  → in `_policy_band_coeffs` und post-solve `values` dict
# min_key/max_key → in `targets` dict (PolicyProfile-Eintraege)
# min_halfwidth → Mindesthalbbreite fuer Penalty-Normierung
# ---------------------------------------------------------------------------
POLICY_BAND_SPECS: Tuple[Tuple[str, str, str, str, str, float], ...] = (
    ("DLG-Policy: ME-Dichte",          "me_kgdm",              "me_kgdm_min",          "me_kgdm_max",        "MJ/kg TM",  0.20),
    ("DLG-Policy: CP-Dichte",          "cp_kgdm",              "cp_kgdm_min",          "cp_kgdm_max",        "g/kg TM",  10.00),
    ("DLG-Policy: sidP-Dichte",        "sidp_kgdm",            "sidp_kgdm_min",        "sidp_kgdm_max",      "g/kg TM",   8.00),
    ("DLG-Policy: pabKH (max)",        "pabkh_kgdm",           None,                   "pabkh_max",          "g/kg TM",  15.00),
    ("DLG-Policy: Rohfett XL (max)",   "xl_kgdm",              "xl_kgdm_min",          "xl_kgdm_max",        "g/kg TM",   5.00),
    ("DLG-Policy: Grundfutteranteil",  "forage_share_pct",     "forage_share_min_pct", "forage_share_max_pct","%TM",      5.00),
    ("DLG-Policy: aNDFomGF+CoP (min)", "andfom_gf_cop_kgdm",   "andfom_gf_cop_min",    None,                 "g/kg TM",  20.00),
    ("DLG-Policy: aNDFom (min)",       "andfom_kgdm",          "ndf_kgdm_min",         None,                 "g/kg TM",  20.00),
)


def policy_band_coeffs(band_key: str, feeds: List[Dict[str, Any]]) -> Optional[List[float]]:
    """Liefert die Futtermittel-Koeffizienten fuer das angegebene Band.

    Rueckgabe ``None`` bedeutet: Band hat kein lineares LP-Modell und wird
    ausschliesslich post-solve ausgewertet.
    """
    if band_key == "me_kgdm":
        return [float(f.get("me") or 0.0) for f in feeds]
    if band_key == "cp_kgdm":
        return [float(f.get("cp") or 0.0) for f in feeds]
    if band_key == "sidp_kgdm":
        return [float(f.get("sidp") or 0.0) for f in feeds]
    if band_key == "pabkh_kgdm":
        return [
            float(f.get("st") or 0.0)
            + float(f.get("zu") or 0.0)
            - float(f.get("bst") or 0.0)
            for f in feeds
        ]
    if band_key == "xl_kgdm":
        return [float(f.get("xl") or 0.0) for f in feeds]
    if band_key == "andfom_gf_cop_kgdm":
        return [
            float(f.get("ndf") or 0.0) if (f.get("forage") or f.get("structural_coproduct")) else 0.0
            for f in feeds
        ]
    if band_key == "andfom_kgdm":
        return [float(f.get("ndf") or 0.0) for f in feeds]
    if band_key == "forage_share_pct":
        return [100.0 if f.get("forage") else 0.0 for f in feeds]
    return None


def policy_profile_band_evaluate(
    targets: Optional[Dict[str, Any]],
    values: Dict[str, Any],
    relaxation_policy: str,
) -> List[Dict[str, Any]]:
    """Bewertet Ist-Werte einer Ration gegen DLG-01|2025-Referenzkorridore.

    Rueckgabe: Liste von constraint_status-kompatiblen Eintraegen mit Klasse B.
    Innerhalb des Bandes gilt deviation_norm = 0, also penalty = 0.
    """
    if not targets:
        return []

    out: List[Dict[str, Any]] = []
    factor = _RELAXATION_FACTORS.get(relaxation_policy, 1.0)
    klass_weight = _PENALTY_CLASS_WEIGHTS.get("B", 3.0)

    for display_name, value_key, min_key, max_key, unit, min_halfwidth in POLICY_BAND_SPECS:
        raw_value = values.get(value_key)
        if raw_value is None:
            continue
        try:
            actual = float(raw_value)
        except (TypeError, ValueError):
            continue

        lo_raw = targets.get(min_key) if min_key else None
        hi_raw = targets.get(max_key) if max_key else None
        lo = float(lo_raw) if lo_raw is not None else None
        hi = float(hi_raw) if hi_raw is not None else None
        if lo is None and hi is None:
            continue

        if lo is not None and hi is not None:
            halfwidth = max(min_halfwidth, 0.5 * (hi - lo))
        else:
            anchor = lo if lo is not None else hi
            halfwidth = max(min_halfwidth, 0.10 * abs(anchor or 1.0))

        if lo is not None and actual < lo:
            violation = lo - actual
            target_display = lo
            direction = "min"
            status = "violated"
        elif hi is not None and actual > hi:
            violation = actual - hi
            target_display = hi
            direction = "max"
            status = "violated"
        else:
            violation = 0.0
            if lo is not None and hi is not None:
                target_display = 0.5 * (lo + hi)
            else:
                target_display = lo if lo is not None else hi
            direction = "target"
            status = "ok"

        deviation_norm = violation / halfwidth if halfwidth > 0 else 0.0
        penalty = _PENALTY_BASE_COST * klass_weight * factor * deviation_norm

        out.append({
            "name": display_name,
            "kind": "weich",
            "class": "B",
            "unit": unit,
            "target": round(float(target_display or 0.0), 3),
            "target_min": round(lo, 3) if lo is not None else None,
            "target_max": round(hi, 3) if hi is not None else None,
            "direction": direction,
            "actual": round(actual, 3),
            "difference": round(actual - float(target_display or 0.0), 3),
            "fulfilled": deviation_norm < 1e-6,
            "deviation_norm": round(deviation_norm, 3),
            "penalty_cost": round(penalty, 4),
            "status": status,
            "source": "policy_profile",
        })

    return out


def build_policy_band_lp_extension(
    targets: Optional[Dict[str, Any]],
    feeds: List[Dict[str, Any]],
    relaxation_policy: str,
    dmi_typ_kg: float,
) -> Dict[str, Any]:
    """Baut die Slack-Erweiterung des LP fuer die DLG-01|2025-Band-Constraints.

    Rueckgabe-Dict mit:
      - ``n_slacks``     Anzahl eingefuehrter Slack-Variablen
      - ``rows``         zusaetzliche A_ub-Zeilen (mit Slack-Eintraegen)
      - ``rhs``          zusaetzliche b_ub-Werte (immer 0.0 bei Dichte-Bands)
      - ``slack_costs``  Objective-Anteile je Slack (EUR pro g-Verletzung)
      - ``slack_bounds`` Bounds je Slack (immer (0, None))
      - ``slack_meta``   Liste mit {name, unit, direction, class, halfwidth, weight}
    """
    out: Dict[str, Any] = {
        "n_slacks": 0,
        "rows": [],
        "rhs": [],
        "slack_costs": [],
        "slack_bounds": [],
        "slack_meta": [],
    }
    if not targets or not feeds:
        return out

    _n_feeds = len(feeds)  # noqa: F841
    factor = _RELAXATION_FACTORS.get(relaxation_policy, 1.0)
    klass_weight = _PENALTY_CLASS_WEIGHTS.get("B", 3.0)
    dmi_scale = max(1.0, float(dmi_typ_kg))

    slacks: List[Dict[str, Any]] = []
    slack_rows: List[List[float]] = []

    for display_name, value_key, min_key, max_key, unit, min_halfwidth in POLICY_BAND_SPECS:
        coeffs = policy_band_coeffs(value_key, feeds)
        if coeffs is None:
            continue
        lo_raw = targets.get(min_key) if min_key else None
        hi_raw = targets.get(max_key) if max_key else None
        lo = float(lo_raw) if lo_raw is not None else None
        hi = float(hi_raw) if hi_raw is not None else None
        if lo is None and hi is None:
            continue

        if lo is not None and hi is not None:
            halfwidth = max(min_halfwidth, 0.5 * (hi - lo))
        else:
            anchor = lo if lo is not None else hi
            halfwidth = max(min_halfwidth, 0.10 * abs(anchor or 1.0))

        weight = _PENALTY_BASE_COST * klass_weight * factor / (halfwidth * dmi_scale)

        if lo is not None:
            feed_row = [-(c - lo) for c in coeffs]
            slack_rows.append(feed_row)
            slacks.append({
                "name": f"{display_name} (min)",
                "unit": unit,
                "direction": "min",
                "band_min": lo,
                "band_max": hi,
                "halfwidth": halfwidth,
                "weight": weight,
                "slack_sign": -1.0,
            })

        if hi is not None:
            feed_row = [(c - hi) for c in coeffs]
            slack_rows.append(feed_row)
            slacks.append({
                "name": f"{display_name} (max)",
                "unit": unit,
                "direction": "max",
                "band_min": lo,
                "band_max": hi,
                "halfwidth": halfwidth,
                "weight": weight,
                "slack_sign": -1.0,
            })

    if not slacks:
        return out

    n_slacks = len(slacks)
    full_rows: List[List[float]] = []
    for row_idx, feed_row in enumerate(slack_rows):
        slack_cols = [0.0] * n_slacks
        slack_cols[row_idx] = float(slacks[row_idx].get("slack_sign") or -1.0)
        full_rows.append(feed_row + slack_cols)

    out.update({
        "n_slacks": n_slacks,
        "rows": full_rows,
        "rhs": [0.0] * n_slacks,
        "slack_costs": [float(s["weight"]) for s in slacks],
        "slack_bounds": [(0.0, None)] * n_slacks,
        "slack_meta": slacks,
    })
    return out


# DLG 01|2025 / GfE 2023 Kohlenhydrat- und Ca:P-Zielkorridore (nur Anzeige-Tachos,
# NICHT penalty-/LP-bindend). Quellen:
#   - Staerke/Zucker: DLG-Information 01|2025 (Kohlenhydratversorgung Milchkuh)
#   - Ca:P-Verhaeltnis: GfE 2023 (Mengenelement-Verhaeltnis)
# Tupel: (Anzeigename, value_key, lo, hi, unit, min_halfwidth)
DISPLAY_GAUGE_SPECS: Tuple[Tuple[str, str, Optional[float], Optional[float], str, float], ...] = (
    ("Stärke", "staerke_kgdm", 150.0, 250.0, "g/kg TM", 20.0),
    ("Zucker", "zucker_kgdm", 30.0, 70.0, "g/kg TM", 10.0),
    ("Fett (XL)", "xl_kgdm", 25.0, 50.0, "g/kg TM", 5.0),
    ("Ca:P-Verhältnis", "ca_p_ratio", 1.5, 2.0, "", 0.2),
)


def display_gauge_bands(values: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Zusaetzliche Anzeige-Tachos (Staerke/Zucker/Fett/Ca:P) aus den Ist-Dichten.

    Diese Baender werden ausschliesslich fuer die Cockpit-Tacho-Reihe erzeugt und
    fliessen NICHT in constraint_status oder penalty_summary ein (kein LP-Bezug,
    keine Strafkosten). Fehlt ein Ist-Wert, wird der Tacho ausgelassen.
    """
    dmi = float(values.get("dmi_kg") or 0.0)
    ca = values.get("ca_g")
    p = values.get("p_g")
    derived: Dict[str, Optional[float]] = {
        "staerke_kgdm": (float(values["staerke_g"]) / dmi) if (values.get("staerke_g") is not None and dmi > 0) else None,
        "zucker_kgdm": (float(values["zucker_g"]) / dmi) if (values.get("zucker_g") is not None and dmi > 0) else None,
        "xl_kgdm": values.get("xl_kgdm"),
        "ca_p_ratio": (float(ca) / float(p)) if (ca is not None and p not in (None, 0)) else None,
    }
    out: List[Dict[str, Any]] = []
    for name, key, lo, hi, unit, min_hw in DISPLAY_GAUGE_SPECS:
        actual = derived.get(key)
        if actual is None:
            continue
        halfwidth = max(min_hw, 0.5 * ((hi or 0) - (lo or 0))) if (lo is not None and hi is not None) else min_hw
        if lo is not None and actual < lo:
            violation = lo - actual
            direction = "min"
            target_display = lo
            status = "violated"
        elif hi is not None and actual > hi:
            violation = actual - hi
            direction = "max"
            target_display = hi
            status = "violated"
        else:
            violation = 0.0
            target_display = 0.5 * ((lo or 0) + (hi or 0)) if (lo is not None and hi is not None) else (lo if lo is not None else hi)
            direction = "target"
            status = "ok"
        deviation_norm = violation / halfwidth if halfwidth > 0 else 0.0
        out.append({
            "name": name,
            "kind": "weich",
            "class": "C",
            "unit": unit,
            "target": round(float(target_display or 0.0), 3),
            "target_min": lo,
            "target_max": hi,
            "direction": direction,
            "actual": round(float(actual), 3),
            "difference": round(float(actual) - float(target_display or 0.0), 3),
            "fulfilled": deviation_norm < 1e-6,
            "deviation_norm": round(deviation_norm, 3),
            "penalty_cost": 0.0,
            "status": status,
            "source": "display_only",
        })
    return out


def build_policy_profile_evaluation(
    profile_key: Optional[str],
    targets: Optional[Dict[str, Any]],
    bands: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Liefert das Policy-Profil-Evaluation-Objekt fuer das Response.

    - ``bands``: alle ausgewerteten Band-Checks (auch ok-Zeilen).
    - ``violations``: nur verletzte Baender.
    - ``penalty_total``: Summe Penalty-Kosten aus dem Policy-Profil.
    """
    if not profile_key or not targets:
        return None
    violations = [b for b in bands if b.get("status") == "violated"]
    penalty_total = sum(float(b.get("penalty_cost") or 0.0) for b in bands)
    return {
        "profile": profile_key,
        "label": targets.get("label"),
        "bands": bands,
        "violation_count": len(violations),
        "violations": violations,
        "penalty_total": round(penalty_total, 4),
        "source": "DLG 01|2025 Tab. 13-15 (Leistungs-/Physiologiestufen)",
    }
