"""Governance: genau ein Alembic-Head (COMPAT-GOV / init_db)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_alembic_has_single_head():
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "heads"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    head_lines = [ln for ln in result.stdout.splitlines() if "(head)" in ln]
    assert len(head_lines) == 1, (
        "Mehrere Alembic-Heads — Merge-Migration erforderlich:\n" + result.stdout
    )
