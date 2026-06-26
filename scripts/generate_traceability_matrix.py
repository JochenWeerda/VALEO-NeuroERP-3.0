"""TRACEABILITY-MATRIX-001 — Erzeugt Slice↔Test↔Doku-Verknüpfungsmatrix.

Liest alle docs/agent-ops/slices/*.yaml und verknüpft mit:
- Tests: sucht nach Slice-ID in tests/**/*.py und playwright-tests/**/*.spec.ts
- Doku: dateibesitz-Einträge aus Slice-YAML

Ausgabe: docs/quality-assurance/traceability-matrix.md

Verwendung:
    python scripts/generate_traceability_matrix.py [--min-coverage 0.95]
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REPO = Path(__file__).parent.parent
SLICES_DIR = REPO / "docs/agent-ops/slices"
TESTS_DIR = REPO / "tests"
PLAYWRIGHT_DIR = REPO / "playwright-tests"
OUTPUT = REPO / "docs/quality-assurance/traceability-matrix.md"

# Nur Slices der letzten N Tage betrachten (via created-Datum oder Dateimod)
RECENCY_DAYS = 90


def _parse_slice(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")

    if HAS_YAML:
        try:
            data = yaml.safe_load(text)
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            pass

    # Fallback: einfaches Regex-Parsing
    def _field(key: str) -> str:
        m = re.search(rf'^{key}:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
        return m.group(1).strip() if m else ""

    files = re.findall(r'^\s*-\s+(.+?)\s*$', text, re.MULTILINE)

    return {
        "slice_id": _field("slice_id"),
        "title": _field("title"),
        "status": _field("status"),
        "created": _field("created"),
        "dateibesitz": [f.strip() for f in files if "/" in f],
    }


def find_test_references(slice_id: str) -> list[str]:
    refs = []
    pattern = re.compile(re.escape(slice_id), re.IGNORECASE)
    for test_dir in [TESTS_DIR, PLAYWRIGHT_DIR]:
        if not test_dir.exists():
            continue
        for ext in ["*.py", "*.spec.ts", "*.test.ts"]:
            for f in test_dir.rglob(ext):
                if "__pycache__" in str(f):
                    continue
                try:
                    if pattern.search(f.read_text(encoding="utf-8", errors="replace")):
                        refs.append(str(f.relative_to(REPO)).replace("\\", "/"))
                except Exception:
                    pass
    return refs


def load_slices() -> list[dict]:
    slices = []
    for path in sorted(SLICES_DIR.glob("*.yaml")):
        data = _parse_slice(path)
        if data and data.get("slice_id"):
            data["_file"] = path.name
            slices.append(data)
    for path in sorted(SLICES_DIR.glob("*.yml")):
        data = _parse_slice(path)
        if data and data.get("slice_id"):
            data["_file"] = path.name
            slices.append(data)
    return slices


def build_matrix(slices: list[dict]) -> list[dict]:
    rows = []
    for s in slices:
        sid = s.get("slice_id", "?")
        tests = find_test_references(sid)
        docs = [f for f in s.get("dateibesitz", []) if f.endswith(".md") or "docs/" in f]
        rows.append({
            "slice_id": sid,
            "title": s.get("title", ""),
            "status": s.get("status", "?"),
            "created": s.get("created", ""),
            "tests": tests,
            "docs": docs,
            "has_test": len(tests) > 0,
            "has_doc": len(docs) > 0,
            "covered": len(tests) > 0 and len(docs) > 0,
        })
    return rows


def build_markdown(rows: list[dict]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    completed = [r for r in rows if r["status"] in ("abgeschlossen", "completed", "done")]
    covered = [r for r in completed if r["covered"]]
    coverage = len(covered) / len(completed) if completed else 0.0

    lines = [
        "---",
        "title: Traceability-Matrix (TRACEABILITY-MATRIX-001)",
        "description: Slice↔Test↔Doku-Verknüpfungsmatrix für alle bekannten Slices.",
        "type: reference",
        "audience: [qa, lead, entwickler]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {datetime.now(timezone.utc).date().isoformat()}",
        "version: 3.0.0",
        "---",
        "",
        "# Traceability-Matrix",
        "",
        f"> Generiert via `scripts/generate_traceability_matrix.py` · {ts}",
        "",
        "## Zusammenfassung",
        "",
        "| Metrik | Wert |",
        "|---|---|",
        f"| Slices gesamt | {len(rows)} |",
        f"| Abgeschlossene Slices | {len(completed)} |",
        f"| Mit Test + Doku | {len(covered)} |",
        f"| Coverage | **{coverage:.0%}** |",
        "",
    ]

    # Abgeschlossene Slices
    lines += [
        "## Abgeschlossene Slices",
        "",
        "| Slice | Titel | Tests | Doku | Status |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(completed, key=lambda x: x["slice_id"]):
        test_count = len(r["tests"])
        doc_count = len(r["docs"])
        status = "OK" if r["covered"] else ("WARN" if r["has_test"] or r["has_doc"] else "GAP")
        lines.append(
            f"| `{r['slice_id']}` | {r['title'][:50]} | {test_count} | {doc_count} | {status} |"
        )
    lines.append("")

    # Lücken
    gaps = [r for r in completed if not r["covered"]]
    if gaps:
        lines += [
            "## Offene Lücken (abgeschlossen ohne Test oder Doku)",
            "",
        ]
        for r in gaps:
            lines.append(f"- `{r['slice_id']}`: tests={len(r['tests'])}, docs={len(r['docs'])}")
        lines.append("")

    # In-Progress Slices
    in_progress = [r for r in rows if r["status"] not in ("abgeschlossen", "completed", "done")]
    if in_progress:
        lines += [
            "## In Arbeit / Offen",
            "",
            "| Slice | Status |",
            "|---|---|",
        ]
        for r in sorted(in_progress, key=lambda x: x["slice_id"]):
            lines.append(f"| `{r['slice_id']}` | {r['status']} |")
        lines.append("")

    lines.append(f"*Stand: {ts} · {len(rows)} Slices · Coverage {coverage:.0%} · Slice: TRACEABILITY-MATRIX-001*")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-coverage", type=float, default=None,
                        help="Exit 1 wenn Coverage unter Schwellwert (0.0-1.0)")
    args = parser.parse_args()

    slices = load_slices()
    if not slices:
        print("Keine Slice-YAMLs gefunden.", file=sys.stderr)
        return 1

    print(f"Geladen: {len(slices)} Slices")
    rows = build_matrix(slices)
    md = build_markdown(rows)
    OUTPUT.write_text(md, encoding="utf-8")

    completed = [r for r in rows if r["status"] in ("abgeschlossen", "completed", "done")]
    covered = [r for r in completed if r["covered"]]
    coverage = len(covered) / len(completed) if completed else 0.0
    print(f"Geschrieben: {OUTPUT} ({len(completed)} abgeschl., Coverage {coverage:.0%})")

    if args.min_coverage is not None and coverage < args.min_coverage:
        print(f"FEHLER: Coverage {coverage:.0%} < Schwellwert {args.min_coverage:.0%}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
