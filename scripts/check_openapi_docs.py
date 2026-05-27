#!/usr/bin/env python3
"""
CI regression gate: OpenAPI summary coverage on endpoint files.

Fails if the number of routes WITHOUT a summary INCREASES beyond baseline.
Run:  python scripts/check_openapi_docs.py [--threshold N]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"
ROUTE_RE = re.compile(r"@router\.(get|post|put|patch|delete)\(")
SUMMARY_RE = re.compile(r"\bsummary\s*=")


def _scan(path: str) -> tuple[int, int]:
    """Return (total_routes, routes_with_summary) for a file."""
    try:
        content = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return 0, 0
    routes = len(ROUTE_RE.findall(content))
    summaries = len(SUMMARY_RE.findall(content))
    return routes, min(summaries, routes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=int, default=0,
        help="Max allowed routes without summary (baseline: 0 — 100% coverage achieved)",
    )
    args = parser.parse_args()

    total_routes = 0
    total_with_summary = 0
    files_without: list[tuple[str, int, int]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        routes, with_summary = _scan(path)
        total_routes += routes
        total_with_summary += with_summary
        missing = routes - with_summary
        if missing > 0:
            files_without.append((fname, routes, with_summary))

    total_missing = total_routes - total_with_summary
    pct = (total_with_summary / total_routes * 100) if total_routes else 0.0

    print(f"OpenAPI summary coverage: {total_with_summary}/{total_routes} routes ({pct:.1f}%)")
    print(f"Routes missing summary: {total_missing} (threshold: {args.threshold})")

    if files_without:
        print(f"\nTop files by missing summaries:")
        for fname, routes, with_sum in sorted(files_without, key=lambda x: -(x[1] - x[2]))[:10]:
            print(f"  {fname:50s} {with_sum}/{routes}")

    if total_missing > args.threshold:
        print(
            f"\nFAIL: {total_missing} routes without summary exceeds threshold {args.threshold}.",
            file=sys.stderr,
        )
        print("Add summary= to new routes or improve coverage.", file=sys.stderr)
        return 1

    print("\nOK — OpenAPI doc coverage within baseline.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
