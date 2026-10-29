"""Project the approved domain command transport into the central UI adapter."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core.screen_definitions_harvest_controls import COMMAND_PATHS
from modules.agrar.contracts.harvest_control_v1 import (CalculationApproveIn, ContextCommandIn,
    FinancialReleaseIn, MeasurementAttestIn, RuleBindIn, RuleCreateIn, RuleDecisionIn)

INPUTS = {"create_rule": RuleCreateIn, "approve_rule": RuleDecisionIn, "revoke_rule": RuleDecisionIn,
          "bind_rule": RuleBindIn, "attest": MeasurementAttestIn, "calculate": ContextCommandIn,
          "approve_calculation": CalculationApproveIn, "release": FinancialReleaseIn}
OUTPUT = ROOT / "packages/frontend-web/src/components/mask-builder/runtime/harvest-control-contract.generated.json"


def render():
    return json.dumps({"schema_version": 1, "adapter": "harvest.control.v1", "paths": COMMAND_PATHS,
        "request_schemas": {key: model.model_json_schema() for key, model in INPUTS.items()}},
        ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("DRIFT: harvest.control.v1 transport projection differs."); return 1
        print("harvest.control.v1 projection synchronized."); return 0
    OUTPUT.write_text(expected, encoding="utf-8"); print("harvest.control.v1 projection generated."); return 0


if __name__ == "__main__":
    raise SystemExit(main())
