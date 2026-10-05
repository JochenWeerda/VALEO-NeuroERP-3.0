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


def coverage_source(root: Path, filename: str) -> Path:
    """Coverage keys are canonical Python paths relative to app, never escapes."""
    if (not isinstance(filename, str) or not filename.endswith('.py')
            or any(char in filename for char in '\\:\0\n\r\t')
            or any(part in {'', '.', '..'} for part in filename.split('/'))):
        raise ValueError(f'Ungueltiger Coverage-Pfad: {filename!r}')
    source = root / 'app' / filename
    if not source.resolve().is_relative_to((root / 'app').resolve()):
        raise ValueError(f'Coverage-Pfad ausserhalb app: {filename!r}')
    return source


def coverage_changes(root: Path, before: dict, after: dict, base: str,
                     tracked_before: set[str]) -> list[str]:
    old, new = flatten(before), flatten(after)
    paths = {}
    errors = []
    for filename in sorted(old.keys() | new.keys()):
        try:
            paths[filename] = coverage_source(root, filename)
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        return errors
    removed = old.keys() - new.keys()
    if not removed:
        return compare(old, new, 'up')
    target = git(root, 'rev-parse', '--verify', 'HEAD^{commit}').strip()
    tracked_after = set(filter(None, git(root, 'ls-tree', '-r', '--name-only', '-z', target).split('\0')))
    fields = git(root, 'diff', '--name-status', '-z', '--find-renames', base, target).split('\0')
    renamed, added = {}, set()
    index = 0
    while index < len(fields) and fields[index]:
        status, filename = fields[index:index + 2]
        index += 2
        if status.startswith(('R', 'C')):
            successor = fields[index]
            index += 1
            if status.startswith('R'):
                renamed[filename] = successor
            added.add(successor)
        elif status == 'A':
            added.add(filename)
    retired = set()
    for filename in sorted(removed):
        tracked_name = f'app/{filename}'
        source = paths[filename]
        # A worktree deletion alone, an untracked replacement, or a broken
        # symlink is not proof that the target commit retired the module.
        if tracked_name in tracked_after or source.exists() or source.is_symlink():
            continue
        if tracked_name in renamed:
            target_name = renamed[tracked_name]
            if not target_name.startswith('app/'):
                errors.append(f'{filename}: Coverage-Nachfolger ausserhalb app verlangt eigenen Coverage-Vertrag: {target_name}')
                continue
            successor = target_name.removeprefix('app/')
            if new.get(successor, -1) < old[filename]:
                errors.append(f'{filename}: Coverage-Nachfolger {successor} muss mindestens {old[filename]} behalten')
                continue
        elif tracked_name in tracked_before:
            # Rewritten moves can fall below Git's rename similarity. Do not
            # assume newly added app modules are unrelated to retired code.
            unprotected = [path for path in sorted(added) if path.endswith('.py') and not path.startswith('tests/')
                           and (not path.startswith('app/') or new.get(path.removeprefix('app/'), -1) < old[filename])]
            if unprotected:
                errors.append(f'{filename}: Loeschung mit ungeschuetzten neuen Modulen: {", ".join(unprotected)}')
                continue
        retired.add(filename)
    errors.extend(compare({key: value for key, value in old.items() if key not in retired}, new, 'up'))
    return errors


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
    tracked = set(filter(None, git(root, "ls-tree", "-r", "--name-only", "-z", commit).split('\0')))
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
            changes = (coverage_changes(root, before[field], after[field], commit, tracked)
                       if path == 'config/coverage_ratchet_baseline.json'
                       else compare(before[field], after[field], direction))
            errors.extend(f"{path}: {error}" for error in changes)
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
