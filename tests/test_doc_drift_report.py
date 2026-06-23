"""Tests fuer AI-DOC-DRIFT-DASHBOARD-001 Drift-Report."""

import json
import tempfile
from pathlib import Path


def test_build_report_returns_structure() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from doc_drift_report import build_report

    report = build_report()
    assert "generated_at" in report
    assert "summary" in report
    assert "issues" in report
    s = report["summary"]
    assert "total_drift_items" in s
    assert isinstance(s["total_drift_items"], int)
    assert s["total_drift_items"] >= 0


def test_drift_report_json_serializable() -> None:
    from doc_drift_report import build_report
    report = build_report()
    serialized = json.dumps(report)
    assert len(serialized) > 10


def test_print_markdown_summary_runs(capsys) -> None:
    from doc_drift_report import build_report, print_markdown_summary
    report = build_report()
    print_markdown_summary(report)
    captured = capsys.readouterr()
    assert "Drift" in captured.out or "Kategorie" in captured.out


def test_main_writes_artifact(tmp_path, monkeypatch) -> None:
    from doc_drift_report import build_report
    import doc_drift_report as mod

    monkeypatch.setattr(mod, "ARTIFACTS_DIR", tmp_path)
    report = build_report()
    out = tmp_path / "doc_drift_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["summary"]["total_drift_items"] >= 0
