from __future__ import annotations

from scripts.check_fibu_cutover_mapping import validate_mapping


def _approved_mapping() -> dict:
    return {
        "metadata": {
            "approval_status": "approved",
            "approved_by": "finance-lead",
            "approved_at": "2026-04-24",
        },
        "accounts": [{"source": "L3-1000", "target": "1000", "status": "approved"}],
        "tax_codes": [{"source": "L3-V19", "target": "UST19", "rate": 19.0, "status": "approved"}],
        "cost_centers": [{"source": "L3-CC", "target": "CC", "status": "approved"}],
        "counter_accounts": [{"source_context": "ap_invoice.goods", "target": "3400", "status": "approved"}],
    }


def test_validate_mapping_accepts_fully_approved_cutover_mapping() -> None:
    summary = validate_mapping(_approved_mapping())

    assert summary["status"] == "ready"
    assert summary["blockers"] == []
    assert summary["section_counts"]["accounts"] == 1


def test_validate_mapping_blocks_draft_and_missing_sections() -> None:
    mapping = _approved_mapping()
    mapping["metadata"]["approval_status"] = "draft"
    mapping["tax_codes"] = []

    summary = validate_mapping(mapping)

    assert summary["status"] == "blocked"
    assert "metadata.approval_status must be approved" in summary["blockers"]
    assert "tax_codes must contain at least one mapping entry" in summary["blockers"]
