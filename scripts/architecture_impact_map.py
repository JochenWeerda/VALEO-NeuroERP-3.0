#!/usr/bin/env python3
"""Architecture Impact Map — laden, validieren, Pfade matchen.

Reine Bibliothek (P1): kein CLI, kein vor_push-Wire.
"""

from __future__ import annotations

import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP_PATH = REPO_ROOT / "config" / "architecture-impact-map.yaml"

# Exakte Namen aus scripts/vor_push.py REGISTER (Spalte 0). Hardcodierte
# Whitelist fuer Schema-Validierung; Tests vergleichen zusaetzlich mit Import.
KNOWN_REGISTER_IDS: frozenset[str] = frozenset(
    {
        "Baseline-Integritaet",
        "Improvement-Pipelines (Godfiles, Paginierung, ...)",
        "Doc-Generatoren (OpenAPI, C4, Architektur-Index, MCP, Aktionsmatrix)",
        "Tabellenkatalog (Lineage)",
        "RLS-Inventar (frisches Schema)",
        "RLS-Domaenenmatrix",
        "Pflichtstruktur der Domaenen",
        "Tabellenzuordnung der Domaenen",
        "CLI-Register der Maskenaktionen",
        "Aktionskatalog der KI-Bedienung",
        "Masken-Studio-Ratsche",
        "Domaenenabnahme (M4)",
        "Maskenfamilien-Versionen",
        "Belegmasken-Versionen",
        "Studio-Screen-Katalog",
        "Docs-Governance",
    }
)

REQUIRED_CLASS_FIELDS = (
    "id",
    "description",
    "globs",
    "contracts",
    "generators",
    "checks_dbfree",
    "register_ids",
    "hints",
    "requires_db",
)

DEFAULT_STRUCTURAL_PREFIXES = (
    "app/",
    "alembic/",
    "modules/",
    "packages/frontend-web/",
)


class ImpactMapError(ValueError):
    """Ungueltige Map oder Schemaverletzung."""


@dataclass(frozen=True)
class ImpactClass:
    id: str
    description: str
    globs: tuple[str, ...]
    contracts: tuple[str, ...]
    generators: tuple[str, ...]
    checks_dbfree: tuple[str, ...]
    register_ids: tuple[str, ...]
    hints: tuple[str, ...]
    requires_db: bool
    pr232_refs: tuple[str, ...] = ()

    def matches(self, path: str) -> bool:
        normalized = _normalize_path(path)
        return any(_glob_match(normalized, pattern) for pattern in self.globs)


@dataclass
class ImpactReport:
    """Aggregiertes Match-Ergebnis fuer eine Pfadliste."""

    classes: list[ImpactClass] = field(default_factory=list)
    matched_paths: dict[str, list[str]] = field(default_factory=dict)
    unmapped_paths: list[str] = field(default_factory=list)
    unmapped_structural: bool = False
    generators: list[str] = field(default_factory=list)
    checks_dbfree: list[str] = field(default_factory=list)
    register_ids: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    requires_db: bool = False
    pr232_refs: list[str] = field(default_factory=list)

    @property
    def class_ids(self) -> list[str]:
        return [c.id for c in self.classes]

    def to_dict(self) -> dict[str, Any]:
        return {
            "classes": [asdict(c) for c in self.classes],
            "class_ids": self.class_ids,
            "matched_paths": self.matched_paths,
            "unmapped_paths": list(self.unmapped_paths),
            "unmapped_structural": self.unmapped_structural,
            "generators": list(self.generators),
            "checks_dbfree": list(self.checks_dbfree),
            "register_ids": list(self.register_ids),
            "hints": list(self.hints),
            "requires_db": self.requires_db,
            "pr232_refs": list(self.pr232_refs),
        }


@dataclass(frozen=True)
class ImpactMap:
    version: int
    classes: tuple[ImpactClass, ...]
    structural_prefixes: tuple[str, ...] = DEFAULT_STRUCTURAL_PREFIXES

    def class_by_id(self, class_id: str) -> ImpactClass | None:
        for item in self.classes:
            if item.id == class_id:
                return item
        return None


