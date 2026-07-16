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

        min_kg_fm = component.get("min_kg_fm")
        max_kg_fm = component.get("max_kg_fm")
        position: dict[str, Any] = {
            "feed_id": feed_id,
            "name": str(feed.get("name") or feed_id),
            "kg_fm": kg_fm,
            "kg_tm": kg_tm,
            "cost_eur": cost_eur,
            "min_kg_fm": float(min_kg_fm) if min_kg_fm is not None else None,
            "max_kg_fm": float(max_kg_fm) if max_kg_fm is not None else None,
            "dm_frac": dm_frac,
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
    findings = _build_bound_findings(positions, requirements)
    findings += _build_findings(totals, requirements, coverage)
    findings.sort(key=lambda finding: SEVERITY_ORDER.index(finding["severity"]))
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


def _build_bound_findings(
    positions: list[Mapping[str, Any]],
    requirements: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Strukturelle Grenzkonflikte VOR jedem Solverlauf benennen (FEED-EDITOR-024,
    Lastenheft 6.7: konfliktverursachende Grenzen benennen)."""
    findings: list[dict[str, Any]] = []

    for position in positions:
        name = position["name"]
        min_kg = position.get("min_kg_fm")
        max_kg = position.get("max_kg_fm")
        kg_fm = float(position["kg_fm"])
        if min_kg is not None and max_kg is not None and min_kg > max_kg:
            findings.append(_finding(
                "bounds_conflict", "critical", "bounds", min_kg, max_kg,
                f"{name}: Mindestmenge {min_kg:.1f} kg FM liegt ueber der Hoechstmenge "
                f"{max_kg:.1f} kg FM — Grenzen an dieser Position widersprechen sich.",
                feed_id=str(position["feed_id"]),
                remediation=f"Minimum fuer {name} auf hoechstens {max_kg:.1f} kg senken oder Maximum anheben.",
            ))
            continue
        if min_kg is not None and kg_fm < float(min_kg):
            findings.append(_finding(
                "amount_outside_bounds", "high", "bounds", kg_fm, float(min_kg),
                f"{name}: Menge {kg_fm:.1f} kg FM unterschreitet die Mindestmenge "
                f"{float(min_kg):.1f} kg FM.",
                feed_id=str(position["feed_id"]),
                remediation=f"Menge von {name} auf mindestens {float(min_kg):.1f} kg FM anheben oder Minimum lockern.",
            ))
        elif max_kg is not None and kg_fm > float(max_kg):
            findings.append(_finding(
                "amount_outside_bounds", "high", "bounds", kg_fm, float(max_kg),
                f"{name}: Menge {kg_fm:.1f} kg FM ueberschreitet die Hoechstmenge "
                f"{float(max_kg):.1f} kg FM.",
                feed_id=str(position["feed_id"]),
                remediation=f"Menge von {name} auf hoechstens {float(max_kg):.1f} kg FM senken oder Maximum anheben.",
            ))

    dmi_max = requirements.get("dmi_max_kg")
    if dmi_max is not None:
        bounded = [p for p in positions if p.get("min_kg_fm") is not None]
        min_dm_sum = sum(float(p["min_kg_fm"]) * float(p.get("dm_frac") or 0.0) for p in bounded)
        if bounded and min_dm_sum > float(dmi_max):
            names = ", ".join(str(p["name"]) for p in bounded)
            findings.append(_finding(
                "min_sum_exceeds_dmi_band", "critical", "dm_kg", min_dm_sum, float(dmi_max),
                f"Die Mindestmengen ({names}) ergeben zusammen {min_dm_sum:.1f} kg TM und "
                f"sprengen das TM-Band (max. {float(dmi_max):.1f} kg) — keine Loesung moeglich, "
                "Mindestgrenzen dieser Positionen lockern.",
                remediation=f"TM-wirksame Mindestgrenzen fuer {names} zusammen um mindestens {min_dm_sum - float(dmi_max):.1f} kg TM reduzieren.",
            ))

    return findings


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
             target: float | None, message: str, *, feed_id: str | None = None,
             remediation: str | None = None) -> dict[str, Any]:
    finding: dict[str, Any] = {"code": code, "severity": severity, "metric": metric,
                               "actual": actual, "target": target, "message": message}
    if feed_id is not None:
        finding["feed_id"] = feed_id
    if remediation is not None:
        finding["remediation"] = remediation
    return finding


# ── Variantenvergleich (FEED-EDITOR-023) ────────────────────────────────────

COMPARE_METRICS: tuple[str, ...] = ("dm_kg", "fm_kg", "cost_eur", *NUTRIENT_KEYS.keys())


def compare_drafts(base: Mapping[str, Any], variant: Mapping[str, Any]) -> dict[str, Any]:
    """Deterministischer Diff zweier Draft-Bewertungen (gleiches Bedarfsprofil).

    Entfernte/hinzugefuegte Komponenten behalten auf der fehlenden Seite
    ``None`` (unbekannt) — nie eine nullwertig guenstige 0 (FEED-MASK-010).
    Reihenfolge: Basisreihenfolge, danach Neuzugaenge der Variante.
    """
    base_positions = {p["feed_id"]: p for p in base["positions"]}
    variant_positions = {p["feed_id"]: p for p in variant["positions"]}

    component_diff: list[dict[str, Any]] = []
    ordered_ids = [p["feed_id"] for p in base["positions"]]
    ordered_ids += [p["feed_id"] for p in variant["positions"] if p["feed_id"] not in base_positions]

    for feed_id in ordered_ids:
        base_position = base_positions.get(feed_id)
        variant_position = variant_positions.get(feed_id)
        base_kg = float(base_position["kg_fm"]) if base_position else None
        variant_kg = float(variant_position["kg_fm"]) if variant_position else None
        if base_position and variant_position:
            change = "changed" if base_kg != variant_kg else "unchanged"
        elif base_position:
            change = "removed"
        else:
            change = "added"
        component_diff.append({
            "feed_id": feed_id,
            "name": str((variant_position or base_position or {}).get("name") or feed_id),
            "base_kg_fm": base_kg,
            "variant_kg_fm": variant_kg,
            "delta_kg_fm": (variant_kg - base_kg) if (base_kg is not None and variant_kg is not None) else None,
            "change": change,
        })

    metric_diff = [{
        "metric": metric,
        "label": METRIC_LABELS.get(metric, metric),
        "base": float(base["totals"].get(metric, 0.0)),
        "variant": float(variant["totals"].get(metric, 0.0)),
        "delta": float(variant["totals"].get(metric, 0.0)) - float(base["totals"].get(metric, 0.0)),
    } for metric in COMPARE_METRICS]

    return {
        "component_diff": component_diff,
        "metric_diff": metric_diff,
        "base_findings": list(base["findings"]),
        "variant_findings": list(variant["findings"]),
    }
