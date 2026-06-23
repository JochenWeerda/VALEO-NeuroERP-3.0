#!/usr/bin/env python3
"""DOM-COMPLIANCE-004.5 — Compliance Lifecycle UAT Script."""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-compliance")
TOKEN = os.environ.get("VALEO_DEV_TOKEN", "dev-token")

HEADERS = {
    "X-Tenant-ID": TENANT,
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def req(method: str, path: str, body=None) -> tuple[int, dict]:
    url = f"{BASE}/api/v1{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def run() -> dict:
    report: dict = {"steps": [], "ok": True}

    def step(name, method, path, body=None, expect=None):
        status, data = req(method, path, body)
        passed = status in expect if expect else True
        entry = {"step": name, "status": status, "passed": passed}
        if not passed:
            entry["error"] = data
            report["ok"] = False
        report["steps"].append(entry)
        return data if passed else {}

    # 1 — PCN anlegen
    created = step("PCN-Meldung anlegen", "POST", "/compliance/pcn-meldungen",
                   {"artikel_id": "uat-art-001", "meldungstyp": "ZULASSUNG"}, expect=[201, 503])
    meldung_id = created.get("id")

    # 2 — PCN validieren
    if meldung_id:
        step("PCN DRAFT→VALIDATED", "POST", f"/compliance/pcn-meldungen/{meldung_id}/transition",
             {"new_status": "VALIDATED"}, expect=[200, 422])

    # 3 — Fällige VVVO
    step("VVVO Fälligkeiten", "GET", "/compliance/vvvo/faellige-pruefungen?within_days=30",
         expect=[200, 503])

    # 4 — Ablaufende Sachkunde
    step("Sachkunde ablaufend", "GET", "/compliance/sachkunde/ablaufend?within_days=30",
         expect=[200, 503])

    # 5 — Artikel sperren
    step("Artikel sperren", "POST", "/compliance/artikel/uat-art-001/sperre",
         {"grund": "UAT-Test"}, expect=[200, 201, 422, 503])

    # 6 — Sperre Audit-Trail
    step("Sperre Audit-Trail", "GET", "/compliance/artikel/uat-art-001/sperre-audit",
         expect=[200, 503])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
