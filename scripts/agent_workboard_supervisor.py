from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import yaml as _yaml  # type: ignore
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


DEFAULT_WORKBOARD = Path("docs/agent-ops/active-workboard.md")
DEFAULT_SLICES_DIR = Path("docs/agent-ops/slices")
SLICE_HEADING_RE = re.compile(r"^##\s+([A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+)\s*$")
FIELD_RE = re.compile(r"^\*\*(?P<name>[^:*]+):\*\*\s*(?P<value>.*)$")
CHECK_RE = re.compile(r"`([^`\n]+)`")

DONE_MARKERS = ("abgeschlossen", "erledigt", "implementiert")
IN_PROGRESS_MARKERS = ("in arbeit",)
RESERVED_MARKERS = ("reserviert",)
OPEN_MARKERS = ("offen",)

REQUIRED_FIELDS = ("status", "owner", "file_ownership")


@dataclass(frozen=True)
class WorkboardSlice:
    slice_id: str
    heading: str
    status: str
    status_class: str
    owner: str | None
    goal: str | None
    file_ownership: str | None
    acceptance_criteria: str | None
    checks: list[str]
    risks: str | None
    start_line: int
    end_line: int


@dataclass(frozen=True)
class SliceFile:
    """Represents a YAML slice file from docs/agent-ops/slices/."""
    slice_id: str
    status: str
    owner: str | None
    goal: str | None
    file_ownership: list[str]
    acceptance_criteria: str | None
    checks: list[str]
    risks: str | None
    source_path: Path


@dataclass
class ValidationError:
    slice_id: str
    field: str
    message: str


def _status_class(status: str) -> str:
    value = status.strip().lower()
    if any(marker in value for marker in DONE_MARKERS):
        return "done"
    if any(marker in value for marker in RESERVED_MARKERS):
        return "reserved"
    if any(marker in value for marker in IN_PROGRESS_MARKERS):
        return "in_progress"
    if value in OPEN_MARKERS:
        return "open"
    return "unknown"


