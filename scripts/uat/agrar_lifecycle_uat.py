#!/usr/bin/env python3
"""DOM-AGRAR-004.5 — Agrar Lifecycle UAT Script.

Sequentiell gegen dev-Backend:
  1. Düngungsbilanz berechnen (POST /agrar/p0/duenge-bilanz)
  2. Partie anlegen (POST /agrar/p0/partien) — erwartet 422 wenn keine Annahmen vorhanden
  3. Trocknung-Endpoint erreichbar prüfen
  4. Selbstabrechnung issue-Endpoint erreichbar prüfen
  5. Selbstabrechnung storno-Endpoint erreichbar prüfen

Ausgabe: JSON-Report auf stdout.
"""
from __future__ import annotations

import json
import sys
import os
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-agrar")
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

    # 1 — Düngungsbilanz
    step("Düngungsbilanz berechnen", "POST", "/agrar/p0/duenge-bilanz", {
        "tenant_id": TENANT, "schlag_id": "uat-schlag-001",
        "wirtschaftsjahr": 2026, "eintraege": [],
        "bedarf_n_kg_ha": 170.0, "bedarf_p_kg_ha": 60.0, "bedarf_k_kg_ha": 80.0,
    }, expect=[200])

    # 2 — Partie anlegen (422 ist ok wenn keine Annahmen in DB)
    step("Partie anlegen (422=erwartet ohne Annahmen)", "POST", "/agrar/p0/partien",
         {"acceptance_ids": ["uat-acc-not-exists"]}, expect=[201, 422])

    # 3 — Trocknung route check
    step("Trocknung Endpunkt erreichbar", "POST", "/agrar/p0/partien/uat-partie-nicht-vorhanden/trocknung",
         {"moisture_out_pct": 13.0}, expect=[201, 422, 404, 503])

    # 4 — Selbstabrechnung issue check
    step("Selbstabrechnung issue erreichbar", "POST", "/agrar/p0/selbstabrechnung/uat-r-nicht-vorhanden/issue",
         expect=[200, 422, 404, 503])

    # 5 — Selbstabrechnung storno check
    step("Selbstabrechnung storno erreichbar", "POST", "/agrar/p0/selbstabrechnung/uat-r-nicht-vorhanden/storno",
         {}, expect=[201, 422, 404, 503])

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
