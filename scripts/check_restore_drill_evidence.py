#!/usr/bin/env python3
"""Fail-closed-Check: Existiert ein aktuelles Restore-Drill-Protokoll? (SPEC-P0-08)

Liest docs/operations/drill-protocols/restore-drill-*.json und bewertet:

  exit 0  — juengstes Protokoll vorhanden, status=passed, nicht aelter als --max-age-days
  exit 2  — KEIN Protokoll vorhanden => external_gate (Betreiber muss Drill fahren);
            fail-closed fuer Release-Gates, aber unterscheidbar von technischem Fehler
  exit 1  — Protokoll vorhanden, aber failed/rto_missed/zu alt/unlesbar

Nutzung:  python scripts/check_restore_drill_evidence.py [--max-age-days 90] [--strict]
          --strict behandelt auch exit 2 als Fehler (fuer Release-Gates).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = REPO_ROOT / "docs" / "operations" / "drill-protocols"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-age-days", type=int, default=90,
                        help="Maximales Alter des juengsten Drill-Protokolls (Default 90)")
    parser.add_argument("--strict", action="store_true",
                        help="Fehlendes Protokoll (external_gate) ebenfalls als Fehler werten")
    args = parser.parse_args()

    protocols = sorted(PROTO_DIR.glob("restore-drill-*.json")) if PROTO_DIR.exists() else []
    if not protocols:
        print(
            "EXTERNAL_GATE: Kein Restore-Drill-Protokoll unter docs/operations/drill-protocols/ — "
            "Betreiber muss scripts/run_restore_drill.sh gegen eine produktionsnahe Umgebung "
            "ausfuehren und das Protokoll committen (15-min-RTO-Nachweis)."
        )
        return 1 if args.strict else 2

    latest = protocols[-1]
    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FEHLER: Drill-Protokoll {latest.name} unlesbar: {exc}")
        return 1

    executed_raw = str(data.get("executed_at", ""))
    try:
        executed = dt.datetime.fromisoformat(executed_raw.replace("Z", "+00:00"))
    except ValueError:
        print(f"FEHLER: {latest.name}: executed_at fehlt oder ist kein ISO-Datum")
        return 1

    age_days = (dt.datetime.now(dt.timezone.utc) - executed).days
    status = data.get("status")
    rto_met = data.get("rto_met") is True

    problems = []
    if status != "passed":
        problems.append(f"status={status!r} (erwartet 'passed')")
    if not rto_met:
        problems.append("rto_met != true")
    if age_days > args.max_age_days:
        problems.append(f"Protokoll ist {age_days} Tage alt (max {args.max_age_days})")

    if problems:
        print(f"FEHLER: {latest.name}: " + "; ".join(problems))
        return 1

    print(f"OK: Restore-Drill-Evidenz aktuell — {latest.name} ({age_days} Tage alt, RTO erfuellt).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
