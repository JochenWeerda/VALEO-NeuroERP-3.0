"""DOM-DOC-004 Nachweisraum-Lebenszyklus UAT (Evidence → Artefakt-Upload → Freigabe
→ Wiedervorlage → GoBD-Export).

Treibt die öffentliche API gegen einen vorhandenen Docflow-Vorgang: Evidence-Sicht,
Artefakt-Upload (SHA-256) + Freigabe-Transition, Wiedervorlage + Worklist, GoBD-
Exportpaket (Prüfsumme) und DMS-Probe. Erzeugte Zeilen werden per ID entfernt,
mutierte Header zurückgesetzt.

Mutiert nur mit ``--execute``. Voraussetzung: Backend :8000.
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

DOC = os.getenv("VALEO_DOC_UAT_DOC", "SIV-2026-000005")


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
    print(f"DOM-DOC-004 Nachweisraum-Lifecycle-UAT gegen {API_BASE_URL} (execute={execute})")

    # 1) Evidence-Sicht
    ev = call("GET", f"/api/v1/docflow/evidence/detail?doc={DOC}")
    expect(ev.get("found") is True, f"{DOC} Evidence gefunden")

    # 2) DMS-Probe (ehrlich gegated)
    probe = call("GET", "/api/v1/docflow/evidence/paperless-probe")
    expect("konfiguriert" in probe, "Paperless-Probe liefert ehrlichen Status")
    evidence["paperless_konfiguriert"] = probe["konfiguriert"]

    if not execute:
        print("\n(dry-run) Mutationen übersprungen — mit --execute ausführen.")
        return {"status": "passed (read-only)", **evidence}

    db = SessionLocal()
    artifact_id = None
    followup_id = None
    try:
        # 3) Artefakt-Upload + Freigabe
        up = call("POST", "/api/v1/docflow/evidence/artifacts",
                  {"doc": DOC, "fileName": "uat.pdf", "content": "UAT-Inhalt", "artifactType": "other"})
        artifact_id = up["artifact_id"]
        expect(up["version"] >= 1 and len(up["sha256"]) == 64, "Artefakt hochgeladen (SHA-256)")
        fr = call("POST", f"/api/v1/docflow/evidence/artifacts/{artifact_id}/freigabe", {"zielStatus": "freigegeben"})
        expect(fr["freigabe_status"] == "freigegeben", "Artefakt freigegeben")

        # 4) Wiedervorlage + Worklist
        wv = call("POST", "/api/v1/docflow/evidence/followups",
                  {"doc": DOC, "art": "wiedervorlage", "betreff": "UAT-Frist", "faelligAm": "2026-06-01"})
        followup_id = wv["followup_id"]
        worklist = call("GET", "/api/v1/docflow/evidence/wiedervorlagen")["items"]
        expect(any(w["followup_id"] == followup_id and w["ueberfaellig"] for w in worklist),
               "Wiedervorlage erscheint überfällig in der Worklist")

        # 5) GoBD-Exportpaket
        pkg = call("POST", "/api/v1/docflow/evidence/gobd-export", {"doc": DOC})
        m = pkg["manifest"]
        expect(len(m["pruefsumme_sha256"]) == 64 and m["anzahl_artefakte"] >= 1, "GoBD-Manifest mit Prüfsumme erzeugt")
        evidence["pruefsumme"] = m["pruefsumme_sha256"][:12]

        print("\nUAT bestanden — räume Testdaten auf …")
        return {"status": "passed", **evidence}
    finally:
        if artifact_id:
            db.execute(text("DELETE FROM domain_docflow.document_artifacts WHERE id = :id"), {"id": artifact_id})
        if followup_id:
            db.execute(text("DELETE FROM domain_docflow.document_followups WHERE id = :id"), {"id": followup_id})
        db.execute(text("UPDATE domain_docflow.document_headers SET exported_at = NULL, exported_by = NULL "
                        "WHERE doc_number = :d AND tenant_id = :t"), {"d": DOC, "t": TENANT_ID})
        db.commit()
        db.close()
        print("  ✓ Testdaten entfernt / Header zurückgesetzt")


def main() -> None:
    ap = argparse.ArgumentParser(description="DOM-DOC-004 Nachweisraum-Lebenszyklus UAT")
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
