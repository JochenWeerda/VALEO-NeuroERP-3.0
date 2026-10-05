"""Verbraucher-Lineage: Tabelle → Code unter app/ → native ScreenDefinition.

Erntet Roh-SQL (domain_schema.tabelle) und ORM (__tablename__ + schema).
Masken kommen ueber dataSources.entity — optionales Feld ``table`` oder
Tabellen, die die Datei mit dem Entity-Endpunkt referenziert.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "app"

QUALIFIED_TABLE_RE = re.compile(r"\b(domain_[a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)\b")
WRITE_BEFORE_RE = re.compile(
    r"(?:INSERT\s+INTO|DELETE\s+FROM|UPDATE|MERGE\s+INTO|TRUNCATE(?:\s+TABLE)?)\s+$",
    re.IGNORECASE,
)
TABLENAME_RE = re.compile(r"""__tablename__\s*=\s*['"]([a-z][a-z0-9_]*)['"]""")
SCHEMA_RE = re.compile(r"""['"]schema['"]\s*:\s*['"](domain_[a-z][a-z0-9_]*)['"]""")

_SKIP_DIR_NAMES = {"__pycache__", ".venv", "node_modules"}


def endpoint_needle(endpoint: str) -> str:
    path = (endpoint or "").strip()
    if path.startswith("/api/v1"):
        path = path[7:]
    path = re.sub(r"/\{[^}]+\}", "", path)
    return path.rstrip("/") or "/"


def split_qualified(name: str) -> tuple[str, str] | None:
    text = (name or "").strip()
    if "." not in text:
        return None
    schema, table = text.split(".", 1)
    table = table.split(".", 1)[0]
    if not schema.startswith("domain_") or not table:
        return None
    return schema, table


def _is_write(prefix: str) -> bool:
    return bool(WRITE_BEFORE_RE.search(prefix))


def harvest_python_text(relpath: str, text: str) -> dict[tuple[str, str], dict[str, set[str]]]:
    """Ordnet eine Datei den Tabellen zu, die sie nennt."""
    found: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: {"read_by": set(), "written_by": set()}
    )
    for match in QUALIFIED_TABLE_RE.finditer(text):
        key = (match.group(1), match.group(2))
        prefix = text[max(0, match.start() - 80) : match.start()]
        bucket = "written_by" if _is_write(prefix) else "read_by"
        found[key][bucket].add(relpath)

    tables = [(m.start(), m.group(1)) for m in TABLENAME_RE.finditer(text)]
    schemas = [(m.start(), m.group(1)) for m in SCHEMA_RE.finditer(text)]
    if tables and schemas:
        for tpos, tname in tables:
            after = [schema for spos, schema in schemas if spos > tpos]
            schema = after[0] if after else (schemas[0][1] if len(schemas) == 1 else None)
            if schema is None:
                continue
            found[(schema, tname)]["read_by"].add(relpath)
    return found


def iter_app_python(app_root: Path | None = None) -> Iterable[Path]:
    root = app_root or APP_ROOT
    for path in root.rglob("*.py"):
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def harvest_python(repo_root: Path | None = None, app_root: Path | None = None) -> dict[tuple[str, str], dict[str, set[str]]]:
    repo = repo_root or REPO_ROOT
    app = app_root or (repo / "app")
    merged: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: {"read_by": set(), "written_by": set()}
    )
    for path in iter_app_python(app):
        rel = path.relative_to(repo).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for key, buckets in harvest_python_text(rel, text).items():
            merged[key]["read_by"].update(buckets["read_by"])
            merged[key]["written_by"].update(buckets["written_by"])
    return merged


def load_native_screens() -> list[dict[str, Any]]:
    try:
        from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    except Exception:  # noqa: BLE001 — Generator darf ohne Maskenmodul weiterlaufen
        return []
    screens: list[dict[str, Any]] = []
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        definition = get_screen_definition(screen_id)
        if not definition:
            continue
        adapter = definition.get("adapter") or {}
        if adapter.get("type") != "native":
            continue
        screens.append(definition)
    return screens


def _entity_source(screen: dict[str, Any]) -> dict[str, Any] | None:
    for source in screen.get("dataSources") or []:
        if source.get("key") == "entity":
            return source
    return None


def index_files_by_needle(
    repo_root: Path,
    app_root: Path | None = None,
) -> dict[str, str]:
    """relpath → Dateitext, nur app/*.py."""
    repo = repo_root
    app = app_root or (repo / "app")
    texts: dict[str, str] = {}
    for path in iter_app_python(app):
        texts[path.relative_to(repo).as_posix()] = path.read_text(encoding="utf-8", errors="replace")
    return texts


def tables_for_endpoint(
    endpoint: str,
    file_texts: dict[str, str],
    file_tables: dict[str, set[tuple[str, str]]],
) -> set[tuple[str, str]]:
    """Nur Dateien, die den Endpunkt als Router-Praefix tragen — kein Volltext-Treffer."""
    needle = endpoint_needle(endpoint)
    if needle == "/":
        return set()
    found: set[tuple[str, str]] = set()
    for relpath, text in file_texts.items():
        if f'prefix="{needle}"' not in text and f"prefix='{needle}'" not in text:
            continue
        found.update(file_tables.get(relpath, set()))
    return found


