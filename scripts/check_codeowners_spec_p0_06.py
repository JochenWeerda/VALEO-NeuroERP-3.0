#!/usr/bin/env python3
"""SPEC-P0-06: CODEOWNERS muss finanz-/sicherheitskritische Pfade abdecken.

Exit 0 — alle Pflichtpfade vorhanden
Exit 1 — fehlende Eintraege
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEOWNERS = REPO / ".github" / "CODEOWNERS"

# Audit SPEC-P0-06 + erweiterte GoBD-/CI-Pfade
REQUIRED_GLOBS = (
    "/app/services/finance*",
    "/app/api/v1/endpoints/pos*",
    "/alembic/",
    "/.github/",
)


def main() -> int:
    if not CODEOWNERS.is_file():
        print("FEHLER: .github/CODEOWNERS fehlt")
        return 1
    text = CODEOWNERS.read_text(encoding="utf-8")
    missing = [g for g in REQUIRED_GLOBS if g not in text]
    if missing:
        print("FEHLER: CODEOWNERS fehlen Pflichtpfade (SPEC-P0-06):")
        for g in missing:
            print(f"  - {g}")
        return 1
    if "SPEC-P0-06" not in text:
        print("FEHLER: CODEOWNERS-Kommentar muss SPEC-P0-06 referenzieren (Assessor-Gate)")
        return 1
    print(f"OK: CODEOWNERS deckt {len(REQUIRED_GLOBS)} SPEC-P0-06-Pfade ab.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
