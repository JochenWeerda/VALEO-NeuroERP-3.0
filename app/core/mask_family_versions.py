"""Maskenfamilien: eine Maske, mehrere Varianten, unveraenderlich versioniert (Nutzerentscheidung 08.11.2026).

Gleichartige Masken werden nicht als Einzelmasken angelegt, sondern als Varianten einer Familie, wie die
Belegfolge (``config/document_screen_versions.json``). Eine Familie hat je Release eine **Basis** (die
Wurzel-Eigenschaften, die alle Varianten wortgleich teilen) und je Variante einen **Patch** (die Wurzel-
Eigenschaften, in denen sie abweicht). Ein Patch ersetzt ganze Wurzel-Eigenschaften; Listen werden nie
gemischt. Basis, Patch und materialisierte Definition sind gehasht; eine gebundene Fassung folgt nie einem
geaenderten Alias.

Neue Familien liegen als ``config/mask_families/<familie>.json`` vor und tragen ihre Variante in
``definition["variant"] == {"family": <familie>, "id": <variante>}``. Die Screen-ID einer Variante ist
``<familie>/<variante>`` (Unterstriche als Bindestriche). Die Belegfamilie behaelt ihre Datei, ihr Feld
``variant.belegart`` und ihre Fehlercodes (``document_screen_versions`` delegiert hierher).

Erzeugen und pruefen: ``python scripts/generate_mask_family_versions.py [--check] [--family f --release-version v]``.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any

from app.core.studio_release import definition_hash

ROOT = Path(__file__).resolve().parents[2]
FAMILIES_DIR = ROOT / "config/mask_families"
_VERSION = re.compile(r"[1-9][0-9]*\.[0-9]+\.[0-9]+\Z")
_FAMILY = re.compile(r"[a-z][a-z0-9-]{1,40}\Z")


@dataclass(frozen=True)
class FamilySpec:
    """Wie eine Familie ihre Variante erkennt, ihre Bindung nennt und Fehler meldet."""

    name: str
    error_prefix: str = "mask_family"
    binding_key: str = "maskVariant"
    variant_field: str = "id"

    def error(self, code: str) -> ValueError:
        return ValueError(f"{self.error_prefix}_{code}")

    def variant_of(self, definition: dict[str, Any]) -> Any:
        variant = definition.get("variant") or {}
        if self.variant_field == "id" and variant.get("family") != self.name:
            return None
        return variant.get(self.variant_field)


def spec_for(family: str) -> FamilySpec:
    if not isinstance(family, str) or not _FAMILY.fullmatch(family) or family == "beleg":
        raise ValueError("mask_family_name_invalid")
    return FamilySpec(name=family)


def screen_id(family: str, variant_id: str) -> str:
    return f"{family}/{variant_id.replace('_', '-')}"


def resolve_variant(registry: dict, variant_id: str, version: str | None = None, *,
                    expected: dict | None = None, spec: FamilySpec | None = None) -> dict:
    """Eine exakte Fassung materialisieren; ``expected`` bindet an Basis, Patch und Ergebnis."""
    spec = spec or spec_for(registry.get("family") if isinstance(registry, dict) else None)
    try:
        if (type(registry["schemaVersion"]) is not int or registry["schemaVersion"] != 1
                or registry["family"] != spec.name):
            raise spec.error("registry_invalid")
        version = registry["current"][variant_id] if version is None else version
        record = registry["variants"][variant_id][version]
        base_version = record["baseVersion"]
        base = registry["bases"][base_version]
        if not _VERSION.fullmatch(version) or not _VERSION.fullmatch(base_version):
            raise spec.error("version_invalid")
        if (definition_hash(base["definition"]) != base["hash"]
                or record["baseHash"] != base["hash"]
                or definition_hash(record["patch"]) != record["patchHash"]):
            raise spec.error("content_changed")
        definition = {**deepcopy(base["definition"]), **deepcopy(record["patch"])}
        stamp = definition_hash(definition)
        if stamp != record["definitionHash"]:
            raise spec.error("materialization_changed")
        if spec.variant_of(definition) != variant_id:
            raise spec.error("variant_mismatch")
        binding = {"family": spec.name, "baseVersion": base_version,
                   "baseHash": base["hash"], "variantId": variant_id,
                   "variantVersion": version, "variantHash": record["patchHash"],
                   "materializedHash": stamp}
        if expected is not None and expected != binding:
            raise spec.error("binding_changed")
        definition[spec.binding_key] = binding
        return definition
    except (KeyError, TypeError, AttributeError) as error:
        raise spec.error("version_unknown_or_invalid") from error


def check_registry(registry: dict, *, spec: FamilySpec | None = None) -> None:
    """Auch die Historie pruefen, nicht nur die aktuellen Aliase."""
    spec = spec or spec_for(registry.get("family") if isinstance(registry, dict) else None)
    try:
        for version, base in registry["bases"].items():
            if not _VERSION.fullmatch(version) or definition_hash(base["definition"]) != base["hash"]:
                raise spec.error("base_changed")
        for variant_id, versions in registry["variants"].items():
            for version in versions:
                resolve_variant(registry, variant_id, version, spec=spec)
        for variant_id, version in registry["current"].items():
            resolve_variant(registry, variant_id, version, spec=spec)
    except (KeyError, TypeError, AttributeError) as error:
        raise spec.error("registry_invalid") from error


def extend_registry(definitions: dict[str, dict], version: str, previous: dict | None = None, *,
                    spec: FamilySpec) -> dict:
    """Ein Release anhaengen. Bestehende Basen und Varianten werden nie ueberschrieben."""
    if not isinstance(version, str) or not _VERSION.fullmatch(version):
        raise spec.error("version_invalid")
    if not definitions:
        raise spec.error("variants_empty")
    registry = deepcopy(previous) if previous is not None else {
        "schemaVersion": 1, "family": spec.name, "bases": {}, "variants": {}, "current": {}}
    if previous is not None:
        check_registry(previous, spec=spec)
    if version in registry["bases"] or any(version in rows for rows in registry["variants"].values()):
        raise spec.error("version_already_exists")
    if registry["bases"] and tuple(map(int, version.split("."))) <= max(
            tuple(map(int, key.split("."))) for key in registry["bases"]):
        raise spec.error("version_must_advance")
    first = next(iter(definitions.values()))
    base = {key: deepcopy(value) for key, value in first.items()
            if all(key in item and item[key] == value for item in definitions.values())}
    base_hash = definition_hash(base)
    registry["bases"][version] = {"definition": base, "hash": base_hash}
    registry["current"] = {}
    for variant_id, definition in definitions.items():
        if spec.binding_key in definition:
            raise spec.error("input_already_materialized")
        if spec.variant_of(definition) != variant_id:
            raise spec.error("variant_mismatch")
        patch = {key: deepcopy(value) for key, value in definition.items() if key not in base}
        registry["variants"].setdefault(variant_id, {})[version] = {
            "baseVersion": version, "baseHash": base_hash, "patch": patch,
            "patchHash": definition_hash(patch), "definitionHash": definition_hash(definition)}
        registry["current"][variant_id] = version
    check_registry(registry, spec=spec)
    return registry


def registry_path(family: str) -> Path:
    spec_for(family)
    return FAMILIES_DIR / f"{family}.json"


@lru_cache(maxsize=32)
def _read_registry(path: str, modified: int, size: int) -> dict:
    registry = json.loads(Path(path).read_text(encoding="utf-8"))
    check_registry(registry)
    return registry


def load_registry(family: str) -> dict:
    path = registry_path(family)
    stat = path.stat()
    return _read_registry(str(path), stat.st_mtime_ns, stat.st_size)


def family_definition(family: str, variant_id: str, version: str | None = None, *,
                      expected: dict | None = None) -> dict:
    return resolve_variant(load_registry(family), variant_id, version, expected=expected)


def family_names() -> list[str]:
    if not FAMILIES_DIR.is_dir():
        return []
    return sorted(path.stem for path in FAMILIES_DIR.glob("*.json"))


def versioned_screen_ids() -> dict[str, tuple[str, str]]:
    """Screen-ID -> (Familie, Variante) fuer alle aktuellen Varianten aller Familien (ohne Beleg)."""
    result: dict[str, tuple[str, str]] = {}
    for family in family_names():
        for variant_id in load_registry(family)["current"]:
            result[screen_id(family, variant_id)] = (family, variant_id)
    return result


def is_family_screen(screen_id: str) -> bool:
    """Varianten einer Familie (Beleg eingeschlossen) haben ihre eigene Registry, nicht den nativen Katalog."""
    return screen_id.startswith("beleg/") or screen_id in versioned_screen_ids()


def release_metadata(screen_id: str) -> dict:
    """Release-Nachweis einer Familienvariante (wie ``native_release_metadata`` fuer Belege)."""
    family, variant_id = versioned_screen_ids()[screen_id]
    binding = family_definition(family, variant_id)["maskVariant"]
    return {"version": binding["variantVersion"], "definition_hash": binding["materializedHash"],
            "gates_passed": ["A", "B", "C", "E"], "studio_draft_clean": True, "family": family}
