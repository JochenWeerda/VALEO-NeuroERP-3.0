"""DOM-CRM-004 Kundenstamm-Lebenszyklus UAT (Dubletten → Ownership → Wiedervorlagen).

Treibt die öffentliche CRM-004-API: Dubletten-Cluster, Merge-Vorschau (read-only),
Ownership-Worklist, Wiedervorlagen-Worklist. Mit ``--execute``: temporäre
Wiedervorlage anlegen/erledigen (Cleanup per DELETE) und Ownership-Zuweisung
mit DB-Rollback am Ende.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Kunden-Stammdaten.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
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
UAT_KUNDE = os.getenv("VALEO_CRM_UAT_KUNDE", "GAP00001")


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
    print(f"  OK {msg}")


def _cleanup_kontakt(db, kontakt_id: str | None) -> None:
    if not kontakt_id:
        return
    db.execute(
        text("DELETE FROM public.kunden_kontakte WHERE id = :id AND tenant_id = :t"),
        {"id": kontakt_id, "t": TENANT_ID},
    )
    db.commit()


def _restore_ownership(db, kunden_nr: str, sales_rep: str | None, dispatcher: str | None) -> None:
    db.execute(
        text(
            "INSERT INTO public.kunden_crm360 (kunden_nr) VALUES (:k) "
            "ON CONFLICT (kunden_nr) DO NOTHING"
        ),
        {"k": kunden_nr},
    )
    db.execute(
        text(
            "UPDATE public.kunden_crm360 SET sales_rep_vb = :sr, dispatcher_disp = :dp, "
            "updated_at = now() WHERE kunden_nr = :k"
        ),
        {"sr": sales_rep, "dp": dispatcher, "k": kunden_nr},
    )
    db.commit()


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    cleanup_kontakt_id: str | None = None
    ownership_backup: dict[str, Any] | None = None
    db = SessionLocal()

    print(f"DOM-CRM-004 Kundenstamm-Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    try:
        dup = call("GET", "/api/v1/crm/duplicates?limit=20")
        groups = dup.get("groups") or dup.get("items") or []
        expect(isinstance(groups, list), "Dubletten-API liefert Gruppenliste")
        evidence["duplicate_groups"] = len(groups)
        if groups:
            g0 = groups[0]
            members = g0.get("mitglieder") or g0.get("members") or []
            expect(len(members) >= 2, "Erstes Dubletten-Cluster hat mindestens 2 Mitglieder")
            if len(members) >= 2:
                preview = call(
                    "POST",
                    "/api/v1/crm/duplicates/merge-preview",
                    {
                        "masterNr": members[0].get("kunden_nr") or members[0].get("nr"),
                        "duplicateNr": members[1].get("kunden_nr") or members[1].get("nr"),
                    },
                )
                expect(preview.get("ok") is True or "master" in preview, "Merge-Vorschau erfolgreich")

        unassigned = call("GET", "/api/v1/crm/ownership/unassigned?limit=5")
        items = unassigned.get("items") or []
        expect(isinstance(items, list), "Ownership-Worklist ist Liste")
        expect("total" in unassigned, "Ownership-Worklist hat total")
        evidence["unassigned_total"] = unassigned.get("total")

        wv = call("GET", "/api/v1/crm/kunden-kontakte/wiedervorlagen?tage=365")
        wv_items = wv if isinstance(wv, list) else wv.get("items") or []
        expect(isinstance(wv_items, list), "Wiedervorlagen-API ist Liste")
        evidence["wiedervorlagen_offen"] = len(wv_items)

        if not execute:
            print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
            return {"status": "dry_run", **evidence}

        before = call("GET", f"/api/v1/crm/{UAT_KUNDE}/ownership")
        ownership_backup = {
            "kunden_nr": UAT_KUNDE,
            "sales_rep": before.get("sales_rep"),
            "dispatcher": before.get("dispatcher"),
        }
        assigned = call(
            "PUT",
            f"/api/v1/crm/{UAT_KUNDE}/ownership",
            {
                "salesRep": "UAT-AD",
                "dispatcher": "UAT-ID",
                "grund": "DOM-CRM-004 UAT",
                "bediener": "uat-script",
            },
        )
        expect(assigned.get("ok") is True, f"Ownership {UAT_KUNDE} gesetzt")
        hist = call("GET", f"/api/v1/crm/{UAT_KUNDE}/ownership/history")
        expect(len(hist.get("items") or []) >= 1, "Ownership-Historie protokolliert")

        created = call(
            "POST",
            "/api/v1/crm/kunden-kontakte",
            {
                "kunden_nr": UAT_KUNDE,
                "art": "telefon",
                "kurzinfo": "DOM-CRM-004 UAT WV",
                "wiedervorlage": str(date.today()),
                "bediener": "uat-script",
            },
        )
        cleanup_kontakt_id = str(created.get("id") or "")
        expect(bool(cleanup_kontakt_id), "UAT-Wiedervorlage angelegt")

        wv_after = call("GET", "/api/v1/crm/kunden-kontakte/wiedervorlagen?tage=365")
        wv_after_items = wv_after if isinstance(wv_after, list) else wv_after.get("items") or []
        expect(any(str(x.get("id")) == cleanup_kontakt_id for x in wv_after_items), "WV in Worklist sichtbar")

        done = call(
            "POST",
            f"/api/v1/crm/kunden-kontakte/{cleanup_kontakt_id}/erledigt",
            {"ergebnis": "UAT Serviceabschluss"},
        )
        expect(done.get("erledigt") is True, "Wiedervorlage erledigt mit Ergebnis")
        evidence["wiedervorlage_erledigt"] = True

        print("\nOK DOM-CRM-004 Kundenstamm-Lifecycle-UAT passed")
        return {"status": "passed", **evidence}
    finally:
        if execute:
            _cleanup_kontakt(db, cleanup_kontakt_id)
            if ownership_backup:
                _restore_ownership(
                    db,
                    ownership_backup["kunden_nr"],
                    ownership_backup.get("sales_rep"),
                    ownership_backup.get("dispatcher"),
                )
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="DOM-CRM-004 Kundenstamm UAT")
    parser.add_argument("--execute", action="store_true", help="Mutationen ausführen (mit Cleanup)")
    parser.add_argument("--json", action="store_true", help="JSON-Evidenz auf stdout")
    args = parser.parse_args()
    try:
        result = run(execute=args.execute)
    except UatFailure as exc:
        print(f"\nFAIL {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
