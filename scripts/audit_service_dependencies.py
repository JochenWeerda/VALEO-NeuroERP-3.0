"""Audit every service manifest separately, retaining complete reports on failure.

Run --matrix for CI discovery, --manifest services/.../requirements.txt for one
service, or without either to audit all services. Resolution includes transitives.
Editable workspace distributions have no public advisory identity; pip-audit
still resolves their dependencies, but skips the editable distribution itself.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

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


def audit(manifest: Path, output: Path, timeout: int = 1800) -> int:
    output.mkdir(parents=True, exist_ok=True)
    report = output.resolve() / "pip-audit.json"
    # A failed rerun must never present an older successful report as evidence.
    report.unlink(missing_ok=True)
    command = [sys.executable, "-m", "pip_audit", "-r", str(manifest.resolve()),
               "--strict", "--skip-editable", "--format", "json",
               "--progress-spinner", "off", "--output", str(report)]
    code = 2
    error = None
    with (output / "audit.log").open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(command, cwd=manifest.parent, stdout=log,
                                    stderr=subprocess.STDOUT, timeout=timeout, check=False)
            code = result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
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
