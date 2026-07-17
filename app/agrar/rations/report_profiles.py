"""Profilierte, deterministische Berichtsinhalte (FEED-REP-039).

Reine Funktionen: gleicher Quellzustand + Profil ergibt exakt denselben
Inhalt (und damit denselben content_hash) — keine Zeitstempel im Inhalt,
Erzeugungszeit liegt am Report-Datensatz. Profile:
  feeder  = Mischreihenfolge und Mengen, ohne Preise/Quellendetails
  farmer  = feeder + Gruppe, Tierzahl, Gueltigkeitsfenster
  advisor = farmer + Quellhinweise (Planversion, Rationsversion, Grund)
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

REPORT_PROFILES = ("farmer", "advisor", "feeder")


def content_hash(content: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(content, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _loads(plan_version: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "sequence": item["sequence"],
        "feed_name": item["feed_name"],
        "kg_fm_per_animal": (float(item["kg_fm_per_animal"])
                             if item["kg_fm_per_animal"] is not None else None),
        "target_batch_kg": (float(item["target_batch_kg"])
                            if item["target_batch_kg"] is not None else None),
    } for item in plan_version["instructions"]]


def build_feeding_plan_report(plan_version: dict[str, Any], profile: str) -> dict[str, Any]:
    if profile not in REPORT_PROFILES:
        raise ValueError(f"Unbekanntes Berichtsprofil: {profile}")

    content: dict[str, Any] = {
        "report_type": "feeding_plan",
        "profile": profile,
        "title": f"Fuetterungsplan {plan_version['name']} (Version {plan_version['version_no']})",
        "loads": _loads(plan_version),
    }
    if profile in {"farmer", "advisor"}:
        content["group_name"] = plan_version["group_name"]
        content["animal_count"] = plan_version["animal_count"]
        content["valid_from"] = str(plan_version["valid_from"])
        content["valid_until"] = (str(plan_version["valid_until"])
                                  if plan_version["valid_until"] else None)
    if profile == "advisor":
        content["source"] = {
            "plan_version_id": plan_version["id"],
            "plan_id": plan_version["plan_id"],
            "source_ration_version_id": plan_version["source_ration_version_id"],
            "reason": plan_version.get("reason"),
        }
    return content


def feeding_plan_csv(content: dict[str, Any]) -> str:
    lines = ["sequence;feed_name;kg_fm_per_animal;target_batch_kg"]
    for load in content["loads"]:
        lines.append(";".join([
            str(load["sequence"]),
            str(load["feed_name"]),
            "" if load["kg_fm_per_animal"] is None else f"{load['kg_fm_per_animal']:.3f}",
            "" if load["target_batch_kg"] is None else f"{load['target_batch_kg']:.3f}",
        ]))
    return "\n".join(lines) + "\n"


# ── Berichtspaket 2 (FEED-REP-040) ──────────────────────────────────────────

def _require_reader_profile(report_label: str, profile: str) -> None:
    """consulting/target_actual/trend richten sich an farmer/advisor;
    ein Fuetterer-Profil existiert fachlich nicht (Kap. 6.14)."""
    if profile not in {"farmer", "advisor"}:
        raise ValueError(
            f"Profil '{profile}' ist fuer {report_label} nicht anwendbar "
            "(zulaessig: farmer, advisor)."
        )


# Interne Steuerfelder der Massnahmenverfolgung, die nur der Berater sieht.
_MEASURE_INTERNAL_FIELDS = ("owner_subject", "reminder_date", "escalation_status")


def build_consulting_report(draft: dict[str, Any], profile: str) -> dict[str, Any]:
    _require_reader_profile("Beratungsberichte", profile)
    draft_content = draft["content"]
    content: dict[str, Any] = {
        "report_type": "consulting",
        "profile": profile,
        "title": f"Beratungsbericht {draft_content['case'].get('title')}",
        "case": draft_content["case"],
        "observations": draft_content["observations"],
        "measures": draft_content["measures"],
    }
    if profile == "farmer":
        content["measures"] = [
            {key: value for key, value in measure.items()
             if key not in _MEASURE_INTERNAL_FIELDS}
            for measure in draft_content["measures"]
        ]
    if profile == "advisor":
        content["source"] = {
            "draft_id": draft["id"],
            "draft_version": draft["version"],
            "case_id": draft["case_id"],
        }
    return content


def build_target_actual_report(plan_version: dict[str, Any],
                               aggregation: dict[str, Any],
                               profile: str) -> dict[str, Any]:
    _require_reader_profile("Soll-Ist-Berichte", profile)
    content: dict[str, Any] = {
        "report_type": "target_actual",
        "profile": profile,
        "title": (f"Soll-Ist-Bericht {plan_version['name']} "
                  f"(Planversion {plan_version['version_no']})"),
        "group_name": plan_version["group_name"],
        "record_count": aggregation["record_count"],
        "components": aggregation["components"],
    }
    if profile == "advisor":
        content["cause_breakdown"] = aggregation["cause_breakdown"]
        content["source"] = {
            "plan_version_id": plan_version["id"],
            "plan_id": plan_version["plan_id"],
            "source_ration_version_id": plan_version["source_ration_version_id"],
        }
    return content


_TREND_FARMER_FIELDS = (
    "observation_date", "cow_count", "actual_milk_kg_cow", "actual_dmi_kg_cow",
    "actual_fat_pct", "actual_protein_pct",
)
_TREND_ADVISOR_FIELDS = _TREND_FARMER_FIELDS + (
    "ration_version_no", "plan_version_no", "source",
)


def build_trend_report(group: dict[str, Any], days: list[dict[str, Any]],
                       profile: str) -> dict[str, Any]:
    _require_reader_profile("Verlaufsberichte", profile)
    fields = _TREND_ADVISOR_FIELDS if profile == "advisor" else _TREND_FARMER_FIELDS
    content: dict[str, Any] = {
        "report_type": "trend",
        "profile": profile,
        "title": f"Verlaufsbericht {group['name']}",
        "group_name": group["name"],
        "days": [{key: day.get(key) for key in fields} for day in days],
    }
    if profile == "advisor":
        content["source"] = {"group_id": group["id"]}
    return content


def build_benchmark_report(group: dict[str, Any], benchmark: dict[str, Any],
                           period_comparison: dict[str, Any],
                           profile: str) -> dict[str, Any]:
    """Benchmark-Bericht (FEED-PERF-044): tenant-interner Gruppenvergleich +
    Zeitraumvergleich. Advisor sieht zusaetzlich die Stichprobenkontexte."""
    _require_reader_profile("Benchmark-Berichte", profile)
    content: dict[str, Any] = {
        "report_type": "benchmark",
        "profile": profile,
        "title": f"Benchmark {group['name']}",
        "group_id": group["id"],
        "group_name": group["name"],
        "benchmark": {
            "scope": benchmark["scope"],
            "window_days": benchmark["window_days"],
            "peer_group_count": benchmark["peer_group_count"],
            "metrics": benchmark["metrics"],
            "confidence": benchmark["confidence"],
        },
        "period_comparison": {
            "period_days": period_comparison["period_days"],
            "delta": period_comparison["delta"],
            "confidence": period_comparison["confidence"],
        },
    }
    if profile == "advisor":
        content["benchmark"]["n"] = benchmark["n"]
        content["period_comparison"]["current"] = period_comparison["current"]
        content["period_comparison"]["previous"] = period_comparison["previous"]
        content["source"] = {"group_id": group["id"]}
    return content


def benchmark_csv(content: dict[str, Any]) -> str:
    lines = ["metric;group_avg;peer_median;delta;period_delta"]
    period_delta = content["period_comparison"]["delta"]
    for metric, values in content["benchmark"]["metrics"].items():
        lines.append(";".join([
            metric,
            "" if values["group_avg"] is None else f"{values['group_avg']:.3f}",
            "" if values["peer_median"] is None else f"{values['peer_median']:.3f}",
            "" if values["delta"] is None else f"{values['delta']:.3f}",
            "" if period_delta.get(metric) is None else f"{period_delta[metric]:.3f}",
        ]))
    return "\n".join(lines) + "\n"


def target_actual_csv(content: dict[str, Any]) -> str:
    lines = ["feed_id;feed_name;n;target_kg_sum;actual_kg_sum;delta_kg_sum"]
    for line in content["components"]:
        lines.append(";".join([
            str(line["feed_id"]),
            "" if line["feed_name"] is None else str(line["feed_name"]),
            str(line["n"]),
            f"{line['target_kg_sum']:.3f}",
            f"{line['actual_kg_sum']:.3f}",
            f"{line['delta_kg_sum']:.3f}",
        ]))
    return "\n".join(lines) + "\n"


def trend_csv(content: dict[str, Any]) -> str:
    lines = [";".join(_TREND_FARMER_FIELDS)]
    for day in content["days"]:
        lines.append(";".join(
            "" if day.get(key) is None else str(day[key])
            for key in _TREND_FARMER_FIELDS
        ))
    return "\n".join(lines) + "\n"
