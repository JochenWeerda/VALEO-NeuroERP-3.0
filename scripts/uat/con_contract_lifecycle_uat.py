"""DOM-CON-004 Kontrakt-Lebenszyklus UAT (Fixierung → Engagement → Settlement → Storno).

Treibt die öffentliche API gegen die DEMO-Seed-Kontrakte: liest den Fixierungs-
Arbeitsraum samt MATIF-Bewertung, legt eine Teilfixierung an, prüft Engagement und
Kontraktmahnung, übergibt eine Bewegung an die Abrechnung, prüft die Storno-Sperre
gebuchter Bewegungen und storniert anschließend die Test-Fixierung. Alle erzeugten
Zeilen werden am Ende per recorded ID direkt entfernt; mutierte Seed-Zeilen werden
zurückgesetzt.

Mutiert nur mit ``--execute``. Voraussetzung: Backend auf :8000, Seed via
``scripts/seed_demo_contracts.py``.
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

MATIF_CONTRACT = "DEMO-KT-004"      # MATIF-Verkauf, 300/500 fixiert
OVERDUE_CONTRACT = "DEMO-KT-002"    # überfällig, untererfüllt
SETTLE_CONTRACT = "DEMO-KT-001"     # 2 offene Bewegungen


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
    created_fixing_id: str | None = None
    created_reminder = False

    print(f"DOM-CON-004 Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    # 1) Fixierungs-Arbeitsraum + MATIF-Bewertung (read)
    ws = call("GET", f"/api/v1/contracts/fixing/workspace?kontrakt={MATIF_CONTRACT}")
    expect(ws.get("found") is True, f"{MATIF_CONTRACT} Workspace gefunden")
    s = ws["summary"]
    expect(s["fixiert"] == 300.0 and s["menge_kontrakt"] == 500.0, "Baseline 300/500 fixiert")
    expect(s["bewertbar"] and s["bewertung_fixiert_eur"] is not None, "Mark-to-Market bewertbar")
    evidence["bewertung_fixiert_eur"] = s["bewertung_fixiert_eur"]
    evidence["marktwert_offen_eur"] = s["marktwert_offen_eur"]

    # 2) Engagement (read)
    eng = call("GET", "/api/v1/contracts/engagement")
    arts = {a["artikel"]: a for a in eng["by_article"]}
    expect("Weizen B MATIF" in arts and arts["Weizen B MATIF"]["verkauf_offen"] == 500.0,
           "Engagement führt offenes MATIF-Verkaufsengagement (500)")
    evidence["engagement_netto"] = eng["summary"]["netto"]

    # 3) Kontraktmahnung (read)
    cands = call("GET", "/api/v1/contracts/dunning/candidates")["items"]
    by_no = {c["contract_no"]: c for c in cands}
    expect(OVERDUE_CONTRACT in by_no and by_no[OVERDUE_CONTRACT]["offen"] > 0,
           f"{OVERDUE_CONTRACT} ist Mahnkandidat (überfällig, offen)")

    # 4) Storno-Sperre: Fixierung über offene Menge → 422 (read-only Guard)
    over = call("POST", "/api/v1/contracts/fixing",
                {"kontrakt": MATIF_CONTRACT, "menge": 9999, "matifPreis": 207},
                expected={200, 422})
    expect(over.get("status") == 422, "Überfixierung wird abgelehnt (422)")

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    db = SessionLocal()
    try:
        # 5) Teilfixierung anlegen
        fix = call("POST", "/api/v1/contracts/fixing",
                   {"kontrakt": MATIF_CONTRACT, "menge": 50, "matifPreis": 207, "notiz": "UAT"})
        created_fixing_id = fix["fixing_id"]
        expect(fix["offen_nach"] == 150.0, "Fixierung 50t → offen 150")

        ws2 = call("GET", f"/api/v1/contracts/fixing/workspace?kontrakt={MATIF_CONTRACT}")
        expect(ws2["summary"]["fixiert"] == 350.0, "Workspace zeigt 350 fixiert")

        # 6) Kontraktmahnung erfassen
        rem = call("POST", "/api/v1/contracts/dunning",
                   {"kontrakt": OVERDUE_CONTRACT, "text": "UAT-Mahnung"})
        created_reminder = True
        expect(rem["mahnstufe"] == 1, "Mahnung Stufe 1 erfasst")

        # 7) Settlement-Übergabe + Storno-Sperre gebuchter Bewegung
        ho = call("POST", "/api/v1/contracts/settlement", {"kontrakt": SETTLE_CONTRACT})
        expect(ho["uebergeben"] >= 1, "Bewegung(en) an Abrechnung übergeben")
        st = call("GET", f"/api/v1/contracts/settlement/status?kontrakt={SETTLE_CONTRACT}")
        expect(st["summary"]["abgerechnet"] == 120.0, "120 t abgerechnet")
        mov_id = st["bewegungen"][0]["movement_id"]
        blocked = call("POST", f"/api/v1/contracts/movements/{mov_id}/storno",
                       {"grund": "UAT"}, expected={200, 422})
        expect(blocked.get("status") == 422, "Storno gebuchter Bewegung blockiert (422)")

        # 8) Fixierungs-Storno gibt Menge frei
        stf = call("POST", f"/api/v1/contracts/fixings/{created_fixing_id}/storno", {"grund": "UAT-Rücknahme"})
        expect(stf["frei_menge"] == 50.0, "Fixierungs-Storno gibt 50 t frei")

        print("\nUAT bestanden — räume Testdaten auf …")
        return {"status": "passed", **evidence}
    finally:
        # Cleanup: erzeugte Zeilen entfernen, mutierte Seed-Zeilen zurücksetzen.
        if created_fixing_id:
            db.execute(text("DELETE FROM domain_ops.kon_contract_fixing WHERE fixing_id = :id"),
                       {"id": created_fixing_id})
        if created_reminder:
            db.execute(text("DELETE FROM domain_ops.kon_contract_reminder WHERE text = 'UAT-Mahnung'"))
        db.execute(text(
            "UPDATE domain_ops.kon_contract_movement SET is_invoiced=false, invoice_no=NULL, "
            "settled_at=NULL WHERE invoice_no LIKE :p"), {"p": f"ABR-{SETTLE_CONTRACT}-%"})
        db.commit()
        db.close()
        print("  ✓ Testdaten entfernt / Seed zurückgesetzt")


def main() -> None:
    ap = argparse.ArgumentParser(description="DOM-CON-004 Kontrakt-Lebenszyklus UAT")
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
