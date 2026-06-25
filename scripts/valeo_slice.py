#!/usr/bin/env python3
"""DEV-HARNESS-CLI-001 — Valeo-Slice CLI.

Nutzung:
  python scripts/valeo_slice.py claim <SLICE-ID>
  python scripts/valeo_slice.py verify <SLICE-ID>
  python scripts/valeo_slice.py close <SLICE-ID>
  python scripts/valeo_slice.py status <SLICE-ID>
  python scripts/valeo_slice.py list
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SLICES_DIR = REPO_ROOT / "docs" / "agent-ops" / "slices"
WORKBOARD = REPO_ROOT / "docs" / "agent-ops" / "active-workboard.md"
READINESS_CHECK = REPO_ROOT / "scripts" / "ai-slice-readiness-check.cjs"
GOVERNANCE_CHECK = REPO_ROOT / "scripts" / "docs-governance-check.cjs"

REQUIRED_AI_HARNESS_FIELDS = {
    "fachlicher_vertrag",
    "architektur_vertrag",
    "daten_vertrag",
    "test_vertrag",
    "security_vertrag",
    "betriebs_vertrag",
    "dokumentations_vertrag",
}
REQUIRED_SLICE_FIELDS = {
    "slice_id", "title", "owner", "status", "created_at",
    "goal", "file_ownership", "tests", "risks", "external_gates", "ai_harness",
}


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _run(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def _find_slice_yaml(slice_id: str) -> Path | None:
    for p in SLICES_DIR.glob("*.yaml"):
        try:
            data = _load_yaml(p)
            if data.get("slice_id") == slice_id:
                return p
        except Exception:
            continue
    return None


def _validate_yaml(data: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_SLICE_FIELDS - data.keys()
    if missing:
        errors.append(f"Fehlende Pflicht-Felder: {sorted(missing)}")
    harness = data.get("ai_harness") or {}
    missing_harness = REQUIRED_AI_HARNESS_FIELDS - harness.keys()
    if missing_harness:
        errors.append(f"Fehlende ai_harness-Felder: {sorted(missing_harness)}")
    return errors


def cmd_status(slice_id: str) -> int:
    yaml_path = _find_slice_yaml(slice_id)
    if not yaml_path:
        print(f"[FEHLER] Slice-YAML fuer '{slice_id}' nicht gefunden in {SLICES_DIR}")
        return 1
    data = _load_yaml(yaml_path)
    errors = _validate_yaml(data)
    print(f"Slice:  {slice_id}")
    print(f"YAML:   {yaml_path.relative_to(REPO_ROOT)}")
    print(f"Status: {data.get('status', '?')}")
    print(f"Owner:  {data.get('owner', '?')}")
    if errors:
        print("Schema-Fehler:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("Schema: OK")
    return 0


def cmd_verify(slice_id: str) -> int:
    yaml_path = _find_slice_yaml(slice_id)
    if not yaml_path:
        print(f"[FEHLER] Slice-YAML nicht gefunden: {slice_id}")
        return 1

    data = _load_yaml(yaml_path)
    errors = _validate_yaml(data)
    ok = True

    print(f"=== valeo-slice verify {slice_id} ===")

    if errors:
        print("[FAIL] YAML-Schema:")
        for e in errors:
            print(f"  - {e}")
        ok = False
    else:
        print("[OK]   YAML-Schema")

    if READINESS_CHECK.exists():
        code, out = _run(["node", str(READINESS_CHECK), "--slice", slice_id])
        if code == 0:
            print("[OK]   ai-slice-readiness-check")
        else:
            print(f"[FAIL] ai-slice-readiness-check:\n{out}")
            ok = False
    else:
        print("[SKIP] ai-slice-readiness-check (Script nicht gefunden)")

    if GOVERNANCE_CHECK.exists():
        code, out = _run(["node", str(GOVERNANCE_CHECK), str(yaml_path)])
        if code == 0:
            print("[OK]   docs-governance-check")
        else:
            print(f"[FAIL] docs-governance-check:\n{out}")
            ok = False
    else:
        print("[SKIP] docs-governance-check (Script nicht gefunden)")

    tests = data.get("tests") or []
    for test_cmd in tests:
        parts = test_cmd.split()
        code, out = _run(parts)
        label = test_cmd[:60]
        if code == 0:
            print(f"[OK]   {label}")
        else:
            print(f"[FAIL] {label}\n{out[:300]}")
            ok = False

    print()
    if ok:
        print(f"RESULT: {slice_id} — ALLE CHECKS GRUEN")
    else:
        print(f"RESULT: {slice_id} — CHECKS FEHLGESCHLAGEN")
    return 0 if ok else 1


def cmd_claim(slice_id: str) -> int:
    wb = WORKBOARD.read_text(encoding="utf-8")
    if slice_id in wb:
        print(f"[INFO] {slice_id} ist bereits im Workboard.")
        return 0
    print(f"[INFO] Slice {slice_id} ist noch nicht im Workboard.")
    print("       Bitte Workboard-Eintrag manuell hinzufuegen und committen.")
    print("       Dann Slice-YAML in docs/agent-ops/slices/ anlegen.")
    return 0


def cmd_close(slice_id: str) -> int:
    rc = cmd_verify(slice_id)
    if rc != 0:
        print("[ABBRUCH] Verifikation fehlgeschlagen — Slice kann nicht geschlossen werden.")
        return rc
    yaml_path = _find_slice_yaml(slice_id)
    if yaml_path:
        data = _load_yaml(yaml_path)
        if data.get("status") != "completed":
            print(f"[HINWEIS] YAML-Status ist '{data.get('status')}' — bitte auf 'completed' setzen.")
    print(f"[OK] {slice_id} ist bereit zum Abschluss. Workboard-Eintrag auf 'abgeschlossen' setzen.")
    return 0


def cmd_list() -> int:
    print(f"{'Slice-ID':<40} {'Status':<15} {'Owner'}")
    print("-" * 80)
    for p in sorted(SLICES_DIR.glob("*.yaml")):
        try:
            data = _load_yaml(p)
            sid = data.get("slice_id", p.stem)
            status = data.get("status", "?")
            owner = data.get("owner", "?")
            print(f"{sid:<40} {status:<15} {owner}")
        except Exception:
            print(f"{p.stem:<40} [YAML-FEHLER]")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0

    command = args[0]
    slice_id = args[1] if len(args) > 1 else ""

    if command == "list":
        return cmd_list()
    if command == "status" and slice_id:
        return cmd_status(slice_id)
    if command == "verify" and slice_id:
        return cmd_verify(slice_id)
    if command == "claim" and slice_id:
        return cmd_claim(slice_id)
    if command == "close" and slice_id:
        return cmd_close(slice_id)

    print(f"Unbekannter Befehl: {command}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
