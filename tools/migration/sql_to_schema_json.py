"""Utility to derive JSON schema descriptors from legacy SQL files."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Iterable, List, Optional

COLUMN_PATTERN = re.compile(
    r"^(?P<name>\w+|\"[^\"]+\")\s+(?P<type>[A-Za-z0-9_]+(?:\s*\([^)]*\))?)(?P<rest>.*)$",
    re.IGNORECASE,
)
PRIMARY_KEY_INLINE_PATTERN = re.compile(r"PRIMARY\s+KEY", re.IGNORECASE)
NOT_NULL_PATTERN = re.compile(r"NOT\s+NULL", re.IGNORECASE)
DEFAULT_PATTERN = re.compile(r"DEFAULT\s+([^,]+)", re.IGNORECASE)


@dataclass
class ColumnDescriptor:
    name: str
    type: str
    nullable: bool = True
    default: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


@dataclass
class TableDescriptor:
    schema: str
    name: str
    primaryKey: Optional[str]
    fields: List[ColumnDescriptor]
    rawSource: str

    def to_json(self) -> str:
        payload = asdict(self)
        payload["table"] = f"{self.schema}.{self.name}" if self.schema else self.name
        return json.dumps(payload, indent=2)


def _clean_identifier(value: str) -> str:
    value = value.strip().strip('"')
    return value


def parse_tables(sql: str) -> Iterable[TableDescriptor]:
    lines = sql.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line or line.startswith("--"):
            index += 1
            continue
        if not line.upper().startswith("CREATE TABLE"):
            index += 1
            continue

        # join following lines until closing );
        buffer: List[str] = []
        while index < len(lines):
            buffer.append(lines[index])
            if lines[index].strip().endswith(");"):
                index += 1
                break
            index += 1

        block = "\n".join(buffer)
        header, body = block.split("(", 1)
        body = body.rsplit(")", 1)[0]
        header_tokens = header.replace("CREATE TABLE", "").replace("IF NOT EXISTS", "").strip()
        full_table_name = header_tokens.strip().strip("(")
        if full_table_name.lower().startswith("public."):
            schema, table_name = full_table_name.split(".", 1)
        elif "." in full_table_name:
            schema, table_name = full_table_name.split(".", 1)
        else:
            schema, table_name = "", full_table_name
        schema = _clean_identifier(schema)
        table_name = _clean_identifier(table_name)

        columns: List[ColumnDescriptor] = []
        primary_key: Optional[str] = None

        for raw_line in body.split(",\n"):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            if stripped.upper().startswith("PRIMARY KEY"):
                inside = stripped[stripped.find("(") + 1 : stripped.rfind(")")]
                candidate = inside.split(",")[0].strip()
                primary_key = _clean_identifier(candidate)
                continue
            if stripped.upper().startswith("CONSTRAINT"):
                if "PRIMARY KEY" in stripped.upper():
                    inside = stripped[stripped.find("(") + 1 : stripped.rfind(")")]
                    candidate = inside.split(",")[0].strip()
                    primary_key = _clean_identifier(candidate)
                continue

            match = COLUMN_PATTERN.match(stripped)
            if not match:
                continue
            name = _clean_identifier(match.group("name"))
            col_type = match.group("type").strip()
            remainder = match.group("rest")
            nullable = not bool(NOT_NULL_PATTERN.search(remainder))
            default_match = DEFAULT_PATTERN.search(remainder)
            default = default_match.group(1).strip() if default_match else None
            constraints: List[str] = []
            if PRIMARY_KEY_INLINE_PATTERN.search(remainder):
                primary_key = name
                constraints.append("primary-key")
            if "UNIQUE" in remainder.upper():
                constraints.append("unique")
            if "REFERENCES" in remainder.upper():
                constraints.append("foreign-key")

            columns.append(
                ColumnDescriptor(
                    name=name,
                    type=col_type.strip(),
                    nullable=nullable,
                    default=default,
                    constraints=constraints,
                )
            )

        yield TableDescriptor(schema=schema, name=table_name, primaryKey=primary_key, fields=columns, rawSource=block.strip())


def write_descriptors(tables: Iterable[TableDescriptor], output_dir: Path, prefix: Optional[str] = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for table in tables:
        filename = f"{prefix + '_' if prefix else ''}{table.schema}_{table.name}.json" if table.schema else f"{prefix + '_' if prefix else ''}{table.name}.json"
        target = output_dir / filename
        target.write_text(table.to_json() + "\n", encoding="utf-8")
        print(f"Wrote {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert legacy SQL schema to JSON descriptors.")
    parser.add_argument("--sql", required=True, help="Path to the SQL file to parse.")
    parser.add_argument("--out", default="memory-bank/migration/schemas", help="Directory to place generated JSON files.")
    parser.add_argument("--prefix", default=None, help="Optional prefix for generated filenames.")
    args = parser.parse_args()

    sql_path = Path(args.sql).resolve()
    sql_text = sql_path.read_text(encoding="utf-8")
    tables = list(parse_tables(sql_text))
    output_dir = Path(args.out).resolve()
    write_descriptors(tables, output_dir, args.prefix)


if __name__ == "__main__":
    main()