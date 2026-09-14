"""Audit every service manifest separately, retaining complete reports on failure.

Run --matrix for CI discovery, --manifest services/.../requirements.txt for one
service, or without either to audit all services. Resolution includes transitives.
Editable workspace distributions have no public advisory identity. Their static
PEP 621 dependencies are expanded before complete transitive resolution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def discover(root: Path = ROOT) -> list[Path]:
    manifests = sorted((root / "services").rglob("requirements.txt"))
    if not manifests:
        raise ValueError("No service manifests found; refusing an empty audit")
    return manifests


def matrix(root: Path = ROOT) -> dict:
    return {"include": [{"manifest": p.relative_to(root).as_posix(),
                         "service": p.parent.relative_to(root / "services").as_posix().replace("/", "--")}
                        for p in discover(root)]}


def audit_input(manifest: Path, output: Path) -> Path:
    """Expand static PEP 621 workspace dependencies, without dropping transitives.

    pip-audit's requirements resolver loses editable provenance and then tries
    to find finance-shared on PyPI even with --skip-editable. Fail on unsupported
    metadata rather than silently omit a local package's dependencies.
    """
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not any(line.strip().startswith(("-e ", "--editable ")) for line in lines):
        return manifest
    expanded = []
    workspace = ROOT / "packages"
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("-e ", "--editable ")):
            relative = stripped.split(maxsplit=1)[1].split(" #", 1)[0].strip()
            package = (manifest.parent / relative).resolve()
            if not package.is_relative_to(workspace.resolve()):
                raise ValueError("Editable dependency must be a local workspace package")
            metadata = tomllib.loads((package / "pyproject.toml").read_text(encoding="utf-8"))
            project = metadata["project"]
            if project.get("dynamic"):
                raise ValueError("Dynamic workspace metadata requires an explicit resolver")
            dependencies = project.get("dependencies", [])
            if not isinstance(dependencies, list) or not all(isinstance(d, str) and not d.startswith("-") for d in dependencies):
                raise ValueError("Invalid workspace dependency metadata")
            expanded.append("# Workspace source: " + relative)
            expanded.extend(dependencies)
        elif stripped.startswith(("-r ", "--requirement ", "-c ", "--constraint ")):
            flag, relative = stripped.split(maxsplit=1)
            expanded.append(flag + " " + str((manifest.parent / relative).resolve()))
        else:
            expanded.append(line)
    target = output.resolve() / "audit-requirements.txt"
    target.write_text("\n".join(expanded) + "\n", encoding="utf-8")
    return target


def audit(manifest: Path, output: Path, timeout: int = 1800) -> int:
    output.mkdir(parents=True, exist_ok=True)
    report = output.resolve() / "pip-audit.json"
    # A failed rerun must never present an older successful report as evidence.
    report.unlink(missing_ok=True)
    (output / "status.json").unlink(missing_ok=True)
    code = 2
    error = None
    with (output / "audit.log").open("w", encoding="utf-8") as log:
        try:
            requirements = audit_input(manifest, output)
            command = [sys.executable, "-m", "pip_audit", "-r", str(requirements.resolve()),
                       "--strict", "--format", "json", "--progress-spinner", "off",
                       "--output", str(report)]
            result = subprocess.run(command, cwd=manifest.parent, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout, check=False)
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
            error = type(exc).__name__
            log.write(f"Audit could not complete: {error}\n")
    if code == 0:
        try:
            data = json.loads(report.read_text(encoding="utf-8"))
            dependencies = data["dependencies"]
            if not dependencies or any("skip_reason" in dep or dep.get("vulns") for dep in dependencies):
                code, error = 2, "Incomplete or vulnerable report returned success"
        except (OSError, ValueError, KeyError, TypeError):
            code, error = 2, "Missing or invalid audit report"
    (output / "status.json").write_text(json.dumps({"manifest": manifest.as_posix(),
        "exit_code": code, "error": error}, indent=2) + "\n", encoding="utf-8")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--manifest")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/service-security")
    args = parser.parse_args()
    if args.matrix:
        print(json.dumps(matrix()))
        return 0
    manifests = discover()
    if args.manifest:
        selected = (ROOT / args.manifest).resolve()
        if selected not in [p.resolve() for p in manifests]:
            parser.error("Manifest must be an existing requirements.txt under services/")
        manifests = [selected]
    failures = []
    for manifest in manifests:
        name = manifest.parent.relative_to(ROOT / "services").as_posix().replace("/", "--")
        code = audit(manifest, args.output / name)
        print(f"{name}: audit exit {code}", flush=True)
        if code:
            failures.append(name)
    print(f"Audited {len(manifests)} service manifests; {len(failures)} failed", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
