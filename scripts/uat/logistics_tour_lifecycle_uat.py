"""LOG-LIFE-001 Tour-/Stopp-Storno UAT (fail-closed).

Prüft die öffentliche API: Tour anlegen, Stopp stornieren, Tour stornieren,
Idempotenz (409 bei erneutem Storno). Räumt erzeugte Zeilen per SQL auf.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Schema
``domain_logistics`` (Alembic ``log_logistics_core_20260612``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.database import SessionLocal  # noqa: E402

TENANT_ID = os.getenv("VALEO_UAT_TENANT_ID", "00000000-0000-0000-0000-000000000001")
API_BASE_URL = os.getenv("VALEO_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = float(os.getenv("VALEO_UAT_TIMEOUT_SECONDS", "60"))


class UatFailure(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    token = os.getenv("VALEO_API_TOKEN", "dev-token")
    return {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "Authorization": f"Bearer {token}",
    }


def call(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    expected: set[int] | None = None,
) -> Any:
    expected = expected or {200, 201}
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"{API_BASE_URL}{path}", data=body, headers=_headers(), method=method)
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310
            status, raw = resp.status, resp.read().decode("utf-8")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        if exc.code in expected:
            try:
                return json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return {"_raw": raw, "_http_status": exc.code}
        raise UatFailure(f"{method} {path} → HTTP {exc.code}: {raw}") from exc
    except URLError as exc:
        raise UatFailure(f"{method} {path} failed: {exc}") from exc
    if status not in expected:
        raise UatFailure(f"{method} {path} → HTTP {status}, erwartet {sorted(expected)}: {raw}")
    return json.loads(raw) if raw else None


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise UatFailure(f"Assertion fehlgeschlagen: {msg}")
    print(f"  ✓ {msg}")


def cleanup_tour(db, tour_id: str) -> None:
    db.execute(text("DELETE FROM domain_logistics.tour_events WHERE tour_id = :id"), {"id": tour_id})
    db.execute(text("DELETE FROM domain_logistics.tour_stops WHERE tour_id = :id"), {"id": tour_id})
    db.execute(
        text("DELETE FROM domain_logistics.tours WHERE id = :id AND tenant_id = :t"),
        {"id": tour_id, "t": TENANT_ID},
    )
    db.commit()


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    tour_id: str | None = None

    print(f"LOG-LIFE-001 Tour-Storno-UAT gegen {API_BASE_URL} (execute={execute})")

    listed = call("GET", "/api/v1/logistik/tours", None, expected={200})
    expect(isinstance(listed, list), "GET /logistik/tours liefert Liste")
    evidence["tour_count"] = len(listed)

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    vehicle_id = f"UAT-LOG-LIFE-{uuid.uuid4().hex[:10]}"
    created = call(
        "POST",
        "/api/v1/logistik/tours",
        {
            "vehicle_id": vehicle_id,
            "driver_id": "uat-driver",
            "status": "GEPLANT",
            "notes": "LOG-LIFE-001 UAT",
            "stops": [{"address": "UAT-Stopp 1", "stop_order": 0}],
        },
        expected={201},
    )
    tour_id = str(created.get("id", ""))
    expect(bool(tour_id), "Tour angelegt (201)")
    evidence["tour_id"] = tour_id

    stops = created.get("stops") or []
    expect(len(stops) >= 1, "Mindestens ein Stopp in Create-Response")
    stop_id = str(stops[0].get("id", ""))
    expect(bool(stop_id), "Stopp-ID bekannt")
    evidence["stop_id"] = stop_id

    detail = call("GET", f"/api/v1/logistik/tours/{tour_id}", None, expected={200})
    expect((detail.get("status") or "").upper() == "GEPLANT", "Tour ist GEPLANT")

    stopped = call(
        "POST",
        f"/api/v1/logistik/tours/{tour_id}/stops/{stop_id}/cancel",
        {"grund": "UAT Stopp"},
        expected={200},
    )
    expect((stopped.get("status") or "").upper() == "STORNIERT", "Stopp storniert")

    cancelled = call(
        "POST",
        f"/api/v1/logistik/tours/{tour_id}/cancel",
        {"grund": "UAT Tour"},
        expected={200},
    )
    expect((cancelled.get("status") or "").upper() == "STORNIERT", "Tour storniert")
    expect("[STORNO:" in (cancelled.get("notes") or ""), "Tour-Notiz enthält STORNO-Marker")

    call(
        "POST",
        f"/api/v1/logistik/tours/{tour_id}/cancel",
        {"grund": "nochmal"},
        expected={409},
    )
    print("  ✓ Erneutes Tour-Storno → 409 (erwartet)")

    db = SessionLocal()
    try:
        cleanup_tour(db, tour_id)
        print("  ✓ UAT-Tour bereinigt")
    finally:
        db.close()

    return {"status": "passed", **evidence}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Mutationen ausführen und aufräumen")
    args = parser.parse_args()
    try:
        result = run(execute=args.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except UatFailure as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
