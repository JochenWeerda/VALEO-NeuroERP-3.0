"""Bescheid/Rückmeldung & Wiedervorlage am Vorgang (DOM-DOC-004.3).

Erfasst je Dokument/Vorgang Bescheide, Rückmeldungen und Wiedervorlagen
(domain_docflow.document_followups) mit Fälligkeit und Erledigt-Status und liefert
eine domänenweite Worklist offener (überfälliger) Wiedervorlagen.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_ARTEN = {"bescheid", "rueckmeldung", "wiedervorlage"}


def followup_overdue(faellig_am: Optional[date], status: Optional[str], today: date) -> bool:
    """Reine Überfälligkeits-Prüfung: offen + Fälligkeit in der Vergangenheit."""
    if (status or "offen").lower() != "offen":
        return False
    return bool(faellig_am and faellig_am < today)


def _iso(v):
    return v.isoformat() if hasattr(v, "isoformat") else v


class FollowupError(Exception):
    """Fachlicher Fehler bei Followups (→ HTTP 422)."""


class DocflowFollowupService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _header(self, doc: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, doc_number FROM domain_docflow.document_headers "
                 "WHERE tenant_id = :t AND (id::text = :v OR doc_number = :v) AND deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": doc},
        ).mappings().first()
        return dict(r) if r else None

    def create_followup(self, doc: str, art: str, betreff: Optional[str], text_body: Optional[str],
                        faellig_am: Optional[date] = None, bediener: str = "KIM") -> dict[str, Any]:
        header = self._header(doc)
        if not header:
            raise FollowupError(f"Dokument nicht gefunden: {doc}")
        art_norm = (art or "wiedervorlage").lower()
        if art_norm not in _ARTEN:
            raise FollowupError("Art muss bescheid, rueckmeldung oder wiedervorlage sein.")
        if not (betreff or "").strip():
            raise FollowupError("Betreff ist erforderlich.")
        if art_norm == "wiedervorlage" and not faellig_am:
            raise FollowupError("Wiedervorlage benötigt ein Fälligkeitsdatum.")
        fid = str(uuid.uuid4())
        self.db.execute(
            text("INSERT INTO domain_docflow.document_followups "
                 "(id, tenant_id, header_id, art, betreff, text, faellig_am, status, created_by) "
                 "VALUES (:id, :t, :h, :art, :betr, :txt, :fa, 'offen', :by)"),
            {"id": fid, "t": self.tenant_id, "h": header["id"], "art": art_norm,
             "betr": betreff, "txt": text_body, "fa": faellig_am, "by": bediener},
        )
        self.db.commit()
        return {"ok": True, "followup_id": fid, "doc_number": header["doc_number"], "art": art_norm}

    def complete_followup(self, followup_id: str, bediener: str = "KIM") -> dict[str, Any]:
        r = self.db.execute(
            text("SELECT id, status FROM domain_docflow.document_followups "
                 "WHERE id::text = :id AND tenant_id = :t LIMIT 1"),
            {"id": followup_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            raise FollowupError(f"Followup nicht gefunden: {followup_id}")
        if (r["status"] or "").lower() == "erledigt":
            raise FollowupError("Followup ist bereits erledigt.")
        self.db.execute(
            text("UPDATE domain_docflow.document_followups SET status='erledigt', erledigt_at=now(), "
                 "erledigt_von=:by WHERE id = :id AND tenant_id = :t"),
            {"by": bediener, "id": r["id"], "t": self.tenant_id},
        )
        self.db.commit()
        return {"ok": True, "followup_id": followup_id, "status": "erledigt"}

    def list_followups(self, doc: str) -> dict[str, Any]:
        header = self._header(doc)
        if not header:
            return {"found": False, "detail": "Dokument nicht gefunden."}
        today = date.today()
        rows = self.db.execute(
            text("SELECT id, art, betreff, text, faellig_am, status, erledigt_at, erledigt_von, created_at, created_by "
                 "FROM domain_docflow.document_followups WHERE header_id = :h AND tenant_id = :t "
                 "ORDER BY created_at DESC"),
            {"h": header["id"], "t": self.tenant_id},
        ).mappings().all()
        items = [self._row(r, today) for r in rows]
        return {
            "found": True, "doc_number": header["doc_number"], "followups": items,
            "summary": {
                "anzahl": len(items),
                "offen": sum(1 for i in items if i["status"] == "offen"),
                "ueberfaellig": sum(1 for i in items if i["ueberfaellig"]),
            },
        }

    def open_wiedervorlagen(self, limit: int = 100) -> list[dict]:
        today = date.today()
        rows = self.db.execute(
            text("SELECT f.id, f.art, f.betreff, f.faellig_am, f.status, f.created_by, h.doc_number "
                 "FROM domain_docflow.document_followups f "
                 "JOIN domain_docflow.document_headers h ON h.id = f.header_id AND h.tenant_id = f.tenant_id "
                 "WHERE f.tenant_id = :t AND f.status = 'offen' AND f.art = 'wiedervorlage' "
                 "ORDER BY f.faellig_am NULLS LAST LIMIT :lim"),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        out = []
        for r in rows:
            out.append({
                "followup_id": str(r["id"]), "doc_number": r["doc_number"], "betreff": r["betreff"],
                "faellig_am": _iso(r["faellig_am"]), "bediener": r["created_by"],
                "ueberfaellig": followup_overdue(r["faellig_am"], r["status"], today),
            })
        return out

    @staticmethod
    def _row(r, today: date) -> dict:
        return {
            "followup_id": str(r["id"]), "art": r["art"], "betreff": r["betreff"], "text": r["text"],
            "faellig_am": _iso(r["faellig_am"]), "status": r["status"],
            "ueberfaellig": followup_overdue(r["faellig_am"], r["status"], today),
            "erledigt_at": _iso(r["erledigt_at"]), "erledigt_von": r["erledigt_von"],
            "created_at": _iso(r["created_at"]), "created_by": r["created_by"],
        }
