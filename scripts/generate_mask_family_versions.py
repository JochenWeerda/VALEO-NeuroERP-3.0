"""Maskenfamilien versionieren oder pruefen (config/mask_families/<familie>.json).

    python scripts/generate_mask_family_versions.py --check
    python scripts/generate_mask_family_versions.py --family kontrakt --release-version 1.0.0

Ein Release haengt Basis und Varianten-Patches an; bestehende Fassungen bleiben unveraendert (wie die Belegfamilie,
``scripts/generate_document_screen_versions.py``). ``--check`` prueft, dass jede Familie mit Builder ihre Builder
unveraendert materialisiert und keine Familie ohne Builder liegt.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.mask_family_versions import (  # noqa: E402
    FAMILIES_DIR,
    check_registry,
    extend_registry,
    family_names,
    registry_path,
    resolve_variant,
    spec_for,
)


def family_builders() -> dict:
    """Familie -> Funktion, die alle Varianten-Definitionen baut (eine Quelle je Familienmodul)."""
    from app.core.screen_definitions_family_beleg_liste import FAMILIEN_BUILDER as BELEG_LISTE
    from app.core.screen_definitions_family_bestellvorschlag import FAMILIEN_BUILDER as BESTELLVORSCHLAG
    from app.core.screen_definitions_family_kontrakt import FAMILIEN_BUILDER as KONTRAKT

    return {**KONTRAKT, **BELEG_LISTE, **BESTELLVORSCHLAG}


def current_matches(registry: dict, definitions: dict) -> bool:
    check_registry(registry)
    if set(registry["current"]) != set(definitions):
        return False
    for key, expected in definitions.items():
        actual = resolve_variant(registry, key)
        actual.pop("maskVariant")
        if actual != expected:
            return False
    return True


def write_release(path: Path, family: str, definitions: dict, version: str) -> dict:
    lock = path.with_suffix(".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError("mask_family_release_busy") from error
    pending = None
    try:
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        result = extend_registry(definitions, version, previous, spec=spec_for(family))
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent,
                                         prefix=f"{family}-", suffix=".tmp", delete=False) as target:
            pending = Path(target.name)
            json.dump(result, target, ensure_ascii=False, sort_keys=True, indent=2)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(pending, path)
        pending = None
        return result
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
        os.close(handle)
        lock.unlink()


def check() -> list[str]:
    fehler = []
    builders = family_builders()
    for family in sorted(set(builders) | set(family_names())):
        path = registry_path(family)
        if family not in builders:
            fehler.append(f"{family}: Registry ohne Builder ({path.relative_to(ROOT)})")
            continue
        if not path.is_file():
            fehler.append(f"{family}: kein Release (python scripts/generate_mask_family_versions.py "
                          f"--family {family} --release-version 1.0.0)")
            continue
        registry = json.loads(path.read_text(encoding="utf-8"))
        if not current_matches(registry, builders[family]()):
            fehler.append(f"{family}: Builder weicht vom aktuellen Release ab; neues Release noetig")
    return fehler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--family")
    parser.add_argument("--release-version")
    args = parser.parse_args()
    if args.check:
        fehler = check()
        for zeile in fehler:
            print(zeile)
        print("OK" if not fehler else f"{len(fehler)} Abweichung(en)")
        return 1 if fehler else 0
    if not (args.family and args.release_version):
        parser.error("--family und --release-version (oder --check)")
    builders = family_builders()
    if args.family not in builders:
        parser.error(f"unbekannte Familie {args.family!r}; bekannt: {sorted(builders)}")
    result = write_release(registry_path(args.family), args.family, builders[args.family](), args.release_version)
    print(f"{args.family} {args.release_version}: {sorted(result['current'])} -> {FAMILIES_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
