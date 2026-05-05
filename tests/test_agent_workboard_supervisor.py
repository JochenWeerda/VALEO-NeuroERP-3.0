from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.agent_workboard_supervisor import (
    SliceFile,
    ValidationError,
    claim_proposal,
    handoff_template,
    load_slice_files,
    parse_workboard,
    validate_workboard_slices,
    cmd_validate,
)


WORKBOARD_SAMPLE = """# Active Workboard

## OPEN-SLICE-001

**Von:** Codex
**Stand:** offen
**Ziel des Slices:** Offenen Slice erkennen.
**Dateibesitz:** `a.py`, `tests/test_a.py`
**Abnahmekriterien:** Parser liefert Metadaten.
**Checks:** `pytest tests/test_a.py -q`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Markdown ist weich.

## RESERVED-SLICE-001

**Owner:** Cursor
**Stand:** reserviert
**Ziel des Slices:** Nicht automatisch uebernehmen.

## Arbeitsregel

Kein Slice.

## DONE-SLICE-001

**Stand:** abgeschlossen
**Ziel des Slices:** Bereits fertig.

## DONE-SLICE-002

**Stand:** implementiert, committed und gruen; keine offenen Regressionen.
**Ziel des Slices:** Offen im Satz darf nicht als Status offen gelten.
"""


def test_parse_workboard_detects_slice_status_and_checks():
    slices = parse_workboard(WORKBOARD_SAMPLE)

    assert [item.slice_id for item in slices] == [
        "OPEN-SLICE-001",
        "RESERVED-SLICE-001",
        "DONE-SLICE-001",
        "DONE-SLICE-002",
    ]
    open_slice = slices[0]
    assert open_slice.status_class == "open"
    assert open_slice.owner == "Codex"
    assert open_slice.file_ownership == "`a.py`, `tests/test_a.py`"
    assert open_slice.checks == [
        "pytest tests/test_a.py -q",
        "node scripts/docs-governance-check.cjs",
    ]
    assert slices[-1].status_class == "done"


def test_claim_proposal_is_manual_and_commit_scoped():
    item = parse_workboard(WORKBOARD_SAMPLE)[0]
    proposal = claim_proposal(item, "Agent-1", Path("docs/agent-ops/active-workboard.md"))

    assert "Slice: OPEN-SLICE-001" in proposal
    assert "**Stand:** reserviert" in proposal
    assert "**Owner:** Agent-1" in proposal
    assert "git add docs/agent-ops/active-workboard.md" in proposal
    assert "git commit -m" in proposal
    assert "Start implementation only after" in proposal


def test_handoff_template_contains_required_sections():
    item = parse_workboard(WORKBOARD_SAMPLE)[0]
    template = handoff_template(item, "Agent-1")

    assert "## Handoff OPEN-SLICE-001" in template
    assert "**Owner:** Agent-1" in template
    assert "**Dateibesitz:** `a.py`, `tests/test_a.py`" in template
    assert "**Checks:**" in template
    assert "**Naechster Schritt:**" in template


# ---------------------------------------------------------------------------
# YAML slice file tests
# ---------------------------------------------------------------------------

YAML_VALID = textwrap.dedent("""\
    id: TEST-SLICE-001
    status: reserviert
    owner: Codex
    goal: Ziel des Slices.
    file_ownership:
      - scripts/foo.py
      - tests/test_foo.py
    acceptance_criteria: Alle Tests gruen.
    checks:
      - pytest tests/test_foo.py -q
    risks: Kein Risiko.
""")

YAML_MISSING_OWNER = textwrap.dedent("""\
    id: TEST-SLICE-002
    status: offen
    goal: Ziel ohne Owner.
    file_ownership:
      - scripts/bar.py
""")

YAML_MISSING_FILE_OWNERSHIP = textwrap.dedent("""\
    id: TEST-SLICE-003
    status: reserviert
    owner: Cursor
    goal: Ziel ohne Dateibesitz.
""")


def _make_slice_file(data: str, name: str, tmp_path: Path) -> Path:
    p = tmp_path / name
    p.write_text(data, encoding="utf-8")
    return p


def test_load_slice_files_valid(tmp_path):
    _make_slice_file(YAML_VALID, "TEST-SLICE-001.yaml", tmp_path)
    result = load_slice_files(tmp_path)
    assert len(result) == 1
    sf = result[0]
    assert sf.slice_id == "TEST-SLICE-001"
    assert sf.status == "reserviert"
    assert sf.owner == "Codex"
    assert sf.file_ownership == ["scripts/foo.py", "tests/test_foo.py"]
    assert sf.checks == ["pytest tests/test_foo.py -q"]


