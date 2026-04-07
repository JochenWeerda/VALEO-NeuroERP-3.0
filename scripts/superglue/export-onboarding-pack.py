from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.integrations.services.superglue_onboarding_templates import (
    render_superglue_onboarding_env_template,
    render_superglue_onboarding_pack_json,
    render_superglue_onboarding_vault_template,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Superglue onboarding artifacts for a tenant.")
    parser.add_argument("--tenant", default="default", help="Tenant ID")
    parser.add_argument("--format", choices=("json", "env", "vault"), default="json", help="Output format")
    parser.add_argument("--output", help="Optional output file path")
    args = parser.parse_args()

    if args.format == "json":
        content = render_superglue_onboarding_pack_json(args.tenant)
    elif args.format == "env":
        content = render_superglue_onboarding_env_template(args.tenant)
    else:
        content = render_superglue_onboarding_vault_template(args.tenant)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
