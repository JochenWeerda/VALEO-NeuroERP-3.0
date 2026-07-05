#!/usr/bin/env python3
"""Validiert die Audit-Kontrollmatrizen auf Vollstaendigkeit/Konsistenz (AUDIT-1/2).

Fail-closed: eine unvollstaendige oder verdikt-lose Matrix darf nicht als
Readiness-Evidenz durchgehen.

Prueft:
- ISO-27001 Annex A: genau 93 Controls, jedes mit Verdikt aus zulaessiger Menge,
  external_gate-Controls haben eine Begruendung, referenzierte Evidenz-Repo-Pfade
  existieren (soweit als Datei/Verzeichnis angebbar).
- SOC-2 TSC: alle Pflicht-Common-Criteria-Serien (CC1..CC9) vertreten, jedes
  Kriterium mit Status; external_gate mit Begruendung.

Nutzung: python scripts/check_audit_matrices.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ISO = REPO_ROOT / "config" / "audit" / "iso27001-annex-a-matrix.yaml"
SOC2 = REPO_ROOT / "config" / "audit" / "soc2-tsc-matrix.yaml"

# "conform" (ISO-Sprech) und "pass" (SOC-2/Assessor-Sprech) sind aequivalent.
VALID_STATUS = {"conform", "pass", "minor", "major", "external_gate", "fail"}


def _load(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _evidence_paths(entry: dict) -> list[str]:
    raw = entry.get("evidenz") or entry.get("evidenzquelle") or []
    if isinstance(raw, str):
        # "a; b" oder "a" — nur eindeutige Repo-Pfade pruefen
        raw = [p.strip() for p in raw.replace(";", ",").split(",")]
    out = []
    for p in raw:
        p = str(p).split()[0].strip() if p else ""
        # nur klare Repo-Pfade (mit / und ohne Leerzeichen/Beschreibung)
        if p and "/" in p and " " not in p and not p.endswith(":"):
            out.append(p)
    return out


def check_iso(problems: list[str]) -> None:
    if not ISO.exists():
        problems.append(f"ISO-Matrix fehlt: {ISO.relative_to(REPO_ROOT)}")
        return
    data = _load(ISO)
    controls = data.get("controls", [])
    if len(controls) != 93:
        problems.append(f"ISO Annex A: {len(controls)} Controls (erwartet genau 93)")
    seen = set()
    for ctl in controls:
        cid = ctl.get("control_id", "?")
        if cid in seen:
            problems.append(f"ISO {cid}: doppelt")
        seen.add(cid)
        status = ctl.get("status")
        if status not in VALID_STATUS:
            problems.append(f"ISO {cid}: ungueltiger/fehlender Status {status!r}")
        if status == "external_gate" and not ctl.get("external_gate"):
            problems.append(f"ISO {cid}: external_gate ohne Begruendung")
        if ctl.get("anwendbar") is False and not ctl.get("begruendung_soa"):
            problems.append(f"ISO {cid}: SoA-Ausschluss ohne Begruendung")
        for ev in _evidence_paths(ctl):
            if not (REPO_ROOT / ev).exists():
                problems.append(f"ISO {cid}: Evidenzpfad existiert nicht: {ev}")


def check_soc2(problems: list[str]) -> None:
    if not SOC2.exists():
        problems.append(f"SOC-2-Matrix fehlt: {SOC2.relative_to(REPO_ROOT)}")
        return
    data = _load(SOC2)
    controls = data.get("controls", [])
    ids = {str(c.get("id", "")) for c in controls}
    for cc in range(1, 10):
        if not any(cid.startswith(f"CC{cc}") for cid in ids):
            problems.append(f"SOC-2: Common Criteria CC{cc} fehlt")
    for c in controls:
        cid = c.get("id", "?")
        status = c.get("status")
        if status not in VALID_STATUS:
            problems.append(f"SOC-2 {cid}: ungueltiger/fehlender Status {status!r}")
        if status == "external_gate" and not c.get("external_gate"):
            problems.append(f"SOC-2 {cid}: external_gate ohne Begruendung")
        for ev in _evidence_paths(c):
            if not (REPO_ROOT / ev).exists():
                problems.append(f"SOC-2 {cid}: Evidenzpfad existiert nicht: {ev}")


def main() -> int:
    problems: list[str] = []
    check_iso(problems)
    check_soc2(problems)
    if problems:
        print("FEHLER: Audit-Matrix-Validierung:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("OK: Audit-Matrizen vollstaendig und konsistent (ISO 93/93, SOC-2 CC1-CC9).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
