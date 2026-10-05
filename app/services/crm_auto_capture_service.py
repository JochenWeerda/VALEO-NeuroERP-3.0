"""Automatische Kontakt-Erfassung (KIM-AUTOCAPTURE).

Ein-/ausgehende Kommunikation (Telefon mit Transkript, E-Mail, WhatsApp) wird zu
einem Kunden aufgelöst, per LLM-Gateway zu Betreff + Kurzfassung verdichtet und
automatisch als Kontakt (public.kunden_kontakte, bediener='AUTO') angelegt — damit
nichts Wesentliches verloren geht. Wiederverwendung: LLMGateway (Summary, mit
deterministischem Fallback), CrmKontaktService (Persistenz). Idempotent über `verweis`.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.crm_kontakt_service import CrmKontaktService

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_ART_BY_CHANNEL = {
    "telefon": "telefon",
    "email": "email",
    "whatsapp": "whatsapp",
    "persoenlich": "persoenlich",
    "brief": "brief",
    "fax": "fax",
}


def _norm_phone(raw: str) -> str:
    d = re.sub(r"[^\d]", "", raw or "")
    if d.startswith("0049"):
        d = d[4:]
    elif d.startswith("49") and len(d) > 9:
        d = d[2:]
    elif d.startswith("0"):
        d = d[1:]
    return d


class CrmAutoCaptureService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Kunden-Auflösung ──────────────────────────────────────────────────────
    def _resolve_by_phone(self, peer: Optional[str]) -> Optional[str]:
        norm = _norm_phone(peer or "")
        if len(norm) < 4:
            return None
        tail = norm[-7:]
        try:
            r = self.db.execute(
                text(
                    "SELECT kunden_nr FROM public.kunden "
                    "WHERE tel IS NOT NULL AND regexp_replace(tel, '[^0-9]', '', 'g') LIKE :tail "
                    "ORDER BY length(tel) LIMIT 1"
                ),
                {"tail": f"%{tail}"},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return None
        return r["kunden_nr"] if r else None

    def _resolve_by_email(self, peer: Optional[str]) -> Optional[str]:
        if not peer or "@" not in peer:
            return None
        try:
            r = self.db.execute(
                text("SELECT kunden_nr FROM public.kunden WHERE lower(email) = lower(:e) LIMIT 1"),
                {"e": peer.strip()},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return None
        return r["kunden_nr"] if r else None

    def resolve_customer(self, channel: str, peer: Optional[str], kunden_nr: Optional[str]) -> Optional[str]:
        if kunden_nr:
            return kunden_nr
        if channel == "email":
            return self._resolve_by_email(peer)
        return self._resolve_by_phone(peer)  # telefon/whatsapp/…

    # ── Zusammenfassung (LLM mit Fallback) ────────────────────────────────────
    def _summarize(self, channel: str, content: str) -> tuple[str, str]:
        text_in = (content or "").strip()
        if not text_in:
            return (f"{channel.capitalize()}-Kontakt", "")
        try:
            from app.services.llm_gateway import LLMGateway

            gw = LLMGateway(self.db, self.tenant_id)
            out = gw.complete_or_none(
                prompt=(
                    f"Fasse diesen {channel}-Kontakt für eine CRM-Kontakthistorie zusammen. "
                    "Antworte NUR als JSON {\"betreff\": <max 80 Zeichen>, \"zusammenfassung\": <1-3 Sätze>}.\n\n"
                    + text_in[:4000]
                ),
                system="Du bist ein CRM-Assistent für einen Agrarhandel. Antworte knapp auf Deutsch.",
                max_tokens=400,
            )
            if out:
                m = re.search(r"\{.*\}", out, re.DOTALL)
                data = json.loads(m.group(0) if m else out)
                betreff = (data.get("betreff") or "").strip()[:120]
                zus = (data.get("zusammenfassung") or "").strip()
                if betreff or zus:
                    return (betreff or zus[:80], zus or text_in)
        except Exception:
            pass
        # Deterministischer Fallback: erste Zeile als Betreff, Volltext als Notiz.
        first_line = text_in.splitlines()[0][:80]
        return (first_line or f"{channel.capitalize()}-Kontakt", text_in)

    def _sender_domain(self, peer: Optional[str]) -> Optional[str]:
        if not peer or "@" not in peer:
            return None
        return peer.rsplit("@", 1)[1].strip().lower() or None

    def _propose_email_terms(
        self,
        *,
        mail_id: str,
        subject: Optional[str],
        content: str,
        peer: Optional[str],
        received_at: Optional[datetime],
    ) -> dict:
        if not mail_id or not content.strip():
            return {"status": "skipped", "reason": "missing_mail_id_or_content"}
        try:
            from app.services.calendar_projection_service import CalendarProjectionService

            result = CalendarProjectionService(self.db).propose_email_terms(
                self.tenant_id,
                mail_id=mail_id,
                subject=subject,
                body=content,
                received_at=received_at or datetime.now(UTC),
                sender_domain=self._sender_domain(peer),
            )
            return {"status": "ok", **result}
        except Exception as exc:  # pragma: no cover - defensive capture path
            self.db.rollback()
            return {"status": "error", "reason": str(exc)[:200]}

    # ── Erfassung ─────────────────────────────────────────────────────────────
    def _existing_by_verweis(self, kunden_nr: str, verweis: str) -> Optional[dict]:
        try:
            r = self.db.execute(
                text(
                    "SELECT id FROM public.kunden_kontakte "
                    "WHERE tenant_id = :t AND kunden_nr = :k AND verweis = :v LIMIT 1"
                ),
                {"t": self.tenant_id, "k": kunden_nr, "v": verweis},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return None
        return {"id": str(r["id"])} if r else None

    def capture(
        self,
        *,
        channel: str,
        direction: str = "incoming",
        peer: Optional[str] = None,
        content: str = "",
        kunden_nr: Optional[str] = None,
        betreff: Optional[str] = None,
        verweis: Optional[str] = None,
        bediener: str = "AUTO",
        to_inbox: bool = True,
        received_at: Optional[datetime] = None,
    ) -> dict:
        art = _ART_BY_CHANNEL.get((channel or "").lower(), "telefon")
        richtung = "ein" if (direction or "").lower().startswith(("in", "ein")) else "aus"

        resolved = self.resolve_customer(art, peer, kunden_nr)
        if not resolved:
            # Nicht auflösbar -> nicht still verlieren: in die Klärfall-Inbox legen,
            # damit Innen-/Aussendienst den Kontakt manuell einem Kunden zuordnen kann.
            auto_betreff, notiz = self._summarize(art, content)
            inbox = None
            if to_inbox:
                from app.services.crm_capture_inbox_service import CrmCaptureInboxService

                inbox = CrmCaptureInboxService(self.db, self.tenant_id).add(
                    channel=art,
                    direction=richtung,
                    peer=peer,
                    betreff=(betreff or auto_betreff),
                    zusammenfassung=notiz,
                    content=content,
                    verweis=verweis,
                )
            calendar_proposals = (
                self._propose_email_terms(
                    mail_id=verweis or str((inbox or {}).get("id") or ""),
                    subject=betreff or auto_betreff,
                    content=content,
                    peer=peer,
                    received_at=received_at,
                )
                if art == "email"
                else {"status": "skipped", "reason": "not_email"}
            )
            return {"status": "unresolved", "channel": art, "peer": peer,
                    "inbox_id": (inbox or {}).get("id"), "calendar_proposals": calendar_proposals}

        if verweis:
            existing = self._existing_by_verweis(resolved, verweis)
            if existing:
                return {"status": "duplicate", "id": existing["id"], "kunden_nr": resolved}

        auto_betreff, notiz = self._summarize(art, content)
        kurzinfo = (betreff or auto_betreff)[:200]

        created = CrmKontaktService(self.db, self.tenant_id).create({
            "kunden_nr": resolved,
            "richtung": richtung,
            "art": art,
            "kurzinfo": kurzinfo,
            "notiz": notiz or content or None,
            "bediener": bediener or "AUTO",
            "verweis": verweis,
        })
        calendar_proposals = (
            self._propose_email_terms(
                mail_id=verweis or str(created.get("id") or ""),
                subject=betreff or auto_betreff,
                content=content,
                peer=peer,
                received_at=received_at,
            )
            if art == "email"
            else {"status": "skipped", "reason": "not_email"}
        )
        return {"status": "created", "id": created.get("id"), "kunden_nr": resolved,
                "art": art, "richtung": richtung, "betreff": kurzinfo,
                "calendar_proposals": calendar_proposals}
