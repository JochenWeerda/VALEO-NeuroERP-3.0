from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SECTIONS = ("accounts", "tax_codes", "cost_centers", "counter_accounts")
APPROVED = "approved"


def _load_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Mapping file must contain a YAML object.")
    return data


def validate_mapping(data: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}

    if metadata.get("approval_status") != APPROVED:
        blockers.append("metadata.approval_status must be approved")
    if not metadata.get("approved_by"):
        blockers.append("metadata.approved_by is required")
    if not metadata.get("approved_at"):
        blockers.append("metadata.approved_at is required")

    section_counts: dict[str, int] = {}
    for section in REQUIRED_SECTIONS:
        entries = data.get(section)
        if not isinstance(entries, list) or not entries:
            blockers.append(f"{section} must contain at least one mapping entry")
            section_counts[section] = 0
            continue
        section_counts[section] = len(entries)
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                blockers.append(f"{section}[{idx}] must be an object")
                continue
            source_key = "source_context" if section == "counter_accounts" else "source"
            if not entry.get(source_key):
                blockers.append(f"{section}[{idx}].{source_key} is required")
            if not entry.get("target"):
                blockers.append(f"{section}[{idx}].target is required")
            if entry.get("status") != APPROVED:
                blockers.append(f"{section}[{idx}].status must be approved")
            if section == "tax_codes" and entry.get("rate") is None:
                warnings.append(f"{section}[{idx}].rate is recommended")

    return {
        "status": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "warnings": warnings,
        "section_counts": section_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", type=Path, default=Path("config/fibu_cutover_mapping.yaml"))
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    summary = validate_mapping(_load_mapping(args.mapping))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.strict and summary["blockers"]:
        raise SystemExit("FIBU cutover mapping blockers present")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise
