"""
Prepare a repo-local first-install bundle.

The bundle is intended for a virgin VALEO deployment and collects the pieces
that can be prepared inside the repository before external Ops data exists:

- bootstrap command plan
- Superglue onboarding placeholders
- mapping validation snapshot for L3/service-erp migration
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.config import settings
from app.integrations.services.superglue_onboarding_templates import (
    render_superglue_onboarding_env_template,
    render_superglue_onboarding_pack_json,
    render_superglue_onboarding_vault_template,
)
from scripts.validate_mapping import load_mapping, load_raw_metadata, validate_entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a first-install bundle for VALEO NeuroERP.")
    parser.add_argument("--tenant", default="default", help="Tenant ID for onboarding templates.")
    parser.add_argument(
        "--mapping",
        type=Path,
        default=Path("config/l3_mapping.yaml"),
        help="L3 mapping file to validate for the migration pack.",
    )
    parser.add_argument(
        "--raw",
        type=Path,
        default=Path("docs/data/l3/raw_tables.json"),
        help="Raw L3 metadata JSON used for validation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("runtime/first-install/bundle"),
        help="Output directory for the generated bundle.",
    )
    return parser.parse_args()


def resolve_runtime_environment() -> str:
    return (os.getenv("VALEO_ENV") or settings.APP_ENV or "development").strip().lower()


def build_install_context(args: argparse.Namespace, findings: list[Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": resolve_runtime_environment(),
        "tenant_id": args.tenant,
        "bootstrap_command": (
            f"python scripts/bootstrap_db.py --seed --superglue-tenant {args.tenant} "
            "--report-json runtime/first-install/bootstrap-report.json"
        ),
        "l3_dry_run_command": (
            f"python scripts/import_l3.py --mapping {args.mapping} --source data/l3_export "
            "--report-json runtime/first-install/l3-dry-run-report.json"
        ),
        "l3_execute_command": (
            f"python scripts/import_l3.py --mapping {args.mapping} --source data/l3_export "
            "--execute --backup-before-execute "
            "--report-json runtime/first-install/l3-execute-report.json"
        ),
        "mapping_findings": [
            {
                "level": item.level,
                "message": item.message,
                "context": item.context,
            }
            for item in findings
        ],
        "external_ops_blockers": [
            "Live tenant secrets for Superglue/platform services",
            "Produktive Zielsystem-URLs je Environment",
            "Environment-spezifische Policy- und Retention-Werte",
            "Vollständige service-erp/L3 Exportdumps für den Execute-Lauf",
        ],
    }


def build_markdown_summary(context: dict[str, Any]) -> str:
    lines = [
        "# First-Install Bundle",
        "",
        f"- Generated at: `{context['generated_at']}`",
        f"- Environment: `{context['environment']}`",
        f"- Tenant: `{context['tenant_id']}`",
        "",
        "## Commands",
        "",
        f"1. `{context['bootstrap_command']}`",
        f"2. `{context['l3_dry_run_command']}`",
        f"3. `{context['l3_execute_command']}`",
        "",
        "## External Ops Blockers",
        "",
    ]
    for blocker in context["external_ops_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Mapping Findings", ""])
    if context["mapping_findings"]:
        for item in context["mapping_findings"]:
            context_label = f" ({item['context']})" if item["context"] else ""
            lines.append(f"- `{item['level']}`{context_label}: {item['message']}")
    else:
        lines.append("- No mapping validation findings.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    mapping = load_mapping(args.mapping)
    raw = load_raw_metadata(args.raw)
    findings, _ = validate_entries(mapping, raw)

    context = build_install_context(args, findings)

    (args.output_dir / "install-context.json").write_text(
        json.dumps(context, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(build_markdown_summary(context), encoding="utf-8")
    (args.output_dir / "superglue-onboarding.json").write_text(
        render_superglue_onboarding_pack_json(args.tenant),
        encoding="utf-8",
    )
    (args.output_dir / "superglue-onboarding.env").write_text(
        render_superglue_onboarding_env_template(args.tenant),
        encoding="utf-8",
    )
    (args.output_dir / "superglue-onboarding.vault").write_text(
        render_superglue_onboarding_vault_template(args.tenant),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
