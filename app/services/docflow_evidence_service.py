"""Dokument-Nachweisraum (DOM-DOC-004) — GoBD-Artefakt-/Vorgangs-Sicht.

Read-only Sicht auf den bestehenden Docflow (domain_docflow): je Dokument die
revisionssichere Artefakt-Ablage (mit SHA-256-Hash), die Vorgangskette
(document_links), Buchungsbezug (document_postings) und der Druck-/Export-Audit
— plus **Lücken** (kein Artefakt, Artefakt ohne Hash, nicht gebucht/exportiert).
Macht die GoBD-Nachweiskette durchgängig prüfbar. Keine Schreibvorgänge.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# doc_types, für die eine Buchung GoBD-relevant erwartet wird.
_BOOKED_EXPECTED = {"sales_invoice", "purchase_invoice", "invoice"}


def evaluate_gaps(header: dict, artifacts: list[dict], postings: list[dict]) -> list[dict]:
    """Reine GoBD-Lücken-Bewertung eines Dokuments (ohne DB) — testbar."""
    gaps: list[dict] = []
    if not artifacts:
        gaps.append({"schwere": "warnung", "text": "Kein Artefakt hinterlegt (keine revisionssichere Ablage)."})
    else:
        if any(not a.get("content_hash_sha256") for a in artifacts):
            gaps.append({"schwere": "warnung", "text": "Artefakt ohne SHA-256-Hash (nicht revisionssicher)."})
        if any(not a.get("storage_key") for a in artifacts):
            gaps.append({"schwere": "info", "text": "Artefakt ohne Ablageort (storage_key fehlt)."})
    doc_type = (header.get("doc_type") or "").lower()
    status = (header.get("status") or "").lower()
    if doc_type in _BOOKED_EXPECTED and status not in ("reversed", "cancelled", "storniert") and not postings:
        gaps.append({"schwere": "info", "text": "Rechnung ohne Buchungsbezug (nicht gebucht)."})
    if doc_type in _BOOKED_EXPECTED and not header.get("exported_at"):
        gaps.append({"schwere": "info", "text": "Noch kein GoBD-Export vermerkt."})
    return gaps


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


class DocflowEvidenceService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _header(self, doc: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT id, doc_type, doc_number, status, source_system, source_ref, "
                "customer_id, supplier_id, total_gross, currency, version, document_date, "
                "printed_at, printed_by, print_count, exported_at, exported_by, created_at "
                "FROM domain_docflow.document_headers "
                "WHERE tenant_id = :t AND (id::text = :v OR doc_number = :v) AND deleted_at IS NULL LIMIT 1"
            ),
            {"t": self.tenant_id, "v": doc},
        ).mappings().first()
        return dict(r) if r else None

    def _artifacts(self, header_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by "
                 "FROM domain_docflow.document_artifacts WHERE header_id = :h AND tenant_id = :t ORDER BY created_at"),
            {"h": header_id, "t": self.tenant_id},
        ).mappings().all()
        return [{"id": str(r["id"]), "typ": r["artifact_type"],
                 "hash": r["content_hash_sha256"], "storage_key": r["storage_key"],
                 "content_hash_sha256": r["content_hash_sha256"],
                 "datei": r["file_name"], "created_at": _iso(r["created_at"]), "created_by": r["created_by"]}
                for r in rows]

    def _links(self, header_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT l.relation_type, l.from_header_id, l.to_header_id, "
                "hf.doc_number AS from_nr, hf.doc_type AS from_typ, "
                "ht.doc_number AS to_nr, ht.doc_type AS to_typ "
                "FROM domain_docflow.document_links l "
                "LEFT JOIN domain_docflow.document_headers hf ON hf.id = l.from_header_id "
                "LEFT JOIN domain_docflow.document_headers ht ON ht.id = l.to_header_id "
                "WHERE l.tenant_id = :t AND (l.from_header_id::text = :h OR l.to_header_id::text = :h)"
            ),
            {"t": self.tenant_id, "h": header_id},
        ).mappings().all()
        out = []
        for r in rows:
            richtung = "ausgehend" if str(r["from_header_id"]) == header_id else "eingehend"
            out.append({"relation": r["relation_type"], "richtung": richtung,
                        "partner_nr": (r["to_nr"] if richtung == "ausgehend" else r["from_nr"]),
                        "partner_typ": (r["to_typ"] if richtung == "ausgehend" else r["from_typ"])})
        return out

    def _postings(self, header_id: str) -> list[dict]:
        rows = self.db.execute(
            text("SELECT posting_type, journal_entry_id, amount, currency, posted_at, posted_by "
                 "FROM domain_docflow.document_postings WHERE header_id = :h AND tenant_id = :t ORDER BY posted_at"),
            {"h": header_id, "t": self.tenant_id},
        ).mappings().all()
        return [{"typ": r["posting_type"], "journal_entry_id": str(r["journal_entry_id"]) if r["journal_entry_id"] else None,
                 "betrag": float(r["amount"]) if r["amount"] is not None else None,
                 "waehrung": r["currency"], "posted_at": _iso(r["posted_at"]), "posted_by": r["posted_by"]}
                for r in rows]

    def evidence(self, doc: str) -> dict:
        header = self._header(doc)
        if not header:
            return {"found": False, "detail": "Dokument nicht gefunden."}
        hid = str(header["id"])
        artifacts = self._artifacts(hid)
        links = self._links(hid)
        postings = self._postings(hid)
        gaps = evaluate_gaps(header, artifacts, postings)
        return {
            "found": True,
            "id": hid,
            "doc_number": header["doc_number"],
            "doc_type": header["doc_type"],
            "status": header["status"],
            "version": header["version"],
            "audit": {
                "printed_at": _iso(header["printed_at"]), "printed_by": header["printed_by"],
                "print_count": header["print_count"],
                "exported_at": _iso(header["exported_at"]), "exported_by": header["exported_by"],
                "created_at": _iso(header["created_at"]),
                "source_system": header["source_system"], "source_ref": header["source_ref"],
            },
            "artefakte": artifacts,
            "vorgangskette": links,
            "buchungen": postings,
            "luecken": gaps,
            "summary": {
                "artefakte": len(artifacts),
                "revisionssicher": bool(artifacts) and all(a.get("hash") for a in artifacts),
                "verkettet": len(links),
                "gebucht": bool(postings),
                "offene_luecken": len(gaps),
            },
        }

    def list_documents(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                """
                SELECT h.doc_number, h.doc_type, h.status, h.document_date, h.total_gross,
                       (SELECT count(*) FROM domain_docflow.document_artifacts a
                        WHERE a.header_id = h.id AND a.tenant_id = h.tenant_id) AS n_art,
                       EXISTS(SELECT 1 FROM domain_docflow.document_artifacts a
                              WHERE a.header_id = h.id AND a.tenant_id = h.tenant_id
                              AND (a.content_hash_sha256 IS NULL OR a.content_hash_sha256 = '')) AS art_ohne_hash,
                       EXISTS(SELECT 1 FROM domain_docflow.document_postings p
                              WHERE p.header_id = h.id AND p.tenant_id = h.tenant_id) AS gebucht
                FROM domain_docflow.document_headers h
                WHERE h.tenant_id = :t AND h.deleted_at IS NULL
                ORDER BY h.created_at DESC LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        out = []
        for r in rows:
            n = int(r["n_art"])
            out.append({
                "doc_number": r["doc_number"], "doc_type": r["doc_type"], "status": r["status"],
                "datum": _iso(r["document_date"]),
                "brutto": float(r["total_gross"]) if r["total_gross"] is not None else None,
                "artefakte": n,
                "revisionssicher": bool(n > 0 and not r["art_ohne_hash"]),
                "gebucht": bool(r["gebucht"]),
            })
        return out
