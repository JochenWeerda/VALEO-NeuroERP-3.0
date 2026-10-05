#!/usr/bin/env python3
"""Ratchet fuer direkte Tagesableitungen im produktiven Python-Code.

Fachliche Tageswerte muessen ueber ``app.core.business_time`` entstehen. Dieses
Gate inventarisiert den vorhandenen Altbestand unter ``app/`` und verhindert,
dass neue direkte Abhaengigkeiten von Host- oder UTC-Kalendertagen hinzukommen.

Erkannt werden import- und aliasfest:

* ``date.today()``
* ``datetime.now(...).date()``
* ``datetime.utcnow().date()``

Die Baseline ist pfad- und musterbezogen. Damit blockiert das Gate auch das
Verschieben einer Altstelle in eine andere Datei. Sinkt der Bestand, muss die
Baseline im selben Commit mit ``--update-baseline`` abgesenkt werden; so kann
eine entfernte Stelle nicht spaeter unbemerkt zurueckkehren.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"
BASELINE_PATH = PROJECT_ROOT / "config" / "business_time_usage_baseline.json"
EXCLUDED_PATHS = {"app/core/business_time.py"}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    kind: str
    source: str


class BusinessTimeVisitor(ast.NodeVisitor):
    """Findet direkte Kalenderquellen und verfolgt datetime-Importaliasse."""

    def __init__(self, path: str, lines: list[str]) -> None:
        self.path = path
        self.lines = lines
        self.module_aliases: set[str] = set()
        self.date_aliases: set[str] = set()
        self.datetime_aliases: set[str] = set()
        self.findings: list[Finding] = []

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            if alias.name == "datetime":
                self.module_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.module == "datetime":
            for alias in node.names:
                local_name = alias.asname or alias.name
                if alias.name == "date":
                    self.date_aliases.add(local_name)
                elif alias.name == "datetime":
                    self.datetime_aliases.add(local_name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        kind = self._kind(node)
        if kind is not None:
            source = self.lines[node.lineno - 1].strip()[:160]
            self.findings.append(Finding(self.path, node.lineno, kind, source))
        self.generic_visit(node)

    def _kind(self, node: ast.Call) -> str | None:
        func = node.func
        if self._is_date_today(func):
            return "date.today"
        if not isinstance(func, ast.Attribute) or func.attr != "date":
            return None
        if not isinstance(func.value, ast.Call):
            return None
        clock = func.value.func
        if self._is_datetime_method(clock, "now"):
            return "datetime.now.date"
        if self._is_datetime_method(clock, "utcnow"):
            return "datetime.utcnow.date"
        if self._is_datetime_method(clock, "today"):
            return "datetime.today.date"
        return None

    def _is_date_today(self, func: ast.AST) -> bool:
        if not isinstance(func, ast.Attribute) or func.attr != "today":
            return False
        owner = func.value
        if isinstance(owner, ast.Name):
            return owner.id in self.date_aliases
        return (
            isinstance(owner, ast.Attribute)
            and owner.attr == "date"
            and isinstance(owner.value, ast.Name)
            and owner.value.id in self.module_aliases
        )

    def _is_datetime_method(self, func: ast.AST, method: str) -> bool:
        if not isinstance(func, ast.Attribute) or func.attr != method:
            return False
        owner = func.value
        if isinstance(owner, ast.Name):
            return owner.id in self.datetime_aliases
        return (
            isinstance(owner, ast.Attribute)
            and owner.attr == "datetime"
            and isinstance(owner.value, ast.Name)
            and owner.value.id in self.module_aliases
        )


def scan_file(path: Path, *, root: Path = PROJECT_ROOT) -> list[Finding]:
    relative = path.relative_to(root).as_posix()
    if relative in EXCLUDED_PATHS:
        return []
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=relative)
    visitor = BusinessTimeVisitor(relative, source.splitlines())
    visitor.visit(tree)
    return sorted(visitor.findings)


def scan(paths: Iterable[Path], *, root: Path = PROJECT_ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(paths):
        findings.extend(scan_file(path, root=root))
    return sorted(findings)


def counts_for(findings: Iterable[Finding]) -> dict[str, dict[str, int]]:
    counts: Counter[tuple[str, str]] = Counter((item.path, item.kind) for item in findings)
    result: dict[str, dict[str, int]] = {}
    for (path, kind), count in sorted(counts.items()):
        result.setdefault(path, {})[kind] = count
    return result


def load_baseline(path: Path = BASELINE_PATH) -> dict[str, dict[str, int]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_counts = data.get("counts", {})
    return {
        str(file_path): {str(kind): int(count) for kind, count in kinds.items()}
        for file_path, kinds in raw_counts.items()
    }


def compare_counts(
    current: Mapping[str, Mapping[str, int]],
    baseline: Mapping[str, Mapping[str, int]],
) -> tuple[dict[str, int], dict[str, int]]:
    current_flat = {
        f"{path}|{kind}": count
        for path, kinds in current.items()
        for kind, count in kinds.items()
    }
    baseline_flat = {
        f"{path}|{kind}": count
        for path, kinds in baseline.items()
        for kind, count in kinds.items()
    }
    keys = set(current_flat) | set(baseline_flat)
    increased = {
        key: current_flat.get(key, 0) - baseline_flat.get(key, 0)
        for key in sorted(keys)
        if current_flat.get(key, 0) > baseline_flat.get(key, 0)
    }
    reduced = {
        key: baseline_flat.get(key, 0) - current_flat.get(key, 0)
        for key in sorted(keys)
        if current_flat.get(key, 0) < baseline_flat.get(key, 0)
    }
    return increased, reduced


def write_baseline(
    counts: Mapping[str, Mapping[str, int]], path: Path = BASELINE_PATH
) -> None:
    payload = {
        "_hinweis": (
            "BUSINESS-TIME-RATCHET-20260930: Direkte Kalenderquellen unter app/. "
            "Die Zaehler duerfen nur sinken. Nach bewusster Bereinigung mit "
            "python scripts/check_business_time_usage.py --update-baseline absenken."
        ),
        "counts": counts,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check(*, update_baseline: bool = False, list_findings: bool = False) -> int:
    try:
        findings = scan(APP_ROOT.rglob("*.py"))
    except (OSError, SyntaxError, UnicodeError) as exc:
        print(f"[FAIL] Business-Time-Inventur konnte nicht gelesen werden: {exc}")
        return 1

    current = counts_for(findings)
    if update_baseline:
        write_baseline(current)
        print(f"[OK] Business-Time-Baseline geschrieben: {len(findings)} Stellen")
        return 0

    try:
        baseline = load_baseline()
    except (OSError, ValueError, TypeError) as exc:
        print(f"[FAIL] Business-Time-Baseline ist nicht lesbar: {exc}")
        return 1

    increased, reduced = compare_counts(current, baseline)
    if list_findings:
        for item in findings:
            print(f"{item.path}:{item.line}: {item.kind}: {item.source}")

    if increased:
        print("[FAIL] Neue oder verschobene direkte Kalenderquellen:")
        for key, delta in increased.items():
            print(f"  +{delta} {key}")
        print("Fachliche Tage ueber business_today()/business_date_at() ableiten.")
        return 1

    if reduced:
        print("[FAIL] Direkte Kalenderquellen wurden abgebaut, aber die Baseline ist veraltet:")
        for key, delta in reduced.items():
            print(f"  -{delta} {key}")
        print("Baseline jetzt absenken: python scripts/check_business_time_usage.py --update-baseline")
        return 1

    print(
        f"[OK] Business-Time-Ratchet unveraendert: {len(findings)} Stellen "
        f"in {len(current)} Dateien."
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Baseline nach bewusster Bereinigung auf den kleineren Bestand setzen",
    )
    parser.add_argument("--list", action="store_true", help="Alle Fundstellen ausgeben")
    args = parser.parse_args()
    sys.exit(check(update_baseline=args.update_baseline, list_findings=args.list))
