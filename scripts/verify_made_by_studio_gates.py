#!/usr/bin/env python3
"""Batch-Verifier für Made-by-Studio-Gates A–C und E auf allen registrierten ScreenDefinitions.

    python scripts/verify_made_by_studio_gates.py              # stdout-Zusammenfassung
    python scripts/verify_made_by_studio_gates.py --json f.json
    python scripts/verify_made_by_studio_gates.py --write-report  # Gate-Report nach docs/

Exit 0 wenn alle Gates A/B/C/E grün, sonst 1 (reine Messung, ändert keine Masken).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.made_by_studio_gates import (  # noqa: E402
    evaluate_all,
    markdown_report,
    summarize,
)

REPORT_PATH = ROOT / "docs" / "architecture" / "uix" / "made-by-studio-gate-report.md"


def _serialize(reports) -> dict:
    return {
        "summary": summarize(reports),
        "screens": [
            {
                "screen_id": r.screen_id,
                "layout_kind": r.layout_kind,
                "gates": {
                    k: {"passed": v.passed, "issues": v.issues, "metrics": v.metrics}
                    for k, v in r.gates.items()
                },
                "studio_draft_violations": r.studio_draft_violations,
            }
            for r in reports
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json", type=Path, help="Vollständiges Ergebnis als JSON")
    parser.add_argument("--write-report", action="store_true", help=f"Markdown nach {REPORT_PATH.relative_to(ROOT)}")
    args = parser.parse_args(argv)

    reports = evaluate_all()
    summary = summarize(reports)
    stand = date.today().isoformat()

    if args.json:
        args.json.write_text(json.dumps(_serialize(reports), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(markdown_report(reports, stand=stand), encoding="utf-8")

    total = summary["total"]
    print(
        f"Made-by-Studio Gates — {total} ScreenDefinitions: "
        f"A={summary['passed']['A']} B={summary['passed']['B']} "
        f"C={summary['passed']['C']} E={summary['passed']['E']} "
        f"(Draft-clean={summary['studio_draft_clean']}, advisory Ø={summary['advisory_score_avg']})"
    )
    for gate in ("A", "B", "C", "E"):
        failed = summary["failed_ids"][gate]
        if failed:
            print(f"  Gate {gate} offen ({len(failed)}): " + ", ".join(failed[:8]) + (" …" if len(failed) > 8 else ""))

    all_green = all(summary["passed"][g] == total for g in ("A", "B", "C", "E"))
    if args.write_report:
        print(f"Report: {REPORT_PATH}")
    return 0 if all_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
