from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.integration_bootstrap import build_integration_bootstrap_summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--probe-plan",
        action="store_true",
        help="Print only the live connectivity probe plan derived from readiness checks.",
    )
    args = parser.parse_args()
    summary = build_integration_bootstrap_summary()
    payload = summary["probe_plan"] if args.probe_plan else summary
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.strict and summary["required_blockers"]:
        raise SystemExit(
            "Required integration bootstrap blockers present: "
            + ", ".join(summary["required_blockers"])
        )


if __name__ == "__main__":
    main()
