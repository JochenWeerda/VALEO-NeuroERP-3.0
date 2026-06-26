"""Tests fuer scripts/generate_code_inventories.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_code_inventories import (
    build_all,
    collect_rows,
    module_summary,
    normalize_for_check,
)

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_module_summary_from_docstring() -> None:
    sample = REPO / "app" / "api" / "v1" / "endpoints" / "health.py"
    if sample.exists():
        summary = module_summary(sample)
        assert summary and summary != "—"


@pytest.mark.unit
def test_build_all_produces_three_files() -> None:
    files = build_all("2026-06-26")
    assert len(files) == 3
    for path, content in files.items():
        assert path.name.endswith("-inventory.md")
        assert "last_reviewed: 2026-06-26" in content
        assert "| Modul | Beschreibung |" in content or "| Modul |" in content


@pytest.mark.unit
def test_collect_rows_skips_init() -> None:
    rows = collect_rows(REPO / "app" / "api" / "v1" / "endpoints", frozenset({"__init__"}))
    stems = {r[0] for r in rows}
    assert "__init__" not in stems


@pytest.mark.unit
def test_normalize_for_check_ignores_review_date() -> None:
    a = "---\nlast_reviewed: 2026-01-01\n---\nbody\n"
    b = "---\nlast_reviewed: 2026-06-26\n---\nbody\n"
    assert normalize_for_check(a) == normalize_for_check(b)
