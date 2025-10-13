#!/usr/bin/env python3
"""Validate the L3 → VALEO-NeuroERP mapping file against extracted metadata.

The validator performs structural checks so that we fail fast before running
ETL jobs. Typical usage:

    python scripts/validate_mapping.py \
        --mapping config/l3_mapping.yaml \
        --raw docs/data/l3/raw_tables.json

Exit code is non-zero if blocking issues are found.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import yaml

ALLOWED_TYPES: Set[str] = {
    "text",
    "integer",
    "bigint",
    "numeric",
    "decimal",
    "float",
    "boolean",
    "date",
    "datetime",
    "timestamp",
    "uuid",
    "json",
}

# Keys we tolerate inside a mapping entry besides the required ones.
KNOWN_KEYS: Set[str] = {
    "target",
    "type",
    "transform",
    "notes",
    "skip",
    "status",
    "default",
    "source_format",
    "sample_value",
    "nullable",
}

# Domain-specific expectations: schema -> column -> rule config.
# Rules can assert expected types and mark them as required.
DOMAIN_RULES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "domain_finance": {
        "currency_code": {
            "type": {"text"},
            "require_type": True,
            "expect_nullable": False,
        },
        "fx_rate": {
            "type": {"numeric", "decimal", "float"},
            "require_type": True,
            "expect_nullable": False,
        },
        "fx_rate_ts": {
            "type": {"datetime", "timestamp"},
            "require_type": True,
            "expect_nullable": False,
        },
        "amount_base": {
            "type": {"numeric", "decimal", "float"},
            "require_type": True,
            "expect_nullable": False,
        },
        "amount_txn": {
            "type": {"numeric", "decimal", "float"},
            "require_type": True,
            "expect_nullable": False,
        },
    },
    "domain_crm": {
        "cancel_reason_id": {
            "type": {"integer", "uuid"},
            "require_type": True,
        },
        "stage": {
            "type": {"text"},
            "require_type": True,
            "expect_transform": {"map_enum"},
        },
        "status": {
            "type": {"text"},
            "require_type": True,
            "expect_transform": {"map_enum"},
        },
        "email": {"type": {"text"}, "require_type": False},
    },
    "domain_inventory": {
        "uom_base": {
            "type": {"text"},
            "require_type": True,
            "expect_nullable": False,
        },
        "lot_id": {
            "type": {"text", "uuid"},
            "require_type": True,
            "expect_nullable": False,
            "require_notes": True,
        },
        "quantity": {
            "type": {"numeric", "decimal", "float"},
            "require_type": True,
            "expect_nullable": False,
        },
    },
    "domain_hr": {
        "person_id": {
            "type": {"uuid"},
            "require_type": True,
            "expect_nullable": False,
        },
        "employment_start": {
            "type": {"date", "datetime", "timestamp"},
            "require_type": True,
            "expect_nullable": False,
        },
        "employment_end": {
            "type": {"date", "datetime", "timestamp"},
            "require_type": True,
            "expect_nullable": True,
        },
    },
    "domain_mfg": {
        "bom_id": {
            "type": {"uuid", "integer"},
            "require_type": True,
        },
        "routing_id": {
            "type": {"uuid", "integer"},
            "require_type": True,
        },
        "event_ts": {
            "type": {"datetime", "timestamp"},
            "require_type": True,
            "expect_nullable": False,
        },
    },
}


@dataclass
class Finding:
    level: str  # "ERROR" | "WARN"
    message: str
    context: Optional[str] = None

    def __str__(self) -> str:
        prefix = f"[{self.level}]"
        if self.context:
            return f"{prefix} {self.context}: {self.message}"
        return f"{prefix} {self.message}"


class ValidationError(Exception):
    """Raised when the mapping file cannot be loaded."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the L3 mapping file.")
    parser.add_argument(
        "--mapping",
        "-m",
        type=Path,
        default=Path("config/l3_mapping.yaml"),
        help="Path to the YAML mapping file.",
    )
    parser.add_argument(
        "--raw",
        "-r",
        type=Path,
        default=Path("docs/data/l3/raw_tables.json"),
        help="Path to the JSON metadata extracted from L3.",
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Treat warnings as errors (exit status 1).",
    )
    parser.add_argument(
        "--report-unmapped",
        action="store_true",
        help="List L3 tables that currently have no mapping entries.",
    )
    return parser.parse_args()