def test_load_slice_files_empty_dir(tmp_path):
    assert load_slice_files(tmp_path) == []


def test_load_slice_files_missing_dir(tmp_path):
    assert load_slice_files(tmp_path / "nonexistent") == []


def test_load_slice_files_multiple(tmp_path):
    _make_slice_file(YAML_VALID, "TEST-SLICE-001.yaml", tmp_path)
    _make_slice_file(YAML_MISSING_OWNER, "TEST-SLICE-002.yaml", tmp_path)
    result = load_slice_files(tmp_path)
    assert len(result) == 2
    ids = {sf.slice_id for sf in result}
    assert ids == {"TEST-SLICE-001", "TEST-SLICE-002"}


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

def _make_sf(slice_id="SF-001", status="reserviert", owner="Codex",
             file_ownership=None, source_path=None) -> SliceFile:
    return SliceFile(
        slice_id=slice_id,
        status=status,
        owner=owner,
        goal="goal",
        file_ownership=file_ownership or ["a.py"],
        acceptance_criteria=None,
        checks=[],
        risks=None,
        source_path=source_path or Path(f"docs/agent-ops/slices/{slice_id}.yaml"),
    )


def test_validate_no_errors_when_yaml_files_are_complete():
    slices = parse_workboard(WORKBOARD_SAMPLE)
    sf = _make_sf("OPEN-SLICE-001")
    errors = validate_workboard_slices(slices, [sf])
    assert errors == []


def test_validate_yaml_missing_owner_is_error(tmp_path):
    _make_slice_file(YAML_MISSING_OWNER, "TEST-SLICE-002.yaml", tmp_path)
    slice_files = load_slice_files(tmp_path)
    errors = validate_workboard_slices([], slice_files)
    assert any(e.field == "owner" and e.slice_id == "TEST-SLICE-002" for e in errors)


def test_validate_yaml_missing_file_ownership_is_error(tmp_path):
    _make_slice_file(YAML_MISSING_FILE_OWNERSHIP, "TEST-SLICE-003.yaml", tmp_path)
    slice_files = load_slice_files(tmp_path)
    errors = validate_workboard_slices([], slice_files)
    assert any(e.field == "file_ownership" and e.slice_id == "TEST-SLICE-003" for e in errors)


def test_validate_markdown_without_yaml_not_checked_by_default():
    """Historical markdown slices without YAML should not fail validation."""
    slices = parse_workboard(WORKBOARD_SAMPLE)
    # RESERVED-SLICE-001 has no owner field in markdown (has Owner: Cursor but no Von)
    # DONE-SLICE-001 has no owner at all — but no YAML file for it
    errors = validate_workboard_slices(slices, [])
    assert errors == []


def test_validate_strict_ids_forces_markdown_check():
    """strict_ids forces validation on a markdown-only slice."""
    workboard = """# WB

## NO-OWNER-001

**Stand:** reserviert
**Dateibesitz:** `a.py`
"""
    slices = parse_workboard(workboard)
    errors = validate_workboard_slices(slices, [], strict_ids={"NO-OWNER-001"})
    assert any(e.field == "owner" and e.slice_id == "NO-OWNER-001" for e in errors)


def test_validate_returns_zero_exit_on_clean(tmp_path):
    _make_slice_file(YAML_VALID, "TEST-SLICE-001.yaml", tmp_path)
    workboard_file = tmp_path / "workboard.md"
    workboard_file.write_text("# WB\n", encoding="utf-8")

    args = MagicMock()
    args.workboard = workboard_file
    args.slices_dir = tmp_path
    args.strict_ids = None
    args.json = False

    assert cmd_validate(args) == 0


def test_validate_returns_nonzero_exit_on_error(tmp_path):
    _make_slice_file(YAML_MISSING_OWNER, "TEST-SLICE-002.yaml", tmp_path)
    workboard_file = tmp_path / "workboard.md"
    workboard_file.write_text("# WB\n", encoding="utf-8")

    args = MagicMock()
    args.workboard = workboard_file
    args.slices_dir = tmp_path
    args.strict_ids = None
    args.json = False

    assert cmd_validate(args) == 1
