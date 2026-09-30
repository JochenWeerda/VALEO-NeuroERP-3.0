#!/usr/bin/env python3
"""Lesender, begrenzter Verbesserungsprueflauf ohne optionalen Pipeline-Service.

Keine Reparaturen, Baseline-Updates, Netzabfragen oder Datenbankmutationen.
Alle unabhaengigen Scanner laufen trotz einzelner Fehler; Fehler bleiben Exit 1.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
CHECKS = {
    "toolchain": ["scripts/check_toolchain_pins.py"],
    "sql-bind-casts": ["scripts/check_sql_bind_casts.py"],
    "sql-fstrings": ["scripts/check_sql_fstrings.py"],
    "business-time": ["scripts/check_business_time_usage.py"],
    "transactions": ["scripts/check_dead_transactions.py"],
    "pagination": ["scripts/check_pagination.py"],
    "godfiles": ["scripts/check_file_size.py"],
    "tenant-classification": ["scripts/check_tenant_isolation.py"],
    "baseline-integrity": ["scripts/check_baseline_integrity.py", "--base", "HEAD"],
}


def run_check(name: str, args: list[str], root: Path, timeout: float) -> dict:
    started = monotonic()
    try:
        result = subprocess.run(
            [sys.executable, *args], cwd=root, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout,
        )
        status = "passed" if result.returncode == 0 else "failed"
        code = result.returncode
        # Keine Rohlogs/Secrets im Report; vollstaendige Scanner-Details lokal abrufen.
        output_hash = hashlib.sha256((result.stdout + result.stderr).encode("utf-8")).hexdigest()
    except subprocess.TimeoutExpired:
        status, code, output_hash = "timeout", None, None
    except OSError:
        status, code, output_hash = "unavailable", None, None
    return {
        "name": name, "status": status, "exit_code": code,
        "duration_seconds": round(monotonic() - started, 3), "output_sha256": output_hash,
    }


def snapshot(root: Path) -> dict:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    diff = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=root)
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=root
    ).decode("utf-8").split("\0")
    checksum = hashlib.sha256(diff)
    for name in sorted(filter(None, untracked)):
        # Eigene Reports sind Ausgaben, keine Eingaben; sonst aendert sich jeder Lauf.
        if name.startswith("artifacts/"):
            continue
        path = root / name
        if path.is_file():
            checksum.update(name.encode("utf-8"))
            checksum.update(hashlib.sha256(path.read_bytes()).digest())
    return {"sha": sha, "worktree_sha256": checksum.hexdigest(), "dirty": bool(diff or any(untracked))}


def run(root: Path, jobs: int, timeout: float) -> dict:
    started = monotonic()
    before = snapshot(root)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run_check, name, args, root, timeout) for name, args in CHECKS.items()]
        checks = [future.result() for future in futures]
    after = snapshot(root)
    stable = before == after
    return {
        "schema_version": 1, "measured_at": datetime.now(timezone.utc).isoformat(),
        **before, "snapshot_stable": stable, "python_version": sys.version.split()[0],
        "duration_seconds": round(monotonic() - started, 3), "checks": checks,
        "status": "passed" if stable and all(c["status"] == "passed" for c in checks) else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=2)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--output", type=Path, default=Path("artifacts/code-improvement.json"))
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout muss positiv sein")
    try:
        report = run(ROOT, args.jobs, args.timeout)
    except (OSError, subprocess.CalledProcessError):
        print("FAIL: Repository-Snapshot nicht nachweisbar", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for check in report["checks"]:
        print(f"{check['name']}: {check['status']} ({check['duration_seconds']}s)")
    if not report["snapshot_stable"]:
        print("FAIL: Arbeitsbaum hat sich waehrend der Messung geaendert.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

