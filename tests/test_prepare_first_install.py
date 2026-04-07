from __future__ import annotations

from scripts.prepare_first_install import build_install_context, build_markdown_summary


def test_build_install_context_lists_external_blockers():
    context = build_install_context(
        type("Args", (), {"tenant": "tenant-a", "mapping": "config/l3_mapping.yaml", "raw": "docs/data/l3/raw_tables.json"})(),
        findings=[],
    )

    assert context["tenant_id"] == "tenant-a"
    assert "Live tenant secrets" in context["external_ops_blockers"][0]
    assert "bootstrap_db.py" in context["bootstrap_command"]


def test_build_markdown_summary_contains_commands_and_blockers():
    markdown = build_markdown_summary(
        {
            "generated_at": "2026-04-07T00:00:00Z",
            "environment": "development",
            "tenant_id": "tenant-a",
            "bootstrap_command": "python scripts/bootstrap_db.py",
            "l3_dry_run_command": "python scripts/import_l3.py --dry-run",
            "l3_execute_command": "python scripts/import_l3.py --execute",
            "external_ops_blockers": ["Live tenant secrets"],
            "mapping_findings": [],
        }
    )

    assert "# First-Install Bundle" in markdown
    assert "python scripts/bootstrap_db.py" in markdown
    assert "Live tenant secrets" in markdown
