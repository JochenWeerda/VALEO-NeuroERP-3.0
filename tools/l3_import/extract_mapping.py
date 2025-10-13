"""
Utility to extract table / column information from the legacy L3 export.

Usage:
    python tools/l3_import/extract_mapping.py \
        --input path/to/L3_Uebersicht\ Tabellen\ und\ Spalten.xhtml \
        --output docs/data/l3/raw_tables.json

The script emits a JSON document of the shape:
{
  "ABSCHLUSS": ["SCHLUESSEL", "JAHR", ...],
  "ABSAGEGRUND": ["ID", "DBID", ...]
}

This provides the starting point for building the mapping file that will
later define how L3 data is translated into the VALEO-NeuroERP schemas.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup  # type: ignore[import]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract L3 table/column metadata.")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        type=Path,
        help="Path to the exported XHTML file from L3.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional output path for the generated JSON mapping (default: stdout).",
    )
    return parser.parse_args()


def extract_mapping(xhtml_path: Path) -> Dict[str, List[str]]:
    html = xhtml_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if table is None:
        raise ValueError("Could not locate <table> element in the provided XHTML file.")

    mapping: Dict[str, List[str]] = defaultdict(list)

    rows = table.find_all("tr")
    for row in rows[1:]:  # Skip header row
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        table_name = cells[0].get_text(strip=True)
        column_name = cells[1].get_text(strip=True)

        if not table_name or not column_name:
            continue

        columns = mapping[table_name]
        if column_name not in columns:
            columns.append(column_name)

    return dict(mapping)


def main() -> None:
    args = parse_arguments()
    mapping = extract_mapping(args.input)

    payload = json.dumps(mapping, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"Wrote raw table metadata to {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
