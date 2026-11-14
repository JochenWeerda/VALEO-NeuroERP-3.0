"""The behavioral workspace tests must render current public Studio definitions."""
import json
from pathlib import Path

from app.core import screen_definitions_domain_batch15 as definitions


def test_workspace_fixtures_match_public_builders():
    keys = (
        "order-to-cash", "procure-to-pay", "inventory-to-settlement",
        "harvest-to-settlement", "contract-to-settlement", "complaint-to-resolution",
        "service-to-customer", "finance-to-close", "compliance-to-report",
    )
    current = {
        key: getattr(definitions, "build_workflow_flow_spine_" + key.replace("-", "_") +
                     "_screen_definition")()
        for key in keys
    }
    fixture = Path(__file__).resolve().parents[1] / (
        "packages/frontend-web/src/__tests__/fixtures/flow-spine-workspaces-studio.json")
    assert json.loads(fixture.read_text(encoding="utf-8")) == current
