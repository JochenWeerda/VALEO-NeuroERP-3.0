#!/usr/bin/env python3
"""
CI regression gate: files over LOC threshold (godfile prevention).

Fails if the count of files > 1000 LOC INCREASES beyond baseline (12).
Run:  python scripts/check_file_size.py [--threshold N] [--warn-at N]
"""

from __future__ import annotations

import argparse
import os
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"
LOC_LIMIT = 1000
WARN_LIMIT = 500


def _loc(path: str) -> int:
    try:
        return open(path, encoding="utf-8").read().count("\n")
    except OSError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=int, default=12,
        help="Max allowed files > 1000 LOC (baseline: 12)",
    )
    args = parser.parse_args()

    over_limit: list[tuple[str, int]] = []
    over_warn: list[tuple[str, int]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        loc = _loc(path)
        if loc > LOC_LIMIT:
            over_limit.append((fname, loc))
        elif loc > WARN_LIMIT:
            over_warn.append((fname, loc))

    print(f"Files > {LOC_LIMIT} LOC (godfiles): {len(over_limit)} (threshold: {args.threshold})")
    for fname, loc in sorted(over_limit, key=lambda x: -x[1]):
        print(f"  {fname:50s} {loc:5d}")

    if over_warn:
        print(f"\nFiles > {WARN_LIMIT} LOC (approaching limit): {len(over_warn)}")
        for fname, loc in sorted(over_warn, key=lambda x: -x[1])[:5]:
            print(f"  {fname:50s} {loc:5d}")

    if len(over_limit) > args.threshold:
        print(
            f"\nFAIL: {len(over_limit)} godfiles exceeds threshold {args.threshold}.",
            file=sys.stderr,
        )
        print("Refactor or split the file into smaller modules.", file=sys.stderr)
        return 1

    print("\nOK — no new godfiles introduced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
