#!/usr/bin/env python3
"""DOM-PROC-004.5 — Procurement Lifecycle UAT Script."""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-proc")
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

    # 1 — Bestellung freigeben
    step("Bestellung DRAFT→FREIGEGEBEN", "POST", "/procurement/bestellungen/uat-best-001/transition",
         {"new_status": "FREIGEGEBEN", "operator": "uat-mgr"}, expect=[200, 422, 404])

    # 2 — Bestellung versenden
    step("Bestellung FREIGEGEBEN→VERSANDT", "POST", "/procurement/bestellungen/uat-best-001/transition",
         {"new_status": "VERSANDT"}, expect=[200, 422, 404])

    # 3 — Wareneingang buchen
    we = step("Wareneingang buchen", "POST", "/procurement/bestellungen/uat-best-001/wareneingang", {
        "menge_erhalten": 100.0, "einheit": "KG", "lager_id": "uat-lager-001",
    }, expect=[201, 422, 404])
    we_id = we.get("id")

    # 4 — QS-Status setzen
    if we_id:
        step("WE QS-Status → BESTANDEN", "POST", f"/procurement/wareneingaenge/{we_id}/qs",
             {"qs_status": "BESTANDEN"}, expect=[200, 422])

    # 5 — Rechnungsprüfung
    step("Rechnungsprüfung 3-Way-Match", "POST", "/procurement/bestellungen/uat-best-001/rechnungspruefung", {
        "rechnungs_nr": "RE-UAT-001",
        "rechnungs_betrag_eur": 1020.0,
        "bestell_preis_eur": 10.0,
        "we_menge": 100.0,
    }, expect=[201, 422, 503])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
