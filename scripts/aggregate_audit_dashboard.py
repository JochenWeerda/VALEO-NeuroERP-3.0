#!/usr/bin/env python3
"""Audit-Dashboard-Aggregation (AUDIT-5).

Liest die Assessor-Simulation + Audit-Matrizen und erzeugt eine Ampel je
Standard (GoBD, DSFinV-K, ISO 27001, SOC 2, DSGVO, Technik/Betrieb).
External_gates werden gelistet, aber nie als "bestanden" gewertet.

Ausgabe: artifacts/audit/audit-dashboard.json + .md
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "artifacts" / "audit"
ASSESSORS = AUDIT_DIR / "assessors.json"
ISO = REPO_ROOT / "config" / "audit" / "iso27001-annex-a-matrix.yaml"
SOC2 = REPO_ROOT / "config" / "audit" / "soc2-tsc-matrix.yaml"

# Assessor-Profil-ID -> Dashboard-Standard
PROFILE_STANDARD = {
    "tax-gobd": "GoBD",
    "cash-register": "DSFinV-K/KassenSichV",
    "information-security": "ISO 27001 (Simulation)",
    "privacy": "DSGVO",
    "operations": "Technik/Betrieb",
    "soc2": "SOC 2",
}


def _ampel_from_statuses(statuses: list[str]) -> str:
    if any(s in ("fail", "major") for s in statuses):
        return "rot"
    if any(s == "external_gate" for s in statuses):
        return "gelb (external_gate offen)"
    if any(s == "minor" for s in statuses):
        return "gelb (minor)"
    return "gruen"


def main() -> int:
    dashboard = {"date": date.today().isoformat(), "standards": {}, "hinweis": "Simulation — external_gates werden nie als bestanden gewertet."}

    if ASSESSORS.exists():
        assessors = json.loads(ASSESSORS.read_text(encoding="utf-8"))
        for profile in assessors.get("profiles", []):
            std = PROFILE_STANDARD.get(profile["id"], profile["id"])
            statuses = [c["status"] for c in profile.get("checks", [])]
            dashboard["standards"][std] = {
                "profile_status": profile.get("status"),
                "ampel": _ampel_from_statuses(statuses),
                "checks": dict(Counter(statuses)),
                "external_gates": [c["id"] for c in profile.get("checks", []) if c["status"] == "external_gate"],
            }

    try:
        import yaml
        if ISO.exists():
            controls = yaml.safe_load(ISO.read_text(encoding="utf-8")).get("controls", [])
            st = [c.get("status") for c in controls]
            dashboard["standards"]["ISO 27001 Annex A (SoA)"] = {
                "controls": len(controls),
                "ampel": _ampel_from_statuses(st),
                "verdikte": dict(Counter(st)),
                "external_gates": sum(1 for s in st if s == "external_gate"),
            }
        if SOC2.exists():
            controls = yaml.safe_load(SOC2.read_text(encoding="utf-8")).get("controls", [])
            st = [c.get("status") for c in controls]
            dashboard["standards"]["SOC 2 TSC"] = {
                "controls": len(controls),
                "ampel": _ampel_from_statuses(st),
                "verdikte": dict(Counter(st)),
                "external_gates": sum(1 for s in st if s == "external_gate"),
            }
    except ImportError:
        dashboard["hinweis"] += " (PyYAML fehlt — Matrizen nicht aggregiert)"

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "audit-dashboard.json").write_text(json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = ["# Audit-Dashboard", "", f"Stand: {dashboard['date']}", "", f"> {dashboard['hinweis']}", "", "| Standard | Ampel | Detail |", "|---|---|---|"]
    for std, info in dashboard["standards"].items():
        detail = info.get("verdikte") or info.get("checks") or {}
        lines.append(f"| {std} | {info['ampel']} | {json.dumps(detail, ensure_ascii=False)} |")
    (AUDIT_DIR / "audit-dashboard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Audit-Dashboard geschrieben:")
    for std, info in dashboard["standards"].items():
        print(f"  {std:32s} {info['ampel']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
