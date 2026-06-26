"""SEMANTIC-ACTION-MATRIX-002 — Vergleicht Action-Matrices mit route-inventory und erzeugt Bericht.

Verwendung:
    python scripts/generate_action_matrix_report.py [--check]

--check: Exit 1 wenn Top-50-Routen ohne Matrix-Eintrag gefunden werden.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml  # PyYAML

REPO = Path(__file__).parent.parent
MATRIX_DIR = REPO / "docs/quality-assurance/action-matrices"
ROUTE_INVENTORY = REPO / "packages/frontend-web/src/app/routing/route-inventory.gen.json"
DOCS_HELP = REPO / "packages/frontend-web/src/lib/docs-help.ts"
OUTPUT_MD = REPO / "docs/quality-assurance/action-matrix-report.md"


def load_matrices() -> list[dict]:
    matrices = []
    for f in sorted(MATRIX_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if data and "chain_id" in data:
                matrices.append(data)
        except Exception as e:
            print(f"Warnung: {f.name} nicht parsebar: {e}", file=sys.stderr)
    return matrices


def load_route_prefixes() -> set[str]:
    if not ROUTE_INVENTORY.exists():
        return set()
    data = json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8"))
    return {r.get("path", "") for r in data.get("routes", []) if r.get("path")}


def load_top50_prefixes() -> list[str]:
    if not DOCS_HELP.exists():
        return []
    text = DOCS_HELP.read_text(encoding="utf-8")
    prefixes = []
    for line in text.splitlines():
        if '": {' in line and "docPath" not in line:
            # Extract key from: "  "prefix": { ..."
            part = line.strip().strip('"').split('"')[0]
            if part and "/" in part:
                prefixes.append(part)
        elif line.strip().startswith('"') and '":{' not in line and ": {" in line:
            key = line.strip().split('"')[1]
            if key and "/" in key:
                prefixes.append(key)
    # Simpler: extract all quoted keys with slashes
    import re
    found = re.findall(r'"([a-z][a-z0-9/_-]+)":\s*\{', text)
    return [f for f in found if "/" in f][:50]


def build_report(matrices: list[dict], route_prefixes: set[str]) -> dict:
    all_actions = []
    for m in matrices:
        for a in m.get("actions", []):
            a["chain_id"] = m["chain_id"]
            a["chain_name"] = m["chain_name"]
            all_actions.append(a)

    # Top-50 aus docs-help
    top50 = load_top50_prefixes()

    # Welche Top-50-Routen haben KEINEN Matrix-Eintrag?
    covered_prefixes = {a["route_prefix"] for a in all_actions}
    missing_in_matrix = [
        p for p in top50
        if not any(p == cp or p.startswith(cp + "/") or cp.startswith(p)
                   for cp in covered_prefixes)
    ]

    green = [a for a in all_actions if a.get("status") == "green"]
    partial = [a for a in all_actions if a.get("status") == "partial"]
    gaps = [a for a in all_actions if a.get("status") == "gap"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "chains": len(matrices),
        "total_actions": len(all_actions),
        "green": len(green),
        "partial": len(partial),
        "gap": len(gaps),
        "top50_missing_matrix": missing_in_matrix,
        "all_actions": all_actions,
        "matrices": matrices,
    }


def build_markdown(report: dict) -> str:
    ts = report["generated_at"][:19].replace("T", " ") + " UTC"
    lines = [
        "---",
        "title: Action-Matrix-Report (SEMANTIC-ACTION-MATRIX-002)",
        "description: Übersicht aller semantischen Prozessketten und E2E-Coverage-Status.",
        "type: reference",
        "audience: [qa, entwickler]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {datetime.now(timezone.utc).date().isoformat()}",
        "version: 3.0.0",
        "---",
        "",
        "# Action-Matrix-Report",
        "",
        f"> Generiert via `scripts/generate_action_matrix_report.py` · {ts}",
        "",
        "## Übersicht",
        "",
        "| Metrik | Wert |",
        "|---|---|",
        f"| Prozessketten | {report['chains']} |",
        f"| Aktionen gesamt | {report['total_actions']} |",
        f"| Green (E2E @critical/@smoke grün) | {report['green']} |",
        f"| Partial (E2E vorhanden, nicht @critical) | {report['partial']} |",
        f"| Gap (keine E2E) | {report['gap']} |",
        "",
    ]

    for m in report["matrices"]:
        lines += [
            f"## {m['chain_name']} (`{m['chain_id']}`)",
            "",
            f"> {m.get('description', '')}",
            f"> Priorität: **{m.get('priority', '?').upper()}**",
            "",
            "| ID | Aktion | Route | Status | E2E-Tag |",
            "|---|---|---|---|---|",
        ]
        for a in m.get("actions", []):
            status_icon = {"green": "GREEN", "partial": "PARTIAL", "gap": "GAP"}.get(a.get("status", ""), "?")
            lines.append(
                f"| `{a['action_id']}` | {a['label']} | `{a['route_prefix']}` | {status_icon} | `{a.get('e2e_tag', '-')}` |"
            )
        gaps = m.get("open_gaps", [])
        if gaps:
            lines += ["", "**Offene Gaps:**", ""]
            for g in gaps:
                lines.append(f"- {g}")
        lines.append("")

    if report["top50_missing_matrix"]:
        lines += [
            "## Top-50-Routen ohne Matrix-Eintrag",
            "",
        ]
        for p in report["top50_missing_matrix"]:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append(f"*Stand: {ts} · {report['total_actions']} Aktionen · Slice: SEMANTIC-ACTION-MATRIX-002*")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Exit 1 wenn Top-50-Routen ohne Matrix")
    args = parser.parse_args()

    matrices = load_matrices()
    if not matrices:
        print("Keine Action-Matrix-YAMLs gefunden.", file=sys.stderr)
        return 1

    route_prefixes = load_route_prefixes()
    report = build_report(matrices, route_prefixes)
    md = build_markdown(report)
    OUTPUT_MD.write_text(md, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT_MD} ({report['total_actions']} Aktionen, {report['gap']} Gaps)")

    if args.check and report["top50_missing_matrix"]:
        print(f"FEHLER: {len(report['top50_missing_matrix'])} Top-50-Routen ohne Matrix-Eintrag", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
