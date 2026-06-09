"""Kunden-Präsente (KIM-S3) — kundenbezogene Geschenke-PR mit Jahr-/AP-Filter."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
_COLS = (
    "id, tenant_id, kunden_nr, contact_id, year, gift_date, occasion, gift_name, "
    "quantity, sales_rep, operator, representative_officer, sequence_number, created_at, updated_at"
)


class CrmGiftService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    @staticmethod
    def _row(r) -> dict:
        d = dict(r)
        d["id"] = str(d["id"])
        if d.get("contact_id") is not None:
            d["contact_id"] = str(d["contact_id"])
        if d.get("quantity") is not None:
            d["quantity"] = float(d["quantity"])
        for k in ("gift_date", "created_at", "updated_at"):
            if d.get(k) is not None:
                d[k] = d[k].isoformat()
        return d

    def list(self, kunden_nr: str, year: Optional[int] = None, contact_id: Optional[str] = None) -> list[dict]:
        sql = f"SELECT {_COLS} FROM public.crm_gifts WHERE tenant_id = :t AND kunden_nr = :k"
        params: dict = {"t": self.tenant_id, "k": kunden_nr}
        if year is not None:
            sql += " AND year = :y"
            params["y"] = year
        if contact_id:
            sql += " AND contact_id = :c"
            params["c"] = contact_id
        sql += " ORDER BY gift_date DESC NULLS LAST, created_at DESC"
        rows = self.db.execute(text(sql), params).mappings().all()
        return [self._row(r) for r in rows]

    def create(self, kunden_nr: str, data: dict) -> dict:
        new_id = str(uuid.uuid4())
        self.db.execute(
            text(
                """
                INSERT INTO public.crm_gifts
                    (id, tenant_id, kunden_nr, contact_id, year, gift_date, occasion, gift_name,
                     quantity, sales_rep, operator, representative_officer, sequence_number)
                VALUES
                    (:id, :t, :k, :cid, :year, :gdate, :occ, :gname,
                     :qty, :rep, :op, :rof, :seq)
                """
            ),
            {
                "id": new_id, "t": self.tenant_id, "k": kunden_nr,
                "cid": data.get("contactId") or None,
                "year": int(data.get("year") or 0),
                "gdate": data.get("date") or None,
                "occ": data.get("occasion"),
                "gname": data.get("giftName"),
                "qty": data.get("quantity") if data.get("quantity") is not None else 1,
                "rep": data.get("salesRepId"),
                "op": data.get("operatorId"),
                "rof": data.get("representativeOfficerId"),
                "seq": data.get("sequenceNumber"),
            },
        )
        self.db.commit()
        r = self.db.execute(text(f"SELECT {_COLS} FROM public.crm_gifts WHERE id = :id"), {"id": new_id}).mappings().first()
        return self._row(r)

    def update(self, gift_id: str, data: dict) -> dict:
        self.db.execute(
            text(
                """
                UPDATE public.crm_gifts SET
                    contact_id = :cid, year = :year, gift_date = :gdate, occasion = :occ,
                    gift_name = :gname, quantity = :qty, sales_rep = :rep, operator = :op,
                    representative_officer = :rof, sequence_number = :seq, updated_at = now()
                WHERE id = :id AND tenant_id = :t
                """
            ),
            {
                "id": gift_id, "t": self.tenant_id,
                "cid": data.get("contactId") or None,
                "year": int(data.get("year") or 0),
                "gdate": data.get("date") or None,
                "occ": data.get("occasion"),
                "gname": data.get("giftName"),
                "qty": data.get("quantity") if data.get("quantity") is not None else 1,
                "rep": data.get("salesRepId"),
                "op": data.get("operatorId"),
                "rof": data.get("representativeOfficerId"),
                "seq": data.get("sequenceNumber"),
            },
        )
        self.db.commit()
        r = self.db.execute(text(f"SELECT {_COLS} FROM public.crm_gifts WHERE id = :id"), {"id": gift_id}).mappings().first()
        return self._row(r) if r else {}

    def delete(self, gift_id: str) -> None:
        self.db.execute(
            text("DELETE FROM public.crm_gifts WHERE id = :id AND tenant_id = :t"),
            {"id": gift_id, "t": self.tenant_id},
        )
        self.db.commit()
