"""Klärfall-Inbox für nicht zuordenbare Auto-Captures (KIM).

Wenn `CrmAutoCaptureService.capture()` keinen Kunden auflösen kann, wird der
Vorgang hier persistiert (statt still verloren zu gehen). Innen-/Aussendienst
ordnet ihn manuell einem Kunden zu — beim Zuordnen wird der reguläre Kontakt in
public.kunden_kontakte angelegt (bediener='AUTO'), und der Inbox-Eintrag auf
`zugeordnet` gesetzt. Alternativ kann ein Eintrag `verworfen` werden.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_COLS = (
    "id, channel, direction, peer, betreff, zusammenfassung, content, verweis, "
    "status, kunden_nr, kontakt_id, resolved_by, resolved_at, created_at"
)


class CrmCaptureInboxService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _row(self, r) -> dict:
        d = dict(r)
        d["id"] = str(d["id"])
        if d.get("kontakt_id") is not None:
            d["kontakt_id"] = str(d["kontakt_id"])
        for k in ("resolved_at", "created_at"):
            if d.get(k) is not None:
                d[k] = d[k].isoformat()
        return d

    # ── Schreiben (aus Auto-Capture) ──────────────────────────────────────────
    def add(
        self,
        *,
        channel: str,
        direction: str = "ein",
        peer: Optional[str] = None,
        betreff: Optional[str] = None,
        zusammenfassung: Optional[str] = None,
        content: Optional[str] = None,
        verweis: Optional[str] = None,
    ) -> dict:
        """Legt einen Klärfall an. Idempotent über `verweis` (gleicher verweis
        liefert den bestehenden Eintrag zurück, kein Duplikat)."""
        if verweis:
            existing = self.db.execute(
                text(
                    f"SELECT {_COLS} FROM public.crm_capture_inbox "
                    "WHERE tenant_id = :t AND verweis = :v LIMIT 1"
                ),
                {"t": self.tenant_id, "v": verweis},
            ).mappings().first()
            if existing:
                return {"status": "duplicate", **self._row(existing)}

        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO public.crm_capture_inbox
                    (id, tenant_id, channel, direction, peer, betreff,
                     zusammenfassung, content, verweis, status)
                VALUES
                    (:id, :t, :channel, :direction, :peer, :betreff,
                     :zus, :content, :verweis, 'offen')
                """
            ),
            {
                "id": new_id,
                "t": self.tenant_id,
                "channel": (channel or "telefon")[:16],
                "direction": (direction or "ein")[:8],
                "peer": (peer or None),
                "betreff": (betreff or None),
                "zus": (zusammenfassung or None),
                "content": (content or None),
                "verweis": (verweis or None),
            },
        )
        self.db.commit()
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM public.crm_capture_inbox WHERE id = :id"), {"id": new_id}
        ).mappings().first()
        return {"status": "inbox", **self._row(r)}

    # ── Lesen ─────────────────────────────────────────────────────────────────
    def list(self, status: str = "offen", limit: int = 200) -> list[dict]:
        rows = self.db.execute(
            text(
                f"SELECT {_COLS} FROM public.crm_capture_inbox "
                "WHERE tenant_id = :t AND (:s = 'alle' OR status = :s) "
                "ORDER BY created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "s": status or "offen", "lim": max(1, min(limit, 1000))},
        ).mappings().all()
        return [self._row(r) for r in rows]

    def count_open(self) -> int:
        r = self.db.execute(
            text("SELECT count(*) AS n FROM public.crm_capture_inbox WHERE tenant_id = :t AND status = 'offen'"),
            {"t": self.tenant_id},
        ).mappings().first()
        return int(r["n"]) if r else 0

    def _get(self, inbox_id: str) -> Optional[dict]:
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM public.crm_capture_inbox WHERE id = :id AND tenant_id = :t"),
            {"id": inbox_id, "t": self.tenant_id},
        ).mappings().first()
        return self._row(r) if r else None

    # ── Zuordnen / Verwerfen ──────────────────────────────────────────────────
    def assign(self, inbox_id: str, kunden_nr: str, resolved_by: Optional[str] = None) -> dict:
        """Ordnet den Klärfall einem Kunden zu: legt den Kontakt in
        kunden_kontakte an und markiert den Inbox-Eintrag als zugeordnet."""
        row = self._get(inbox_id)
        if not row:
            return {"status": "not_found"}
        if row["status"] == "zugeordnet":
            return {"status": "already_assigned", **row}

        from app.services.crm_kontakt_service import CrmKontaktService

        created = CrmKontaktService(self.db, self.tenant_id).create({
            "kunden_nr": kunden_nr,
            "richtung": row.get("direction") or "ein",
            "art": row.get("channel") or "telefon",
            "kurzinfo": (row.get("betreff") or "Kontakt")[:200],
            "notiz": row.get("zusammenfassung") or row.get("content") or None,
            "bediener": "AUTO",
            "verweis": row.get("verweis"),
        })
        self.db.execute(
            text(
                "UPDATE public.crm_capture_inbox SET status='zugeordnet', kunden_nr=:k, "
                "kontakt_id=:kid, resolved_by=:by, resolved_at=now(), updated_at=now() "
                "WHERE id=:id AND tenant_id=:t"
            ),
            {
                "k": kunden_nr,
                "kid": created.get("id"),
                "by": resolved_by or "KIM",
                "id": inbox_id,
                "t": self.tenant_id,
            },
        )
        self.db.commit()
        return {"status": "assigned", "kontakt_id": created.get("id"),
                "kunden_nr": kunden_nr, "id": inbox_id}

    def dismiss(self, inbox_id: str, resolved_by: Optional[str] = None) -> dict:
        row = self._get(inbox_id)
        if not row:
            return {"status": "not_found"}
        self.db.execute(
            text(
                "UPDATE public.crm_capture_inbox SET status='verworfen', resolved_by=:by, "
                "resolved_at=now(), updated_at=now() WHERE id=:id AND tenant_id=:t"
            ),
            {"by": resolved_by or "KIM", "id": inbox_id, "t": self.tenant_id},
        )
        self.db.commit()
        return {"status": "dismissed", "id": inbox_id}
