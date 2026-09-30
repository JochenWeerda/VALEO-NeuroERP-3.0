#!/usr/bin/env python3
"""Abfragebezogene CI-Ratsche fuer .all(); Parameter begrenzen keine Abfrage.

Neue/gewachsene Funde schlagen fehl; nach Abbau muss die Baseline sinken.
Run: python scripts/check_pagination.py [--update-baseline]
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"
ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path("config/pagination_baseline.json")

# Files where unbounded .all() is intentional (reference data, small sets)
EXEMPT_FILES: set[str] = {
    "e2e_chain.py",           # orchestration, not user-facing list
    "command_catalog.py",     # static command catalog
    "agent_tool_contracts.py",  # agent tool list — small bounded set
    "analytics.py",           # analytics aggregations, not entity lists
    # Vollstaendiges Belegaggregat: Teilseiten wuerden Summen/offene Mengen
    # fachlich falsch und die Zwei-Abfragen-je-Beleg-Garantie aufbrechen.
    "document_allocations.py",
}


class QueryScanner(ast.NodeVisitor):
    """Konservative lokale Datenflussanalyse; unbekannte Helfer bleiben Funde.

    .limit/.fetch begrenzen; .offset und HTTP-Parameter allein nicht.
    Funktionen haben getrennte Umgebungen; Grenzen muessen auf allen Zweigen gelten.
    Dynamische Limits brauchen zusaetzlich einen fachlichen HTTP-Vertragstest.
    """

    def __init__(self) -> None:
        self.env: dict[str, bool] = {}
        self.scope = "<module>"
        self.findings: list[tuple[str, int]] = []

    def bounded(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return self.env.get(node.id, False)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in {"limit", "fetch"}:
                value = node.args[0] if node.args else next(
                    (kw.value for kw in node.keywords if kw.arg in {"limit", "count"}), None
                )
                return value is not None and not (
                    isinstance(value, ast.Constant) and value.value is None
                )
            if method in {
                "offset", "order_by", "filter", "filter_by", "where", "options",
                "scalars", "mappings", "unique", "execution_options", "distinct",
                "join", "outerjoin", "group_by", "having", "execute",
            }:
                return self.bounded(node.func.value) or (
                    method == "execute" and bool(node.args) and self.bounded(node.args[0])
                )
        return False

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "all":
            if not self.bounded(node.func.value):
                self.findings.append((self.scope, node.lineno))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        value = self.bounded(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.env[target.id] = value
            else:
                for name in ast.walk(target):
                    if isinstance(name, ast.Name):
                        self.env[name.id] = False
                self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.env[node.target.id] = node.value is not None and self.bounded(node.value)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.env[node.target.id] = self.bounded(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.env[node.target.id] = False

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # Closure kann nach einer spaeteren Neuzuweisung ausgefuehrt werden.
        env = self.env
        self.env = {}
        self.visit(node.body)
        self.env = env

    def visit_FunctionDef(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        env, scope = self.env, self.scope
        self.env = {}
        self.scope = node.name if scope == "<module>" else f"{scope}.{node.name}"
        for statement in node.body:
            self.visit(statement)
        self.env, self.scope = env, scope

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        env, scope = self.env, self.scope
        self.env = {}
        self.scope = node.name if scope == "<module>" else f"{scope}.{node.name}"
        for statement in node.body:
            self.visit(statement)
        self.env, self.scope = env, scope

    def _branches(self, bodies: list[list[ast.stmt]]) -> None:
        before = self.env.copy()
        results = []
        for body in bodies:
            self.env = before.copy()
            for statement in body:
                self.visit(statement)
            results.append(self.env.copy())
        names = set().union(*(result.keys() for result in results))
        self.env = {name: all(result.get(name, False) for result in results) for name in names}

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        self._branches([node.body, node.orelse])

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        self._branches([case.body for case in node.cases] + [[]])

    def visit_For(self, node: ast.For | ast.AsyncFor) -> None:
        self.visit(node.iter)
        before = self.env.copy()
        if isinstance(node.target, ast.Name):
            self.env[node.target.id] = False
        for statement in node.body:
            self.visit(statement)
        after = self.env.copy()
        self.env = {name: value and after.get(name, False) for name, value in before.items()}
        for statement in node.orelse:
            self.visit(statement)

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        before = self.env.copy()
        for statement in node.body:
            self.visit(statement)
        after = self.env.copy()
        self.env = {name: value and after.get(name, False) for name, value in before.items()}
        for statement in node.orelse:
            self.visit(statement)

    def visit_Try(self, node: ast.Try) -> None:
        before = self.env.copy()
        for statement in node.body + node.orelse:
            self.visit(statement)
        success = self.env.copy()
        results = [success]
        for handler in node.handlers:
            # Der Fehler kann nach jeder Zuweisung im try auftreten.
            self.env = {name: False for name in before.keys() | success.keys()}
            for statement in handler.body:
                self.visit(statement)
            results.append(self.env.copy())
        names = set().union(*(result.keys() for result in results))
        self.env = {name: all(result.get(name, False) for result in results) for name in names}
        for statement in node.finalbody:
            self.visit(statement)

    visit_TryStar = visit_Try


def scan_source(content: str) -> list[tuple[str, int]]:
    scanner = QueryScanner()
    scanner.visit(ast.parse(content.lstrip("\ufeff")))
    return scanner.findings


def _has_unbounded_all(content: str) -> int:
    return len(scan_source(content))


def collect(root: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    folder = root / ENDPOINTS_DIR
    if not folder.is_dir():
        raise FileNotFoundError("Endpunktverzeichnis fehlt")
    for path in sorted(folder.glob("*.py")):
        if path.name in EXEMPT_FILES:
            continue
        for scope, _line in scan_source(path.read_text(encoding="utf-8")):
            counts[f"{path.relative_to(root).as_posix()}::{scope}"] += 1
    return dict(sorted(counts.items()))


def ratchet_errors(current: dict[str, int], baseline: dict[str, int]) -> list[str]:
    errors = []
    for key in sorted(current.keys() | baseline.keys()):
        actual, allowed = current.get(key, 0), baseline.get(key, 0)
        if actual > allowed:
            errors.append(f"NEU/GEWACHSEN: {key}: {allowed} -> {actual}")
        elif actual < allowed:
            errors.append(f"BASELINE SENKEN: {key}: {allowed} -> {actual}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--threshold", type=int, help="Veraltet: abfragebezogene Baseline gilt")
    args = parser.parse_args()

    try:
        current = collect(args.root)
        path = args.root / BASELINE
        if args.update_baseline:
            path.write_text(json.dumps({"counts": current}, indent=2) + "\n", encoding="utf-8")
            print(f"Pagination-Baseline: {sum(current.values())} Abfragen in {len(current)} Funktionen")
            return 0
        baseline = json.loads(path.read_text(encoding="utf-8"))["counts"]
        if not isinstance(baseline, dict) or not all(
            isinstance(key, str) and type(value) is int and value >= 0
            for key, value in baseline.items()
        ):
            raise ValueError("counts muss nichtnegative ganzzahlige Zaehler enthalten")
        errors = ratchet_errors(current, baseline)
    except (OSError, ValueError, KeyError, SyntaxError, TypeError) as exc:
        print(f"FAIL: Pagination-Inventur/Baseline ungueltig: {exc}", file=sys.stderr)
        return 1
    print(f"Pagination: {sum(current.values())} Abfragen in {len(current)} Funktionen")
    if args.threshold is not None:
        print("--threshold ist veraltet; die funktionsbezogene Baseline ist verbindlich.")
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
