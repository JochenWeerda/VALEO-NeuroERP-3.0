from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_gitleaks_snapshot_does_not_require_external_lfs_objects():
    path = ROOT / ".github" / "workflows" / "quality-gate.yml"
    text = path.read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    secret_scan = workflow["jobs"]["secret-scan"]

    assert secret_scan["name"] == "Secret Scan (gitleaks)"
    assert "-c filter.lfs.process=" in text
    assert "-c filter.lfs.smudge=cat" in text
    assert "-c filter.lfs.required=false" in text
    assert "archive --format=tar HEAD" in text
    assert "gitleaks/gitleaks:latest" in text
    assert "--baseline-path .gitleaks-baseline.json" in text
