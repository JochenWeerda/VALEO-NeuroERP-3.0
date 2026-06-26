"""Tests fuer scripts/generate_adr_nav.py."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.generate_adr_nav import BEGIN, END, collect_entries, extract_title, render_nav_block

REPO = Path(__file__).resolve().parents[1]
MKDOCS = REPO / "mkdocs.yml"


@pytest.mark.unit
def test_collect_entries_includes_all_adrs_except_readme() -> None:
    entries = collect_entries()
    assert len(entries) >= 35
    paths = {rel for _, rel in entries}
    assert "adr/README.md" not in paths
    assert "adr/adr-001-fibu-domain-reuse-vs-rewrite.md" in paths
    assert "adr/ADR-CRM-001.md" in paths


@pytest.mark.unit
def test_extract_title_from_heading() -> None:
    adr = REPO / "docs" / "adr" / "adr-001-fibu-domain-reuse-vs-rewrite.md"
    title = extract_title(adr)
    assert title.startswith("ADR-001")


@pytest.mark.unit
def test_render_nav_block_has_markers_and_index() -> None:
    block = render_nav_block([("ADR-001 Test", "adr/adr-001-fibu-domain-reuse-vs-rewrite.md")])
    assert BEGIN in block
    assert END in block
    assert "Index: adr/README.md" in block
    assert "ADR-001 Test" in block


@pytest.mark.unit
def test_mkdocs_contains_generated_adr_nav() -> None:
    content = MKDOCS.read_text(encoding="utf-8")
    assert BEGIN in content
    assert END in content
    between = re.search(
        rf"{re.escape(BEGIN)}.*?{re.escape(END)}",
        content,
        re.DOTALL,
    )
    assert between
    section = between.group(0)
    assert section.count("adr/adr-") >= 35
