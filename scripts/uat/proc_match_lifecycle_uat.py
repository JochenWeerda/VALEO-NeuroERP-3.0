"""DOM-PROC-004 Beschaffungs-Match UAT (3-Wege-Match → Folgeaktion → ERS).

Treibt die öffentliche API gegen DEMO-Seed-Bestellungen: liest Match-Spine und
Rechnungsstufe, erfasst eine Folgeaktion bei Abweichung, erzeugt eine ERS-
Gutschrift für Überlieferung und räumt erzeugte Zeilen am Ende per ID auf.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Seed via
``scripts/seed_demo_procurement.py``.
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

PO_OK = "DEMO-PO-001"
PO_OVER = "DEMO-PO-002"


class UatFailure(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    token = os.getenv("VALEO_API_TOKEN", "dev-token")
    return {
        "Content-Type": "application/json",
        "X-Tenant-ID": TENANT_ID,
        "Authorization": f"Bearer {token}",
    }


def call(method: str, path: str, payload: dict[str, Any] | None = None,
         expected: set[int] | None = None) -> Any:
    expected = expected or {200, 201}
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(f"{API_BASE_URL}{path}", data=body, headers=_headers(), method=method)
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310
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


def cleanup(db, follow_up_id: str | None, ers_id: str | None) -> None:
    if follow_up_id:
        db.execute(
            text("DELETE FROM domain_einkauf.procurement_follow_up WHERE id = :id AND tenant_id = :t"),
            {"id": follow_up_id, "t": TENANT_ID},
        )
    if ers_id:
        db.execute(
            text("DELETE FROM domain_einkauf.procurement_ers_credits WHERE id = :id AND tenant_id = :t"),
            {"id": ers_id, "t": TENANT_ID},
        )
    db.commit()


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    follow_up_id: str | None = None
    ers_id: str | None = None

    print(f"DOM-PROC-004 Match-UAT gegen {API_BASE_URL} (execute={execute})")

    m1 = call("GET", f"/api/v1/procurement/match/three-way?bestellung={PO_OK}")
    expect(m1.get("found") is True, f"{PO_OK} gefunden")
    expect(m1["summary"]["drei_wege_abgeglichen"] is True, f"{PO_OK} 3-Wege abgeglichen")
    evidence["po001_geliefert_wert"] = m1["three_way"]["geliefert_wert"]

    m2 = call("GET", f"/api/v1/procurement/match/three-way?bestellung={PO_OVER}")
    expect(m2.get("found") is True, f"{PO_OVER} gefunden")
    expect(m2["summary"]["hat_abweichung"] is True, f"{PO_OVER} Mengenabweichung (überliefert)")
    preview = m2.get("ers_preview") or {}
    expect(preview.get("berechtigt") is True and preview.get("betrag_netto") == 960.0,
           f"{PO_OVER} ERS-Vorschau 960 € (2 t × 480 €)")
    evidence["po002_ers_preview"] = preview.get("betrag_netto")

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    fu = call("POST", "/api/v1/procurement/match/follow-up", {
        "bestellnummer": PO_OVER,
        "action_type": "reklamation",
        "grund": "UAT: Überlieferung Raps 22/20 t",
        "ausnahme_code": "mengenabweichung",
    })
    follow_up_id = fu.get("id")
    expect(follow_up_id, "Folgeaktion Reklamation erfasst")

    ers = call("POST", "/api/v1/procurement/match/ers", {
        "bestellnummer": PO_OVER,
        "grund": "UAT ERS Gutschrift Überlieferung",
    })
    ers_id = ers.get("id")
    expect(ers_id and ers.get("betrag_netto") == 960.0, "ERS-Gutschrift 960 € erzeugt")
    evidence["ers_nummer"] = ers.get("gutschrift_nummer")

    db = SessionLocal()
    try:
        cleanup(db, follow_up_id, ers_id)
        print("  ✓ UAT-Zeilen bereinigt")
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
