from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _workflow(name: str) -> tuple[dict, str]:
    path = ROOT / ".github" / "workflows" / name
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text), text


def test_full_uat_provisions_backend_runtime_and_waits_for_readiness():
    workflow, text = _workflow("e2e-full.yml")
    job = workflow["jobs"]["full-uat"]

    assert "postgres" in job["services"]
    assert "Install backend dependencies" in text
    assert "pip install -r requirements.txt" in text
    assert "python scripts/init_db.py" in text
    assert "cp .env.uat .env" in text
    assert "elif [ -f .env.example ]" in text
    assert "curl --silent --show-error --fail http://127.0.0.1:8000/healthz" in text
    assert "curl --silent --show-error --fail http://127.0.0.1:3000/" in text
    assert "sleep 10" not in text


def test_harvest_peak_requires_an_explicit_reachable_target():
    workflow, text = _workflow("load-test.yml")
    harvest_steps = workflow["jobs"]["harvest-peak"]["steps"]
    step_names = {step.get("name") for step in harvest_steps}

    assert "Zielsystem aufloesen" in step_names
    assert "Zielsystem vorpruefen" in step_names
    assert "STAGING_BASE_URL: ${{ secrets.STAGING_URL }}" in text
    assert "steps.target.outputs.base_url" in text
    assert "connect-timeout 5" in text
    assert "Das externe Performance-Gate bleibt offen." in text
    assert "https://staging.valeo-erp.de" not in text
