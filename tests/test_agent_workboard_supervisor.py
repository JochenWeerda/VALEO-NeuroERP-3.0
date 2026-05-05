from __future__ import annotations

from pathlib import Path

from scripts.agent_workboard_supervisor import (
    claim_proposal,
    handoff_template,
    parse_workboard,
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
