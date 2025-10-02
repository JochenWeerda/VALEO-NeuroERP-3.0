#!/usr/bin/env python3
"""Legacy codebase inventory tool used during CRM migration.

Scans a source directory, collects metadata for code files, and exports
CSV/JSON summaries that feed the migration planning worksheets.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

SUPPORTED_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".py", ".sql", ".json", ".yml", ".yaml"
}

EXCLUDED_DIRS = {
    "node_modules", "__pycache__", ".git", "dist", "build", "coverage"
}

@dataclass
class FileRecord:
    path: str
    extension: str
    size_bytes: int
    lines: int
    domain_hint: str


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


def detect_domain(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    if "crm" in parts:
        return "crm"
    if "erp" in parts:
        return "erp"
    if "analytics" in parts:
        return "analytics"
    if "integration" in parts:
        return "integration"
    return "shared"


def collect_records(root: Path, include: Sequence[str] | None) -> list[FileRecord]:
    records: list[FileRecord] = []
    patterns = [p.lower() for p in include] if include else []

    for file_path in iter_files(root):
        if not file_path.is_file():
            continue
        ext = file_path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue
        relative = file_path.relative_to(root)
        rel_str = str(relative).replace(os.sep, "/")
        if patterns and not any(pattern in rel_str.lower() for pattern in patterns):
            continue

        try:
            size_bytes = file_path.stat().st_size
            with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
                lines = sum(1 for _ in handle)
        except OSError:
            continue

        records.append(
            FileRecord(
                path=rel_str,
                extension=ext,
                size_bytes=size_bytes,
                lines=lines,
                domain_hint=detect_domain(relative),
            )
        )

    return records


def export_csv(records: Sequence[FileRecord], destination: Path) -> None:
    fieldnames = ["path", "extension", "size_bytes", "lines", "domain_hint"]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def export_json(records: Sequence[FileRecord], destination: Path) -> None:
    payload = [asdict(record) for record in records]
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def summarize(records: Sequence[FileRecord]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        bucket = summary[record.domain_hint]
        bucket["files"] += 1
        bucket["lines"] += record.lines
        bucket["bytes"] += record.size_bytes
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Legacy code inventory generator")
    parser.add_argument("project_root", help="Path to VALEO-NeuroERP-2.0 project")
    parser.add_argument("--include", nargs="*", help="Optional path filters (substring match)")
    parser.add_argument("--csv", default="legacy-inventory.csv", help="CSV output path")
    parser.add_argument("--json", default="legacy-inventory.json", help="JSON output path")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.exists():
        raise SystemExit(f"Project root {root} does not exist")

    records = collect_records(root, args.include or [])
    export_csv(records, Path(args.csv).resolve())
    export_json(records, Path(args.json).resolve())

    summary = summarize(records)
    print("Inventory summary by domain:")
    for domain, totals in summary.items():
        print(f"  {domain:12} files={totals['files']:5} lines={totals['lines']:7} bytes={totals['bytes']:9}")


if __name__ == "__main__":
    main()
