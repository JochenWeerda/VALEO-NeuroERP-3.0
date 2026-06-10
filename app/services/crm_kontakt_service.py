"""Kunden-Kontakte (Kontakthistorie + Wiedervorlage) für das Kunden-Cockpit."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_COLS = (
    "id, kunden_nr, richtung, art, kurzinfo, notiz, wiedervorlage, "
    "weiterleitung_an, bediener, verweis, erledigt, created_at"
)


class CrmKontaktService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _row(self, r) -> dict:
        d = dict(r)
        if d.get("wiedervorlage") is not None:
            d["wiedervorlage"] = str(d["wiedervorlage"])
        if d.get("created_at") is not None:
            d["created_at"] = d["created_at"].isoformat()
        d["id"] = str(d["id"])
        return d

    def list_by_kunde(self, kunden_nr: str) -> list[dict]:
        # reviewed-safe: _COLS is a module-owned constant; customer and tenant are bound.
        rows = self.db.execute(
            text(f"SELECT {_COLS} FROM public.kunden_kontakte WHERE kunden_nr = :k AND tenant_id = :t ORDER BY created_at DESC"),
            {"k": kunden_nr, "t": self.tenant_id},
        ).mappings().all()
        return [self._row(r) for r in rows]

    def create(self, data: dict) -> dict:
        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO public.kunden_kontakte
                    (id, kunden_nr, richtung, art, kurzinfo, notiz, wiedervorlage,
                     weiterleitung_an, bediener, verweis, tenant_id)
                VALUES
                    (:id, :kunden_nr, :richtung, :art, :kurzinfo, :notiz, :wiedervorlage,
                     :weiterleitung_an, :bediener, :verweis, :tid)
                """
            ),
            {
                "id": new_id,
                "kunden_nr": data["kunden_nr"],
                "richtung": data.get("richtung") or "aus",
                "art": data.get("art") or "telefon",
                "kurzinfo": data.get("kurzinfo"),
                "notiz": data.get("notiz"),
                "wiedervorlage": data.get("wiedervorlage") or None,
                "weiterleitung_an": data.get("weiterleitung_an"),
                "bediener": data.get("bediener"),
                "verweis": data.get("verweis"),
                "tid": self.tenant_id,
            },
        )
        self.db.commit()
        # reviewed-safe: _COLS is a module-owned constant; the contact id is bound.
        r = self.db.execute(
            text(f"SELECT {_COLS} FROM public.kunden_kontakte WHERE id = :id"), {"id": new_id}
        ).mappings().first()
        return self._row(r)

    def set_erledigt(self, kontakt_id: str, erledigt: bool = True, ergebnis: Optional[str] = None) -> dict:
        # Serviceabschluss: optionales Ergebnis revisionsfest an die Notiz anhängen.
        if ergebnis:
            self.db.execute(
                text(
                    "UPDATE public.kunden_kontakte SET erledigt = :e, "
                    "notiz = COALESCE(notiz || E'\\n', '') || :erg, updated_at = now() "
                    "WHERE id = :id AND tenant_id = :t"
                ),
                {"e": erledigt, "erg": f"[Erledigt] {ergebnis}", "id": kontakt_id, "t": self.tenant_id},
            )
        else:
            self.db.execute(
                text("UPDATE public.kunden_kontakte SET erledigt = :e, updated_at = now() WHERE id = :id AND tenant_id = :t"),
                {"e": erledigt, "id": kontakt_id, "t": self.tenant_id},
            )
        self.db.commit()
        # reviewed-safe: _COLS is a module-owned constant; the contact id is bound.
        r = self.db.execute(text(f"SELECT {_COLS} FROM public.kunden_kontakte WHERE id = :id"), {"id": kontakt_id}).mappings().first()
        return self._row(r) if r else {}

    def wiedervorlagen_offen(self, tage: int = 14) -> list[dict]:
        rows = self.db.execute(
            text(
                f"SELECT {_COLS}, (SELECT name1 FROM public.kunden k WHERE k.kunden_nr = kk.kunden_nr) AS kunde "
                "FROM public.kunden_kontakte kk WHERE tenant_id = :t AND erledigt = FALSE "
                "AND wiedervorlage IS NOT NULL AND wiedervorlage <= (current_date + (:d || ' days')::interval) "
                "ORDER BY wiedervorlage"
            ),
            {"t": self.tenant_id, "d": tage},
        ).mappings().all()
        from datetime import date

        out = []
        today = date.today()
        for r in rows:
            d = self._row(r)
            d["kunde"] = r.get("kunde")
            wv = r.get("wiedervorlage")
            wvd = wv.date() if hasattr(wv, "date") else wv
            try:
                d["ueberfaellig"] = bool(wvd is not None and wvd < today)
            except TypeError:
                d["ueberfaellig"] = False
            out.append(d)
        return out
