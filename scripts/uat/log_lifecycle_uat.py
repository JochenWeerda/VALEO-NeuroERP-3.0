#!/usr/bin/env python3
"""DOM-LOG-004.5 — Logistik Lifecycle UAT Script.

Sequentiell gegen dev-Backend:
  1. Tour anlegen (POST /logistik/tours)
  2. Stopp-Status auf GELIEFERT setzen (PATCH /logistik/tours/{id}/stops/{sid})
  3. Disposition-Check (POST /logistik/tours/{id}/disposition-check)
  4. ePOD-Settlement (POST /logistik/tours/{id}/stops/{sid}/settle)
  5. Tour-Detail lesen (GET /logistik/tours/{id})
  6. Statistiken lesen (GET /logistik/statistics)

Ausgabe: JSON-Report auf stdout.
"""
from __future__ import annotations

import json
import sys
import os
from datetime import datetime, timedelta
import urllib.request
import urllib.error

BASE = os.environ.get("VALEO_BASE_URL", "http://localhost:8000")
TENANT = os.environ.get("VALEO_TENANT_ID", "uat-tenant-log")
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
    report: dict = {"timestamp": datetime.utcnow().isoformat(), "steps": [], "ok": True}

    def step(name: str, method: str, path: str, body=None, expect: int = 200) -> dict:
        status, data = req(method, path, body)
        passed = status == expect
        entry = {"step": name, "method": method, "path": path, "status": status, "passed": passed}
        if not passed:
            entry["error"] = data
            report["ok"] = False
        report["steps"].append(entry)
        return data if passed else {}

    now = datetime.utcnow()

    # 1 — Tour anlegen
    tour = step(
        "Tour anlegen",
        "POST",
        "/logistik/tours",
        {
            "date": now.isoformat(),
            "vehicle_id": "vehicle-uat-log",
            "driver_id": "driver-uat-log",
            "status": "GEPLANT",
            "notes": "UAT DOM-LOG-004",
            "stops": [
                {
                    "address": "Musterstraße 1, 48143 Münster",
                    "lat": 51.96,
                    "lng": 7.62,
                    "stop_order": 0,
                    "planned_arrival": (now + timedelta(hours=1)).isoformat(),
                }
            ],
        },
        expect=201,
    )
    tour_id = tour.get("id")
    stop_id = (tour.get("stops") or [{}])[0].get("id") if tour.get("stops") else None

    if not tour_id:
        report["ok"] = False
        report["fatal"] = "Kein tour_id — weitere Schritte übersprungen"
        return report

    # 2 — Stopp-Status auf GELIEFERT
    if stop_id:
        step(
            "Stopp → GELIEFERT",
            "PATCH",
            f"/logistik/tours/{tour_id}/stops/{stop_id}",
            {"status": "GELIEFERT", "actual_arrival": now.isoformat()},
            expect=200,
        )

    # 3 — Disposition-Check
    disp = step(
        "Disposition-Check",
        "POST",
        f"/logistik/tours/{tour_id}/disposition-check",
        {"capacity_kg": 20000.0},
        expect=200,
    )
    report["disposition_result"] = disp.get("result")

    # 4 — ePOD-Settlement (nur wenn stop GELIEFERT)
    if stop_id:
        step(
            "ePOD-Settlement",
            "POST",
            f"/logistik/tours/{tour_id}/stops/{stop_id}/settle",
            {"recipient_name": "Max Mustermann", "delivered_at": now.isoformat(), "notes": "UAT"},
            expect=201,
        )

    # 5 — Tour-Detail
    step("Tour-Detail lesen", "GET", f"/logistik/tours/{tour_id}", expect=200)

    # 6 — Statistiken
    step("Statistiken lesen", "GET", "/logistik/statistics", expect=200)

    return report


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["ok"] else 1)
