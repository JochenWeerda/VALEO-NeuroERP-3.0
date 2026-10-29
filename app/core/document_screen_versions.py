"""Immutable, content-bound document-screen bases and variants (no business writes)."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import re

from app.core.studio_release import definition_hash

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config/document_screen_versions.json"
_VERSION = re.compile(r"[1-9][0-9]*\.[0-9]+\.[0-9]+\Z")


def resolve_variant(registry, variant_id, version=None, *, expected=None):
    """Resolve an exact version; an expected binding never follows a changed alias."""
    try:
        if type(registry["schemaVersion"]) is not int or registry["schemaVersion"] != 1 or registry["family"] != "beleg":
            raise ValueError("document_screen_registry_invalid")
        version = registry["current"][variant_id] if version is None else version
        record = registry["variants"][variant_id][version]
        base_version = record["baseVersion"]
        base = registry["bases"][base_version]
        if not _VERSION.fullmatch(version) or not _VERSION.fullmatch(base_version):
            raise ValueError("document_screen_version_invalid")
        if (definition_hash(base["definition"]) != base["hash"]
                or record["baseHash"] != base["hash"]
                or definition_hash(record["patch"]) != record["patchHash"]):
            raise ValueError("document_screen_content_changed")
        # Bases contain root properties shared identically by all variants.
        # A variant replaces whole root properties; no ambiguous array merging.
        definition = {**deepcopy(base["definition"]), **deepcopy(record["patch"])}
        stamp = definition_hash(definition)
        if stamp != record["definitionHash"]:
            raise ValueError("document_screen_materialization_changed")
        if definition.get("variant", {}).get("belegart") != variant_id:
            raise ValueError("document_screen_variant_mismatch")
        binding = {"family": "beleg", "baseVersion": base_version,
                   "baseHash": base["hash"], "variantId": variant_id,
                   "variantVersion": version, "variantHash": record["patchHash"],
                   "materializedHash": stamp}
        if expected is not None and expected != binding:
            raise ValueError("document_screen_binding_changed")
        definition["documentVariant"] = binding
        return definition
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("document_screen_version_unknown_or_invalid") from error


def check_registry(registry):
    """Check historical entries too, not just the current aliases."""
    try:
        for version, base in registry["bases"].items():
            if not _VERSION.fullmatch(version) or definition_hash(base["definition"]) != base["hash"]:
                raise ValueError("document_screen_base_changed")
        for variant_id, versions in registry["variants"].items():
            for version in versions:
                resolve_variant(registry, variant_id, version)
        for variant_id, version in registry["current"].items():
            resolve_variant(registry, variant_id, version)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("document_screen_registry_invalid") from error


@lru_cache(maxsize=2)
def _read_registry(path, modified, size):
    registry = json.loads(Path(path).read_text(encoding="utf-8"))
    check_registry(registry)
    return registry


def document_definition(variant_id, version=None, *, expected=None):
    stat = REGISTRY_PATH.stat()
    registry = _read_registry(str(REGISTRY_PATH), stat.st_mtime_ns, stat.st_size)
    return resolve_variant(registry, variant_id, version, expected=expected)


def extend_registry(definitions, version, previous=None):
    """Append a release. Existing base/variant records are never overwritten."""
    if not isinstance(version, str) or not _VERSION.fullmatch(version):
        raise ValueError("document_screen_version_invalid")
    if not definitions:
        raise ValueError("document_screen_variants_empty")
    registry = deepcopy(previous) if previous is not None else {
        "schemaVersion": 1, "family": "beleg", "bases": {}, "variants": {}, "current": {}}
    if previous is not None:
        check_registry(previous)
    if version in registry["bases"] or any(version in rows for rows in registry["variants"].values()):
        raise ValueError("document_screen_version_already_exists")
    if registry["bases"] and tuple(map(int, version.split("."))) <= max(tuple(map(int, key.split("."))) for key in registry["bases"]):
        raise ValueError("document_screen_version_must_advance")
    first = next(iter(definitions.values()))
    base = {key: deepcopy(value) for key, value in first.items()
            if all(key in item and item[key] == value for item in definitions.values())}
    base_hash = definition_hash(base)
    registry["bases"][version] = {"definition": base, "hash": base_hash}
    registry["current"] = {}
    for variant_id, definition in definitions.items():
        if "documentVariant" in definition:
            raise ValueError("document_screen_input_already_materialized")
        patch = {key: deepcopy(value) for key, value in definition.items() if key not in base}
        registry["variants"].setdefault(variant_id, {})[version] = {
            "baseVersion": version, "baseHash": base_hash, "patch": patch,
            "patchHash": definition_hash(patch), "definitionHash": definition_hash(definition)}
        registry["current"][variant_id] = version
    check_registry(registry)
    return registry
