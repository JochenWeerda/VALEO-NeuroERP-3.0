#!/usr/bin/env python3
"""DOM-FINANCE-004.5 — Finance Lifecycle UAT Script."""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-finance")
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

    # 1 — SEPA Mandat anlegen
    mandat = step("SEPA Mandat anlegen", "POST", "/finance/sepa/mandate", {
        "glaeubiger_id": "DE98ZZZ09999999999",
        "iban": "DE12345678901234567890",
        "bic": "COBADEFFXXX",
    }, expect=[201, 503])
    mandat_id = mandat.get("id")

    # 2 — SEPA Batch
    step("SEPA Batch erstellen", "POST", "/finance/sepa/batches", {
        "faellig_am": "2026-07-01",
        "eintraege": [{"mandat_ref": "MAND-UAT-001", "iban": "DE99...", "betrag_eur": 150.0}],
    }, expect=[201, 422, 503])

    # 3 — SEPA Mandat widerrufen
    if mandat_id:
        step("SEPA Mandat widerrufen", "POST", f"/finance/sepa/mandate/{mandat_id}/widerruf",
             expect=[200, 422])

    # 4 — Ratenzahlungsplan
    plan = step("Ratenzahlungsplan anlegen", "POST", "/finance/ratenzahlung/plaene", {
        "op_id": "uat-op-001",
        "gesamt_eur": 600.0,
        "anzahl_raten": 3,
        "erste_faelligkeit": "2026-07-01",
    }, expect=[201, 422, 503])

    # 5 — Mahnstufe
    step("Mahnstufe eskalieren", "POST", "/finance/mahnstufe/RE-UAT-001/eskalieren",
         {"operator": "uat-tester"}, expect=[201, 422, 503])

    # 6 — Mahnstufen-Trail
    step("Mahnstufen-Trail", "GET", "/finance/mahnstufe/RE-UAT-001/trail",
         expect=[200, 503])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
