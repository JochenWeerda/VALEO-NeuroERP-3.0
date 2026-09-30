#!/usr/bin/env python3
"""Pfadbezogene CI-Ratsche fuer Python-Endpunkte ueber 1.000 Zeilen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ENDPOINTS_DIR = Path("app/api/v1/endpoints")
BASELINE_PATH = Path("config/godfile_baseline.json")
LOC_LIMIT = 1000
WARN_LIMIT = 500


def _loc(path: Path) -> int:
    try:
        return path.read_text(encoding="utf-8").count("\n")
    except OSError:
        return 0


def collect_godfiles(root: Path) -> dict[str, int]:
    endpoints = root / ENDPOINTS_DIR
    result: dict[str, int] = {}
    for path in sorted(endpoints.glob("*.py")):
        lines = _loc(path)
        if lines > LOC_LIMIT:
            result[path.relative_to(root).as_posix()] = lines
    return result


def load_baseline(path: Path) -> dict[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    files = data.get("files")
    if not isinstance(files, dict) or not all(
        isinstance(name, str) and isinstance(lines, int) for name, lines in files.items()
    ):
        raise ValueError("Baseline braucht ein Objekt 'files' mit ganzzahligen Zeilenzahlen")
    return dict(sorted(files.items()))


def ratchet_errors(current: dict[str, int], baseline: dict[str, int]) -> list[str]:
    errors: list[str] = []
    for path in sorted(current.keys() - baseline.keys()):
        errors.append(f"NEU: {path} ({current[path]} Zeilen)")
    for path in sorted(baseline.keys() - current.keys()):
        errors.append(f"BASELINE SENKEN: {path} ist kein Godfile mehr")
    for path in sorted(current.keys() & baseline.keys()):
        actual, expected = current[path], baseline[path]
        if actual > expected:
            errors.append(f"GEWACHSEN: {path} {expected} -> {actual} Zeilen")
        elif actual < expected:
            errors.append(f"BASELINE SENKEN: {path} {expected} -> {actual} Zeilen")
    return errors


def write_baseline(path: Path, files: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "description": "Exakte, nur sinkende Baseline produktiver Python-Endpunkte ueber 1000 LOC.",
        "loc_limit": LOC_LIMIT,
        "files": dict(sorted(files.items())),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument(
        "--threshold",
        type=int,
        help="Veraltete Option; die pfadbezogene Baseline ist verbindlich.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    baseline_path = args.baseline or root / BASELINE_PATH
    current = collect_godfiles(root)
    if args.update_baseline:
        write_baseline(baseline_path, current)
        print(f"Godfile-Baseline aktualisiert: {len(current)} Dateien")
        return 0

    baseline = load_baseline(baseline_path)
    print(
        f"Files > {LOC_LIMIT} LOC (godfiles): {len(current)} "
        f"(threshold: {len(baseline)})"
    )
    for path, lines in sorted(current.items(), key=lambda item: -item[1]):
        print(f"  {Path(path).name:50s} {lines:5d}")

    if args.threshold is not None:
        print("Hinweis: --threshold ist veraltet; config/godfile_baseline.json gilt.")

    errors = ratchet_errors(current, baseline)
    if errors:
        print("\nFAIL: Godfile-Ratchet verletzt.", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    approaching = []
    for path in sorted((root / ENDPOINTS_DIR).glob("*.py")):
        lines = _loc(path)
        if WARN_LIMIT < lines <= LOC_LIMIT:
            approaching.append((path.name, lines))
    if approaching:
        print(f"\nFiles > {WARN_LIMIT} LOC (approaching limit): {len(approaching)}")
        for name, lines in sorted(approaching, key=lambda item: -item[1])[:5]:
            print(f"  {name:50s} {lines:5d}")

    print("\nOK — Godfile-Baseline ist exakt; neue oder verschobene Dateien fehlen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
