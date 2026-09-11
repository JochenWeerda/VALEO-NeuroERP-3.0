"""SPEC-P0-08: Restore-Drill-Evidence-Check ist fail-closed und deterministic."""

from __future__ import annotations

import importlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture()
def restore_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    mod = importlib.import_module("scripts.check_restore_drill_evidence")
    monkeypatch.setattr(mod, "PROTO_DIR", tmp_path)
    return mod


def _write_protocol(dir_path: Path, *, status: str, rto_met: bool, days_ago: int = 0) -> Path:
    executed = datetime.now(timezone.utc) - timedelta(days=days_ago)
    path = dir_path / f"restore-drill-{executed.date().isoformat()}.json"
    path.write_text(
        json.dumps(
            {
                "drill_type": "backup-restore",
                "executed_at": executed.isoformat().replace("+00:00", "Z"),
                "operator": "pytest",
                "environment": "test",
                "rto_target_minutes": 15,
                "duration_seconds": 120,
                "duration_minutes": 2,
                "rto_met": rto_met,
                "status": status,
                "error": "",
            }
        ),
        encoding="utf-8",
    )
    return path


def test_missing_protocol_is_external_gate(restore_check, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.argv", ["check_restore_drill_evidence.py"])
    assert restore_check.main() == 2


def test_missing_protocol_strict_fails(restore_check, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.argv", ["check_restore_drill_evidence.py", "--strict"])
    assert restore_check.main() == 1


def test_passed_fresh_protocol_ok(restore_check, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_protocol(tmp_path, status="passed", rto_met=True, days_ago=1)
    monkeypatch.setattr("sys.argv", ["check_restore_drill_evidence.py", "--max-age-days", "90"])
    assert restore_check.main() == 0


def test_failed_or_stale_protocol_errors(restore_check, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_protocol(tmp_path, status="failed", rto_met=False, days_ago=1)
    monkeypatch.setattr("sys.argv", ["check_restore_drill_evidence.py"])
    assert restore_check.main() == 1

    for stale in tmp_path.glob("restore-drill-*.json"):
        stale.unlink()
    _write_protocol(tmp_path, status="passed", rto_met=True, days_ago=120)
    monkeypatch.setattr("sys.argv", ["check_restore_drill_evidence.py", "--max-age-days", "90"])
    assert restore_check.main() == 1


def test_scripts_and_docs_present():
    root = Path(__file__).resolve().parents[1]
    assert (root / "scripts" / "run_restore_drill.sh").is_file()
    assert (root / "scripts" / "check_restore_drill_evidence.py").is_file()
    assert (root / "docs" / "operations" / "drill-protocols" / "README.md").is_file()
