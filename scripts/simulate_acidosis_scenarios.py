"""Ampel- und Azidose-Simulation: verschiedene Rationsvarianten durchspielen.

Zweck: Nachweisen, wie der interne GfE-2023-Solver auf rote Ampelsignale
(peNDF, pabKH, pH_predicted, RMD) in typischen Praxisfaellen reagiert –
inklusive Saisonprofile (Fruehling, Sommer, Herbst) und erzwungener
Extremszenarien.
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("PYTHONHASHSEED", "0")

from app.api.v1.endpoints.rations_optimization import (  # noqa: E402
    _optimize_internal,
    _resolve_runtime_options,
)


def _fmt_light(value: Optional[float], lo: float, hi: float) -> str:
    if value is None:
        return "—   "
    if value < lo:
        return "ROT "
    if value < hi:
        return "GELB"
    return "GRUEN"


def _summary_block(title: str, result: Dict[str, Any]) -> List[str]:
    ind = result.get("dlg_indicators") or {}
    cr = result.get("constraint_report") or []
    cs = result.get("constraint_status") or []
    hard = [c for c in cs if c.get("status") == "hard_violated"]
    soft = [c for c in cs if c.get("status") == "violated"]
    summary = result.get("penalty_summary") or {}
    fan = result.get("fan_calibration") or {}
    status = result.get("status") or ""

    lines: List[str] = []
    lines.append(f"===== {title} =====")
    lines.append(f"Solver-Status: {status}")
    if fan:
        lines.append(
            f"FAN: mode={fan.get('mode')}  "
            f"fani_final={fan.get('fani_final')}  "
            f"converged={fan.get('converged')}"
        )
    lines.append(
        f"Policy-Profil: {result.get('active_policy_profile')}  "
        f"Saisonprofil: {result.get('season_profile')}"
    )

    ph = ind.get("ph_predicted")
    pendf = ind.get("pendf_kgdm")
    pendf_min = ind.get("pendf_min_kgdm")
    pabkh = ind.get("pabkh_kgdm")
    si = ind.get("strukturindex")
    rmd = ind.get("rmd_gn_kgdm")

    lines.append("---- Ampelkritische Indikatoren ----")
    lines.append(
        f"  Pansen-pH (sim):  {ph:.2f}  [{_fmt_light(ph, 5.9, 6.2)}]  "
        f"(Ziel >= 6.2, SARA < 5.9)" if isinstance(ph, (int, float))
        else f"  Pansen-pH: {ph}"
    )
    if isinstance(pendf, (int, float)) and isinstance(pendf_min, (int, float)):
        diff = pendf - pendf_min
        light = "ROT" if diff < 0 else "GELB" if diff < 5 else "GRUEN"
        lines.append(
            f"  peNDF-Dichte:     {pendf:6.1f} g/kg TM  (min {pendf_min:5.1f})  [{light}]"
        )
    if isinstance(pabkh, (int, float)):
        lines.append(
            f"  pabKH-Dichte:     {pabkh:6.1f} g/kg TM  (Limit 210/225)"
        )
    if isinstance(si, (int, float)):
        light = "ROT" if si < 45 else "GELB" if si < 50 else "GRUEN"
        lines.append(f"  Strukturindex:    {si:6.1f}          (Ziel >= 50)  [{light}]")
    if isinstance(rmd, (int, float)):
        lines.append(f"  RMD:              {rmd:6.2f} g N/kg TM")

    lines.append("---- LP-Harteverletzungen ----")
    if not hard:
        lines.append("  (keine)")
    for h in hard[:6]:
        lines.append(f"  HARD: {h.get('name')}  ist={h.get('actual')}  soll={h.get('target')}")
    lines.append("---- LP-Weichverletzungen (Penalty) ----")
    if not soft:
        lines.append("  (keine)")
    for s in soft[:6]:
        lines.append(
            f"  soft: {s.get('name')}  ist={s.get('actual')}  soll={s.get('target')}  "
            f"penalty={s.get('penalty_cost')}"
        )
    lines.append(
        f"Penalty-Summary: total={summary.get('total_cost', 0.0):.3f}  "
        f"A={summary.get('class_a_violations', 0)}  "
        f"B={summary.get('class_b_violations', 0)}  "
        f"C={summary.get('class_c_violations', 0)}"
    )
    warnings = result.get("warnings") or []
    if warnings:
        lines.append("---- Warnungen ----")
        for w in warnings[:8]:
            lines.append(f"  ! {w}")

    sara = result.get("sara_safety_reopt") or {}
    if sara.get("triggered"):
        lines.append("---- SARA-Safety-Reopt ----")
        lines.append(f"  Ausloeser: {sara.get('reason')}")
        lines.append(f"  resolved:  {sara.get('resolved')}")
        lines.append(f"  Hinweis:   {sara.get('resolution_note')}")
        for a in (sara.get("actions") or [])[:6]:
            lines.append(f"  - Massnahme: {a}")
        mb = sara.get("metrics_before") or {}
        ma = sara.get("metrics_after") or {}
        if mb and ma:
            lines.append(
                f"  vorher:  pH={mb.get('ph_predicted')}  peNDF={mb.get('pendf_kgdm')}  "
                f"pabKH={mb.get('pabkh_kgdm')}  Staerke={mb.get('starch_kgdm')}"
            )
            lines.append(
                f"  nachher: pH={ma.get('ph_predicted')}  peNDF={ma.get('pendf_kgdm')}  "
                f"pabKH={ma.get('pabkh_kgdm')}  Staerke={ma.get('starch_kgdm')}"
            )

    ration = result.get("ration") or []
    if ration:
        lines.append("---- Ration (kg TM/d) ----")
        for item in ration[:12]:
            name = item.get("name") or item.get("id", "?")
            kgdm = item.get("kgdm") or item.get("amount_kgdm") or 0.0
            lines.append(f"  {name:<42s} {kgdm:6.2f} kg TM")
    lines.append("")
    return lines


def _base_profile_holstein(milk: float = 35.0) -> Dict[str, Any]:
    return {
        "breed": "Deutsche Holstein",
        "body_weight_kg": 670.0,
        "milk_kg_day": milk,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 100,
        "parity": 2,
        "production_group": "Hochleistung",
    }


def run_variants() -> None:
    variants: List[Dict[str, Any]] = []

    # Variante A: TMR Standard, 35 kg Milch – sollte GRUEN sein
    variants.append({
        "title": "A) TMR Standard 35 kg Milch (baseline)",
        "profile": {**_base_profile_holstein(35.0), "feeding_type": "TMR"},
    })

    # Variante B: TMR Hochleistung 48 kg – peNDF knapp, Azidose-Risiko moeglich
    variants.append({
        "title": "B) TMR Hochleistung 48 kg Milch (Stress-Test peNDF)",
        "profile": {
            **_base_profile_holstein(48.0),
            "body_weight_kg": 680.0,
            "feeding_type": "TMR",
        },
    })

    # Variante C: PMR+Weide Fruehlingsweide (Bruder-Regression)
    variants.append({
        "title": "C) PMR+Weide Fruehjahr spring_mid (Bruder-Regression)",
        "profile": {
            **_base_profile_holstein(28.0),
            "feeding_type": "PMR+Weide",
            "season_profile": "spring_mid",
        },
    })

    # Variante D: PMR+Weide Sommer Hitze mid – automatisch NaHCO3 + DMI-Kuerzung
    variants.append({
        "title": "D) PMR+Weide Sommer Hitze summer_mid (Auto-Buffer-Injection)",
        "profile": {
            **_base_profile_holstein(28.0),
            "feeding_type": "PMR+Weide",
            "season_profile": "summer_mid",
        },
    })

    # Variante E: PMR+Weide Hochsommer late – staerkste Hitze-Reduktion
    variants.append({
        "title": "E) PMR+Weide Hochsommer summer_late (Extremhitze)",
        "profile": {
            **_base_profile_holstein(25.0),
            "feeding_type": "PMR+Weide",
            "season_profile": "summer_late",
        },
    })

    # Variante F: PMR+Weide Herbst – N-reicher Grasaufwuchs
    variants.append({
        "title": "F) PMR+Weide Herbst autumn (N-reicher Aufwuchs)",
        "profile": {
            **_base_profile_holstein(28.0),
            "feeding_type": "PMR+Weide",
            "season_profile": "autumn",
        },
    })

    # Variante G: Provokation – Hochleistung mit stark KF-lastigem Futtermix
    # DLG-IDs: Maissilage mittlere OMD, Gerste-Korn, Mais-Korn, Weizen-Korn,
    # Raps-Extraktionsschrot, Soja-Extraktionsschrot, Stroh (peNDF-Anker).
    variants.append({
        "title": "G) Provokation: 45 kg Milch, sehr KF-lastig (Maissilage + viel Getreide)",
        "profile": {
            **_base_profile_holstein(45.0),
            "body_weight_kg": 680.0,
            "feeding_type": "TMR",
        },
        "feed_ids": [
            "dlg_10500020",   # Mais-Ganzpflanze mittlere OMD (Maissilage)
            "dlg_30820030",   # Gerste Samen
            "dlg_30880030",   # Mais Korn
            "dlg_31190030",   # Weizen Samen
            "dlg_30970130",   # Raps-Extraktionsschrot
            "dlg_31050130",   # Soja-Extraktionsschrot
            "dlg_10610000",   # Gerstenstroh (peNDF-Anker)
            "special_weide_mg_mineral",
            "special_summer_rumen_buffer",
        ],
    })

    # Variante H: SARA-Trigger – Maissilage + viel Getreide, OHNE Gerstenstroh
    # peNDF rutscht unter das stärkeabhängige Minimum, pabKH steigt deutlich.
    variants.append({
        "title": "H) SARA-Trigger: 42 kg Milch, Maissilage + viel Getreide, OHNE Heu/Stroh",
        "profile": {
            **_base_profile_holstein(42.0),
            "body_weight_kg": 680.0,
            "feeding_type": "TMR",
        },
        "feed_ids": [
            "dlg_10500020",   # Maissilage
            "dlg_30820030",   # Gerste
            "dlg_30880030",   # Mais-Korn
            "dlg_31190030",   # Weizen-Korn
            "dlg_30970130",   # Raps-Extraktionsschrot
            "dlg_31050130",   # Soja-Extraktionsschrot
            "special_weide_mg_mineral",
            "special_summer_rumen_buffer",
        ],
    })

    print("\nAmpel/Azidose-Simulation – VALEO NeuroERP Rationsoptimierung\n")
    print(
        "Interpretation: pH GRUEN >= 6.2, GELB 5.9..6.2, ROT < 5.9 (SARA).\n"
        "peNDF GRUEN >= min+5, GELB min..min+5, ROT < min.\n"
    )

    for variant in variants:
        title = variant["title"]
        profile = copy.deepcopy(variant["profile"])
        try:
            opts = _resolve_runtime_options(profile)
            result = _optimize_internal(
                profile,
                feed_ids=variant.get("feed_ids"),
                runtime_options=opts,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"===== {title} =====")
            print(f"FEHLER: {exc!r}\n")
            continue
        for line in _summary_block(title, result):
            print(line)


if __name__ == "__main__":
    run_variants()
