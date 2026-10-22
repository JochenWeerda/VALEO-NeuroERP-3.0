"""Generate or check the native Studio release catalog (config/studio_screen_versions.json).

    python scripts/generate_studio_screen_versions.py
    python scripts/generate_studio_screen_versions.py --check
    python scripts/generate_studio_screen_versions.py --release-version 1.0.0

Only ScreenDefinitions that pass Made-by-Studio Gates A/B/C/E with a clean Studio-Draft projection
are written. Beleg varianten remain in config/document_screen_versions.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.studio_screen_versions import (  # noqa: E402
    REGISTRY_PATH,
    build_catalog_entry,
    check_registry,
    current_matches,
)
from app.services.made_by_studio_gates import evaluate_all  # noqa: E402


def _native_definitions() -> dict[str, dict]:
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry
    from app.services.made_by_studio_gates import load_registered_definitions

    ensure_stamm_screen_registry()
    return {sid: definition for sid, definition in load_registered_definitions().items()
            if sid and not sid.startswith("beleg/") and definition}


def _release_payload(version: str) -> dict:
    reports = {report.screen_id: report for report in evaluate_all()}
    screens: dict[str, dict] = {}
    release_ready = 0
    for screen_id, definition in sorted(_native_definitions().items()):
        report = reports.get(screen_id)
        if report is None:
            raise ValueError(f"studio_screen_missing_gate_report:{screen_id}")
        gates_passed = [gate for gate in ("A", "B", "C", "E") if report.gates[gate].passed]
        draft_clean = not report.studio_draft_violations
        if len(gates_passed) == 4 and draft_clean:
            release_ready += 1
        screens[screen_id] = build_catalog_entry(
            definition,
            version=version,
            gates_passed=gates_passed,
            studio_draft_clean=draft_clean,
        )
    return {
        "schemaVersion": 1,
        "releaseVersion": version,
        "screens": screens,
        "_release_ready_count": release_ready,
    }


def write_release(path: Path, version: str) -> dict:
    lock = path.with_suffix(".lock")
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        lock.unlink(missing_ok=True)
        try:
            handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as retry_error:
            raise ValueError("studio_screen_release_busy") from retry_error
    pending = None
    try:
        payload = _release_payload(version)
        ready = payload.pop("_release_ready_count", 0)
        check_registry(payload, definitions=_native_definitions())
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix="studio-screen-versions-",
            suffix=".tmp",
            delete=False,
        ) as target:
            pending = Path(target.name)
            json.dump(payload, target, ensure_ascii=False, sort_keys=True, indent=2)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        try:
            os.replace(pending, path)
        except PermissionError:
            path.write_text(pending.read_text(encoding="utf-8"), encoding="utf-8")
            pending.unlink(missing_ok=True)
        pending = None
        print(f"Studio screen catalog {version}: {len(payload['screens'])} screens "
              f"({ready} release-ready with gates A/B/C/E and clean draft)")
        return payload
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
        os.close(handle)
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--release-version")
    args = parser.parse_args()
    if args.check and args.release_version:
        parser.error("Choose --check or --release-version, not both")
    definitions = _native_definitions()
    if args.check:
        if not REGISTRY_PATH.is_file():
            parser.exit(1, "Studio screen catalog missing.\n")
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if not current_matches(registry, definitions):
            parser.exit(1, "Studio screen catalog differs from canonical builders or gate evidence.\n")
        print(f"Studio screen catalog synchronized: {len(registry.get('screens', {}))} screens")
        return 0
    version = args.release_version
    if not version:
        if REGISTRY_PATH.is_file():
            version = json.loads(REGISTRY_PATH.read_text(encoding="utf-8")).get("releaseVersion") or "1.0.0"
        else:
            version = "1.0.0"
    write_release(REGISTRY_PATH, version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
