"""SPEC-P0-06: CODEOWNERS-Pflichtpfade vorhanden."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]


def test_codeowners_file_exists_and_covers_critical_paths():
    path = ROOT / ".github" / "CODEOWNERS"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "SPEC-P0-06" in text
    for glob in (
        "/app/services/finance*",
        "/app/api/v1/endpoints/pos*",
        "/alembic/",
        "/.github/",
    ):
        assert glob in text, f"missing {glob}"


def test_check_script_exits_zero():
    from scripts.check_codeowners_spec_p0_06 import main

    assert main() == 0
