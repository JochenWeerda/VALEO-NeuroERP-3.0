"""DOM-FIN-004 OP-Lebenszyklus UAT (Aging → Mahnlauf → Zahlungseingang →
Periodenabschluss → DATEV).

Treibt die öffentliche API gegen die DEMO-Finance-Seed: OP-Aging, Mahnkandidaten,
Zahlungseingang/Auszifferung, Periodenabschlussreife und DATEV-Export. Mutierte
Seed-Zeilen werden am Ende per DB zurückgesetzt.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Seed via
``scripts/seed_demo_finance.py``.
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

PAY_OP = "DEMO-RE-100"   # 5000, überfällig


class UatFailure(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    token = os.getenv("VALEO_API_TOKEN", "dev-token")
    return {"Content-Type": "application/json", "X-Tenant-ID": TENANT_ID, "Authorization": f"Bearer {token}"}


def call(method: str, path: str, payload: dict[str, Any] | None = None, expected: set[int] | None = None) -> Any:
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
        raise UatFailure(f"{method} {path} → HTTP {status}: {raw}")
    return json.loads(raw) if raw else None


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise UatFailure(f"Assertion fehlgeschlagen: {msg}")
    print(f"  ✓ {msg}")


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    print(f"DOM-FIN-004 OP-Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    # 1) OP-Aging
    op = call("GET", "/api/v1/finance/offene-posten?typ=alle")
    expect(op["summary"]["anzahl"] >= 4, "OP-Aging listet ≥ 4 Posten")
    evidence["summe_offen"] = op["summary"]["summe_offen"]

    # 2) Mahnkandidaten
    cand = call("GET", "/api/v1/finance/mahnlauf/candidates")["items"]
    expect(len(cand) >= 1, "Mindestens ein Mahnkandidat")

    # 3) DATEV-Export
    datev = call("GET", "/api/v1/finance/datev-export?typ=alle")
    expect(datev["zeilen"] >= 4 and "Soll/Haben" in datev["csv"], "DATEV-Buchungsstapel erzeugt")
    evidence["datev_zeilen"] = datev["zeilen"]

    # 4) Periodenabschluss-Reife
    per = call("GET", "/api/v1/finance/perioden")["items"]
    expect(any(not p["abschlussreif"] for p in per), "Mind. eine Periode nicht abschlussreif (offene OP)")

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    db = SessionLocal()
    try:
        # 5) Zahlungseingang voll ausziffern
        pay = call("POST", "/api/v1/finance/zahlungseingang", {"rechnungsnr": PAY_OP, "betrag": 5000})
        expect(pay["voll_ausgeziffert"] is True and pay["op_status"] == "ausgeziffert",
               f"{PAY_OP} voll ausgeziffert")

        # 6) Erneute Zahlung → 422
        again = call("POST", "/api/v1/finance/zahlungseingang", {"rechnungsnr": PAY_OP, "betrag": 1}, expected={200, 422})
        expect(again.get("status") == 422, "Erneute Auszifferung blockiert (422)")

        print("\nUAT bestanden — setze Seed zurück …")
        return {"status": "passed", **evidence}
    finally:
        db.execute(text("DELETE FROM domain_shared.op_auszifferungen WHERE rechnungsnr = :r AND tenant_id = :t"),
                   {"r": PAY_OP, "t": TENANT_ID})
        db.execute(text("UPDATE domain_erp.offene_posten SET offen = 5000, op_status = 'offen' "
                        "WHERE rechnungsnr = :r AND tenant_id = :t"), {"r": PAY_OP, "t": TENANT_ID})
        db.commit()
        db.close()
        print("  ✓ Seed zurückgesetzt (OP wieder offen)")


def main() -> None:
    ap = argparse.ArgumentParser(description="DOM-FIN-004 OP-Lebenszyklus UAT")
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
