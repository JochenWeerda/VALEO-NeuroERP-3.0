#!/usr/bin/env python3
"""Ratschen gegen den Ausgangscommit pruefen, nicht gegen sich selbst."""
from __future__ import annotations

import argparse
import ast
import json
import math
import io
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
POLICIES = {
    "config/godfile_baseline.json": ("files", "down"),
    "config/business_time_usage_baseline.json": ("counts", "down"),
    "config/pagination_baseline.json": ("counts", "down"),
    "config/coverage_ratchet_baseline.json": ("thresholds", "up"),
}


def flatten(data: dict, prefix: str = "") -> dict[str, float]:
    if not isinstance(data, dict):
        raise ValueError("Baseline muss ein Objekt sein")
    result = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError("Baseline-Schluessel muss Text sein")
        name = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, name))
        elif type(value) in {int, float} and math.isfinite(value) and value >= 0:
            result[name] = value
        else:
            raise ValueError(f"Ungueltiger Baseline-Wert: {name}")
    return result


def compare(before: dict, after: dict, direction: str) -> list[str]:
    old, new = flatten(before), flatten(after)
    errors = []
    if direction == "down":
        for key, value in new.items():
            if value > old.get(key, 0):
                errors.append(f"{key}: {old.get(key, 0)} -> {value} (Anhebung verboten)")
    elif direction == "up":
        for key, value in old.items():
            if key not in new or new[key] < value:
                errors.append(f"{key}: {value} -> {new.get(key, 'entfernt')} (Absenkung verboten)")
    else:
        raise ValueError("Unbekannte Richtung")
    return errors


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], encoding="utf-8", stderr=subprocess.PIPE
    )


def exemptions(source: str) -> set[str]:
    for node in ast.parse(source.lstrip("\ufeff")).body:
        target = node.target if isinstance(node, ast.AnnAssign) else (
            node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None
        )
        if isinstance(target, ast.Name) and target.id == "EXEMPT_FILES":
            values = ast.literal_eval(node.value)
            if not isinstance(values, set) or not all(isinstance(value, str) for value in values):
                raise ValueError("EXEMPT_FILES muss eine explizite Menge sein")
            return values
    raise ValueError("EXEMPT_FILES fehlt")


def check(root: Path, base: str) -> list[str]:
    # --verify beendet Optionen; danach nur die aufgeloeste Commit-ID verwenden.
    commit = git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}").strip()
    tracked = set(git(root, "ls-tree", "-r", "--name-only", commit).splitlines())
    errors = []
    scanner_path = "scripts/check_pagination.py"
    old_exempt = exemptions(git(root, "show", f"{commit}:{scanner_path}"))
    new_exempt = exemptions((root / scanner_path).read_text(encoding="utf-8"))
    for name in sorted(new_exempt - old_exempt):
        errors.append(f"Neue dateiweite Pagination-Ausnahme verboten: {name}")
    for path, (field, direction) in POLICIES.items():
        current = root / path
        if not current.is_file():
            errors.append(f"Baseline fehlt: {path}")
            continue
        after = json.loads(current.read_text(encoding="utf-8"))
        if path in tracked:
            before = json.loads(git(root, "show", f"{commit}:{path}"))
            if path.endswith("godfile_baseline.json") and after.get("loc_limit") != before.get("loc_limit"):
                errors.append("Godfile-LOC-Grenze darf nicht geaendert werden")
            errors.extend(f"{path}: {error}" for error in compare(before[field], after[field], direction))
        elif path == "config/pagination_baseline.json":
            # Neue Messmethode: Erstbaseline darf nur Altbestand des Ausgangscommits enthalten.
            from collections import Counter
            from scripts.check_pagination import scan_source

            counts: Counter[str] = Counter()
            # Ein Git-Aufruf statt eines Prozesses je Endpunkt; keine Extraktion.
            archive = subprocess.check_output(
                ["git", "-C", str(root), "archive", commit, "app/api/v1/endpoints"]
            )
            with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
                for member in tree:
                    name = member.name
                    if not member.isfile() or not name.endswith(".py"):
                        continue
                    if "/" in name.removeprefix("app/api/v1/endpoints/") or Path(name).name in new_exempt:
                        continue
                    source = tree.extractfile(member).read().decode("utf-8")
                    for scope, _line in scan_source(source):
                        counts[f"{name}::{scope}"] += 1
            errors.extend(f"{path}: {error}" for error in compare(dict(counts), after[field], "down"))
        else:
            errors.append(f"Ausgangsbaseline fehlt: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base", default="HEAD", help="PR-Basis bzw. vorheriger Push-Commit")
    args = parser.parse_args()
    try:
        errors = check(args.root, args.base)
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError, SyntaxError) as exc:
        print(f"FAIL: Baseline-Integritaet nicht nachweisbar ({type(exc).__name__})", file=sys.stderr)
        return 1
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Baseline-Integritaet: {'FAIL' if errors else 'OK'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main())
