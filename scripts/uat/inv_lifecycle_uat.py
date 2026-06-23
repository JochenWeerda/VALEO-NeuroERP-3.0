#!/usr/bin/env python3
"""DOM-INV-004.5 — Inventory Lifecycle UAT Script.

Sequentiell gegen dev-Backend:
  1. Lot anlegen (POST /lager/lots)
  2. Lots auflisten FEFO (GET /lager/lots)
  3. Lot verbrauchen (POST /lager/lots/{id}/consume)
  4. Korrektur anlegen (POST /lager/bestandskorrektur)
  5. Korrektur stornieren (POST /lager/korrekturen/{id}/storno)
  6. Reason codes lesen (GET /lager/reason-codes)

Ausgabe: JSON-Report auf stdout.
"""
from __future__ import annotations

import json
import sys
import os
from datetime import date, timedelta
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-inv")
TOKEN = os.environ.get("VALEO_DEV_TOKEN", "dev-token")

HEADERS = {
    "X-Tenant-ID": TENANT,
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


def req(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    url = f"{BASE}/api/v1{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def run() -> dict:
    report: dict = {"timestamp": date.today().isoformat(), "steps": [], "ok": True}

    def step(name: str, method: str, path: str, body=None, expect: int = 200) -> dict:
        status, data = req(method, path, body)
        passed = status == expect
        entry = {"step": name, "method": method, "path": path, "status": status, "passed": passed}
        if not passed:
            entry["error"] = data
            report["ok"] = False
        report["steps"].append(entry)
        return data if passed else {}

    mhd = (date.today() + timedelta(days=90)).isoformat()

    # 1 — Lot anlegen
    lot = step(
        "Lot anlegen",
        "POST",
        "/lager/lots",
        {
            "article_id": "uat-article-inv",
            "warehouse_id": "uat-warehouse-inv",
            "lot_number": f"UAT-LOT-{date.today()}",
            "initial_qty": 2000.0,
            "unit": "kg",
            "mhd": mhd,
        },
        expect=201,
    )
    lot_id = lot.get("id")

    # 2 — Lots auflisten
    step("Lots FEFO auflisten", "GET", "/lager/lots?article_id=uat-article-inv", expect=200)

    # 3 — Lot verbrauchen
    if lot_id:
        step(
            "Lot verbrauchen (500 kg)",
            "POST",
            f"/lager/lots/{lot_id}/consume",
            {"quantity": 500.0},
            expect=200,
        )

    # 4 — Bestandskorrektur
    korr = step(
        "Bestandskorrektur anlegen",
        "POST",
        "/lager/bestandskorrektur",
        {
            "article_id": "uat-article-inv",
            "warehouse_id": "uat-warehouse-inv",
            "menge": -50.0,
            "grund": "schwund",
            "bemerkung": "UAT DOM-INV-004",
        },
        expect=201,
    )
    korr_id = korr.get("movement_id") or korr.get("id")

    # 5 — Storno
    if korr_id:
        step(
            "Korrektur stornieren",
            "POST",
            f"/lager/korrekturen/{korr_id}/storno",
            {"bemerkung": "UAT Storno"},
            expect=201,
        )

    # 6 — Reason Codes
    step("Reason Codes lesen", "GET", "/lager/reason-codes", expect=200)

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
