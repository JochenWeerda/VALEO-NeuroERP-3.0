#!/usr/bin/env python3
"""SPEC-P1-04 — Inventur: keine stubReason auf nativen ScreenDefinitions.

Prüft alle ScreenDefinitions mit adapter.temporary=False.
Exit 0 = OK, Exit 1 = Verstöße.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition  # noqa: E402


def main() -> int:
    violations: list[str] = []

    for screen_id in sorted(SCREEN_DEFINITION_BUILDERS.keys()):
        sd = get_screen_definition(screen_id)
        if not sd:
            continue
        if sd.get("adapter", {}).get("temporary", True):
            continue

        for action in sd.get("actions", []):
            key = action.get("key", "?")
            if action.get("stubReason"):
                violations.append(f"{screen_id}/{key}: stubReason={action['stubReason']!r}")

            endpoint = action.get("commandEndpoint")
            if endpoint and action.get("stubReason"):
                violations.append(f"{screen_id}/{key}: commandEndpoint + stubReason gleichzeitig")

            # Mutations-Actions ohne Endpoint (edit-only ausgenommen)
            if (
                not endpoint
                and not action.get("stubReason")
                and action.get("key") not in ("edit",)
                and action.get("dangerLevel") in ("moderate", "high", "critical")
            ):
                violations.append(f"{screen_id}/{key}: high-risk action ohne commandEndpoint")

    if violations:
        print("Mask commandEndpoint inventory FAILED:\n")
        for v in violations:
            print(f"  - {v}")
        return 1

    native_count = sum(
        1 for sid in SCREEN_DEFINITION_BUILDERS
        if not (get_screen_definition(sid) or {}).get("adapter", {}).get("temporary", True)
    )
    print(f"Mask commandEndpoint inventory OK ({native_count} native ScreenDefinitions, 0 stubReason).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
