#!/usr/bin/env python3
"""
CI regression gate: unbounded .all() queries without pagination.

Fails if the count of files with .all() but no skip/limit pagination INCREASES
beyond the baseline (60). This prevents regressions while allowing gradual improvement.

Run:  python scripts/check_pagination.py [--threshold N]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

# Files where unbounded .all() is intentional (reference data, small sets)
EXEMPT_FILES: set[str] = {
    "e2e_chain.py",           # orchestration, not user-facing list
    "command_catalog.py",     # static command catalog
    "agent_tool_contracts.py",  # agent tool list — small bounded set
    "analytics.py",           # analytics aggregations, not entity lists
}


def _has_unbounded_all(content: str) -> int:
    """Return count of .all() calls without nearby skip/limit."""
    has_pagination = bool(re.search(
        r"skip\s*[=:]|limit\s*[=:]|PaginationParams|get_pagination|\.offset\(",
        content,
    ))
    all_calls = content.count(".all()")
    if has_pagination or all_calls == 0:
        return 0
    return all_calls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--threshold", type=int, default=60,
        help="Max allowed files with unbounded .all() (baseline: 60)",
    )
    args = parser.parse_args()

    offenders: list[tuple[str, int]] = []

    for fname in sorted(os.listdir(ENDPOINTS_DIR)):
        if not fname.endswith(".py") or fname in EXEMPT_FILES:
            continue
        path = os.path.join(ENDPOINTS_DIR, fname)
        content = open(path, encoding="utf-8").read()
        count = _has_unbounded_all(content)
        if count > 0:
            offenders.append((fname, count))

    print(f"Files with unbounded .all(): {len(offenders)} (threshold: {args.threshold})")
    for fname, cnt in sorted(offenders, key=lambda x: -x[1])[:10]:
        print(f"  {fname:50s} {cnt} .all() calls")

    if len(offenders) > args.threshold:
        print(
            f"\nFAIL: {len(offenders)} files exceed threshold {args.threshold}.",
            file=sys.stderr,
        )
        return 1

    print("OK — no pagination regression.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
