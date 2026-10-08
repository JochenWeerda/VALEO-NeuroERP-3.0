#!/usr/bin/env python3
"""Generate ki-usability mask-action catalog from ScreenDefinitions.

Usage:
  python scripts/generate_screen_action_catalog.py
  python scripts/generate_screen_action_catalog.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from app.core.screen_action_catalog import build_screen_action_catalog, catalog_stats  # noqa: E402

OUT = REPO / "services" / "ki-usability" / "app" / "data" / "screen_mask_actions.json"


def render_payload() -> dict:
    catalog = build_screen_action_catalog()
    stats = catalog_stats(catalog)
    return {
        "schemaVersion": 1,
        "generator": "scripts/generate_screen_action_catalog.py",
        "stats": stats,
        "actions": catalog,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed JSON drifts from ScreenDefinitions",
    )
    args = parser.parse_args()
    payload = render_payload()
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        if not OUT.is_file():
            print(f"MISSING {OUT.relative_to(REPO)}", file=sys.stderr)
            return 1
        current = OUT.read_text(encoding="utf-8")
        if current != text:
            print(
                f"DRIFT {OUT.relative_to(REPO)} — run: "
                "python scripts/generate_screen_action_catalog.py",
                file=sys.stderr,
            )
            return 1
        print(
            f"OK {OUT.relative_to(REPO)} "
            f"({payload['stats']['actions']} actions, "
            f"{payload['stats']['screens_with_actions']} screens)"
        )
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(
        f"Wrote {OUT.relative_to(REPO)} "
        f"({payload['stats']['actions']} actions, "
        f"{payload['stats']['screens_with_actions']} screens)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
