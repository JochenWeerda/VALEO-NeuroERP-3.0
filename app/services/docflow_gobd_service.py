"""GoBD-Exportpaket & DMS-/Paperless-Liveprobe (DOM-DOC-004.4).

Bündelt je Vorgang ein revisionssicheres GoBD-Exportpaket (Manifest mit Artefakt-
Hashes, Vorgangskette, Buchungen, Followups + Prüfsumme über die Artefakt-Hashes)
und vermerkt den Export am Header (`exported_at`/`exported_by`). Zusätzlich eine
tolerante Liveprobe gegen das DMS (Paperless-ngx) — fehlt die Konfiguration oder ist
der Dienst nicht erreichbar, wird das ehrlich als Gate ausgewiesen (kein Schein-OK).
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.docflow_evidence_service import DocflowEvidenceService

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def build_gobd_manifest(evidence: dict, exported_at: str, exported_by: str) -> dict:
    """Reines GoBD-Manifest aus der Evidence-Sicht (ohne DB) — testbar.

    Prüfsumme = SHA-256 über die sortierten Artefakt-Hashes (Manifest-Integrität)."""
    artefakte = evidence.get("artefakte", []) or []
    hashes = sorted(a.get("hash") or "" for a in artefakte)
    pruefsumme = hashlib.sha256("|".join(hashes).encode("utf-8")).hexdigest()
    revisionssicher = bool(artefakte) and all(a.get("hash") for a in artefakte)
    return {
        "vorgang": evidence.get("doc_number"),
        "doc_type": evidence.get("doc_type"),
        "status": evidence.get("status"),
        "version": evidence.get("version"),
        "exportiert_am": exported_at,
        "exportiert_von": exported_by,
        "artefakte": [
            {"datei": a.get("datei"), "sha256": a.get("hash"), "typ": a.get("typ")}
            for a in artefakte
        ],
        "anzahl_artefakte": len(artefakte),
        "vorgangskette": len(evidence.get("vorgangskette", []) or []),
        "buchungen": len(evidence.get("buchungen", []) or []),
        "offene_luecken": len(evidence.get("luecken", []) or []),
        "revisionssicher": revisionssicher,
        "pruefsumme_sha256": pruefsumme,
    }


class DocflowGobdService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def export_package(self, doc: str, bediener: str = "KIM") -> dict[str, Any]:
        evidence = DocflowEvidenceService(self.db, self.tenant_id).evidence(doc)
        if not evidence.get("found"):
            return {"found": False, "detail": evidence.get("detail", "Dokument nicht gefunden.")}
        exported_at = datetime.now(timezone.utc).isoformat()
        manifest = build_gobd_manifest(evidence, exported_at, bediener)
        # Export am Header vermerken (schließt die „kein GoBD-Export"-Lücke).
        self.db.execute(
            text("UPDATE domain_docflow.document_headers SET exported_at = now(), exported_by = :by "
                 "WHERE (id::text = :v OR doc_number = :v) AND tenant_id = :t"),
            {"by": bediener, "v": doc, "t": self.tenant_id},
        )
        self.db.commit()
        return {"found": True, "manifest": manifest}

    def paperless_probe(self) -> dict[str, Any]:
        """Tolerante DMS-/Paperless-Erreichbarkeitsprobe — ehrlich gegated."""
        url = (os.getenv("PAPERLESS_URL") or os.getenv("PAPERLESS_NGX_URL")
               or os.getenv("DMS_BASE_URL") or os.getenv("DMS_ADAPTER_URL") or "").rstrip("/")
        if not url:
            return {"konfiguriert": False, "erreichbar": False, "url": None,
                    "detail": "Keine DMS-/Paperless-URL konfiguriert (PAPERLESS_URL/DMS_BASE_URL)."}
        try:
            req = Request(url, method="GET", headers={"User-Agent": "valeo-gobd-probe"})
            with urlopen(req, timeout=4) as resp:  # noqa: S310 - konfiguriertes internes Ziel
                code = resp.status
            return {"konfiguriert": True, "erreichbar": 200 <= code < 500, "url": url,
                    "detail": f"HTTP {code}"}
        except HTTPError as exc:
            # Auch 401/403/404 belegen Erreichbarkeit des Dienstes.
            return {"konfiguriert": True, "erreichbar": True, "url": url, "detail": f"HTTP {exc.code}"}
        except (URLError, OSError) as exc:
            return {"konfiguriert": True, "erreichbar": False, "url": url, "detail": f"nicht erreichbar: {exc}"}
