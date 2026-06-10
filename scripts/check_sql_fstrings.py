#!/usr/bin/env python3
"""
CI-Gate: SQL f-string Injection Check.

Prüft ob neue SQL f-Strings ohne # nosec S608 Kommentar eingefügt wurden.
Alle existierenden Stellen wurden manuell gereviewed und mit # nosec S608
oder einem erklärenden Kommentar versehen.

Exit 0 = OK, Exit 1 = neue unflagged SQL f-strings gefunden.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def check() -> int:
    violations: list[str] = []
    for py_file in Path("app").rglob("*.py"):
        try:
            lines = py_file.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines):
                if re.search(r'text\s*\(\s*f["\']|\.execute\s*\(\s*f["\']', line):
                    # Flagged with nosec or reviewed comment on current or preceding line?
                    review_context = "\n".join(lines[max(0, i - 3):i + 1])
                    if (
                        "nosec" not in review_context
                        and "# reviewed-safe" not in review_context
                    ):
                        violations.append(f"{py_file}:{i + 1}: {line.strip()[:100]}")
        except Exception:
            pass

    if violations:
        print(f"[FAIL] {len(violations)} ungeflagged SQL f-string(s) gefunden:")
        for v in violations:
            print(f"  {v}")
        print("\nBehebung: Entweder auf parametrisierte Queries umstellen oder")
        print("  # nosec S608 — <Begründung warum safe> hinzufügen wenn reviewed.")
        return 1

    print(f"[OK] Alle SQL f-strings sind reviewed (nosec/reviewed-safe kommentiert).")
    return 0


if __name__ == "__main__":
    sys.exit(check())
