"""DOM-SALES-004 O2C-Lebenszyklus UAT (Match → Kreditlimit → Storno-Rückfluss).

Treibt die öffentliche API gegen die DEMO-Sales-Seed: Positions-Match Auftrag↔
Lieferschein, Kreditlimit-Ampel, Lieferungs-Storno (durchgängig, Menge wird wieder
offen) inkl. Fail-closed-Guard für berechnete Lieferungen. Mutierte Seed-Zeilen
werden am Ende per DB zurückgesetzt.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Seed via
``scripts/seed_demo_sales.py``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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

ORDER = "DEMO-AUF-001"
DELIVERY = "DEMO-LS-001"


class UatFailure(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    token = os.getenv("VALEO_API_TOKEN", "dev-token")
    return {"Content-Type": "application/json", "X-Tenant-ID": TENANT_ID,
            "Authorization": f"Bearer {token}"}


def call(method: str, path: str, payload: dict[str, Any] | None = None,
         expected: set[int] | None = None) -> Any:
    expected = expected or {200, 201}
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"{API_BASE_URL}{path}", data=body, headers=_headers(), method=method)
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310 - local UAT target
            status, raw = resp.status, resp.read().decode("utf-8")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        if exc.code in expected:
            return json.loads(raw) if raw else None
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


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    print(f"DOM-SALES-004 O2C-Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    # 1) Positions-Match
    m = call("GET", f"/api/v1/sales/match?auftrag={ORDER}")
    expect(m.get("found") is True, f"{ORDER} Match gefunden")
    pos = {p["artikel_nr"]: p for p in m["positionen"]}
    expect(pos["MILCHLEISTUNG-18"]["status"] == "vollstaendig", "Pos MILCHLEISTUNG-18 vollständig (25/25)")
    expect(pos["MINERAL-RIND"]["status"] == "teilgeliefert" and pos["MINERAL-RIND"]["offen"] == 2.0,
           "Pos MINERAL-RIND teilgeliefert (3/5, 2 offen)")
    evidence["match_hat_abweichung"] = m["summary"]["hat_abweichung"]

    # 2) Kreditlimit-Ampel
    c = call("GET", f"/api/v1/sales/credit-check?auftrag={ORDER}")
    expect(c["kredit"]["ampel"] == "warnung", "Kreditlimit-Ampel = warnung")
    expect(c["kredit"]["auslastung_neu_pct"] == 86.5, "Auslastung mit Auftrag 86,5 %")
    evidence["kredit_ampel"] = c["kredit"]["ampel"]

    # 3) Storno-Guard auf berechneten Lieferschein → 422
    blocked = call("POST", f"/api/v1/sales/deliveries/{DELIVERY}/storno",
                   {"grund": "UAT"}, expected={200, 422})
    expect(blocked.get("status") == 422, "Storno berechneter Lieferung blockiert (422)")

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    db = SessionLocal()
    invoice_backup = None
    try:
        # Rechnung temporär entfernen, um den durchgängigen Storno zu zeigen.
        invoice_backup = db.execute(
            text("SELECT invoice_number FROM domain_sales.delivery_notes "
                 "WHERE delivery_note_number = :d AND tenant_id = :t"),
            {"d": DELIVERY, "t": TENANT_ID},
        ).scalar()
        db.execute(text("UPDATE domain_sales.delivery_notes SET invoice_number = NULL "
                        "WHERE delivery_note_number = :d AND tenant_id = :t"),
                   {"d": DELIVERY, "t": TENANT_ID})
        db.commit()

        # 4) Storno (durchgängig)
        st = call("POST", f"/api/v1/sales/deliveries/{DELIVERY}/storno", {"grund": "UAT-Fehllieferung"})
        expect(st["status"] == "storniert", "Lieferschein storniert")

        m2 = call("GET", f"/api/v1/sales/match?auftrag={ORDER}")
        pos2 = {p["artikel_nr"]: p for p in m2["positionen"]}
        expect(pos2["MILCHLEISTUNG-18"]["geliefert"] == 0.0 and pos2["MILCHLEISTUNG-18"]["status"] == "offen",
               "Nach Storno: MILCHLEISTUNG-18 wieder offen (0 geliefert)")

        print("\nUAT bestanden — setze Seed zurück …")
        return {"status": "passed", **evidence}
    finally:
        db.execute(text(
            "UPDATE domain_sales.delivery_notes SET status='geliefert', is_delivered=true, "
            "storno_grund=NULL, invoice_number=:inv WHERE delivery_note_number=:d AND tenant_id=:t"),
            {"inv": invoice_backup or "DEMO-RE-001", "d": DELIVERY, "t": TENANT_ID})
        db.commit()
        db.close()
        print("  ✓ Seed zurückgesetzt (Lieferschein aktiv + Rechnung)")


def main() -> None:
    ap = argparse.ArgumentParser(description="DOM-SALES-004 O2C-Lebenszyklus UAT")
    ap.add_argument("--execute", action="store_true", help="Mutationen ausführen (sonst read-only)")
    args = ap.parse_args()
    try:
        result = run(args.execute)
    except UatFailure as exc:
        print(f"\nUAT FEHLGESCHLAGEN: {exc}")
        sys.exit(1)
    print("\n" + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
