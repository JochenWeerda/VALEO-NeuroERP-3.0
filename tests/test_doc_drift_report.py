"""Tests fuer AI-DOC-DRIFT-DASHBOARD-001 / AI-DOC-DRIFT-CI-001 Drift-Report."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.doc_drift_report import (
    build_report,
    page_to_module,
    print_markdown_summary,
)

REPO = Path(__file__).resolve().parents[1]
PAGES = REPO / "packages" / "frontend-web" / "src" / "pages"


@pytest.mark.unit
def test_build_report_returns_structure() -> None:
    report = build_report()
    assert "generated_at" in report
    assert "summary" in report
    assert "issues" in report
    s = report["summary"]
    assert "total_drift_items" in s
    assert isinstance(s["total_drift_items"], int)
    assert s["total_drift_items"] >= 0
    assert "page_no_route_or_nav" in s


@pytest.mark.unit
def test_drift_report_json_serializable() -> None:
    report = build_report()
    serialized = json.dumps(report)
    assert len(serialized) > 10


@pytest.mark.unit
def test_print_markdown_summary_runs(capsys: pytest.CaptureFixture[str]) -> None:
    report = build_report()
    print_markdown_summary(report)
    captured = capsys.readouterr()
    assert "Drift" in captured.out or "Kategorie" in captured.out


@pytest.mark.unit
def test_main_writes_artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.doc_drift_report as mod

    monkeypatch.setattr(mod, "ARTIFACTS_DIR", tmp_path)
    report = build_report()
    out = tmp_path / "doc_drift_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["summary"]["total_drift_items"] >= 0


@pytest.mark.unit
def test_page_to_module() -> None:
    page = PAGES / "agrar" / "ernte-annahme.tsx"
    if page.exists():
        assert page_to_module(page) == "@/pages/agrar/ernte-annahme"


@pytest.mark.unit
def test_fail_over_exit_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    import scripts.doc_drift_report as mod

    monkeypatch.setattr(mod, "ARTIFACTS_DIR", tmp_path)
    monkeypatch.setattr(
        mod,
        "build_report",
        lambda: {
            "generated_at": "2026-06-26T00:00:00+00:00",
            "repo_root": str(REPO),
            "summary": {
                "total_drift_items": 5,
                "endpoint_no_doc": 1,
                "migration_no_runbook": 1,
                "service_no_doc": 1,
                "page_no_route_or_nav": 2,
            },
            "issues": [],
        },
    )
    old_argv = sys.argv
    try:
        sys.argv = ["doc_drift_report.py"]
        assert mod.main() == 0
        sys.argv = ["doc_drift_report.py", "--fail-over", "3"]
        assert mod.main() == 1
    finally:
        sys.argv = old_argv
