#!/usr/bin/env python3
"""
Generate a complete mask-builder JSON (L3 layout) from the SQL schema definition.

Usage:
    python generate-complete-mask-from-sql.py \
        [--sql l3-migration-toolkit/generate-complete-kundenstamm-sql.py] \
        [--base-config packages/frontend-web/src/config/mask-builder-valeo-modern.json] \
        [--output l3-migration-toolkit/mask-builder-kundenstamm-complete.json] \
        [--update-frontend]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_sql = repo_root / "l3-migration-toolkit" / "generate-complete-kundenstamm-sql.py"
    default_base = repo_root / "packages" / "frontend-web" / "src" / "config" / "mask-builder-valeo-modern.json"
    default_output = Path(__file__).resolve().parent / "mask-builder-kundenstamm-complete.json"

    parser = argparse.ArgumentParser(description="Generate mask builder JSON from SQL schema.")
    parser.add_argument("--sql", type=Path, default=default_sql, help="Path to generate-complete-kundenstamm-sql.py")
    parser.add_argument("--base-config", type=Path, default=default_base, help="Base JSON config to enrich.")
    parser.add_argument("--output", type=Path, default=default_output, help="Output JSON path for the generated mask builder config.")
    parser.add_argument("--update-frontend", action="store_true", help="Also overwrite the frontend config with the generated payload.")
    return parser.parse_args()


def load_sql_tables(sql_path: Path) -> Dict[str, str]:
    spec = importlib.util.spec_from_file_location("kundenstamm_sql", sql_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load SQL module from {sql_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    if not hasattr(module, "SQL_TABLES"):
        raise RuntimeError("SQL module does not expose SQL_TABLES.")
    return getattr(module, "SQL_TABLES")


def humanize_label(column: str) -> str:
    parts = column.replace("_", " ").split()
    if not parts:
        return column
    normalized = " ".join(word.capitalize() for word in parts)
    normalized = normalized.replace("Nr", "Nr.")
    return normalized


def component_for_type(col_type: str) -> str:
    lower = col_type.lower()
    if "boolean" in lower:
        return "Toggle"
    if "timestamp" in lower or ("date" in lower and "time" in lower):
        return "DateTime"
    if "date" in lower:
        return "Date"
    if any(token in lower for token in ("int", "numeric", "decimal", "double", "real")):
        return "Number"
    if "text" in lower and "long" in lower:
        return "TextArea"
    return "Text"


def parse_table_sql(table_name: str, sql: str) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    current_section: Dict[str, Any] = {"title": "Allgemein", "fields": []}

    comment_re = re.compile(r"--\s*(.+)")
    column_re = re.compile(
        r'^"?([a-zA-Z_][\w]*)"?\s+([a-zA-Z]+(?:\(\d+(?:,\s*\d+)?\))?(?:\s+[a-zA-Z]+)?)',
        re.IGNORECASE,
    )

    for line in sql.splitlines():
        stripped = line.strip().rstrip(",")
        if not stripped:
            continue
        if stripped.upper().startswith("CREATE TABLE") or stripped == ");":
            continue
        if stripped.startswith("--"):
            match = comment_re.match(stripped)
            if not match:
                continue
            title = match.group(1).strip()
            if not title or title.lower().startswith("primary key") or title.startswith("Tabellen-ID"):
                continue
            if current_section["fields"]:
                sections.append(current_section)
            current_section = {"title": title, "fields": []}
            continue

        match = column_re.match(stripped)
        if not match:
            continue
        col_name, col_type = match.groups()
        required = "NOT NULL" in stripped.upper() or "PRIMARY KEY" in stripped.upper()
        field = {
            "comp": component_for_type(col_type),
            "bind": f"{table_name}.{col_name}",
            "label": humanize_label(col_name),
            "optional": not required,
            "validators": ["required"] if required else [],
        }
        current_section.setdefault("grid", 3)
        current_section["fields"].append(field)

    if current_section["fields"]:
        sections.append(current_section)

    return sections


def build_generated_views(sql_tables: Dict[str, str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    views: List[Dict[str, Any]] = []
    nav_entries: List[Dict[str, str]] = []

    for table_name, table_sql in sql_tables.items():
        sections = parse_table_sql(table_name, table_sql)
        if not sections:
            continue
        view_id = f"table_{table_name}"
        nav_entries.append(
            {
                "id": view_id,
                "label": humanize_label(table_name),
                "icon": "Layers",
            }
        )
        views.append(
            {
                "id": view_id,
                "label": humanize_label(table_name),
                "sections": sections,
            }
        )
    return views, nav_entries


def enrich_config(base_path: Path, generated_views: List[Dict[str, Any]], nav_entries: List[Dict[str, str]]) -> Dict[str, Any]:
    base_config = json.loads(base_path.read_text(encoding="utf-8"))
    existing_nav_ids = {entry["id"] for entry in base_config.get("layout", {}).get("nav", [])}
    filtered_nav = [entry for entry in nav_entries if entry["id"] not in existing_nav_ids]
    existing_view_ids = {view["id"] for view in base_config.get("views", []) if isinstance(view, dict) and "id" in view}
    filtered_views = [view for view in generated_views if view["id"] not in existing_view_ids]
    base_config.setdefault("layout", {}).setdefault("nav", []).extend(filtered_nav)
    base_config.setdefault("views", []).extend(filtered_views)
    return base_config


def main() -> None:
    args = parse_args()
    sql_tables = load_sql_tables(args.sql)
    generated_views, nav_entries = build_generated_views(sql_tables)

    enriched_config = enrich_config(args.base_config, generated_views, nav_entries)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(enriched_config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[mask-builder] Generated config written to {args.output}")

    if args.update_frontend:
        args.base_config.write_text(json.dumps(enriched_config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[mask-builder] Frontend config updated at {args.base_config}")


if __name__ == "__main__":
    main()
