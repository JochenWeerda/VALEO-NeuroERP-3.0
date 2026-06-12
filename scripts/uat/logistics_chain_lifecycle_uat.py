"""LOG-CHAIN-001 Ketten-Lifecycle UAT (Audit Bruchstelle 2, read-heavy).

Prüft die öffentliche API entlang **Lieferschein-Ref → Tour mit Hints → Fracht simulate
→ Supply-Chain Traceability (Read) → Tour-Storno**. Räumt erzeugte Zeilen per SQL auf.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Schema ``domain_logistics``,
optional Verkaufs-Seed mit ``DEMO-LS-001`` (``scripts/seed_demo_sales.py``).
Ohne ``DEMO-LS-001``: Dry-run und ``--execute`` führen nur noch Reads aus
(Traceability-Tickets, Tourenliste) und beenden mit ``status: skipped (no DEMO-LS-001)``.
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
from urllib.parse import urlencode
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


def call_get(path: str, params: dict[str, Any] | None = None, expected: set[int] | None = None) -> Any:
    qs = urlencode({k: v for k, v in (params or {}).items() if v is not None})
    full = f"{path}?{qs}" if qs else path
    return call("GET", full, None, expected=expected)


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise UatFailure(f"Assertion fehlgeschlagen: {msg}")
    print(f"  [OK] {msg}")


def cleanup_tour(db, tour_id: str) -> None:
    db.execute(text("DELETE FROM domain_logistics.tour_events WHERE tour_id = :id"), {"id": tour_id})
    db.execute(text("DELETE FROM domain_logistics.tour_stops WHERE tour_id = :id"), {"id": tour_id})
    db.execute(
        text("DELETE FROM domain_logistics.tours WHERE id = :id AND tenant_id = :t"),
        {"id": tour_id, "t": TENANT_ID},
    )
    db.commit()


def cleanup_tariff(db, tariff_id: str) -> None:
    db.execute(
        text("DELETE FROM domain_logistics.freight_tariffs WHERE id = :id"),
        {"id": tariff_id},
    )
    db.commit()


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    print(f"LOG-CHAIN-001 Ketten-Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    tickets = call_get("/api/v1/supply-chain/traceability/tickets", {"limit": 5}, expected={200})
    expect(isinstance(tickets, dict) and "items" in tickets, "GET traceability/tickets liefert items")
    evidence["traceability_ticket_count"] = len(tickets.get("items") or [])

    listed = call("GET", "/api/v1/logistik/tours", None, expected={200})
    expect(isinstance(listed, list), "GET /logistik/tours liefert Liste")
    evidence["tour_count"] = len(listed)

    ls = call_get(
        "/api/v1/logistik/sales-delivery-note-by-ref",
        {"ref": "DEMO-LS-001"},
        expected={200, 404},
    )
    if not isinstance(ls, dict) or ls.get("delivery_note_number") != "DEMO-LS-001":
        print("\n  (skip) DEMO-LS-001 nicht gefunden — seed_demo_sales.py ausführen für volle Kette.")
        if not execute:
            return {"status": "passed (read-only, no spine)", **evidence}
        return {"status": "skipped (no DEMO-LS-001)", **evidence}

    expect(ls.get("delivery_note_number") == "DEMO-LS-001", "LS-Resolve DEMO-LS-001")
    evidence["ls_id"] = ls.get("id")

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    carrier = f"UAT-LOG-CHAIN-{uuid.uuid4().hex[:10]}"
    tariff_id: str | None = None
    tour_id: str | None = None
    db = SessionLocal()
    try:
        tcreate = call(
            "POST",
            "/api/v1/logistik/freight-tariffs",
            {
                "carrier_id": carrier,
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 12.0,
                "min_charge": 2.5,
            },
            expected={201},
        )
        tariff_id = str(tcreate.get("id", ""))
        expect(bool(tariff_id), "Fracht-Tarif angelegt")
        evidence["tariff_id"] = tariff_id

        sim = call_get(
            "/api/v1/logistik/freight-cost/simulate",
            {
                "carrier_id": carrier,
                "distance_km": 100.0,
                "weight_kg": 100.0,
                "postal_code_from": "10115",
                "postal_code_to": "20095",
            },
            expected={200},
        )
        expect(sim.get("freight_cost_eur") is not None, "Fracht simulate liefert Kosten")

        vehicle_id = f"UAT-CHAIN-TOUR-{uuid.uuid4().hex[:10]}"
        created = call(
            "POST",
            "/api/v1/logistik/tours",
            {
                "vehicle_id": vehicle_id,
                "driver_id": "uat-chain-driver",
                "status": "GEPLANT",
                "notes": "LOG-CHAIN-001 UAT",
                "stops": [
                    {
                        "address": "UAT Ketten-Stopp",
                        "stop_order": 0,
                        "delivery_note_ref": "DEMO-LS-001",
                    }
                ],
            },
            expected={201},
        )
        tour_id = str(created.get("id", ""))
        expect(bool(tour_id), "Tour mit LS-Ref angelegt")
        evidence["tour_id"] = tour_id

        detail = call_get(
            f"/api/v1/logistik/tours/{tour_id}",
            {"include_delivery_hints": "true"},
            expected={200},
        )
        stops = detail.get("stops") or []
        expect(len(stops) >= 1, "Tour-Detail hat Stopps")
        hint = stops[0].get("delivery_note_hint")
        expect(hint is not None, "delivery_note_hint gesetzt")
        expect(
            hint.get("delivery_note_number") == "DEMO-LS-001",
            "Hint zeigt DEMO-LS-001",
        )

        cancelled = call(
            "POST",
            f"/api/v1/logistik/tours/{tour_id}/cancel",
            {"grund": "UAT LOG-CHAIN-001"},
            expected={200},
        )
        expect((cancelled.get("status") or "").upper() == "STORNIERT", "Tour storniert")

        if tariff_id:
            cleanup_tariff(db, tariff_id)
            print("  [OK] Fracht-Tarif bereinigt")
        if tour_id:
            cleanup_tour(db, tour_id)
            print("  [OK] UAT-Tour bereinigt")
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
