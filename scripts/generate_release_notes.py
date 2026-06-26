"""DOC-RELEASE-NOTES-001 — Generiert Release-Notes aus CHANGELOG + abgeschlossenen Slices.

Verwendung:
    python scripts/generate_release_notes.py [--version VERSION]

Output: docs/benutzerhandbuch/release-notes.md
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
CHANGELOG = REPO / "CHANGELOG.md"
SLICES_DIR = REPO / "docs/agent-ops/slices"
OUTPUT = REPO / "docs/benutzerhandbuch/release-notes.md"


def get_git_version() -> str:
    import subprocess
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"], cwd=REPO, text=True
        ).strip()
        return tag
    except Exception:
        return "3.0.0-dev"


def parse_changelog_sections(text: str) -> list[dict]:
    sections = []
    current = None
    for line in text.splitlines():
        m = re.match(r'^## \[(.+?)\](?:\s*-\s*(\d{4}-\d{2}-\d{2}))?', line)
        if m:
            if current:
                sections.append(current)
            current = {"version": m.group(1), "date": m.group(2) or "", "lines": []}
        elif current and line.strip():
            current["lines"].append(line)
    if current:
        sections.append(current)
    return sections


def load_completed_slices(days: int = 90) -> list[dict]:
    slices = []
    for path in sorted(SLICES_DIR.glob("*.yaml")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "abgeschlossen" not in text and "completed" not in text:
            continue
        if HAS_YAML:
            try:
                data = yaml.safe_load(text)
                if isinstance(data, dict) and data.get("slice_id"):
                    slices.append(data)
                    continue
            except Exception:
                pass
        # Fallback regex
        sid = re.search(r'^slice_id:\s*(.+)$', text, re.MULTILINE)
        title = re.search(r'^title:\s*"?(.+?)"?\s*$', text, re.MULTILINE)
        created = re.search(r'^created:\s*"?(\d{4}-\d{2}-\d{2})"?', text, re.MULTILINE)
        if sid:
            slices.append({
                "slice_id": sid.group(1).strip(),
                "title": title.group(1).strip() if title else "",
                "created": created.group(1) if created else "",
                "status": "abgeschlossen",
            })
    return slices


def build_markdown(version: str, changelog_sections: list[dict], slices: list[dict]) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "---",
        "title: Release Notes",
        "description: Änderungsprotokoll und Release-History für VALEO NeuroERP 3.0.",
        "type: reference",
        "audience: [alle]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {ts}",
        "version: 3.0.0",
        "---",
        "",
        "# Release Notes — VALEO NeuroERP 3.0",
        "",
        f"> Generiert via `scripts/generate_release_notes.py` · Stand: {ts}  ",
        "> Quelle: `CHANGELOG.md` + abgeschlossene Slice-YAMLs",
        "",
    ]

    # CHANGELOG Sections
    for sec in changelog_sections:
        v = sec["version"]
        d = f" — {sec['date']}" if sec["date"] else ""
        lines.append(f"## Version {v}{d}")
        lines.append("")
        for l in sec["lines"]:
            lines.append(l)
        lines.append("")

    # Slice-Übersicht
    recent_slices = [s for s in slices if s.get("created", "") >= "2026-01-01"]
    if recent_slices:
        lines += [
            f"## Abgeschlossene Slices (2026 · {len(recent_slices)} Stück)",
            "",
            "| Slice | Titel | Datum |",
            "|---|---|---|",
        ]
        for s in sorted(recent_slices, key=lambda x: x.get("created", ""), reverse=True)[:50]:
            sid = s.get("slice_id", "?")
            title = s.get("title", "")[:60]
            created = s.get("created", "")
            lines.append(f"| `{sid}` | {title} | {created} |")
        lines.append("")

    lines.append(f"*Generiert {ts} · {len(slices)} Slices · Slice: DOC-RELEASE-NOTES-001*")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=None)
    args = parser.parse_args()

    version = args.version or get_git_version()
    changelog_text = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    sections = parse_changelog_sections(changelog_text)
    slices = load_completed_slices()

    md = build_markdown(version, sections, slices)
    OUTPUT.write_text(md, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT} (v{version}, {len(slices)} Slices)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
