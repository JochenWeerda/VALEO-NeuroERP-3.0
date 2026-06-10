"""Kunden-Zusammenführung (DOM-CRM-004.2).

Führt eine Dublette (Verlierer) in einen Master-Kunden zusammen: die 1:n-CRM-
Historie wird umgehängt, der Verlierer per `geloescht=true` + `merged_into`
markiert (nicht physisch gelöscht → revisionssicher), und der Vorgang in
public.crm_merge_log protokolliert. Alles in EINER Transaktion.

Bewusst nur die CRM-Historie (Kontakte/Ansprechpartner/Präsente/…) — Finanz-/
Belegdaten hängen an business_partner_id und bleiben unberührt (separater
Business-Partner-Merge). 1:1-Profilsatelliten des Verlierers werden nicht
umgehängt (PK-Konflikt-Gefahr); sie verbleiben am soft-gelöschten Verlierer.
"""

from __future__ import annotations

import json
import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# 1:n-Historientabellen, deren kunden_nr auf den Master umgehängt wird.
_MOVABLE = [
    "kunden_kontakte", "kunden_ansprechpartner", "crm_gifts", "crm_capture_inbox",
    "crm_notifications", "crm_contact_marketing_prefs", "tapi_calls",
    "whatsapp_bestellungen", "kunden_adressen", "kunden_email_verteiler", "kunden_freitext",
]


class MergeError(Exception):
    """Fachlicher Fehler bei der Zusammenführung (→ HTTP 422)."""


class CrmMergeService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _kunde(self, nr: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT kunden_nr, name1, plz, ort, COALESCE(geloescht,false) AS geloescht, merged_into "
                 "FROM public.kunden WHERE kunden_nr = :nr"),
            {"nr": nr},
        ).mappings().first()
        return dict(r) if r else None

    def _count(self, table: str, nr: str) -> int:
        try:
            return int(self.db.execute(
                text(f"SELECT count(*) FROM public.{table} WHERE kunden_nr = :nr"), {"nr": nr}
            ).scalar() or 0)
        except Exception:
            self.db.rollback()
            return 0

    def _validate(self, master_nr: str, duplicate_nr: str) -> tuple[dict, dict]:
        if master_nr == duplicate_nr:
            raise MergeError("Master und Dublette sind identisch.")
        master = self._kunde(master_nr)
        dup = self._kunde(duplicate_nr)
        if not master:
            raise MergeError(f"Master-Kunde nicht gefunden: {master_nr}")
        if not dup:
            raise MergeError(f"Dublette nicht gefunden: {duplicate_nr}")
        if master["geloescht"]:
            raise MergeError("Master-Kunde ist gelöscht/zusammengeführt.")
        if dup["geloescht"]:
            raise MergeError("Dublette ist bereits gelöscht/zusammengeführt.")
        return master, dup

    def preview(self, master_nr: str, duplicate_nr: str) -> dict:
        master, dup = self._validate(master_nr, duplicate_nr)
        moved = {t: self._count(t, duplicate_nr) for t in _MOVABLE}
        return {
            "ok": True,
            "master": master, "duplicate": dup,
            "verschiebt": {t: c for t, c in moved.items() if c > 0},
            "summe_datensaetze": sum(moved.values()),
        }

    def merge(self, master_nr: str, duplicate_nr: str, bediener: str = "KIM") -> dict:
        master, dup = self._validate(master_nr, duplicate_nr)
        moved: dict[str, int] = {}
        try:
            for table in _MOVABLE:
                res = self.db.execute(
                    text(f"UPDATE public.{table} SET kunden_nr = :m WHERE kunden_nr = :d"),
                    {"m": master_nr, "d": duplicate_nr},
                )
                if res.rowcount:
                    moved[table] = int(res.rowcount)
            self.db.execute(
                text("UPDATE public.kunden SET geloescht = true, merged_into = :m, geaendert_am = now() "
                     "WHERE kunden_nr = :d"),
                {"m": master_nr, "d": duplicate_nr},
            )
            self.db.execute(
                text("INSERT INTO public.crm_merge_log (id, tenant_id, master_nr, duplicate_nr, moved, bediener) "
                     "VALUES (:id, :t, :m, :d, CAST(:moved AS JSONB), :by)"),
                {"id": str(uuid.uuid4()), "t": self.tenant_id, "m": master_nr, "d": duplicate_nr,
                 "moved": json.dumps(moved), "by": bediener},
            )
            self.db.commit()
        except Exception as exc:  # noqa: BLE001 — atomar: bei Fehler kein Teil-Merge
            self.db.rollback()
            raise MergeError(f"Zusammenführung fehlgeschlagen: {exc}")
        return {"ok": True, "master_nr": master_nr, "duplicate_nr": duplicate_nr,
                "verschoben": moved, "summe_datensaetze": sum(moved.values())}
