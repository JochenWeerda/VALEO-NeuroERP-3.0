"""FEED-CHAIN-001 Produktion→Charge-Durchstich UAT (Mischfutter).

Prüft die öffentliche API: Rezept wählen, Produktionsauftrag anlegen, freigeben
(Verbrauchs-Snapshot + Bestandsabzug), fertig melden (Fertigwaren-Charge in
``domain_ops.ops_chargen`` mit Mischprotokoll), Trace auflösen. Räumt erzeugte
Zeilen per SQL auf (inkl. Bestandsrückgabe über den Snapshot).

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000, Alembic
``feed_chain_verbrauch_20260612``; mindestens ein aktives Rezept mit Komponenten
und ausreichend Komponentenbestand (sonst FAILED mit fachlicher Meldung).
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

# Windows-Konsole läuft oft mit cp1252 — UTF-8 erzwingen, damit ✓ druckbar ist.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

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


def cleanup(db, auftrag_id: str, charge_id: str | None, verbrauch: list[dict] | None) -> None:
    """UAT-Spuren entfernen; Bestandsabzug über den Snapshot zurückgeben."""
    for row in verbrauch or []:
        if row.get("einzelfutter_id"):
            db.execute(
                text(
                    "UPDATE domain_shared.futtermittel_einzelfutter "
                    "SET verfuegbar_t = verfuegbar_t + :m WHERE id = :i"
                ),
                {"m": row["menge_t"], "i": row["einzelfutter_id"]},
            )
    if charge_id:
        db.execute(text("DELETE FROM domain_ops.ops_chargen WHERE id = :i"), {"i": charge_id})
    db.execute(
        text(
            "DELETE FROM domain_shared.futtermittel_produktionsauftraege "
            "WHERE id = :i AND tenant_id = :t"
        ),
        {"i": auftrag_id, "t": TENANT_ID},
    )
    db.commit()


def run(execute: bool) -> dict[str, Any]:
    evidence: dict[str, Any] = {}

    print(f"FEED-CHAIN-001 Produktions-Ketten-UAT gegen {API_BASE_URL} (execute={execute})")

    rezepte = call("GET", "/api/v1/produktion/mischfutter/rezepte", None, expected={200})
    expect(isinstance(rezepte, list), "GET /produktion/mischfutter/rezepte liefert Liste")
    kandidaten = [r for r in rezepte if r.get("komponenten")]
    expect(bool(kandidaten), "Mindestens ein Rezept mit Komponenten vorhanden")
    rezept = kandidaten[0]
    evidence["rezept"] = {"id": rezept["id"], "name": rezept["name"]}

    verfuegbarkeit = call("GET", "/api/v1/produktion/mischfutter/verfuegbarkeit", None, expected={200})
    expect(isinstance(verfuegbarkeit, list), "GET /verfuegbarkeit liefert Liste")
    evidence["komponenten_im_bestand"] = len(verfuegbarkeit)

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    chargen_id = f"UAT-MF-{uuid.uuid4().hex[:8].upper()}"
    auftrag = call(
        "POST",
        "/api/v1/produktion/mischfutter/auftrag",
        {"rezept_id": rezept["id"], "menge_t": 0.5, "chargen_id": chargen_id,
         "bemerkung": "FEED-CHAIN-001 UAT"},
        expected={201},
    )
    auftrag_id = str(auftrag.get("id", ""))
    expect(bool(auftrag_id), "Produktionsauftrag angelegt (201)")
    evidence["auftrag_id"] = auftrag_id
    evidence["chargen_id"] = chargen_id

    charge_id: str | None = None
    verbrauch: list[dict] | None = None
    db = SessionLocal()
    try:
        freigegeben = call(
            "PATCH",
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            {"status": "freigegeben", "freigegeben_von": "uat"},
            expected={200},
        )
        verbrauch = freigegeben.get("verbrauch") or []
        expect(bool(verbrauch), "Freigabe persistiert Verbrauchs-Snapshot")
        expect(freigegeben.get("bestands_abzug_erfolgt") is True, "Bestandsabzug erfolgt")

        call(
            "PATCH",
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            {"status": "in_produktion"},
            expected={200},
        )
        fertig = call(
            "PATCH",
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            {"status": "fertig"},
            expected={200},
        )
        charge_id = fertig.get("charge_id")
        expect(bool(charge_id), "fertig erzeugt Fertigwaren-Charge (charge_id gesetzt)")

        charge = call("GET", f"/api/v1/chargen/{charge_id}", None, expected={200})
        expect(charge.get("chargenId") == chargen_id, "Charge trägt die Auftrags-chargen_id")
        expect(bool(charge.get("rohstoffe")), "Charge enthält Mischprotokoll (rohstoffe)")
        expect(
            (charge.get("produktionsprozess") or {}).get("produktionsauftrag_id") == auftrag_id,
            "Charge referenziert den Produktionsauftrag",
        )

        trace = call(
            "GET",
            f"/api/v1/produktion/mischfutter/auftraege/{chargen_id}/trace",
            None,
            expected={200},
        )
        expect(trace.get("kette_geschlossen") is True, "Trace: Kette geschlossen")
        expect(len(trace.get("komponenten") or []) >= 1, "Trace listet Komponenten")
        evidence["charge_id"] = charge_id

        call(
            "PATCH",
            f"/api/v1/produktion/mischfutter/auftrag/{auftrag_id}/status",
            {"status": "storniert"},
            expected={409},
        )
        print("  ✓ Storno nach fertig → 409 (erwartet, kein Übergang)")
    finally:
        cleanup(db, auftrag_id, charge_id, verbrauch)
        print("  ✓ UAT-Spuren bereinigt (Auftrag, Charge, Bestandsrückgabe)")
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
