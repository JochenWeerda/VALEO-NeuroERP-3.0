"""Verify pinned Python test toolchain versions across requirements files and CI."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PINS_PATH = PROJECT_ROOT / "config/release-toolchain-pins.json"
WORKFLOW_GLOBS = (
    PROJECT_ROOT / ".github/workflows/quality-gate.yml",
    PROJECT_ROOT / ".github/workflows/release-gates.yml",
    PROJECT_ROOT / ".github/workflows/sonarcloud.yml",
    PROJECT_ROOT / ".github/workflows/ci.yml",
)


def _parse_requirement_pin(line: str, package: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(package)}==([^\s#]+)")
    match = pattern.match(line.strip())
    return match.group(1) if match else None


def _read_requirements_lines(path: Path) -> list[str]:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8")
    return text.splitlines()


def _check_requirements_file(path: Path, packages: dict[str, str], failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"Missing requirements file: {path.as_posix()}")
        return

    content = _read_requirements_lines(path)
    for package, expected in packages.items():
        found = next(
            (_parse_requirement_pin(line, package) for line in content if _parse_requirement_pin(line, package)),
            None,
        )
        if found is None:
            failures.append(f"{path.as_posix()}: missing pin for {package}=={expected}")
        elif found != expected:
            failures.append(
                f"{path.as_posix()}: {package}=={found} (expected {package}=={expected})"
            )


def _check_workflows(failures: list[str]) -> None:
    loose_install = re.compile(r"pip install .*pytest-cov(?!==)")
    for workflow in WORKFLOW_GLOBS:
        if not workflow.exists():
            continue
        text = workflow.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if loose_install.search(line) and "requirements.txt" not in line:
                failures.append(
                    f"{workflow.as_posix()}:{line_no}: unpinned pytest-cov install: {line.strip()}"
                )


def main() -> None:
    pins = json.loads(PINS_PATH.read_text(encoding="utf-8"))
    packages = pins["python_packages"]
    failures: list[str] = []

    for rel_path in pins.get("requirements_files_strict", []):
        _check_requirements_file(PROJECT_ROOT / rel_path, packages, failures)

    for rel_path, package_names in pins.get("requirements_files_partial", {}).items():
        subset = {name: packages[name] for name in package_names}
        _check_requirements_file(PROJECT_ROOT / rel_path, subset, failures)

    _check_workflows(failures)

    if failures:
        raise SystemExit(
            "Toolchain pin drift detected:\n- " + "\n- ".join(failures)
        )

    print("Toolchain pins OK.")


if __name__ == "__main__":
    main()
