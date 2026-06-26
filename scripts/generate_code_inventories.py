#!/usr/bin/env python3
"""Generiert Code-Inventar-Seiten fuer Drift-Report und MkDocs.

Ausgabe:
  - docs/schnittstellen/endpoint-inventory.md
  - docs/entwickler/service-inventory.md
  - docs/admin/migration-inventory.md

Verwendung:
    python scripts/generate_code_inventories.py
    python scripts/generate_code_inventories.py --check
"""

from __future__ import annotations

import argparse
import ast
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS_DIR = REPO_ROOT / "app" / "api" / "v1" / "endpoints"
SERVICES_DIR = REPO_ROOT / "app" / "services"
ALEMBIC_DIR = REPO_ROOT / "alembic" / "versions"

OUTPUTS = {
    "endpoint": REPO_ROOT / "docs" / "schnittstellen" / "endpoint-inventory.md",
    "service": REPO_ROOT / "docs" / "entwickler" / "service-inventory.md",
    "migration": REPO_ROOT / "docs" / "admin" / "migration-inventory.md",
}

META = {
    "endpoint": {
        "title": "API-Endpoint-Inventar",
        "type": "reference",
        "audience": "[entwickler, integrator]",
        "heading": "API-Endpoint-Inventar",
        "intro": (
            "Vollständiges Inventar aller FastAPI-Endpoint-Module mit Kurzbeschreibung. "
            "Beschreibungen sind aus den Modul-Docstrings extrahiert."
        ),
        "section": "Endpoint-Module",
        "column": "Modul",
    },
    "service": {
        "title": "Service-Inventar",
        "type": "reference",
        "audience": "[entwickler, qa]",
        "heading": "Service-Inventar",
        "intro": (
            "Vollständiges Inventar aller Backend-Service-Module mit Kurzbeschreibung. "
            "Beschreibungen sind aus den Modul-Docstrings extrahiert."
        ),
        "section": "Service-Module",
        "column": "Modul",
    },
    "migration": {
        "title": "Datenbank-Migrations-Inventar",
        "type": "reference",
        "audience": "[entwickler, betrieb]",
        "heading": "Datenbank-Migrations-Inventar",
        "intro": (
            "Vollständiges Inventar aller Alembic-Migrationsskripte mit Kurzbeschreibung. "
            "Beschreibungen sind aus den Datei-Docstrings extrahiert."
        ),
        "section": "Migrationsskripte",
        "column": "Modul",
    },
}


def module_summary(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return "—"
    doc = ast.get_docstring(tree)
    if not doc:
        return "—"
    for line in doc.strip().splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if len(set(cleaned)) == 1 and cleaned[0] in "-=_":
            continue
        return cleaned.replace("|", "/")
    return "—"


def collect_rows(directory: Path, skip: frozenset[str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not directory.exists():
        return rows
    for path in sorted(directory.glob("*.py")):
        stem = path.stem
        if stem in skip or stem.startswith("__"):
            continue
        rows.append((stem, module_summary(path)))
    return rows


def render(kind: str, rows: list[tuple[str, str]], today: str) -> str:
    meta = META[kind]
    lines = [
        "---",
        f"title: {meta['title']}",
        f"type: {meta['type']}",
        f"audience: {meta['audience']}",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {today}",
        "version: 3.0.0",
        f"description: {meta['intro']}",
        "---",
        "",
        f"# {meta['heading']}",
        "",
        f"> Automatisch generiert via `python scripts/generate_code_inventories.py`. **Nicht manuell bearbeiten.**",
        "",
        meta["intro"],
        "",
        f"## {meta['section']}",
        "",
        f"| {meta['column']} | Beschreibung |",
        "|---|---|",
    ]
    for stem, summary in rows:
        lines.append(f"| `{stem}` | {summary} |")
    lines.append("")
    return "\n".join(lines)


def build_all(today: str | None = None) -> dict[Path, str]:
    today = today or date.today().isoformat()
    return {
        OUTPUTS["endpoint"]: render(
            "endpoint",
            collect_rows(ENDPOINTS_DIR, frozenset({"__init__", "health", "deps"})),
            today,
        ),
        OUTPUTS["service"]: render(
            "service",
            collect_rows(SERVICES_DIR, frozenset()),
            today,
        ),
        OUTPUTS["migration"]: render(
            "migration",
            collect_rows(ALEMBIC_DIR, frozenset({"__init__", "env"})),
            today,
        ),
    }


def normalize_for_check(content: str) -> str:
    """Ignoriert last_reviewed und Generator-Hinweis beim Drift-Vergleich."""
    lines: list[str] = []
    for line in content.splitlines():
        if line.startswith("last_reviewed:"):
            continue
        if line.startswith("> Automatisch generiert"):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Code-Inventar-Markdown generieren")
    parser.add_argument("--check", action="store_true", help="Drift-Pruefung (Exit 1 bei Abweichung).")
    args = parser.parse_args()

    generated = build_all()

    if args.check:
        drift = []
        for path, content in generated.items():
            if not path.exists():
                drift.append(path)
                continue
            if normalize_for_check(path.read_text(encoding="utf-8")) != normalize_for_check(content):
                drift.append(path)
        if drift:
            print(
                "DRIFT: Inventar-Dateien nicht aktuell. "
                "Bitte 'python scripts/generate_code_inventories.py' ausfuehren.",
                file=sys.stderr,
            )
            for p in drift:
                print(f"  - {p.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        print(f"OK: {len(generated)} Inventar-Dateien aktuell.")
        return 0

    for path, content in generated.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Updated {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
