"""Deterministische Draft-Bewertung des Rationseditors (FEED-EDITOR-021).

Reine Funktion ohne Persistenz und ohne Solverlauf: Komponenten (kg FM) werden
ueber die kanonischen Solver-Feed-Daten (feed_catalog.build_solver_feed) zu
Positions- und Gesamtwerten verdichtet und gegen ein Bedarfsprofil verglichen.

Regeln (Lastenheft 6.8/7.1):
- Fehlende Naehrstoffwerte werden nie als 0 summiert; die Kennzahl wird je
  Futter als unvollstaendige Abdeckung ausgewiesen (coverage + Info-Befund).
- Befunde tragen Code, Schweregrad und verstaendlichen Text (nie nur Farbe).
- Gleiches Eingabebild liefert exakt dasselbe Ergebnis (reproduzierbar).
"""
from __future__ import annotations

from typing import Any, Mapping

# Kennzahl -> (Solver-Feed-Schluessel je kg TM, Einheit)
NUTRIENT_KEYS: dict[str, tuple[str, str]] = {
    "me_mj": ("me", "MJ"),
    "cp_g": ("cp", "g"),
    "sidp_g": ("sidp", "g"),
    "ndf_g": ("ndf", "g"),
    "starch_g": ("st", "g"),
    "sugar_g": ("zu", "g"),
}

# Toleranzen fuer Befunde: 2 % Unterdeckung gilt als Defizit, ab +10 % Ueberschuss.
DEFICIT_TOLERANCE = 0.98
SURPLUS_FACTOR = 1.10

# Vier Prioritaetsstufen (FEED-EDITOR-022, Maskenvertrag FEED-MASK-009):
# critical = fachlicher Blocker, high = Unterdeckung/Bandverletzung,
# medium = Auffaelligkeit (z. B. Ueberschuss), info = Hinweis/Datenqualitaet.
SEVERITY_ORDER: tuple[str, ...] = ("critical", "high", "medium", "info")

METRIC_LABELS = {
    "me_mj": "Energie (ME)",
    "sidp_g": "Protein (sidP)",
    "cp_g": "Rohprotein",
    "ndf_g": "NDF",
    "starch_g": "Staerke",
    "sugar_g": "Zucker",
    "dm_kg": "TM-Aufnahme",
}


def evaluate_draft(
    components: list[Mapping[str, Any]],
    feeds: Mapping[str, Mapping[str, Any]],
    requirements: Mapping[str, Any],
) -> dict[str, Any]:
    positions: list[dict[str, Any]] = []
    totals: dict[str, float] = {"dm_kg": 0.0, "fm_kg": 0.0, "cost_eur": 0.0}
    coverage: dict[str, dict[str, Any]] = {
        metric: {"complete": True, "missing_feed_ids": []} for metric in NUTRIENT_KEYS
    }
    for metric in NUTRIENT_KEYS:
        totals[metric] = 0.0

    for component in components:
        feed_id = str(component["feed_id"])
        feed = feeds.get(feed_id)
        if feed is None:
            raise LookupError(f"Futtermittel {feed_id} nicht gefunden.")
        kg_fm = float(component["kg_fm"])
        dm_frac = float(feed.get("dm_frac") or 0.0)
        kg_tm = kg_fm * dm_frac
        cost_eur = kg_tm * float(feed.get("price") or 0.0)

        position: dict[str, Any] = {
            "feed_id": feed_id,
            "name": str(feed.get("name") or feed_id),
            "kg_fm": kg_fm,
            "kg_tm": kg_tm,
            "cost_eur": cost_eur,
        }
        totals["fm_kg"] += kg_fm
        totals["dm_kg"] += kg_tm
        totals["cost_eur"] += cost_eur

        for metric, (key, _unit) in NUTRIENT_KEYS.items():
            raw = feed.get(key)
            if raw is None:
                coverage[metric]["complete"] = False
                coverage[metric]["missing_feed_ids"].append(feed_id)
                position[metric] = None
            else:
                contribution = kg_tm * float(raw)
                position[metric] = contribution
                totals[metric] += contribution

        positions.append(position)

    deltas = _build_deltas(totals, requirements)
    findings = _build_findings(totals, requirements, coverage)
    return {
        "positions": positions,
        "totals": totals,
        "coverage": coverage,
        "deltas": deltas,
        "findings": findings,
    }


