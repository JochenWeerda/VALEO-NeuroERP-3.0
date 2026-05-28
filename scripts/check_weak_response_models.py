#!/usr/bin/env python3
"""
CI-Check: Schwache response_model-Typen in FastAPI-Endpoints.

Schwache Typen verschlechtern OpenAPI-Dokumentation, verhindern
Validierung und erschweren die Client-Code-Generierung.

Verbotene Muster (werden gezählt):
    response_model=dict
    response_model=list
    response_model=Any
    response_model=dict[str, Any]
    response_model=Dict[str, Any]

Erlaubte Ausnahmen (nicht gezählt):
    response_model=None          (kein Body, z. B. 204)
    response_class=Response      (StreamingResponse / FileResponse)

Verwendung:
    python scripts/check_weak_response_models.py
    python scripts/check_weak_response_models.py --threshold 750
    python scripts/check_weak_response_models.py --verbose

Exit-Code 1 wenn Anzahl den Schwellwert überschreitet.
Baseline: 1451 (Stand 2026-05-28) → 1427 (admin_mobile) → 1346 (compat) — bei jeder Migrierungswelle senken.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

# Regex für schwache response_model-Typen
# Nicht geflaggt: list[EchtesSchema], Optional[EchtesSchema]
WEAK_PATTERNS = [
    # Bare dict (ohne Typ-Argument) — kein Pydantic-Modell
    re.compile(r"response_model\s*=\s*dict(?!\s*\[)"),
    # Bare list (ohne Typ-Argument)
    re.compile(r"response_model\s*=\s*list(?!\s*\[)"),
    # Any — komplett untypisiert
    re.compile(r"response_model\s*=\s*Any\b"),
    # dict[str, Any] oder Dict[str, Any] — schwach typisiert
    re.compile(r"response_model\s*=\s*[Dd]ict\[str\s*,\s*Any\]"),
    re.compile(r"response_model\s*=\s*[Dd]ict\[str\s*,\s*[Dd]ict"),
    # list[dict[...]] — Liste von unstrukturierten Dicts
    re.compile(r"response_model\s*=\s*[Ll]ist\[dict"),
    re.compile(r"response_model\s*=\s*[Ll]ist\[Dict"),
]

EXEMPT_PATTERNS = [
    re.compile(r"response_model\s*=\s*None"),
    re.compile(r"response_class\s*=\s*Response"),
]


def _is_exempt_line(line: str) -> bool:
    return any(p.search(line) for p in EXEMPT_PATTERNS)


def _count_weak(path: str) -> tuple[int, list[tuple[int, str]]]:
    """Returns (count, [(lineno, line), ...])."""
    findings: list[tuple[int, str]] = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if _is_exempt_line(line):
                continue
            if any(p.search(line) for p in WEAK_PATTERNS):
                findings.append((lineno, line.rstrip()))
    return len(findings), findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for weak response_model types (dict/list/Any)."
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=1346,
        help="Max allowed weak response_model usages (baseline: 1451 → 1427 admin_mobile → 1346 compat, 2026-05-28)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show all findings")
    parser.add_argument("--strict", action="store_true", help="Fail on any weak type (threshold=0)")
    args = parser.parse_args()

    threshold = 0 if args.strict else args.threshold

    total_weak = 0
    file_counts: list[tuple[str, int, list[tuple[int, str]]]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        count, findings = _count_weak(path)
        if count > 0:
            file_counts.append((fname, count, findings))
            total_weak += count

    # Bericht
    total_endpoints = len([f for f in os.listdir(ENDPOINTS_DIR) if f.endswith(".py")])
    print(f"Schwache response_model-Typen: {total_weak} in {len(file_counts)}/{total_endpoints} Dateien")
    print(f"Schwellwert: {threshold}")

    if args.verbose or args.strict:
        print("\nDateien mit schwachen Typen (absteigende Reihenfolge):")
        for fname, count, findings in sorted(file_counts, key=lambda x: -x[1])[:30]:
            print(f"  {fname:55s} {count:3d}x")
            if args.verbose:
                for lineno, line in findings[:3]:
                    print(f"      L{lineno}: {line.strip()}")

    if total_weak > threshold:
        print(
            f"\nFEHL: {total_weak} schwache Typen überschreiten Schwellwert {threshold}.",
            file=sys.stderr,
        )
        print(
            "Migriere response_model=dict/list/Any auf echte Pydantic-Schemas.",
            file=sys.stderr,
        )
        print(
            "Basis-Klassen: from app.api.v1.schemas.base import StatusResponse, IDResponse, ListResponse",
            file=sys.stderr,
        )
        return 1

    print("OK — Keine Regression bei schwachen response_model-Typen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
