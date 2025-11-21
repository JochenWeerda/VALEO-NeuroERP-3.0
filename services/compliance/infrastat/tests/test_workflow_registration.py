from __future__ import annotations

from app.workflow.registration import _build_intrastat_definition


def test_intrastat_workflow_definition_structure() -> None:
    definition = _build_intrastat_definition()

    assert definition["name"] == "intrastat_monthly_cycle"
    assert "collecting" in definition["states"]
    event_types = {transition["event_type"] for transition in definition["transitions"]}
    assert "intrastat.submission.failed" in event_types
    assert "intrastat.validation.completed" in event_types
