"""CRM-Benachrichtigungen — internes In-App-Postfach + externe Fachberater-Mail.

Teil von KIM-L3-BACKEND-001. Aus dem Kontakt-CC im KIM-Cockpit werden interne
Mitarbeiter/Abteilungen (persistente Notification, In-App sichtbar) oder externe
Fachberater (E-Mail, best-effort ueber den vorhandenen NotificationService)
benachrichtigt. Ohne SMTP-Konfiguration bleibt die externe Zustellung graceful
protokolliert (Status 'queued') statt zu scheitern.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_COLS = (
    "id, tenant_id, kunden_nr, kontakt_id, sender, recipient, channel, "
    "betreff, kommentar, status, created_at, read_at"
)


class CrmNotificationService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    @staticmethod
    def _row(r) -> dict:
        d = dict(r)
        d["id"] = str(d["id"])
        if d.get("kontakt_id") is not None:
            d["kontakt_id"] = str(d["kontakt_id"])
        for k in ("created_at", "read_at"):
            if d.get(k) is not None:
                d[k] = d[k].isoformat()
        return d

    def _insert(self, *, recipient: str, channel: str, betreff: Optional[str], kommentar: Optional[str],
                sender: Optional[str], kunden_nr: Optional[str], kontakt_id: Optional[str],
                status: str) -> dict:
        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO public.crm_notifications
                    (id, tenant_id, kunden_nr, kontakt_id, sender, recipient, channel,
                     betreff, kommentar, status)
                VALUES
                    (:id, :tid, :knr, :kid, :sender, :recipient, :channel,
                     :betreff, :kommentar, :status)
                """
            ),
            {
                "id": new_id, "tid": self.tenant_id, "knr": kunden_nr,
                "kid": kontakt_id, "sender": sender, "recipient": recipient,
                "channel": channel, "betreff": betreff, "kommentar": kommentar,
                "status": status,
            },
        )
        self.db.commit()
        # reviewed-safe: _COLS is a module-owned constant; the identifier is bound.
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM public.crm_notifications WHERE id = :id"), {"id": new_id}
        ).mappings().first()
        return self._row(r)

    def notify_internal(self, *, recipient: str, betreff: Optional[str] = None,
                        kommentar: Optional[str] = None, sender: Optional[str] = None,
                        kunden_nr: Optional[str] = None, kontakt_id: Optional[str] = None) -> dict:
        """Persistente interne Benachrichtigung an Mitarbeiter/Abteilung (In-App-Postfach)."""
        return self._insert(
            recipient=recipient, channel="internal", betreff=betreff, kommentar=kommentar,
            sender=sender, kunden_nr=kunden_nr, kontakt_id=kontakt_id, status="unread",
        )

    def notify_external(self, *, email: str, betreff: Optional[str] = None,
                        kommentar: Optional[str] = None, sender: Optional[str] = None,
                        kunden_nr: Optional[str] = None, kontakt_id: Optional[str] = None) -> dict:
        """Externe Fachberater-Mail (best-effort) + protokollierter Datensatz."""
        status = "queued"
        try:
            from app.services.notification_service import NotificationService

            result = NotificationService().send_notification(
                "email", email, betreff or "VALEO NeuroERP — CRM-Hinweis", kommentar or "",
            )
            status = "sent" if (result or {}).get("success") else "queued"
        except Exception as exc:  # best-effort: ohne SMTP/Config bleibt es 'queued'
            logger.info("Externe Benachrichtigung konnte nicht direkt versendet werden: %s", exc)
            status = "queued"
        return self._insert(
            recipient=email, channel="email", betreff=betreff, kommentar=kommentar,
            sender=sender, kunden_nr=kunden_nr, kontakt_id=kontakt_id, status=status,
        )

    def dispatch_cc(self, *, cc: str, betreff: Optional[str], kommentar: Optional[str],
                    sender: Optional[str], kunden_nr: Optional[str],
                    kontakt_id: Optional[str] = None) -> dict:
        """CC-Wert routen: enthaelt '@' -> externe Mail, sonst interner Empfaenger."""
        if "@" in (cc or ""):
            return self.notify_external(
                email=cc, betreff=betreff, kommentar=kommentar, sender=sender,
                kunden_nr=kunden_nr, kontakt_id=kontakt_id,
            )
        return self.notify_internal(
            recipient=cc, betreff=betreff, kommentar=kommentar, sender=sender,
            kunden_nr=kunden_nr, kontakt_id=kontakt_id,
        )

    def inbox(self, recipient: str, only_unread: bool = False, limit: int = 50) -> list[dict]:
        sql = (
            f"SELECT {_COLS} FROM public.crm_notifications "
            "WHERE tenant_id = :t AND recipient = :r"
        )
        if only_unread:
            sql += " AND status = 'unread'"
        sql += " ORDER BY created_at DESC LIMIT :lim"
        rows = self.db.execute(text(sql), {"t": self.tenant_id, "r": recipient, "lim": limit}).mappings().all()
        return [self._row(r) for r in rows]

    def mark_read(self, notification_id: str) -> dict:
        self.db.execute(
            text(
                "UPDATE public.crm_notifications SET status = 'read', read_at = now() "
                "WHERE id = :id AND tenant_id = :t"
            ),
            {"id": notification_id, "t": self.tenant_id},
        )
        self.db.commit()
        # reviewed-safe: _COLS is a module-owned constant; the identifier is bound.
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM public.crm_notifications WHERE id = :id"), {"id": notification_id}
        ).mappings().first()
        return self._row(r) if r else {}
