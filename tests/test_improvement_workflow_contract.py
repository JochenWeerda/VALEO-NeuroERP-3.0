import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8-sig"))


def test_frontendtests_blockieren_und_erzeugen_nachweis():
    job = workflow("quality-gate.yml")["jobs"]["frontend"]
    tests = [step for step in job["steps"] if "vitest run" in step.get("run", "")]
    assert len(tests) == 1
    assert "||" not in tests[0]["run"]
    assert not tests[0].get("continue-on-error", False)
    assert "--coverage.reportsDirectory=coverage" in tests[0]["run"]
    package = json.loads((ROOT / "packages/frontend-web/package.json").read_text(encoding="utf-8"))
    assert package["devDependencies"]["@vitest/coverage-v8"] == "4.1.11"


def test_sonar_verbraucht_nachweise_statt_tests_zu_wiederholen():
    sonar = workflow("sonarcloud.yml")
    runs = [step.get("run", "") for step in sonar["jobs"]["sonarcloud"]["steps"]]
    assert not any("pytest" in run or "vitest" in run or "pip install" in run for run in runs)
    assert any("verify_quality_evidence.py" in run for run in runs)
    assert sonar["permissions"]["contents"] == "read"
    call = workflow("quality-gate.yml")["jobs"]["sonar-analysis"]
    assert {"backend", "frontend", "improvement-integrity"} <= set(call["needs"])


def test_nightly_berichtet_ohne_push():
    nightly = workflow("ai-engineering-metrics.yml")
    assert nightly["permissions"]["contents"] == "read"
    steps = nightly["jobs"]["metrics"]["steps"]
    assert not any("git push" in step.get("run", "") for step in steps)
    assert any("run_improvement_pipelines.py" in step.get("run", "") for step in steps)


def test_scanner_laufen_unabhaengig_vom_backend():
    jobs = workflow("quality-gate.yml")["jobs"]
    assert jobs["improvement-integrity"]["needs"] == ["path-guard"]
    backend_commands = "\n".join(step.get("run", "") for step in jobs["backend"]["steps"])
    assert "check_pagination.py" not in backend_commands
    assert "check_file_size.py" not in backend_commands


def test_keine_pr_aenderung_umgeht_qualitaetsgate():
    gate = workflow("quality-gate.yml")
    events = gate.get("on", gate.get(True))
    assert "paths" not in events["pull_request"]
    guards = "\n".join(step.get("run", "") for step in gate["jobs"]["path-guard"]["steps"])
    assert 'check_baseline_integrity.py --base "${{ steps.range.outputs.base }}"' in guards


def test_openapi_artefaktkorrekturen_starten_driftabnahme():
    gate = workflow('openapi-drift.yml')
    events = gate.get('on', gate.get(True))
    assert {
        'app/**', 'requirements.txt', 'docs/schnittstellen/openapi.json',
        'scripts/generate_openapi.py', '.github/workflows/openapi-drift.yml',
    } <= set(events['push']['paths'])
    checks = [step for step in gate['jobs']['openapi-check']['steps']
              if 'generate_openapi.py --check' in step.get('run', '')]
    assert len(checks) == 1
    assert not checks[0].get('continue-on-error', False)
