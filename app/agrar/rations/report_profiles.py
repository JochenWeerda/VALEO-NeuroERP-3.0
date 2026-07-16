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