def file_table_index(
    python_lineage: dict[tuple[str, str], dict[str, set[str]]],
) -> dict[str, set[tuple[str, str]]]:
    index: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for key, buckets in python_lineage.items():
        for relpath in buckets["read_by"] | buckets["written_by"]:
            index[relpath].add(key)
    return index


def freeze_lineage(
    python_lineage: dict[tuple[str, str], dict[str, set[str]]],
) -> dict[tuple[str, str], dict[str, list[str]]]:
    frozen: dict[tuple[str, str], dict[str, list[str]]] = {}
    for key, buckets in python_lineage.items():
        frozen[key] = {
            "read_by": sorted(buckets.get("read_by") or []),
            "written_by": sorted(buckets.get("written_by") or []),
            "screens": sorted(buckets.get("screens") or []),
        }
    return frozen


def attach_screens(
    python_lineage: dict[tuple[str, str], dict[str, set[str]]],
    screens: list[dict[str, Any]],
    file_texts: dict[str, str],
) -> None:
    """Haengt native Screen-IDs an die Tabellen ihrer Entity-Quelle."""
    file_tables = file_table_index(python_lineage)
    for screen in screens:
        screen_id = screen.get("id") or "?"
        entity = _entity_source(screen)
        if entity is None:
            continue
        resolved: set[tuple[str, str]] = set()
        explicit = split_qualified(str(entity.get("table") or ""))
        if explicit:
            resolved.add(explicit)
        endpoint = entity.get("endpoint") or ""
        if endpoint:
            resolved.update(tables_for_endpoint(endpoint, file_texts, file_tables))
        for key in resolved:
            python_lineage.setdefault(key, {"read_by": set(), "written_by": set()})
            python_lineage[key].setdefault("screens", set()).add(screen_id)


def screen_entity_failures(
    screens: list[dict[str, Any]],
    catalog_tables: set[tuple[str, str]],
    python_lineage: dict[tuple[str, str], dict[str, set[str]]] | None = None,
    file_texts: dict[str, str] | None = None,
) -> list[str]:
    """Native Entity-Quelle darf nicht auf eine Tabelle zeigen, die der Katalog nicht kennt.

    Nur das optionale Feld ``dataSources.entity.table`` ist der Vertrag.
    Router-SQL haengt als Verbraucher; Code-Refs ohne Katalog-Treffer
    (falsches Schema, geplante Tabellen) fallen hier nicht.
    """
    del python_lineage, file_texts
    failures: list[str] = []
    for screen in screens:
        screen_id = screen.get("id") or "?"
        entity = _entity_source(screen)
        if entity is None:
            continue
        named: set[tuple[str, str]] = set()
        explicit = split_qualified(str(entity.get("table") or ""))
        if explicit:
            named.add(explicit)
        # Router-Tabellen haengen in attach_screens als Verbraucher, nicht in diesem Gate.
        for schema, table in sorted(named):
            if (schema, table) not in catalog_tables:
                failures.append(
                    f"{screen_id}: {schema}.{table} fehlt im Katalog"
                )
    return failures


def collect_lineage(
    repo_root: Path | None = None,
    *,
    catalog_tables: set[tuple[str, str]] | None = None,
    screens: list[dict[str, Any]] | None = None,
    app_root: Path | None = None,
) -> tuple[dict[tuple[str, str], dict[str, list[str]]], list[str]]:
    """Erntet Code-Verbraucher und optional das Screen-Gate gegen den Katalog."""
    repo = repo_root or REPO_ROOT
    python_lineage = harvest_python(repo, app_root)
    texts = index_files_by_needle(repo, app_root)
    loaded_screens = screens if screens is not None else load_native_screens()
    attach_screens(python_lineage, loaded_screens, texts)
    frozen = freeze_lineage(python_lineage)
    failures: list[str] = []
    if catalog_tables is not None:
        failures = screen_entity_failures(
            loaded_screens, catalog_tables, python_lineage, texts
        )
    return frozen, failures


def harvest_lineage(
    repo_root: Path | None = None,
    screens: list[dict[str, Any]] | None = None,
    app_root: Path | None = None,
) -> dict[tuple[str, str], dict[str, list[str]]]:
    frozen, _failures = collect_lineage(
        repo_root, screens=screens, app_root=app_root
    )
    return frozen


def attach_lineage(payload: dict[str, Any], lineage: dict[tuple[str, str], dict[str, list[str]]]) -> None:
    schemas = payload.get("schemas") or {}
    for (schema, table), buckets in lineage.items():
        body = schemas.get(schema, {}).get("tables", {}).get(table)
        if body is None:
            continue
        if buckets.get("read_by"):
            body["read_by"] = buckets["read_by"]
        if buckets.get("written_by"):
            body["written_by"] = buckets["written_by"]
        if buckets.get("screens"):
            body["screens"] = buckets["screens"]