def _build_deltas(totals: Mapping[str, float], requirements: Mapping[str, Any]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for metric, target_key in (("me_mj", "me_mj"), ("sidp_g", "sidp_g")):
        target = requirements.get(target_key)
        if target is not None:
            deltas.append({
                "metric": metric,
                "actual": totals[metric],
                "target": float(target),
                "delta": totals[metric] - float(target),
            })
    dmi_target = requirements.get("dmi_target_kg")
    if dmi_target is not None:
        deltas.append({
            "metric": "dm_kg",
            "actual": totals["dm_kg"],
            "target": float(dmi_target),
            "delta": totals["dm_kg"] - float(dmi_target),
        })
    return deltas


def _build_findings(
    totals: Mapping[str, float],
    requirements: Mapping[str, Any],
    coverage: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    dmi_min = requirements.get("dmi_min_kg")
    dmi_max = requirements.get("dmi_max_kg")
    dm_kg = totals["dm_kg"]
    if dmi_min is not None and dm_kg < float(dmi_min):
        findings.append(_finding(
            "dmi_below_band", "high", "dm_kg", dm_kg, float(dmi_min),
            f"TM-Aufnahme {dm_kg:.1f} kg liegt unter dem Band ({float(dmi_min):.1f}–{float(dmi_max or 0):.1f} kg): "
            "Ration traegt die Zielaufnahme nicht.",
        ))
    elif dmi_max is not None and dm_kg > float(dmi_max):
        findings.append(_finding(
            "dmi_above_band", "high", "dm_kg", dm_kg, float(dmi_max),
            f"TM-Aufnahme {dm_kg:.1f} kg liegt ueber dem Band (max. {float(dmi_max):.1f} kg): "
            "Menge reduzieren oder Band pruefen.",
        ))

    for metric, deficit_code, surplus_code in (
        ("me_mj", "energy_deficit", "energy_surplus"),
        ("sidp_g", "protein_deficit", "protein_surplus"),
    ):
        target = requirements.get(metric)
        if target is None:
            continue
        actual = totals[metric]
        target_f = float(target)
        label = METRIC_LABELS[metric]
        if actual < target_f * DEFICIT_TOLERANCE:
            findings.append(_finding(
                deficit_code, "high", metric, actual, target_f,
                f"{label}: {actual:.0f} deckt den Bedarf von {target_f:.0f} nicht — Unterdeckung "
                f"{target_f - actual:.0f}.",
            ))
        elif actual > target_f * SURPLUS_FACTOR:
            findings.append(_finding(
                surplus_code, "medium", metric, actual, target_f,
                f"{label}: {actual:.0f} liegt deutlich ueber dem Bedarf von {target_f:.0f} — "
                "Kosten und Stoffwechselbelastung pruefen.",
            ))

    for metric, state in coverage.items():
        if not state["complete"]:
            label = METRIC_LABELS.get(metric, metric)
            findings.append(_finding(
                f"{metric}_incomplete", "info", metric, totals[metric], None,
                f"{label}: Summe unvollstaendig — fuer {len(state['missing_feed_ids'])} Futtermittel "
                "fehlt der Analysewert (Teilsumme nur aus bekannten Beitraegen).",
            ))

    findings.sort(key=lambda finding: SEVERITY_ORDER.index(finding["severity"]))
    return findings


def _finding(code: str, severity: str, metric: str, actual: float,
             target: float | None, message: str) -> dict[str, Any]:
    return {"code": code, "severity": severity, "metric": metric,
            "actual": actual, "target": target, "message": message}