def _extract_fields(block_lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    for raw in block_lines:
        line = raw.rstrip()
        match = FIELD_RE.match(line)
        if match:
            current = match.group("name").strip().lower()
            fields[current] = match.group("value").strip()
            continue
        if current and line and not line.startswith("## "):
            fields[current] = f"{fields[current]}\n{line}".strip()
    return fields


def _checks_from_text(value: str | None) -> list[str]:
    if not value:
        return []
    return [match.strip() for match in CHECK_RE.findall(value) if match.strip()]


def parse_workboard(text: str) -> list[WorkboardSlice]:
    lines = text.splitlines()
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = SLICE_HEADING_RE.match(line.strip())
        if match:
            headings.append((index, match.group(1)))

    slices: list[WorkboardSlice] = []
    for pos, (start, slice_id) in enumerate(headings):
        end = headings[pos + 1][0] if pos + 1 < len(headings) else len(lines)
        block = lines[start + 1 : end]
        fields = _extract_fields(block)
        status = fields.get("stand", "unknown")
        checks = _checks_from_text(fields.get("checks"))
        slices.append(
            WorkboardSlice(
                slice_id=slice_id,
                heading=slice_id,
                status=status,
                status_class=_status_class(status),
                owner=fields.get("owner") or fields.get("von"),
                goal=fields.get("ziel des slices"),
                file_ownership=fields.get("dateibesitz"),
                acceptance_criteria=fields.get("abnahmekriterien"),
                checks=checks,
                risks=fields.get("offene risiken"),
                start_line=start + 1,
                end_line=end,
            )
        )
    return slices


def load_slices(path: Path) -> list[WorkboardSlice]:
    return parse_workboard(path.read_text(encoding="utf-8"))


def load_slice_files(slices_dir: Path) -> list[SliceFile]:
    """Load all YAML slice files from slices_dir. Requires PyYAML."""
    if not _YAML_AVAILABLE:
        print("Warning: PyYAML not installed; YAML slice files not loaded.", file=sys.stderr)
        return []
    if not slices_dir.exists():
        return []
    result: list[SliceFile] = []
    for yaml_path in sorted(slices_dir.glob("*.yaml")):
        data = _yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        file_ownership = data.get("file_ownership") or []
        if isinstance(file_ownership, str):
            file_ownership = [file_ownership]
        checks_raw = data.get("checks") or []
        result.append(SliceFile(
            slice_id=str(data.get("id", yaml_path.stem)),
            status=str(data.get("status", "unknown")),
            owner=data.get("owner") or None,
            goal=data.get("goal") or None,
            file_ownership=list(file_ownership),
            acceptance_criteria=data.get("acceptance_criteria") or None,
            checks=list(checks_raw),
            risks=data.get("risks") or None,
            source_path=yaml_path,
        ))
    return result


def validate_workboard_slices(
    slices: list[WorkboardSlice],
    slice_files: list[SliceFile],
    strict_ids: set[str] | None = None,
) -> list[ValidationError]:
    """
    Validate slices against REQUIRED_FIELDS.

    If strict_ids is given, only those slice_ids are checked from the markdown.
    YAML slice files are always fully validated.
    """
    errors: list[ValidationError] = []
    yaml_ids = {sf.slice_id for sf in slice_files}

    # Validate markdown slices that have a corresponding YAML file (or are in strict_ids)
    for sl in slices:
        should_check = sl.slice_id in yaml_ids or (strict_ids and sl.slice_id in strict_ids)
        if not should_check:
            continue
        if not sl.status or sl.status.strip().lower() == "unknown":
            errors.append(ValidationError(sl.slice_id, "status", "Status is missing or unknown"))
        if not sl.owner:
            errors.append(ValidationError(sl.slice_id, "owner", "Owner is missing"))
        if not sl.file_ownership:
            errors.append(ValidationError(sl.slice_id, "file_ownership", "Dateibesitz is missing"))

    # Validate YAML slice files (always strict)
    for sf in slice_files:
        if not sf.status or sf.status.strip().lower() == "unknown":
            errors.append(ValidationError(sf.slice_id, "status", f"status missing in {sf.source_path.name}"))
        if not sf.owner:
            errors.append(ValidationError(sf.slice_id, "owner", f"owner missing in {sf.source_path.name}"))
        if not sf.file_ownership:
            errors.append(ValidationError(sf.slice_id, "file_ownership", f"file_ownership missing in {sf.source_path.name}"))

    return errors


def claim_proposal(item: WorkboardSlice, owner: str, workboard: Path) -> str:
    commit_msg = f"chore(workboard): claim {item.slice_id}"
    return "\n".join(
        [
            f"Slice: {item.slice_id}",
            f"Status: {item.status}",
            f"Owner: {owner}",
            "",
            "Manual claim steps:",
            f"1. Edit {workboard.as_posix()}: set `**Stand:** reserviert` and `**Owner:** {owner}`.",
            f"2. Commit only the workboard: `git add {workboard.as_posix()} && git commit -m {shlex.quote(commit_msg)}`.",
            "3. Start implementation only after the claim commit exists.",
        ]
    )


def handoff_template(item: WorkboardSlice, owner: str) -> str:
    return "\n".join(
        [
            f"## Handoff {item.slice_id}",
            "",
            f"**Owner:** {owner}",
            "**Stand:** <kurzer Status>",
            f"**Ziel:** {item.goal or '<Ziel nachtragen>'}",
            f"**Dateibesitz:** {item.file_ownership or '<Dateien nachtragen>'}",
            "**Geaendert:**",
            "- <Datei/Pfad>: <Kurzbeschreibung>",
            "**Checks:**",
            "- <Befehl>: <Ergebnis>",
            "**Offene Risiken:**",
            f"- {item.risks or '<Risiko oder none>'}",
            "**Naechster Schritt:**",
            "- <konkreter naechster Schritt>",
        ]
    )


def _filter_slices(
    slices: Iterable[WorkboardSlice],
    status_class: str | None,
    slice_id: str | None,
) -> list[WorkboardSlice]:
    result = list(slices)
    if status_class:
        result = [item for item in result if item.status_class == status_class]
    if slice_id:
        result = [item for item in result if item.slice_id == slice_id]
    return result


def _print_json(items: object) -> None:
    out = json.dumps(items, indent=2, ensure_ascii=True)
    sys.stdout.write(out + "\n")


def cmd_list(args: argparse.Namespace) -> int:
    items = _filter_slices(load_slices(args.workboard), args.status, args.slice_id)
    if args.json:
        _print_json([asdict(item) for item in items])
        return 0
    for item in items:
        print(f"{item.slice_id}\t{item.status_class}\t{item.status}")
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    items = _filter_slices(load_slices(args.workboard), None, args.slice_id)
    if not items:
        print(f"Slice not found: {args.slice_id}", file=sys.stderr)
        return 2
    item = items[0]
    if item.status_class != "open":
        print(
            f"Slice {item.slice_id} is {item.status_class}; claim proposal requires status open.",
            file=sys.stderr,
        )
        return 1
    print(claim_proposal(item, args.owner, args.workboard))
    return 0


def cmd_checks(args: argparse.Namespace) -> int:
    items = _filter_slices(load_slices(args.workboard), None, args.slice_id)
    if not items:
        print(f"Slice not found: {args.slice_id}", file=sys.stderr)
        return 2
    checks = items[0].checks
    if args.json:
        _print_json({"slice_id": args.slice_id, "checks": checks})
        return 0
    if not checks:
        print(f"No check commands documented for {args.slice_id}.")
        return 0
    for check in checks:
        print(check)
    if args.run:
        for check in checks:
            print(f"\n$ {check}")
            completed = subprocess.run(check, shell=True, cwd=args.cwd)
            if completed.returncode:
                return completed.returncode
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    items = _filter_slices(load_slices(args.workboard), None, args.slice_id)
    if not items:
        print(f"Slice not found: {args.slice_id}", file=sys.stderr)
        return 2
    print(handoff_template(items[0], args.owner))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    slices = load_slices(args.workboard)
    slice_files = load_slice_files(args.slices_dir)

    strict_ids: set[str] | None = None
    if args.strict_ids:
        strict_ids = set(args.strict_ids.split(","))

    errors = validate_workboard_slices(slices, slice_files, strict_ids=strict_ids)

    if args.json:
        _print_json([{"slice_id": e.slice_id, "field": e.field, "message": e.message} for e in errors])
    else:
        if not errors:
            print(f"OK: {len(slices)} markdown slices, {len(slice_files)} YAML slice files — no validation errors.")
        else:
            for e in errors:
                print(f"ERROR [{e.slice_id}] {e.field}: {e.message}")

    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only VALEO workboard supervisor inspired by Symphony."
    )
    parser.add_argument("--workboard", type=Path, default=DEFAULT_WORKBOARD)
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List detected workboard slices.")
    list_parser.add_argument("--status", choices=["open", "reserved", "in_progress", "done", "unknown"])
    list_parser.add_argument("--slice-id")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list)

    claim_parser = sub.add_parser("claim-proposal", help="Print manual claim steps for an open slice.")
    claim_parser.add_argument("slice_id")
    claim_parser.add_argument("--owner", default="Codex")
    claim_parser.set_defaults(func=cmd_claim)

    checks_parser = sub.add_parser("checks", help="Print or run documented checks for a slice.")
    checks_parser.add_argument("slice_id")
    checks_parser.add_argument("--json", action="store_true")
    checks_parser.add_argument("--run", action="store_true")
    checks_parser.add_argument("--cwd", default=".")
    checks_parser.set_defaults(func=cmd_checks)

    handoff_parser = sub.add_parser("handoff-template", help="Print a standardized handoff block.")
    handoff_parser.add_argument("slice_id")
    handoff_parser.add_argument("--owner", default="Codex")
    handoff_parser.set_defaults(func=cmd_handoff)

    validate_parser = sub.add_parser(
        "validate",
        help="Validate workboard slices and YAML slice files for required fields.",
    )
    validate_parser.add_argument(
        "--slices-dir", type=Path, default=DEFAULT_SLICES_DIR,
        help="Directory containing YAML slice files (default: docs/agent-ops/slices).",
    )
    validate_parser.add_argument(
        "--strict-ids",
        help="Comma-separated slice IDs to validate in markdown even without YAML file.",
    )
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
