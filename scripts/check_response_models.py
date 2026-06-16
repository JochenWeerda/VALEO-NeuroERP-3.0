#!/usr/bin/env python3
"""
CI reporting tool: Routes without response_model in FastAPI endpoint files.

Does NOT fail CI — reports counts and tracks progress over time.
Run:  python scripts/check_response_models.py [--threshold N]
      N = max allowed untyped routes (default: 916 — current baseline)

Raises exit code 1 only if the count INCREASES beyond the threshold,
preventing regressions while allowing gradual improvement.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

# Files where response_model is intentionally absent for technical reasons:
# - 204 No Content routes (response_class=Response, response_model=None)
# - File-download routes (StreamingResponse)
# These are NOT counted as gaps.
EXEMPT_PATTERNS = [
    r"response_class\s*=\s*Response",  # 204 No Content
    r"response_model\s*=\s*None",
]


def _count_untyped(content: str) -> tuple[int, int]:
    """Return (untyped_routes, total_routes)."""
    routes_with = len(re.findall(
        r"@router\.(get|post|put|patch|delete)[^)]*response_model",
        content, re.DOTALL,
    ))
    total = len(re.findall(r"@router\.(get|post|put|patch|delete)", content))
    # Count exempt patterns (204 + None)
    exempt = sum(
        len(re.findall(p, content)) for p in EXEMPT_PATTERNS
    )
    untyped = max(0, total - routes_with - exempt)
    return untyped, total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=int, default=916,
        help="Max allowed untyped routes (baseline: 916)",
    )
    parser.add_argument(
        "--baseline-file",
        help=(
            "Optional JSON baseline with total_untyped and per-file untyped "
            "counts. When present, per-file regressions fail even if the "
            "global threshold is unchanged."
        ),
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    total_untyped = 0
    total_routes = 0
    files_with_gaps: list[tuple[str, int, int]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        content = open(path, encoding="utf-8").read()
        untyped, total = _count_untyped(content)
        total_untyped += untyped
        total_routes += total
        if untyped > 0:
            files_with_gaps.append((fname, untyped, total))

    typed = total_routes - total_untyped
    pct = round(100 * typed / total_routes, 1) if total_routes else 0

    print(f"Response model coverage: {typed}/{total_routes} routes ({pct}%)")
    print(f"Untyped routes: {total_untyped} (threshold: {args.threshold})")

    if args.baseline_file:
        with open(args.baseline_file, encoding="utf-8") as f:
            baseline = json.load(f)
        allowed_by_file = baseline.get("files", {})
        file_lookup = {fname: u for fname, u, _ in files_with_gaps}
        regressions: list[str] = []
        for fname, current in sorted(file_lookup.items()):
            allowed = int(allowed_by_file.get(fname, 0))
            if current > allowed:
                regressions.append(f"{fname}: {current} > {allowed}")
        allowed_total = int(baseline.get("total_untyped", args.threshold))
        if total_untyped > allowed_total:
            regressions.append(f"total_untyped: {total_untyped} > {allowed_total}")
        if regressions:
            print("\nFAIL: response model baseline regressed.", file=sys.stderr)
            for item in regressions[:20]:
                print(f"  {item}", file=sys.stderr)
            if len(regressions) > 20:
                print(f"  ... {len(regressions) - 20} more", file=sys.stderr)
            return 1
        print(f"OK - response model baseline: {args.baseline_file}")

    if args.verbose:
        print("\nFiles with untyped routes (top 20):")
        for fname, u, t in sorted(files_with_gaps, key=lambda x: -x[1])[:20]:
            print(f"  {fname:50s} {u:4d}/{t:4d}")

    if total_untyped > args.threshold:
        print(
            f"\nFAIL: {total_untyped} untyped routes exceeds threshold {args.threshold}.",
            file=sys.stderr,
        )
        print(
            "Response model coverage REGRESSED. Add response_model= to new routes.",
            file=sys.stderr,
        )
        return 1

    print("OK — no regression in response model coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