def load_mapping(path: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    if not path.exists():
        raise ValidationError(f"Mapping file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise ValidationError(f"Failed to parse mapping YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationError("Mapping YAML must define a dictionary at top-level.")

    # Ensure nested structure is dict -> dict -> dict
    normalized: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for table_name, columns in data.items():
        if not isinstance(table_name, str):
            raise ValidationError("Table names in mapping must be strings.")
        if columns is None:
            columns = {}
        if not isinstance(columns, dict):
            raise ValidationError(
                f"Expected mapping for table '{table_name}' to be a dictionary."
            )
        normalized_columns: Dict[str, Dict[str, Any]] = {}
        for column_name, payload in columns.items():
            if not isinstance(column_name, str):
                raise ValidationError(
                    f"Column names for table '{table_name}' must be strings."
                )
            if payload is None:
                payload = {}
            if not isinstance(payload, dict):
                raise ValidationError(
                    f"Mapping for {table_name}.{column_name} must be a dictionary."
                )
            normalized_columns[column_name] = payload
        normalized[table_name] = normalized_columns
    return normalized


def load_raw_metadata(path: Path) -> Dict[str, List[str]]:
    if not path.exists():
        raise ValidationError(f"Raw metadata JSON not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise ValidationError(f"Failed to parse raw metadata JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("Raw metadata JSON must contain an object at top-level.")

    # Normalize to str -> list[str]
    normalized: Dict[str, List[str]] = {}
    for table_name, columns in data.items():
        if not isinstance(table_name, str):
            raise ValidationError("Table names in raw metadata must be strings.")
        if not isinstance(columns, list):
            raise ValidationError(
                f"Expected list of columns for raw table '{table_name}'."
            )
        normalized[table_name] = [str(col) for col in columns]
    return normalized


def validate_entries(
    mapping: Dict[str, Dict[str, Dict[str, Any]]],
    raw: Dict[str, List[str]],
) -> Tuple[List[Finding], Dict[str, int]]:
    findings: List[Finding] = []
    target_usage: Dict[str, List[str]] = defaultdict(list)
    coverage_counter: Dict[str, int] = defaultdict(int)

    for table_name, columns in mapping.items():
        if table_name not in raw:
            findings.append(
                Finding(
                    "ERROR",
                    "Table not present in raw L3 metadata.",
                    context=table_name,
                )
            )
            continue

        for column_name, payload in columns.items():
            context = f"{table_name}.{column_name}"

            if column_name not in raw[table_name]:
                findings.append(
                    Finding(
                        "ERROR",
                        "Column not present in raw L3 metadata.",
                        context=context,
                    )
                )

            unknown_keys = set(payload.keys()) - KNOWN_KEYS
            if unknown_keys:
                findings.append(
                    Finding(
                        "WARN",
                        f"Unknown keys in mapping entry: {', '.join(sorted(unknown_keys))}",
                        context=context,
                    )
                )

            skip = bool(payload.get("skip", False))
            target = payload.get("target")
            if skip:
                if target:
                    findings.append(
                        Finding(
                            "WARN",
                            "Entry marked as skip but still defines a target; remove one.",
                            context=context,
                        )
                    )
                continue

            if not target:
                findings.append(
                    Finding("ERROR", "Missing required 'target' attribute.", context=context)
                )
            else:
                target_usage[target].append(context)
                coverage_counter[table_name] += 1

                if target.count(".") < 2:
                    findings.append(
                        Finding(
                            "ERROR",
                            "Target must follow 'schema.table.column' (at least two dots).",
                            context=context,
                        )
                    )

            entry_type = payload.get("type")
            if entry_type:
                normalized_type = str(entry_type).lower()
                if normalized_type not in ALLOWED_TYPES:
                    findings.append(
                        Finding(
                            "WARN",
                            f"Type '{entry_type}' not in allowed set: {sorted(ALLOWED_TYPES)}",
                            context=context,
                        )
                    )

            findings.extend(
                apply_domain_specific_rules(payload, context)
            )

    # Detect duplicate targets
    for target, sources in target_usage.items():
        if len(sources) > 1:
            src_list = ", ".join(sorted(sources))
            findings.append(
                Finding(
                    "ERROR",
                    f"Target referenced multiple times ({len(sources)}): {src_list}",
                    context=target,
                )
            )

    return findings, coverage_counter


def report_unmapped(
    mapping: Dict[str, Dict[str, Dict[str, Any]]],
    raw: Dict[str, List[str]],
) -> List[str]:
    """Return tables from raw metadata that do not appear in the mapping."""
    mapped_tables = {table.lower() for table in mapping}
    unmapped: List[str] = [
        table for table in sorted(raw) if table.lower() not in mapped_tables
    ]
    return unmapped


def format_summary(
    findings: Iterable[Finding],
    coverage: Dict[str, int],
) -> str:
    error_count = sum(1 for f in findings if f.level == "ERROR")
    warn_count = sum(1 for f in findings if f.level == "WARN")
    total_refs = sum(coverage.values())
    tables_with_mappings = len([table for table, count in coverage.items() if count])

    lines = [
        "Validation summary:",
        f"  Tables with mapped columns : {tables_with_mappings}",
        f"  Total mapped columns       : {total_refs}",
        f"  Errors                     : {error_count}",
        f"  Warnings                   : {warn_count}",
        "",
    ]
    return "\n".join(lines)


def parse_target(target: str) -> Optional[Tuple[str, str, str]]:
    parts = target.split(".")
    if len(parts) < 3:
        return None
    schema = parts[0]
    column = parts[-1]
    table = ".".join(parts[1:-1])
    return schema, table, column


def apply_domain_specific_rules(
    payload: Dict[str, Any],
    context: str,
) -> List[Finding]:
    """Apply opinionated domain checks based on target schema/column names."""
    findings: List[Finding] = []
    target = payload.get("target")
    if not target:
        return findings

    parsed = parse_target(target)
    if not parsed:
        return findings
    schema, _, column = parsed
    rules_for_schema = DOMAIN_RULES.get(schema)
    if not rules_for_schema:
        return findings

    column_rules = rules_for_schema.get(column)
    if not column_rules:
        return findings

    declared_type = payload.get("type")
    if column_rules.get("require_type") and not declared_type:
        findings.append(
            Finding(
                "ERROR",
                "Type is required for this domain column but missing.",
                context=context,
            )
        )
        return findings

    if declared_type:
        normalized = str(declared_type).lower()
        expected_types = column_rules.get("type")
        if expected_types and normalized not in expected_types:
            findings.append(
                Finding(
                    "WARN",
                    f"Type '{declared_type}' does not match expected {sorted(expected_types)} for domain column.",
                    context=context,
                )
            )

    if "expect_nullable" in column_rules:
        expected_nullable = bool(column_rules["expect_nullable"])
        if "nullable" not in payload:
            findings.append(
                Finding(
                    "ERROR",
                    "Nullable flag required for this domain column but missing.",
                    context=context,
                )
            )
        else:
            nullable_value = payload.get("nullable")
            if not isinstance(nullable_value, bool):
                findings.append(
                    Finding(
                        "WARN",
                        f"Nullable flag should be boolean, got '{nullable_value}'.",
                        context=context,
                    )
                )
            elif nullable_value != expected_nullable:
                findings.append(
                    Finding(
                        "WARN",
                        f"Expected nullable={expected_nullable} but found {nullable_value}.",
                        context=context,
                    )
                )

    if "expect_transform" in column_rules:
        expected_transforms = {str(item) for item in column_rules["expect_transform"]}
        transform_value = payload.get("transform")
        if transform_value is None:
            findings.append(
                Finding(
                    "ERROR",
                    f"Transform required for this domain column but missing (expected one of {sorted(expected_transforms)}).",
                    context=context,
                )
            )
        else:
            if isinstance(transform_value, str):
                actual_transforms = {transform_value}
            elif isinstance(transform_value, (list, tuple, set)):
                actual_transforms = {str(item) for item in transform_value}
            else:
                findings.append(
                    Finding(
                        "WARN",
                        f"Unexpected transform format '{transform_value}' (expected string or list).",
                        context=context,
                    )
                )
                actual_transforms = set()
            if actual_transforms and actual_transforms.isdisjoint(expected_transforms):
                findings.append(
                    Finding(
                        "WARN",
                        f"Transform {sorted(actual_transforms)} does not include required transforms {sorted(expected_transforms)}.",
                        context=context,
                    )
                )

    if column_rules.get("require_notes") and not payload.get("notes"):
        findings.append(
            Finding(
                "WARN",
                "Notes required for this domain column but missing.",
                context=context,
            )
        )

    return findings


def main() -> None:
    args = parse_args()

    try:
        mapping = load_mapping(args.mapping)
        raw = load_raw_metadata(args.raw)
    except ValidationError as exc:
        print(f"[FATAL] {exc}", file=sys.stderr)
        sys.exit(2)

    findings, coverage = validate_entries(mapping, raw)

    for finding in findings:
        print(finding)

    print(format_summary(findings, coverage))

    if args.report_unmapped:
        unmapped_tables = report_unmapped(mapping, raw)
        if unmapped_tables:
            print("Tables without mapping entries (sample):")
            for table in unmapped_tables[:50]:
                print(f"  - {table}")
            if len(unmapped_tables) > 50:
                print(f"  ... ({len(unmapped_tables) - 50} more)")
        else:
            print("All raw tables have at least one mapping entry.")

    has_errors = any(f.level == "ERROR" for f in findings)
    has_warnings = any(f.level == "WARN" for f in findings)

    if has_errors or (args.fail_on_warn and has_warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
