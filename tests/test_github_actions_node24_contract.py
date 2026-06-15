from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    "ci.yml",
    "docs-governance.yml",
    "e2e-full.yml",
    "e2e-smoke.yml",
    "pytest-postgres-require-db.yml",
    "quality-gate.yml",
    "release-gates.yml",
    "security-scan.yml",
    "sonarcloud.yml",
)
CURRENT_ACTIONS = (
    "actions/checkout@v6",
    "actions/setup-node@v6",
    "actions/setup-python@v6",
    "pnpm/action-setup@v6",
)


def test_central_workflows_opt_into_node24_action_runtime():
    for name in WORKFLOWS:
        path = ROOT / ".github" / "workflows" / name
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))

        assert workflow["env"]["FORCE_JAVASCRIPT_ACTIONS_TO_NODE24"] == "true"


def test_central_workflows_use_current_action_majors():
    combined = ""
    for name in WORKFLOWS:
        path = ROOT / ".github" / "workflows" / name
        combined += path.read_text(encoding="utf-8")

    for action in CURRENT_ACTIONS:
        assert action in combined, f"central workflows do not use {action}"

    assert "actions/checkout@v4" not in combined
    assert "actions/checkout@v5" not in combined
    assert "actions/setup-node@v4" not in combined
    assert "actions/setup-node@v5" not in combined
    assert "actions/setup-python@v5" not in combined
    assert "pnpm/action-setup@v2" not in combined
    assert "pnpm/action-setup@v4" not in combined
