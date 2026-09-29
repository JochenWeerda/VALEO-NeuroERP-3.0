from pathlib import Path


WORKFLOW = Path(".github/workflows/openapi-drift.yml")


def test_openapi_drift_workflow_is_read_only_and_fail_closed() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "contents: read" in source
    assert "contents: write" not in source
    assert "python scripts/generate_openapi.py --check" in source
    assert "git push" not in source
    assert "git commit" not in source
    assert "generate_openapi.py\n" not in source
    assert "continue-on-error" not in source