def _normalize_path(path: str) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Uebersetzt Gitignore-aehnliche Globs (inkl. ``**``) in ein Regex."""
    i = 0
    out: list[str] = ["^"]
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    out.append("$")
    return re.compile("".join(out))


def _glob_match(path: str, pattern: str) -> bool:
    """Gitignore-aehnliches Glob mit ``**`` (ohne Inhaltsheuristik)."""
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)
    if _glob_to_regex(pattern).match(path):
        return True
    # Basename-only Muster (z. B. ``**/mask*`` trifft auch reine Dateinamen)
    if "/" not in pattern.rstrip("*?"):
        return _glob_to_regex(pattern).match(path.split("/")[-1]) is not None
    return False


def _as_str_tuple(value: Any, field_name: str, class_id: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ImpactMapError(
            f"Klasse {class_id!r}: Feld {field_name!r} muss eine Liste sein"
        )
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ImpactMapError(
                f"Klasse {class_id!r}: {field_name!r} darf nur Strings enthalten"
            )
        out.append(item)
    return tuple(out)


def _parse_class(raw: Any, index: int) -> ImpactClass:
    if not isinstance(raw, dict):
        raise ImpactMapError(f"classes[{index}] muss ein Mapping sein")
    missing = [name for name in REQUIRED_CLASS_FIELDS if name not in raw]
    if missing:
        raise ImpactMapError(
            f"classes[{index}] (id={raw.get('id')!r}): fehlende Pflichtfelder: {', '.join(missing)}"
        )
    class_id = raw["id"]
    if not isinstance(class_id, str) or not class_id:
        raise ImpactMapError(f"classes[{index}]: id muss nicht-leerer String sein")
    if not isinstance(raw["description"], str):
        raise ImpactMapError(f"Klasse {class_id!r}: description muss String sein")
    if not isinstance(raw["requires_db"], bool):
        raise ImpactMapError(f"Klasse {class_id!r}: requires_db muss bool sein")

    register_ids = _as_str_tuple(raw["register_ids"], "register_ids", class_id)
    unknown = [rid for rid in register_ids if rid not in KNOWN_REGISTER_IDS]
    if unknown:
        raise ImpactMapError(
            f"Klasse {class_id!r}: unbekannte register_ids: {', '.join(unknown)}"
        )

    globs = _as_str_tuple(raw["globs"], "globs", class_id)
    if not globs:
        raise ImpactMapError(f"Klasse {class_id!r}: globs darf nicht leer sein")

    return ImpactClass(
        id=class_id,
        description=raw["description"],
        globs=globs,
        contracts=_as_str_tuple(raw["contracts"], "contracts", class_id),
        generators=_as_str_tuple(raw["generators"], "generators", class_id),
        checks_dbfree=_as_str_tuple(raw["checks_dbfree"], "checks_dbfree", class_id),
        register_ids=register_ids,
        hints=_as_str_tuple(raw["hints"], "hints", class_id),
        requires_db=bool(raw["requires_db"]),
        pr232_refs=_as_str_tuple(raw.get("pr232_refs") or [], "pr232_refs", class_id),
    )


def load_map(path: Path | str | None = None) -> ImpactMap:
    """Lädt und validiert die Impact-Map."""
    map_path = Path(path) if path else DEFAULT_MAP_PATH
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ImpactMapError("PyYAML fehlt") from exc

    if not map_path.is_file():
        raise ImpactMapError(f"Map nicht gefunden: {map_path}")

    data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ImpactMapError("Map-Wurzel muss ein Mapping sein")
    if "version" not in data:
        raise ImpactMapError("Map: Pflichtfeld version fehlt")
    if "classes" not in data or not isinstance(data["classes"], list):
        raise ImpactMapError("Map: classes muss eine Liste sein")
    if not data["classes"]:
        raise ImpactMapError("Map: classes darf nicht leer sein")

    classes = tuple(_parse_class(item, i) for i, item in enumerate(data["classes"]))
    ids = [c.id for c in classes]
    if len(ids) != len(set(ids)):
        raise ImpactMapError("Map: doppelte class ids")

    prefixes_raw = data.get("structural_prefixes") or list(DEFAULT_STRUCTURAL_PREFIXES)
    if not isinstance(prefixes_raw, list) or not all(
        isinstance(p, str) for p in prefixes_raw
    ):
        raise ImpactMapError("structural_prefixes muss Liste von Strings sein")

    return ImpactMap(
        version=int(data["version"]),
        classes=classes,
        structural_prefixes=tuple(prefixes_raw),
    )


def _is_structural(path: str, prefixes: Sequence[str]) -> bool:
    normalized = _normalize_path(path)
    return any(
        normalized == p.rstrip("/") or normalized.startswith(p)
        for p in prefixes
    )


def _unique_preserve(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def match_paths(
    paths: Sequence[str],
    impact_map: ImpactMap | None = None,
    *,
    map_path: Path | str | None = None,
) -> ImpactReport:
    """Matched Pfade gegen die Map; Union aller treffenden Klassen."""
    loaded = impact_map if impact_map is not None else load_map(map_path)
    matched: dict[str, ImpactClass] = {}
    matched_paths: dict[str, list[str]] = {}
    unmapped: list[str] = []

    for raw_path in paths:
        path = _normalize_path(raw_path)
        hits = [cls for cls in loaded.classes if cls.matches(path)]
        if not hits:
            if _is_structural(path, loaded.structural_prefixes):
                unmapped.append(path)
            continue
        for cls in hits:
            matched[cls.id] = cls
            matched_paths.setdefault(cls.id, []).append(path)

    ordered = [cls for cls in loaded.classes if cls.id in matched]
    generators = _unique_preserve(g for cls in ordered for g in cls.generators)
    checks = _unique_preserve(c for cls in ordered for c in cls.checks_dbfree)
    registers = _unique_preserve(r for cls in ordered for r in cls.register_ids)
    hints = _unique_preserve(h for cls in ordered for h in cls.hints)
    refs = _unique_preserve(r for cls in ordered for r in cls.pr232_refs)

    return ImpactReport(
        classes=ordered,
        matched_paths={k: matched_paths[k] for k in [c.id for c in ordered]},
        unmapped_paths=unmapped,
        unmapped_structural=bool(unmapped),
        generators=generators,
        checks_dbfree=checks,
        register_ids=registers,
        hints=hints,
        requires_db=any(cls.requires_db for cls in ordered),
        pr232_refs=refs,
    )


def main(argv: list[str] | None = None) -> int:
    """Minimaler Smoke: Map laden und Schema validieren."""
    args = list(sys.argv[1:] if argv is None else argv)
    path = Path(args[0]) if args else DEFAULT_MAP_PATH
    try:
        impact_map = load_map(path)
    except ImpactMapError as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2
    print(f"OK: version={impact_map.version} classes={len(impact_map.classes)}")
    for cls in impact_map.classes:
        print(f"  - {cls.id} (requires_db={cls.requires_db})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
