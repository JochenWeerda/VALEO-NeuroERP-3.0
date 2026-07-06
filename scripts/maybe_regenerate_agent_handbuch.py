#!/usr/bin/env python
"""Regeneriert docs/agent-handbuch/ wenn relevante Quellen gestaged sind.

Wird aus dem pre-commit-Hook aufgerufen, damit Agent-Doku nicht manuell
nachgezogen werden muss.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

TRIGGER_PATHS = {
    "app/core/flow_spine_registry.py",
    "app/core/screen_definitions.py",
    "config/mcp_erp_tools.yaml",
    "scripts/agent_handbuch_sources.py",
    "scripts/generate_agent_handbuch.py",
}

TRIGGER_PREFIXES = (
    "docs/workflows/",
)

OUTPUT_DIR = REPO / "docs" / "agent-handbuch"


def staged_files() -> list[str]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=REPO,
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def should_regenerate(files: list[str]) -> bool:
    for path in files:
        if path in TRIGGER_PATHS:
            return True
        if path.startswith(TRIGGER_PREFIXES) and path.endswith(".md"):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="Nur bei gestagten Trigger-Dateien")
    args = parser.parse_args()

    if args.staged:
        files = staged_files()
        if not should_regenerate(files):
            return 0

    gen = REPO / "scripts" / "generate_agent_handbuch.py"
    subprocess.run([sys.executable, str(gen)], cwd=REPO, check=True)

    if args.staged:
        subprocess.run(["git", "add", str(OUTPUT_DIR)], cwd=REPO, check=True)
        print("maybe_regenerate_agent_handbuch: docs/agent-handbuch/ aktualisiert und gestaged.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
