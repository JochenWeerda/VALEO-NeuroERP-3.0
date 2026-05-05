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
    parser.add_argument(
        "--strict-live",
        action="store_true",
        help="Fail unless every live probe is ready to execute in this environment.",
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
    if args.strict_live:
        blockers = [
            f"{probe['integration_key']}={probe['status']}"
            for probe in summary["probe_plan"]
            if probe["status"] != "ready"
        ]
        if blockers:
            raise SystemExit("Live integration probes not ready: " + ", ".join(blockers))


if __name__ == "__main__":
    main()
