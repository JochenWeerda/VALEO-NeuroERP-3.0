"""Ansprechpartner-Erweiterung (KIM-S4): Werbe-/Marketingpräferenzen + Pseudonymisierung."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_VALID_PREF = {"none", "company", "private"}


class CrmContactExtService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Marketing-/Werbepräferenzen ───────────────────────────────────────────
    def list_marketing(self, contact_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, contact_id, kunden_nr, category_code, category_label, preference, updated_at "
                "FROM public.crm_contact_marketing_prefs WHERE tenant_id = :t AND contact_id = :c "
                "ORDER BY category_label NULLS LAST, category_code"
            ),
            {"t": self.tenant_id, "c": contact_id},
        ).mappings().all()
        out = []
        for r in rows:
            d = dict(r)
            d["id"] = str(d["id"])
            if d.get("updated_at") is not None:
                d["updated_at"] = d["updated_at"].isoformat()
            out.append(d)
        return out

    def set_marketing(self, contact_id: str, category_code: str, preference: str,
                      category_label: Optional[str] = None, kunden_nr: Optional[str] = None) -> dict:
        pref = preference if preference in _VALID_PREF else "none"
        self.db.execute(
            text(
                """
                INSERT INTO public.crm_contact_marketing_prefs
                    (id, tenant_id, contact_id, kunden_nr, category_code, category_label, preference)
                VALUES (:id, :t, :c, :k, :code, :label, :pref)
                ON CONFLICT (tenant_id, contact_id, category_code)
                DO UPDATE SET preference = EXCLUDED.preference,
                              category_label = COALESCE(EXCLUDED.category_label, public.crm_contact_marketing_prefs.category_label),
                              updated_at = now()
                """
            ),
            {
                "id": str(uuid.uuid4()), "t": self.tenant_id, "c": contact_id,
                "k": kunden_nr, "code": category_code, "label": category_label, "pref": pref,
            },
        )
        self.db.commit()
        return {"status": "success", "contact_id": contact_id, "category_code": category_code, "preference": pref}

    # ── DSGVO-Pseudonymisierung ────────────────────────────────────────────────
    def pseudonymize(self, contact_id: str) -> dict:
        """Personenbezogene Felder neutralisieren + Marker setzen (id ist serial-int)."""
        try:
            cid = int(contact_id)
        except (TypeError, ValueError):
            return {"status": "error", "detail": "Ungueltige Ansprechpartner-ID"}
        self.db.execute(
            text(
                "UPDATE public.kunden_ansprechpartner SET "
                "nachname = '[anonymisiert]', vorname = '', telefon1 = NULL, telefon2 = NULL, "
                "mobil = NULL, geburtsdatum = NULL, pseudonymized_at = now() "
                "WHERE id = :id"
            ),
            {"id": cid},
        )
        self.db.commit()
        return {"status": "success", "contact_id": contact_id}
