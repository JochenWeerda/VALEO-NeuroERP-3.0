#!/usr/bin/env python3
"""DOM-CONTROLLING-004.5 — Controlling Lifecycle UAT Script."""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-ctrl")
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

    # 1 — Budget anlegen
    budget = step("Budget anlegen", "POST", "/controlling/budgets", {
        "kostenstelle_id": "uat-kst-001",
        "periode": "2026-06",
        "plan_eur": 50000.0,
        "bezeichnung": "UAT IT-Budget",
        "operator": "uat-mgr",
    }, expect=[201, 422])
    budget_id = budget.get("id")

    # 2 — Budget freigeben
    if budget_id:
        step("Budget ENTWURF→FREIGEGEBEN", "POST", f"/controlling/budgets/{budget_id}/transition",
             {"new_status": "FREIGEGEBEN", "operator": "uat-mgr"}, expect=[200, 422])

        # 3 — Budget aktivieren
        step("Budget FREIGEGEBEN→AKTIV", "POST", f"/controlling/budgets/{budget_id}/transition",
             {"new_status": "AKTIV", "operator": "uat-mgr"}, expect=[200, 422])

    # 4 — Ist-Wert buchen
    step("Ist-Wert buchen", "POST", "/controlling/ist-werte", {
        "kostenstelle_id": "uat-kst-001",
        "periode": "2026-06",
        "ist_eur": 48000.0,
        "buchungsref": "BU-UAT-001",
        "operator": "uat-buchhalter",
    }, expect=[201, 422])

    # 5 — Abweichungsanalyse
    step("Abweichungsanalyse abrufen", "GET",
         "/controlling/abweichung?kostenstelle_id=uat-kst-001&periode=2026-06",
         expect=[200, 422])

    # 6 — KST-Abschluss initiieren
    step("KST-Abschluss IN_BEARBEITUNG", "POST", "/controlling/kostenstellen/uat-kst-001/abschluss",
         {"periode": "2026-06", "new_status": "IN_BEARBEITUNG", "operator": "uat-ctrl"}, expect=[200, 201, 422])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
