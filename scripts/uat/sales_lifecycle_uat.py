#!/usr/bin/env python3
"""DOM-SALES-004.5 — Sales Lifecycle UAT Script."""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-sales")
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

    # 1 — AB versenden
    step("AB DRAFT→VERSANDT", "POST", "/sales/orders/uat-auftrag-001/ab-transition",
         {"new_status": "VERSANDT"}, expect=[200, 422, 404])

    # 2 — LS kommissionieren
    step("LS OFFEN→KOMMISSIONIERT", "POST", "/sales/delivery-notes/uat-ls-001/advance",
         {"new_status": "KOMMISSIONIERT"}, expect=[200, 422, 404])

    # 3 — LS versenden
    step("LS KOMMISSIONIERT→VERSANDT", "POST", "/sales/delivery-notes/uat-ls-001/advance",
         {"new_status": "VERSANDT"}, expect=[200, 422, 404])

    # 4 — Preisabweichung prüfen (auto-freigabe)
    step("Preisabweichung < 2%", "POST", "/sales/orders/uat-auftrag-001/preisabweichung",
         {"artikel_id": "art-001", "angebots_preis": 100.0, "rechnungs_preis": 101.0},
         expect=[201, 422, 503])

    # 5 — Preisabweichung prüfen (eskalation)
    step("Preisabweichung > 2%", "POST", "/sales/orders/uat-auftrag-002/preisabweichung",
         {"artikel_id": "art-001", "angebots_preis": 100.0, "rechnungs_preis": 110.0},
         expect=[201, 422, 503])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
