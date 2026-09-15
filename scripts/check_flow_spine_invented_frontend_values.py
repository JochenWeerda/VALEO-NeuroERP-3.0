#!/usr/bin/env python3
"""FSX-003 Frontend-Gate: erfundene Anzeigewerte im Workflow-JSX.

Das Muster, das FSX-002 entfernt hat, war nie im Backend sichtbar:

    {node.kpis[0]?.value ?? '92%'}
    style={{ width: '92%' }}

Ein Registry-Test faengt das nicht. Dieses Gate sucht genau diese Klasse —
Nullish-Fallback auf eine Prozent-/Zahlenliteral und fest verdrahtete
Balkenbreite — und sonst nichts.

Absichtich eng: unter ``components/workflow`` und ``pages/workflow`` liegen
heute 0 Treffer. Ein repo-weites Verbot von ``??`` waere eine Regel mit
Dutzenden bis Hunderten Fundstellen (leere Listen, Default-Knoten, 0-Zaehler)
und wuerde stummgeschaltet. Deshalb kein ESLint-``no-magic-numbers`` und kein
pauschales ``??``.

Erlaubt bleiben:
- strukturelle Fallbacks (``?? []``, ``?? nodes[0]``, ``?? ''``)
- Layoutbreiten ``0%`` und ``100%``
- eine Zeile mit ``fsx-invented-ok:`` plus Begruendung

Exit 0 = sauber, Exit 1 = Treffer.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SCOPE_DIRS = (
    Path("packages/frontend-web/src/components/workflow"),
    Path("packages/frontend-web/src/pages/workflow"),
)

SOURCE_SUFFIXES = {".ts", ".tsx"}
SKIP_NAME_MARKERS = (".test.", ".spec.", ".stories.")
ALLOW_COMMENT = "fsx-invented-ok:"
ALLOWED_WIDTH_PERCENTS = {0.0, 100.0}

# ``?? '92%'`` / ``?? "12.5%"`` — Anzeigewert ohne Quelle.
NULLISH_PERCENT = re.compile(r"\?\?\s*['\"](\d+(?:\.\d+)?)%['\"]")
# ``?? '92'`` — dieselbe Klasse ohne Prozentzeichen.
NULLISH_NUMERIC_STRING = re.compile(r"\?\?\s*['\"](\d+(?:\.\d+)?)['\"]")
# ``width: '92%'`` in Inline-Styles. 0 % und 100 % sind Layout, kein KPI.
STYLE_WIDTH_PERCENT = re.compile(r"\bwidth\s*:\s*['\"](\d+(?:\.\d+)?)%['\"]")
# Tailwind-Arbitrary ``w-[92%]``.
TAILWIND_WIDTH_PERCENT = re.compile(r"\bw-\[(\d+(?:\.\d+)?)%\]")


class Finding:
    __slots__ = ("path", "line_no", "kind", "excerpt")

    def __init__(self, path: Path, line_no: int, kind: str, excerpt: str) -> None:
        self.path = path
        self.line_no = line_no
        self.kind = kind
        self.excerpt = excerpt.strip()


def _is_source(path: Path) -> bool:
    if path.suffix not in SOURCE_SUFFIXES:
        return False
    if "__tests__" in path.parts:
        return False
    name = path.name
    return not any(marker in name for marker in SKIP_NAME_MARKERS)


def iter_scoped_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in SCOPE_DIRS:
        directory = root / relative
        if not directory.is_dir():
            continue
        files.extend(path for path in directory.rglob("*") if path.is_file() and _is_source(path))
    return sorted(files)


def _percent_value(raw: str) -> float:
    return float(raw)


def scan_line(path: Path, line_no: int, line: str) -> list[Finding]:
    if ALLOW_COMMENT in line:
        return []
    findings: list[Finding] = []
    if NULLISH_PERCENT.search(line):
        findings.append(Finding(path, line_no, "nullish-percent", line))
    if NULLISH_NUMERIC_STRING.search(line):
        findings.append(Finding(path, line_no, "nullish-numeric-string", line))
    for match in STYLE_WIDTH_PERCENT.finditer(line):
        if _percent_value(match.group(1)) not in ALLOWED_WIDTH_PERCENTS:
            findings.append(Finding(path, line_no, "style-width-percent", line))
    for match in TAILWIND_WIDTH_PERCENT.finditer(line):
        if _percent_value(match.group(1)) not in ALLOWED_WIDTH_PERCENTS:
            findings.append(Finding(path, line_no, "tailwind-width-percent", line))
    return findings


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        findings.extend(scan_line(path, line_no, line))
    return findings


def scan_paths(paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        findings.extend(scan_text(path, text))
    return findings


def format_report(findings: list[Finding], root: Path) -> str:
    lines = [
        "FSX-003 Frontend-Gate: erfundene Anzeigewerte unter components/workflow "
        "und pages/workflow.",
        "",
    ]
    if not findings:
        lines.append("0 Treffer. Das FSX-002-Muster (?? '92%' / width: '92%') ist nicht zurueck.")
        return "\n".join(lines)

    lines.append(f"{len(findings)} Treffer — ein Anzeigewert ohne Quelle:")
    for item in findings:
        rel = item.path.resolve().relative_to(root.resolve()).as_posix()
        lines.append(f"  {rel}:{item.line_no}  [{item.kind}]  {item.excerpt}")
    lines.extend(
        [
            "",
            "Entweder an eine benannte Quelle binden oder als fehlend zeigen.",
            "Ausnahme nur mit Kommentar fsx-invented-ok: <Grund> in derselben Zeile.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository-Wurzel (Tests setzen ein Temporaerverzeichnis).",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    files = iter_scoped_files(root)
    findings = scan_paths(files)
    print(format_report(findings, root))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
