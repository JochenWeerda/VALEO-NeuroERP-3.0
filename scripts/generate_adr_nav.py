#!/usr/bin/env python3
"""Generiert den MkDocs-Nav-Block fuer alle ADRs unter Entwickler → ADRs.

Single Source of Truth sind die Markdown-Dateien in ``docs/adr/`` (ausser README).
Das Skript patcht ``mkdocs.yml`` zwischen den Markern ``# adr-nav:begin`` / ``# adr-nav:end``.

Verwendung:
    python scripts/generate_adr_nav.py
    python scripts/generate_adr_nav.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = REPO_ROOT / "docs" / "adr"
MKDOCS = REPO_ROOT / "mkdocs.yml"
BEGIN = "# adr-nav:begin"
END = "# adr-nav:end"


def extract_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def sort_key(path: Path) -> tuple[int, int, str]:
    stem = path.stem.lower()
    match = re.match(r"adr-(\d+)", stem)
    if match:
        return (0, int(match.group(1)), stem)
    match = re.match(r"adr-crm-(\d+)", stem)
    if match:
        return (1, int(match.group(1)), stem)
    return (2, 0, stem)


def yaml_quote(label: str) -> str:
    if any(ch in label for ch in ':"[]{}'):
        escaped = label.replace('"', '\\"')
        return f'"{escaped}"'
    return label


def render_nav_block(entries: list[tuple[str, str]]) -> str:
    lines = [
        f"      {BEGIN} (generated — scripts/generate_adr_nav.py; do not edit manually)",
        "      - ADRs:",
        "          - Index: adr/README.md",
    ]
    for label, rel_path in entries:
        lines.append(f"          - {yaml_quote(label)}: {rel_path}")
    lines.append(f"      {END}")
    return "\n".join(lines)


def collect_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for path in sorted(ADR_DIR.glob("*.md"), key=sort_key):
        if path.name.lower() == "readme.md":
            continue
        rel = f"adr/{path.name}"
        entries.append((extract_title(path), rel))
    return entries


def patch_mkdocs(block: str, content: str) -> str:
    pattern = re.compile(
        rf"^[ \t]*{re.escape(BEGIN)}.*?^[ \t]*{re.escape(END)}",
        re.MULTILINE | re.DOTALL,
    )
    if not pattern.search(content):
        raise RuntimeError(
            f"Marker {BEGIN!r}/{END!r} fehlen in {MKDOCS}. "
            "Bitte Platzhalter im Entwickler-Abschnitt anlegen."
        )
    return pattern.sub(block, content, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(description="MkDocs ADR-Navigation generieren")
    parser.add_argument("--check", action="store_true", help="Drift-Pruefung (Exit 1 bei Abweichung).")
    args = parser.parse_args()

    entries = collect_entries()
    block = render_nav_block(entries)
    current = MKDOCS.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^[ \t]*{re.escape(BEGIN)}.*?^[ \t]*{re.escape(END)}",
        re.MULTILINE | re.DOTALL,
    )
    if not pattern.search(current):
        print(f"FEHLT: ADR-Nav-Marker in {MKDOCS}", file=sys.stderr)
        return 1

    refreshed = pattern.sub(block, current, count=1)

    if args.check:
        if refreshed != current:
            print(
                f"DRIFT: {MKDOCS} ADR-Nav ist nicht aktuell ({len(entries)} ADRs). "
                "Bitte 'python scripts/generate_adr_nav.py' ausfuehren.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: ADR-Nav aktuell ({len(entries)} ADRs).")
        return 0

    MKDOCS.write_text(refreshed, encoding="utf-8")
    print(f"Updated {MKDOCS} with {len(entries)} ADR nav entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
